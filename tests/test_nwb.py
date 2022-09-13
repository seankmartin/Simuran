import os
from simuran.loaders.nwb_loader import NWBLoader
from simuran.recording import Recording

from datetime import datetime
from dateutil.tz import tzlocal

from pynwb import NWBFile, NWBHDF5IO


def test_nwb_loader():
    # 1. Create an example NWB and write it out
    nwbfile = NWBFile(
        session_description="my first synthetic recording",
        identifier="EXAMPLE_ID",
        session_start_time=datetime.now(tzlocal()),
        experimenter="Dr. Bilbo Baggins",
        lab="Bag End Laboratory",
        institution="University of Middle Earth at the Shire",
        experiment_description="I went on an adventure with thirteen dwarves "
        "to reclaim vast treasures.",
        session_id="LONELYMTN",
    )

    with NWBHDF5IO("ecephys_tutorial.nwb", "w") as io:
        io.write(nwbfile)

    # 3. Set up a recording with metadata
    r = Recording(attrs=dict(source_file="ecephys_tutorial.nwb"))

    # 4. Load that NWB
    r.loader = NWBLoader()

    # 5. Check data is as expected
    r.parse_metadata()
    r.load()
    assert r.data.identifier == "EXAMPLE_ID"

    r.unload()

    os.remove("ecephys_tutorial.nwb")
