import os

from simuran.experiment import Experiment
from simuran.param_handler import ParamHandler
from skm_pyutils.py_config import read_python

main_dir = os.path.dirname(__file__)[:-len(os.sep + "tests")]


def test_param_load():
    params = {
        "hello_world": "banana",
        0: [1, 10, 14.1],
        "chans": {"1": "b"}
    }
    ph_write = ParamHandler(params=params)
    ph_write.write("test_simuran_temp.py")
    ph_read = ParamHandler()
    ph_read.read("test_simuran_temp.py")
    assert ph_read.params["hello_world"] == "banana"
    assert ph_read.params["0"] == [1, 10, 14.1]
    assert ph_read["chans"]["1"] == "b"
    os.remove("test_simuran_temp.py")


def test_experiment():
    ex = Experiment(params_file=os.path.join(
        main_dir, "examples", "example_params.py"))
    assert ex.param_handler["0"]["channels"] == [0, 1, 2, 3]


if __name__ == "__main__":
    test_param_load()
    test_experiment()
