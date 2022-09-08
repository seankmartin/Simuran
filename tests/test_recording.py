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
