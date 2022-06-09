"""File logging configuration for SIMURAN"""
import datetime
import logging
import logging.handlers
import traceback
from pathlib import Path
from typing import Optional, Union

from skm_pyutils.log import (
    FileLogger,
    FileStdoutLogger,
    clear_handlers,
    convert_log_level,
    get_default_log_loc,
)
from skm_pyutils.path import make_path_if_not_exists

# TODO remove these later in favour of built in logging
log = FileLogger("simuran_cli")
out = FileStdoutLogger()


def default_log_location():
    log_location = Path.home() / ".simuran" / "app.log"
    log_location.parent.mkdir(parents=False, exist_ok=True)
    return log_location


def set_only_log_to_file(
    log_location: Union[str, "Path"],
    logger: Optional["logging.Logger"] = None,
    log_level: Union[str, int] = "DEBUG",
):
    logger = logging.getLogger("simuran") if logger is None else logger
    fh = logging.FileHandler(log_location, mode="w")
    fh.setFormatter(default_formatter())
    fh.setLevel(convert_log_level(log_level))
    clear_handlers(logger)
    logger.addHandler(fh)
    return fh


def establish_main_logger(logger: "logging.Logger") -> None:
    """
    Set the handlers on the simuran logger and simuran.module loggers.

    TODO check can remove logging
    """
    logger.setLevel(logging.DEBUG)
    formatter = default_formatter()

    fh = logging.handlers.RotatingFileHandler(
        default_log_location(), backupCount=5, maxBytes=100000
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)


def default_formatter():
    return logging.Formatter(
        fmt="%(levelname)s - %(name)s: %(asctime)s %(message)s",
        datefmt="%d/%m/%Y %I:%M:%S %p",
    )


def log_exception(ex, more_info="", location=None):
    """
    Log an expection to file and additional info.

    Parameters
    ----------
    ex : Exception
        The python exception that occurred
    more_info : str, optional
        Additional string to log, default is ""
    location : str, optional
        Where to store the log, default is
        home/.skm_python/caught_errors.txt

    Returns
    -------
    None

    """
    if location is None:
        default_loc = get_default_log_loc("caught_errors.txt")
    else:
        default_loc = location

    now = datetime.datetime.now()
    make_path_if_not_exists(default_loc)
    with open(default_loc, "a+") as f:
        f.write("\n----------Caught Exception at {}----------\n".format(now))
        traceback.print_exc(file=f)
    log.error(
        "{} failed with caught exception.\nSee {} for more information.".format(
            more_info, default_loc
        ),
        exc_info=False,
    )
