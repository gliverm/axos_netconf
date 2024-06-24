"""
The intent of this module is to be a collection of miscellaneous
utility functions used by the app.
"""

import time
import json
import sys
import yaml
from loguru import logger

from app.lib.cli_utils.errors import DeviceCfgError

singlelogger = None


class StructuredMessage:
    """To add structured data to log message."""

    def __init__(self, message, /, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return f"{self.message} : {json.dumps(self.kwargs)}"


def get_logger(app: str, level="DEBUG") -> logger:
    """Initialize logging for app returning logger."""
    global singlelogger

    if singlelogger is None:
        logobj = logger
        logger_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            f"{app} | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        logobj.add(
            sys.stdout,
            level=level,
            format=logger_format,
            colorize=None,
            serialize=False,
        )
        singlelogger = logger
        return logobj
    return singlelogger


def load_yaml_file(filename: str) -> object:
    """Read in YAML data and return dictionary"""
    try:
        with open(filename, "r", encoding="utf8") as infile:
            params = yaml.safe_load(infile)
    except FileNotFoundError as err:
        time.sleep(1)
        raise DeviceCfgError(f"Cannot find file {filename}. err: {err}")
    except IOError as err:
        time.sleep(1)
        raise DeviceCfgError(
            f"I/O error({err.errno}): {err.strerror}  filename: {filename}, err: {err}"
        )
    except yaml.YAMLError as error:
        msg = "YAMLError Something went wrong while parsing params.yaml file."
        err_problem_mark = getattr(error, "problem_mark", None)
        if err_problem_mark is not None:
            err_context = getattr(error, "context", None)
            err_problem = getattr(error, "problem", None)
            msg += str(err_problem_mark) + "\n "
            msg += str(err_problem) + " "
            if err_context is not None:
                msg += str(err_context)
            msg += "\nPlease correct data and retry."
        time.sleep(1)
        raise DeviceCfgError(msg)
    return params
