import pytest
import os
from simuran.analysis.analysis_handler import AnalysisHandler


def add(a, b):
    if type(a) != float:
        raise TypeError("a must be a float")
    if type(b) != str:
        raise ValueError("b must be a string")
    return f"{b} {str(a)}"


def unpack(a):
    return dict(hi=a[0], bye=a[1])


class TestAnalysisHandler(object):
    @pytest.fixture
    def ah(self):
        ah = AnalysisHandler(handle_errors=False, verbose=True)
        ah.add_analysis(add, [(1.34, "hi"), (1.1, "3"), (1.0, "hello")])
        ah.add_analysis(unpack, [([4, 3],)])

        return ah

    def test_analysis_basics(self, ah):
        ah.add_analysis(tuple, [([1, 2, 3, 4],)])
        ah.run(pbar=True)
        assert ah.results["add"] == "hi 1.34"
        assert ah.results["add_2"] == "hello 1.0"
        df = ah.save_results_to_table(filename="test.csv")
        assert df.loc["add", 0] == "hi 1.34"
        os.remove("test.csv")

        ah.reset()
        assert len((ah.results.keys())) == 0
