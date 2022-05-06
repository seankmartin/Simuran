import os
from pathlib import Path
from pprint import pformat

from simuran.param_handler import ParamHandler
from simuran.recording import Recording

main_dir = os.path.dirname(__file__)[: -len(os.sep + "tests")]


def test_param_load():
    params = {"hello_world": "banana", 0: [1, 10, 14.1], "chans": {"1": "b"}}
    ph_write = ParamHandler(dictionary=params)
    ph_write.write("test_simuran_temp.py")
    ph_read = ParamHandler(source_file=Path("test_simuran_temp.py"))
    ph_read.read()
    assert ph_read.dictionary["hello_world"] == "banana"
    assert ph_read["0"] == [1, 10, 14.1]
    assert ph_read["chans"]["1"] == "b"
    os.remove("test_simuran_temp.py")


def test_recording_setup():
    metadata = ParamHandler(
        source_file=os.path.join(
            main_dir, "simuran", "params", "simuran_base_params.py"
        )
    )
    ex = Recording(metadata=metadata)
    assert ex.metadata["signals"]["region"][0] == "ACC"
    assert ex.signals.group_by_property("region", "BLA")[1] == [30, 31]


if __name__ == "__main__":
    test_param_load()
    metadata = ParamHandler(
        source_file=os.path.join(
            main_dir, "simuran", "params", "simuran_base_params.py"
        )
    )
    str_1 = pformat(str(metadata.dictionary))
    str_2 = metadata.to_str()
    print(metadata)
    test_recording_setup()
