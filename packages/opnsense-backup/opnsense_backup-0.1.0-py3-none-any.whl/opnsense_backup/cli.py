"""Parse the arguments, read the configuration file and fetch the backup
from the opnsense firewall
"""

import argparse
import re
import base64

from os import environ, path, scandir, stat, remove
from datetime import datetime as dt
from urllib.parse import urlparse

import httpx
from yaml import safe_load
from schema import Schema, SchemaError, And, Or, Optional, Use

from prometheus_client import Gauge, CollectorRegistry, write_to_textfile

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA512

__version__ = "0.1.0"

DEFAULT_CONFIGURATION_FILE = path.join(
    environ["HOME"], ".config", "opnsense-backup", "config.yml"
)

SCHEMA = Schema(
    {
        "opnsense": Schema(
            {
                Optional("url", default="https://opnsense"): And(
                    str, lambda s: len(s) > 0
                ),
                "key": And(str, lambda s: len(s) > 0),
                "secret": And(str, lambda s: len(s) > 0),
                Optional("ssl_verify", default=True): Or(
                    bool, And(str, lambda s: len(s) > 0)
                ),
                Optional("backup_password"): And(str, lambda s: len(s) > 0),
            },
        ),
        Optional(
            "output", default={"directory": ".", "name": "opnsense-%Y%m%d%H%M.xml"}
        ): Schema(
            {
                Optional("directory"): And(str, lambda s: len(s) > 0),
                Optional("name", default="opnsense-%Y%m%d%H%M.xml"): And(
                    str, lambda s: len(s) > 0
                ),
                Optional("keep"): And(Use(int), lambda x: x > 0),
            },
        ),
        Optional("metrics"): Schema(
            {
                "directory": And(str, lambda s: len(s) > 0),
                Optional("suffix"): And(str, lambda s: len(s) > 0),
            },
        ),
    }
)


def parse_arguments():
    """Parse the arguments

    Returns
    -------
    dict
        parsed arguments
    """

    parser = argparse.ArgumentParser(
        prog="opnsense-backup",
        description=f"A tool to fetch backups from the opnsense firewall (v{ __version__ })",
    )

    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_CONFIGURATION_FILE,
        metavar="FILE",
        type=argparse.FileType("r"),
        help="the configuration file (default: %(default)s)",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="the output file (default is specified in the configuration file)",
    )

    return vars(parser.parse_args())


def parse_configuration(stream):
    """Parse the configuration file

    Parameters
    ----------
    stream : io.IOBase | str
        Stream to read the configuration from.

    Returns
    -------
    dict
        Parsed and validated configuration
    """
    config = SCHEMA.validate(safe_load(stream))

    return config


def fetch_backup(opnsense_config: dict, out_file: str):
    """Fetch the backup from the firewall

    Parameters
    ----------
    opnsense_config : dict
        opnsense configuration
    out_file : str
        Path to the output file
    """
    response = httpx.get(
        opnsense_config["url"] + "/api/core/backup/download/this",
        auth=httpx.BasicAuth(
            username=opnsense_config["key"], password=opnsense_config["secret"]
        ),
        verify=opnsense_config["ssl_verify"],
    )

    response.raise_for_status()

    data = (
        response.content.decode()
        if not "backup_password" in opnsense_config
        else encrypt_opnsense_style(
            response.content, opnsense_config["backup_password"]
        )
    )

    with open(out_file, "w", encoding="utf-8") as file:
        file.write(data)


def rotate_files(output_config: dict):
    """Rotate the files

    Parameters
    ----------
    output_config : dict
        Configuration
    """
    files = sorted(
        [
            f.name
            for f in scandir(output_config["directory"])
            if f.is_file and re.search(r"\.xml$", f.name)
        ]
    )

    while len(files) > output_config["keep"]:
        remove(path.join(output_config["directory"], files.pop(0)))


def encrypt_opnsense_style(data: bytes, password: str) -> str:
    """
    Encrypts a byte array (e.g., config XML bytes) exactly like OPNsense does for
    its configuration backups.

    - AES-256-CBC
    - Key derivation: PBKDF2-HMAC-SHA512 with 100,000 iterations
    - Random 8-byte salt (OpenSSL 'salted' format: 'Salted__' + salt + ciphertext)
    - PKCS7 padding
    - The encrypted payload is then base64-encoded and wrapped with OPNsense headers/footers

    Returns the full encrypted backup string as seen in downloaded .xml files.
    """
    # Generate random 8-byte salt
    salt = get_random_bytes(8)

    # Derive 32-byte key + 16-byte IV using PBKDF2-HMAC-SHA512, 100000 iterations
    key_iv = PBKDF2(
        password=password.encode("utf-8"),
        salt=salt,
        dkLen=48,  # 32 bytes key + 16 bytes IV
        count=100000,
        hmac_hash_module=SHA512,
    )
    key = key_iv[:32]
    iv = key_iv[32:48]

    # Encrypt with AES-256-CBC and PKCS7 padding
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(pad(data, AES.block_size))

    # OpenSSL salted format
    encrypted_payload = b"Salted__" + salt + ciphertext

    # Base64 encode the payload
    b64_payload = base64.b64encode(encrypted_payload).decode("utf-8")

    # Split into 76-character lines (OPNsense uses 76, common for base64 in text files)
    b64_lines = "\n".join(
        [b64_payload[i : i + 76] for i in range(0, len(b64_payload), 76)]
    )

    # Add OPNsense wrapper (current as of 2024/2025 versions)
    header = (
        "---- BEGIN config.xml ----\n"
        "Version: OPNsense 25.7.10\n"
        "Cipher: AES-256-CBC\n"
        "PBKDF2: 100000\n"
        "Hash: SHA512\n"
        "\n"
    )
    footer = "\n---- END config.xml ----\n"

    full_backup = header + b64_lines + footer

    return full_backup


def main():
    """_summary_

    Raises
    ------
    ValueError
        Configuration is invalid
    ValueError
        Output directory does not exist
    """
    arguments = parse_arguments()

    try:
        config = parse_configuration(arguments["config"])
    except SchemaError as ex:
        raise ValueError(
            "configuration invalid\n" + str(ex.with_traceback(None))
        ) from None

    arguments["config"].close()

    now = dt.now()

    # If the file was given through an argument, use that and skip the rotation
    # If not, use the configuration to construct the file name and do the rotation
    # if requested and the directory was provided as an absolute path
    if arguments["output"] is not None:
        out_file = arguments["output"]
        rotate = False
    else:
        if not path.isdir(config["output"]["directory"]):
            raise ValueError(
                f"Target directory {config['output']['directory']} does not exist or is not a directory"  # pylint: disable=line-too-long
            )
        rotate = (
            path.isabs(config["output"]["directory"]) and "keep" in config["output"]
        )
        out_file = path.join(
            config["output"]["directory"], now.strftime(config["output"]["name"])
        )

    fetch_backup(config["opnsense"], out_file)

    if rotate:
        rotate_files(config["output"])

    if "metrics" in config:
        registry = CollectorRegistry()
        backup_time = Gauge(
            "opnsense_backup_timestamp_seconds",
            "Time the backup was started.",
            ["host"],
            registry=registry,
        )
        backup_size = Gauge(
            "opnsense_backup_size_bytes",
            "Size of the backup.",
            ["host"],
            registry=registry,
        )

        if not path.isdir(config["metrics"]["directory"]):
            raise ValueError(
                f"Metrics directory {config['metrics']['directory']} does not exist or is not a directory"  # pylint: disable=line-too-long
            )

        metrics_file = path.join(config["metrics"]["directory"], "opnsense-backup")
        if "suffix" in config["metrics"]:
            metrics_file += "-" + config["metrics"]["suffix"]

        metrics_file += ".prom"

        host = urlparse(config["opnsense"]["url"]).hostname
        backup_time.labels(host).set_to_current_time()
        backup_size.labels(host).set(stat(out_file).st_size)

        write_to_textfile(metrics_file, registry)
