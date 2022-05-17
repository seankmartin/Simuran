from dataclasses import dataclass
from typing import TYPE_CHECKING

import pynwb
from simuran.loaders.base_loader import MetadataLoader

if TYPE_CHECKING:
    from simuran.recording import Recording


@dataclass
class NWBLoader(MetadataLoader):
    """
    Load NWB data.

    Currently, need to call recording.data.close() when done.

    """

    def parse_metadata(self, recording: "Recording") -> None:
        recording.source_file = recording.attrs["source_file"]

    def load_recording(self, recording) -> "Recording":
        try:
            nwb_io = pynwb.NWBHDF5IO(recording.source_file, "r")
        except OSError as e:
            print("{} is not a valid NWB file".format(recording.source_file))
            raise (e)
        recording.data = nwb_io.read()
        recording._nwb_io = nwb_io

    def unload(self, recording: "Recording") -> None:
        if hasattr(recording, "_nwb_io"):
            recording._nwb_io.close()
            delattr(recording, "_nwb_io")
