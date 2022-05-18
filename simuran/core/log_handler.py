"""File logging configuration for SIMURAN"""
import datetime
import logging
import logging.handlers
import traceback
from pathlib import Path

from skm_pyutils.py_log import FileLogger, FileStdoutLogger, get_default_log_loc
from skm_pyutils.py_path import make_path_if_not_exists

log = FileLogger("simuran_cli")
out = FileStdoutLogger()
print = out.print


def default_log_location():
    log_location = Path.home() / ".simuran" / "app.log"
    log_location.parent.mkdir(parents=False, exist_ok=True)
    return log_location


def establish_main_logger(logger: "logging.Logger") -> None:
    """
    Set the handlers on the simuran logger and simuran.module loggers.

    TODO check can remove logging
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(levelname)s: %(asctime)s %(message)s",
        datefmt="%d/%m/%Y %I:%M:%S %p",
    )

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
