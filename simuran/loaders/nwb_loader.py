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

    Attributes
    ----------
    mode : str
        The mode to open the file in, by default "r"
        But "a" and "w" are other options for example.

    """

    mode: str = "r"

    def parse_metadata(self, recording: "Recording") -> None:
        options = ["nwb_file", "source_file"]
        for option in options:
            if option in recording.attrs:
                recording.source_file = recording.attrs[option]
                break
        else:
            raise ValueError(
                f"Please provide one of {options} as metadata for NWB parsing"
            )

    def load_recording(self, recording) -> "Recording":
        try:
            load_namespaces = True if self.mode == "r" else False
            nwb_io = pynwb.NWBHDF5IO(
                recording.source_file, self.mode, load_namespaces=load_namespaces
            )
        except OSError as e:
            print(f"{recording.source_file} is not a valid NWB file")
            raise (e)
        except TypeError as e:
            print(f"{recording.source_file} is not a valid type for NWB file")
            raise (e)
        recording.data = nwb_io.read()
        recording._nwb_io = nwb_io

    def unload(self, recording: "Recording") -> None:
        if hasattr(recording, "_nwb_io"):
            try:
                recording._nwb_io.close()
            except TypeError:
                delattr(recording, "_nwb_io")
            else:
                delattr(recording, "_nwb_io")
