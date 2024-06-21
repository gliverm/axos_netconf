"""
Performs health check via netconf to E9 device as a method to check
connectivity and device health.

Typer works off of Python hints to validate arguments
Pydantic used to augment Typer as needed for greater specifity

Note: TDQM may not handle keyboardInterupt well at all times.  This can
be an extra progress bar line printed or a traceback within TDQM.
Open issue:   https://github.com/tqdm/tqdm/issues/548

"""

from typing import List
import os
import time
import sys
import random
import string
from pathlib import Path
from enum import Enum
from pydantic import BaseModel, field_validator, ValidationError
from tqdm import tqdm
import typer
from typing_extensions import Annotated
from dotenv import load_dotenv

from lib.base_logger import getlogger

LOGGER = getlogger("healthchk", "DEBUG")

from lib.axos_netconf.base import NetconfSession
from lib.axos_netconf.errors import NetconfSessionError, NetconfAuthenticationError
from lib.cli_utils.devicecfg import Devices
from lib.errors_base import ToolboxError

app = typer.Typer(
    add_completion=False, context_settings={"help_option_names": ["-h", "--help"]}
)


class CheckTypeEnum(str, Enum):
    edit_config = "edit-config"
    get_config = "get-config"


def generate_random_string(length: int) -> str:
    """Generate a random string of length"""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def main(
    axoshost: str,
    checktype: CheckTypeEnum,
    username: str,
    password: str,
    port: int,
    repeat: int,
    interval: float,
):
    """Main function"""

    # TODO consider timeout as a parameter
    timeout = 60
    netconf_conn = NetconfSession(
        hostname=axoshost,
        port=port,
        timeout=timeout,
        username=username,
        password=password,
    )

    counter = 0
    while True:
        try:
            start = time.time()
            with netconf_conn as conn:
                if checktype == CheckTypeEnum.get_config:
                    response = conn.getcfg_system_location()
                else:
                    location = f"{"healthchk-"}{generate_random_string(10)}"
                    response = conn.editcfg_system_location(location)
            elapsed = time.time() - start
            if response.ok:
                LOGGER.info(
                    f"Health check success: checktype:{checktype.lower()} axoshost:{axoshost} elapsed_time:{elapsed:.3f}s"
                )
            else:
                LOGGER.error(
                    f"Health check failed. checktype:{checktype.lower()} axoshost:{axoshost} error={response.error}"
                )

        except NetconfAuthenticationError as err:
            LOGGER.critical(f"Connection Authentication error.  error={err}")
            sys.exit(1)
        except NetconfSessionError as err:
            # Making the assumption the E9 is not reachable or not listening on the port
            LOGGER.critical(f"Connection error.  error={err}")
            sys.exit(1)
        except KeyboardInterrupt:
            LOGGER.info("CTRL+C pressed - exiting")
            sys.exit(1)

        if repeat != 0:
            counter += 1
            if counter == repeat:
                break
            else:
                time.sleep(interval)


@app.command(help="Perform a simple health check via netconf to E9 device")
def healthchk(
    # TODO better error checking for values
    axoshost: Annotated[
        str,
        typer.Argument(
            help="axos host ip to send netconf commands", show_default=False
        ),
    ],
    checktype: Annotated[
        CheckTypeEnum,
        typer.Option(
            "--checktype",
            "-t",
            help="Type of NetConf to perform",
            show_default=True,
        ),
    ] = CheckTypeEnum.get_config,
    username: Annotated[
        str,
        typer.Option(
            "--username",
            "-u",
            help="Netconf session username [env var: NETCONF_USER]",
            show_default=False,
        ),
    ] = os.getenv("NETCONF_USER"),
    password: Annotated[
        str,
        typer.Option(
            "--password",
            "-pwd",
            help="Netconf session username password [env var: NETCONF_PASSWORD]",
            show_default=False,
        ),
    ] = os.getenv("NETCONF_PASSWORD"),
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            min=0,
            max=65535,
            help="Netconf port to connect to",
            show_default=True,
        ),
    ] = 830,
    repeat: Annotated[
        int,
        typer.Option(
            "--repeat",
            "-r",
            min=0,
            max=65535,
            help="Number of times to repeat health check 0=infinity",
        ),
    ] = 1,
    interval: Annotated[
        float,
        typer.Option(
            "--interval",
            "-i",
            help="interval in seconds",
        ),
    ] = 0.1,
):
    """
    Perform a Netconf command against target and report elapsed time as a simple health check.
    """

    main(axoshost, checktype, username, password, port, repeat, interval)


if __name__ == "__main__":
    try:
        load_dotenv()
        app()
    except KeyboardInterrupt:
        LOGGER.info("CTRL+C pressed - exiting")
        sys.exit(1)
