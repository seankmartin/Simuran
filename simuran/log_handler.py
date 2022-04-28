"""File logging configuration for SIMURAN"""
import datetime
import logging
import traceback

from skm_pyutils.py_path import make_path_if_not_exists
from skm_pyutils.py_log import get_default_log_loc, FileLogger

from skm_pyutils.py_log import FileLogger, FileStdoutLogger

log = FileLogger("simuran_cli")
out = FileStdoutLogger()
print = out.print


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
