from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Union
from pathlib import Path

from one.api import ONE
import one
from brainbox.io.one import SpikeSortingLoader
from ibllib.atlas import AllenAtlas
import pandas as pd

from simuran.loaders.base_loader import MetadataLoader

if TYPE_CHECKING:
    from simuran import Recording
    from pandas import DataFrame


@dataclass
class OneAlyxLoader(MetadataLoader):
    """
    Load One alyx data from online/cache.

    Attributes
    ----------
    one : ONE
        The ONE alyx instance
    atlas : AllenAtlas
        The allen brain atlas to use to associate data with.
    cache_directory : str
        The path to the directory to store data in.

    """

    one: Optional["ONE"] = None
    atlas: Optional["AllenAtlas"] = None
    cache_directory: Optional[Union[str, "Path"]] = None
    mode: str = "auto"

    def __post_init__(self):
        if self.one is None:
            self.create_cache()

    def create_cache(self):
        one_instance = ONE(
            base_url="https://openalyx.internationalbrainlab.org",
            password="international",
            silent=True,
            cache_dir=self.cache_directory,
            mode=self.mode,
        )
        param_file_location = one.params.iopar.getfile(one.params._PAR_ID_STR)
        p = Path(param_file_location) / ".caches"
        p.unlink(missing_ok=True)
        one.params.CACHE_DIR_DEFAULT = self.cache_directory
        one.params.setup(silent=True)
        self.one = one_instance
        if self.atlas is None:
            self.atlas = AllenAtlas()
        self.sessions = self.one.alyx.rest("insertions", "list")
        self._probe_dict = {}
        for s in self.sessions:
            self._probe_dict.setdefault(s["session"], []).append(s["id"])

    def find_eid(self, lab, subject, details=True):
        return self.one.search(lab=lab, subject=subject, details=details)

    def describe_dataset(self, eid: str):
        return self.one.list_datasets(eid=eid, collection="alf", details=True)

    def get_sessions_table(self) -> "DataFrame":
        all_insertions = pd.DataFrame([s for s in self.sessions])
        return all_insertions.drop_duplicates(subset=["session"])

    def parse_metadata(self, recording: "Recording") -> None:
        id_ = recording.attrs.get("session")
        if id_ is None:
            id_ = recording.attrs.get("experiment_id")
        if id_ is None:
            raise KeyError("No session or experiment_id set in recording.attrs")
        recording.source_file = id_

    def load_recording(self, recording: "Recording") -> "Recording":
        exclude = recording.attrs.get("data_to_exclude", ["full_details", "motion"])
        recording.data = self._download_data(recording.source_file, exclude=exclude)
        recording.attrs["quality_control"] = recording.data.pop("quality_control")
        recording.attrs["extended_quality_control"] = recording.data.pop(
            "extended_quality_control"
        )
        return recording

    def summarise(self, recording: "Recording") -> "Recording":
        out_dict = {}
        for key, value in recording.data.items():
            out_dict[key] = type(value)

        pass_ = recording.attrs["quality_control"]

        output_str = (
            f"This dataset is a {pass_} and is summarised as follows:\n"
            + f"It contains the following data keys and data types {out_dict}\n"
        )

        out_dict = {}
        for key, value in recording.data.items():
            if hasattr(value, "keys"):
                out_dict[key] = [k for k in value.keys()]
            elif hasattr(value, "columns"):
                out_dict[key] = value.columns
            else:
                out_dict[key] = f"of type {type(value)}"

        for key, value in out_dict.items():
            output_str += f"The {key} is {value}\n"

        output_str += f"\nThe full quality control is {recording.attrs['extended_quality_control']}"

        print(output_str)
        return output_str

    def _download_data(self, eid, exclude=[]):
        session_data = [
            "trials",
            "wheels",
            "wheelMoves",
            "licks",
        ]
        if not "camera" in exclude:
            session_data += ["leftCamera", "bodyCamera", "rightCamera"]

        if not "motion" in exclude:
            session_data += [
                "leftROIMotionEnergy",
                "bodyROIMotionEnergy",
                "rightROIMotionEnergy",
            ]

        return_dict = {}
        for sd in session_data:
            try:
                return_dict[sd] = self.one.load_object(eid, sd, collection="alf")
            except Exception:
                continue

        for pid in self._probe_dict[eid]:
            name = self.one.alyx.rest("insertions", "list", id=pid)[0]["name"]
            return_dict[f"{name}"] = self._get_probe_data(pid)

        if not "full_details" in exclude:
            return_dict["full_details"] = self.one.get_details(eid, full=True)
            return_dict["quality_control"] = return_dict["full_details"]["qc"]
            return_dict["extended_quality_control"] = return_dict["full_details"][
                "extended_qc"
            ]
        else:
            full = self.one.get_details(eid, full=True)
            return_dict["quality_control"] = full["qc"]
            return_dict["extended_quality_control"] = full["extended_qc"]
        return return_dict

    def _get_probe_data(self, pid):
        # Alternatively, one can instantiate the spike sorting loader using the session unique identifier eid and the probe name pname
        sl = SpikeSortingLoader(pid=pid, one=self.one, atlas=self.atlas)
        spikes, clusters, channels = sl.load_spike_sorting()
        clusters = sl.merge_clusters(spikes, clusters, channels)
        clusters_df = pd.DataFrame(clusters)

        # Filter to only have good units as per data release
        # return clusters_df.loc[clusters["label"] == 1]

        return spikes, clusters_df
    
    # TODO add download function.
    # TODO also add some protocol / structure for what is roughly expected to be in such a loader function.
