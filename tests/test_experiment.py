import os

from simuran.experiment import Experiment
from simuran.param_creator import ParamHandler
from skm_pyutils.py_config import read_python


def test_setup():
    params = {"hello_world": "banana"}
    ph_write = ParamHandler(params=params)
    ph_write.write("test_simuran_temp.py")
    ph_read = ParamHandler()
    ph_read.read("test_simuran_temp.py")
    assert ph_read.params["hello_world"] == "banana"
    os.remove("test_simuran_temp.py")


if __name__ == "__main__":
    test_setup()
