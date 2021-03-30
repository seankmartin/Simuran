import os
import urllib.request

import numpy as np

from simuran.recording import Recording
from simuran.param_handler import ParamHandler

main_dir = os.path.dirname(__file__)[: -len(os.sep + "tests")]


def fetch_axona_data():
    base_url = (
        "https://gin.g-node.org/seankmartin/SIMURAN_Test_Data/raw/master/AxonaData/"
    )
    filenames = [
        "010416b-LS3-50Hz10.V5.ms.2",
        "010416b-LS3-50Hz10.V5.ms.eeg",
        "010416b-LS3-50Hz10.V5.ms_2.cut",
        "010416b-LS3-50Hz10.V5.ms_2.txt",
        "010416b-LS3-50Hz10.V5.ms.set",
    ]
    full_filenames = [
        os.path.join(main_dir, "tests", "resources", "temp", "axona", f)
        for f in filenames
    ]
    full_urls = [base_url + f for f in filenames]

    for i in range(len(filenames)):
        if not os.path.isfile(full_filenames[i]):
            urllib.request.urlretrieve(full_urls[i], full_filenames[i])

    return full_filenames


def test_param_load():
    params = {"hello_world": "banana", 0: [1, 10, 14.1], "chans": {"1": "b"}}
    ph_write = ParamHandler(params=params)
    ph_write.write("test_simuran_temp.py")
    ph_read = ParamHandler()
    ph_read.read("test_simuran_temp.py")
    assert ph_read.params["hello_world"] == "banana"
    assert ph_read.params["0"] == [1, 10, 14.1]
    assert ph_read["chans"]["1"] == "b"
    os.remove("test_simuran_temp.py")


def test_recording_setup():
    ex = Recording(
        param_file=os.path.join(main_dir, "simuran", "params", "simuran_base_params.py")
    )
    assert ex.param_handler["signals"]["region"][0] == "ACC"
    assert ex.signals.group_by_property("region", "BLA")[1] == [30, 31]


def test_nc_recording_loading(delete=False):
    from neurochat.nc_lfp import NLfp
    from neurochat.nc_spike import NSpike
    from neurochat.nc_spatial import NSpatial
    from simuran.loaders.nc_loader import NCLoader

    main_test_dir = os.path.join(main_dir, "tests", "resources", "temp", "axona")
    os.makedirs(main_test_dir, exist_ok=True)

    axona_files = fetch_axona_data()

    # Load using SIMURAN auto detection.
    ex = Recording(
        param_file=os.path.join(
            main_dir, "tests", "resources", "params", "axona_test.py"
        ),
        base_file=main_test_dir,
        load=False,
    )
    ex.signals[0].load()
    ex.units[0].load()
    ex.units[0].underlying.set_unit_no(1)
    ex.spatial.load()

    # Load using NeuroChaT
    lfp = NLfp()
    lfp.set_filename(os.path.join(main_test_dir, "010416b-LS3-50Hz10.V5.ms.eeg"))
    lfp.load(system="Axona")

    unit = NSpike()
    unit.set_filename(os.path.join(main_test_dir, "010416b-LS3-50Hz10.V5.ms.2"))
    unit.load(system="Axona")
    unit.set_unit_no(1)

    spatial = NSpatial()
    spatial.set_filename(os.path.join(main_test_dir, "010416b-LS3-50Hz10.V5.ms_2.txt"))
    spatial.load(system="Axona")

    assert np.all(ex.signals[0].underlying.get_samples() == lfp.get_samples())
    assert np.all(ex.units[0].underlying.get_unit_stamp() == unit.get_unit_stamp())
    assert np.all(ex.units[0].underlying.get_unit_tags() == unit.get_unit_tags())
    assert np.all(ex.spatial.underlying.get_pos_x() == spatial.get_pos_x())

    ncl = NCLoader()
    ncl.load_params["system"] = "Axona"
    loc = os.path.join(main_dir, "tests", "resources", "temp", "axona")
    file_locs, _ = ncl.auto_fname_extraction(
        loc,
        verbose=False,
        unit_groups=[
            2,
        ],
        sig_channels=[
            1,
        ],
    )
    clust_locs = [os.path.basename(f) for f in file_locs["Clusters"] if f is not None]
    assert "010416b-LS3-50Hz10.V5.ms_2.cut" in clust_locs

    if delete:
        for f in axona_files:
            os.remove(f)


if __name__ == "__main__":
    test_nc_recording_loading(delete=False)
    test_param_load()
    test_recording_setup()
