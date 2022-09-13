import pytest
from simuran.analysis.analysis_handler import AnalysisHandler


class TestAnalysisHandler(object):
    @pytest.fixture
    def ah(self):
        def add(a, b):
            if type(a) != float:
                raise TypeError("a must be a float")
            if type(b) != str:
                raise ValueError("b must be a string")
            return f"{b} {str(a)}"

        ah = AnalysisHandler(handle_errors=False, verbose=True)
        ah.add_fn(add, 1.34, "hi")
        ah.add_fn(add, 1.1, "3")
        ah.add_fn(add, 1.0, "hello")
        return ah

    def test_analysis_basics(self, ah):
        ah.run_all(pbar=True)
        assert ah.results["add"] == "hi 1.34"
        assert ah.results["add_2"] == "hello 1.0"

        ah.reset()
        assert len((ah.results.keys())) == 0
