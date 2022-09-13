import os

import pytest
from simuran.core.param_handler import ParamHandler
from simuran import config_from_file


@pytest.mark.parametrize("file_type", [(".yaml"), (".json"), (".py")])
def test_read_write(file_type):
    params = {"hello_world": "banana", 0: [1, 10, 14.1], "chans": {"1": "b"}}
    ph_write = ParamHandler(attrs=params)
    ph_write.write(f"test_simuran_temp{file_type}")
    ph_read = config_from_file(f"test_simuran_temp{file_type}")
    assert ph_read.attrs["hello_world"] == "banana"
    if file_type == ".yaml":
        assert ph_read[0] == [1, 10, 14.1]
    else:
        assert ph_read["0"] == [1, 10, 14.1]
    assert ph_read["chans"]["1"] == "b"
    os.remove(f"test_simuran_temp{file_type}")


def test_dict_passes():
    ph = ParamHandler()
    ph.setdefault("a", "val")
    assert ph.get("a") == "val"
    assert ph.get("b", "hi") == "hi"
    assert len(ph.values()) == 1
    assert len(ph.keys()) == 1
    ph.pop("a")
    assert len(ph.items()) == 0
    ph["1"] = 100
    assert "1" in ph
    assert ph.setdefault("1") == 100
    ph.clear()
    assert len(ph) == 0
