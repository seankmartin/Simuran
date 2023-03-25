import os
import logging

from simuran.core.log_handler import (
    establish_main_logger,
    set_only_log_to_file,
    default_log_location,
)


def add(a, b):
    if type(a) != float:
        raise TypeError("a must be a float")
    if type(b) != str:
        raise ValueError("b must be a string")

    return b + str(a)


def test_simuran_logging():
    logger = logging.getLogger("simuran")
    establish_main_logger(logger)
    logger.warning("Here is a log")
    default_location = default_log_location()

    set_only_log_to_file("test.log", logger=logger)
    logger.warning("Here is a new warning")

    logging.shutdown()
    with open(default_location, "r") as f:
        assert "Here is a log" in f.read()
    with open("test.log", "r") as f:
        assert "Here is a new warning" in f.read()
    os.remove(default_location)
    os.remove("test.log")
