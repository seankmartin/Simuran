import os
from pathlib import Path
from pprint import pformat

from simuran.loaders.base_loader import MetadataLoader
from simuran.param_handler import ParamHandler
from simuran.recording import Recording

main_dir = os.path.dirname(__file__)[: -len(os.sep + "tests")]


def test_param_load():
    params = {"hello_world": "banana", 0: [1, 10, 14.1], "chans": {"1": "b"}}
    ph_write = ParamHandler(attrs=params)
    ph_write.write("test_simuran_temp.py")
    ph_read = ParamHandler(source_file=Path("test_simuran_temp.py"))
    ph_read.read()
    assert ph_read.attrs["hello_world"] == "banana"
    assert ph_read["0"] == [1, 10, 14.1]
    assert ph_read["chans"]["1"] == "b"
    os.remove("test_simuran_temp.py")


def test_recording_setup():
    metadata = ParamHandler(
        source_file=os.path.join(
            main_dir, "simuran", "params", "simuran_base_params.py"
        )
    )
    loader = MetadataLoader()
    ex = Recording(metadata=metadata, loader=loader)
    loader.parse_metadata(ex)
    assert ex.metadata["signals"]["region"][0] == "ACC"
    assert set(ex.available_data) == set(
        ("signals", "units", "spatial", "loader", "loader_kwargs")
    )


if __name__ == "__main__":
    test_param_load()
    metadata = ParamHandler(
        source_file=os.path.join(
            main_dir, "simuran", "params", "simuran_base_params.py"
        )
    )
    str_1 = pformat(str(metadata.attrs))
    str_2 = metadata.to_str()
    print(metadata)
    test_recording_setup()
