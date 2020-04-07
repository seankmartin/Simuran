import os

import numpy as np

from simuran.recording import Recording
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


def test_recording_setup():
    ex = Recording(param_file=os.path.join(
        main_dir, "simuran", "params", "default_params.py"))
    assert ex.param_handler["signals"]["region"][0] == "ACC"
    assert ex.signals.group_by_property("region", "BLA")[1] == [30, 31]


def test_nc_recording_loading():
    from neurochat.nc_lfp import NLfp
    from neurochat.nc_spike import NSpike
    from neurochat.nc_spatial import NSpatial

    loc = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSCa1_muscimol\01082018\t1_smallsq_beforeinfusion"
    ex = Recording(param_file=os.path.join(
        main_dir, "examples", "nc_params.py"),
        base_file=loc, load=False)
    ex.signals[11].load()
    ex.signals[12].load()
    ex.units[5].load()
    ex.units[5].underlying.set_unit_no(1)
    ex.spatial.load()
    lfp = NLfp()
    lfp.set_filename(
        os.path.join(loc,
                     "01082018_CanCSubCa1_muscimol_smallsq_before_1_1.eeg12"))
    lfp.load(system="Axona")

    unit = NSpike()
    unit.set_filename(os.path.join(
        loc, "01082018_CanCSubCa1_muscimol_smallsq_before_1_1.10"))
    unit.load(system="Axona")
    unit.set_unit_no(1)

    spatial = NSpatial()
    spatial.set_filename(os.path.join(
        loc, "01082018_CanCSubCa1_muscimol_smallsq_before_1_1_10.txt"))
    spatial.load(system="Axona")

    assert np.all(ex.signals[11].underlying.get_samples() == lfp.get_samples())
    assert np.all(ex.units[5].underlying.get_unit_stamp() ==
                  unit.get_unit_stamp())
    assert np.all(ex.spatial.underlying.get_pos_x() == spatial.get_pos_x())


def test_nc_loader_fname_extract():
    from simuran.loaders.nc_loader import NCLoader
    ncl = NCLoader()
    ncl.load_params["system"] = "Axona"
    loc = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSCa1_muscimol\01082018\t1_smallsq_beforeinfusion"
    file_locs, _ = ncl.auto_fname_extraction(
        loc, verbose=False, unit_groups=[1, 2, 3, 4, 9, 10, 11, 12])
    clust_locs = [
        os.path.basename(f) for f in file_locs["Clusters"] if f is not None]
    assert "01082018_CanCSubCa1_muscimol_smallsq_before_1_1_10.cut" in clust_locs


if __name__ == "__main__":
    test_nc_recording_loading()
    test_nc_loader_fname_extract()
    test_param_load()
    test_recording_setup()
