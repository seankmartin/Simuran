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
        recording.source_file = recording.metadata["source_file"]

    def load_recording(self, recording) -> "Recording":
        nwb_io = pynwb.NWBHDF5IO(recording.source_file, "r")
        recording.data = nwb_io.read()
        recording.nwb_io = nwb_io
