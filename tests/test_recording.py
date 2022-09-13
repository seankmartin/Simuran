import os

from simuran.core.param_handler import ParamHandler
from simuran.loaders.base_loader import MetadataLoader
from simuran.recording import Recording

main_dir = os.path.dirname(__file__)[: -len(f"{os.sep}tests")]


def test_recording_setup():
    metadata = ParamHandler(
        source_file=os.path.join(
            main_dir, "tests", "resources", "params", "simuran_base_params.py"
        ),
        name="mapping",
    )

    loader = MetadataLoader()
    ex = Recording(attrs=metadata, loader=loader)
    loader.parse_metadata(ex)
    assert ex.attrs["signals"]["region"][0] == "ACC"
    assert set(ex.available_data) == {
        "signals",
        "units",
        "spatial",
        "loader",
        "loader_kwargs",
    }


def test_recording_save_name():
    source_file = "fake_dir/fake_dir2/fake_name.txt"
    r = Recording(source_file=source_file)

    name = r.get_name_for_save()
    assert name == "fake_dir--fake_dir2--fake_name"

    name2 = r.get_name_for_save(rel_dir="fake_dir")
    assert name2 == "fake_dir2--fake_name"
