import os
import urllib

import numpy as np
from neurochat.nc_lfp import NLfp
from neurochat.nc_spatial import NSpatial
from neurochat.nc_spike import NSpike
from simuran.loaders.nc_loader import NCLoader
from simuran.param_handler import ParamHandler
from simuran.recording import Recording

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


def test_nc_recording_loading(delete=False):
    main_test_dir = os.path.join(main_dir, "tests", "resources", "temp", "axona")
    os.makedirs(main_test_dir, exist_ok=True)

    axona_files = fetch_axona_data()

    # Load using SIMURAN auto detection.
    metadata = ParamHandler(
        source_file=os.path.join(
            main_dir, "tests", "resources", "params", "axona_test.py"
        )
    )
    metadata["source_file"] = axona_files[-1]

    loader = NCLoader(system="Axona", loader_kwargs={"pos_extension": ".txt"})
    ex = Recording(metadata=metadata, loader=loader)
    ex.parse_metadata()

    ex.load()

    ex.units[0]["underlying"].set_unit_no(1)
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

    assert np.all(ex.signals[0]["underlying"].get_samples() == lfp.get_samples())
    assert np.all(ex.units[0]["underlying"].get_unit_stamp() == unit.get_unit_stamp())
    assert np.all(ex.units[0]["underlying"].get_unit_tags() == unit.get_unit_tags())
    assert np.all(ex.spatial["underlying"].get_pos_x() == spatial.get_pos_x())

    ncl = NCLoader()
    ncl.system = "Axona"
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
