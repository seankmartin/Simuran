import os

from simuran.analysis.analysis_handler import AnalysisHandler
from skm_pyutils.log import get_default_log_loc


def add(a, b):
    if type(a) != float:
        raise TypeError("a must be a float")
    if type(b) != str:
        raise ValueError("b must be a string")

    return b + str(a)


def test_analysis_logging():
    if os.path.isfile(get_default_log_loc("caught_errors.txt")):
        os.remove(get_default_log_loc("caught_errors.txt"))
    ah = AnalysisHandler(handle_errors=True)
    ah.add_fn(add, 1.34, "hi")
    ah.add_fn(add, 1.1, 3)
    ah.add_fn(add, 1, "hello")

    ah.run_all_fns()

    with open(get_default_log_loc("caught_errors.txt"), "r") as f:
        contents = f.read()
        assert "TypeError" in contents
        assert "ValueError" in contents

    return ah
