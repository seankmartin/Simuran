import os

from simuran.experiment import Experiment
from simuran.param_creator import ParamHandler
from skm_pyutils.py_config import read_python


def test_setup():
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
    assert ph_read.params["chans"]["1"] == "b"
    os.remove("test_simuran_temp.py")


if __name__ == "__main__":
    test_setup()
