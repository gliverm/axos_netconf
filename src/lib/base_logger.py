"""
Base logger for app

Only a single logger instance is allowed otherwise duplicate messages will occur.

Order matters. Import getlogger before subsequent modules and make the call to
getlogger immediately after the getlogger import.

Main module:
    from app.base_logger import getlogger
    LOGGER = getlogger('<appname>')
  
Other modules:
    from app.base_logger import getlogger
    LOGGER = getlogger(__name__)
"""

import sys
from loguru import logger

singlelogger = None


def getlogger(name: str = "CalixTool", level="DEBUG") -> logger:
    """Initialize logging for app returning logger object."""
    global singlelogger

    if singlelogger is None:
        logobj = logger
        logobj.remove()
        logger_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            f"{name} | "
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
        singlelogger = logobj

    return singlelogger
