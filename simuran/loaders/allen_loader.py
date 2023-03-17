from pathlib import Path
from dataclasses import dataclass, field
from os.path import isfile, splitext
from pathlib import Path
from typing import Type, Union, Optional, TYPE_CHECKING

from allensdk.brain_observatory.behavior.behavior_project_cache.project_cache_base import (
    ProjectCacheBase,
)
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
    VisualBehaviorNeuropixelsProjectCache,
)
import pandas as pd

from simuran.loaders.base_loader import MetadataLoader
from simuran.recording import Recording

if TYPE_CHECKING:
    from pandas import DataFrame


@dataclass
class BaseAllenLoader(MetadataLoader):
    cache_class_type: Type[ProjectCacheBase]
    cache_directory: Union[str, Path]
    manifest: Optional[str]
    cache: Optional["ProjectCacheBase"] = None

    def create_s3_cache(self):
        """Create an instance of the cache class for s3."""
        self.cache = self.cache_class_type.from_s3_cache(cache_dir=self.cache_directory)
        if self.manifest is not None:
            self.cache.load_manifest(self.manifest)

    def create_local_cache(self):
        """Create an instance of the cache class for local data only."""
        self.cache = self.cache_class_type.from_local_cache(self.cache_directory)
        if self.manifest is not None:
            self.cache.load_manifest(self.manifest)

    def path_to_nwb(self, recording: "Recording") -> str:
        """Return the path to the nwb file for a given recording."""
        name_dict = self._map_class_to_values()
        t, session_name = name_dict["t"], name_dict["session_name"]
        id_ = name_dict["id"]
        manifest_file = self.cache.current_manifest()
        manifest_version = splitext(manifest_file)[0].split("_")[-1][1:]
        id_ = recording.attrs[id_]

        path_start = (
            Path(self.cache.fetch_api.cache._cache_dir)
            / f"visual-behavior-{t}-{manifest_version}"
            / session_name
        )
        if session_name == "behavior_ecephys_sessions":
            return path_start / str(id_) / f"{session_name[9:-1]}_{id_}.nwb"
        else:
            return path_start / f"{session_name[:-1]}_{id_}.nwb"

    def parse_metadata(self, recording: "Recording") -> None:
        """
        Parse the information into the recording object.

        In this case, pulls out some information from the
        session table about this recording.

        Parameters
        ----------
        recording: simuran.Recording
            The recording object to parse into.

        Returns
        -------
        None

        """
        recording.source_file = self.path_to_nwb(recording)
        recording.attrs["downloaded"] = isfile(recording.source_file)
        recording.attrs["id_name"] = self._map_class_to_values()["id"]

    def load_recording(self, recording: "Recording") -> "Recording":
        """Load a recording into memory using AllenSDK."""
        t = self._map_class_to_values()
        experiment_id = recording.attrs[t["id"]]
        try:
            if t["unique"] == 1:
                experiment = self.cache.get_behavior_ophys_experiment(experiment_id)
            elif t["unique"] == 2:
                experiment = self.cache.get_ecephys_session(
                    ecephys_session_id=experiment_id
                )
        except FileNotFoundError:
            fpath = self.path_to_nwb(recording)
            print(f"Please download {fpath} before trying to load it.")
            return recording
        recording.data = experiment
        return recording

    def get_units(self) -> "DataFrame":
        all_units = self.cache.get_unit_table()
        channels = self.cache.get_channel_table()
        merged_units = all_units.merge(
            channels,
            left_on="ecephys_channel_id",
            right_index=True,
            suffixes=(None, "_y"),
        )
        return merged_units

    def get_sessions_table(self) -> "DataFrame":
        allen_sessions = self.cache.get_ecephys_session_table()
        allen_sessions = allen_sessions.dropna(subset=["file_id"])
        return allen_sessions

    def _map_class_to_values(self):
        name_dict = {}
        if self.cache_class_type.__name__ == "VisualBehaviorOphysProjectCache":
            name_dict["session_name"] = "behavior_ophys_experiments"
            name_dict["t"] = "ophys"
            name_dict["id"] = "ophys_experiment_id"
            name_dict["unique"] = 1
        elif self.cache_class_type.__name__ == "VisualBehaviorNeuropixelsProjectCache":
            if (self.manifest is not None) and ("0.4.0" in self.manifest):
                name_dict["session_name"] = "behavior_ecephys_sessions"
            else:
                name_dict["session_name"] = "ecephys_sessions"
            name_dict["t"] = "neuropixels"
            name_dict["id"] = "ecephys_session_id"
            name_dict["unique"] = 2
        else:
            raise ValueError(f"Unsupported cache type {self.cache_class_type.__name__}")

        return name_dict


@dataclass
class AllenOphysLoader(BaseAllenLoader):
    """
    Load AIS ophys data VBO from a cache.

    Attributes
    ----------
    cache : VisualBehaviorOphysProjectCache
        The AIS ophys cache to load data from.

    Parameters
    ----------
    cache_directory : str
        Where to store the cached data.
    manifest : str
        The name of the .json manifest file to use (version).
    local : bool
        If true, instantiate a local cache over

    """

    cache: Optional["VisualBehaviorOphysProjectCache"] = None
    cache_class_type: Type[ProjectCacheBase] = field(
        repr=False, init=False, default=VisualBehaviorOphysProjectCache
    )
    local: bool = False

    def __post_init__(self):
        if self.cache is not None:
            return
        if self.local:
            self.create_local_cache()
        else:
            self.create_s3_cache()


@dataclass
class AllenVisualBehaviorLoader(BaseAllenLoader):
    """
    Load AIS VBN dataset.

    Attributes
    ----------
    cache : VisualBehaviorOphysProjectCache
        The AIS ophys cache to load data from.

    Parameters
    ----------
    cache_directory : str
        Where to store the cached data.
    manifest : str
        The name of the .json manifest file to use (version).
    local : bool
        If true, instantiate a local cache over
    """

    cache: Optional["VisualBehaviorNeuropixelsProjectCache"] = None
    cache_class_type: Type[ProjectCacheBase] = field(
        repr=False, init=False, default=VisualBehaviorNeuropixelsProjectCache
    )
    local: bool = False

    def __post_init__(self):
        if self.cache is not None:
            return
        if self.local:
            self.create_local_cache()
        else:
            self.create_s3_cache()

    def get_all_units(self):
        all_units = self.cache.get_unit_table()
        channels = self.cache.get_channel_table()
        return all_units.merge(
            channels,
            left_on="ecephys_channel_id",
            right_index=True,
            suffixes=(None, "_y"),
        )

    def download_data(self, session_id: Optional[int] = None):
        if session_id is None:
            sessions = self.get_sessions_table()
            for session_id, row in sessions.iterrows():
                self.cache.get_ecephys_session(ecephys_session_id=session_id)
        else:
            self.cache.get_ecephys_session(ecephys_session_id=session_id)
