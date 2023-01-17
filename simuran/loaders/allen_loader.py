from pathlib import Path
from dataclasses import dataclass, field
from os.path import isfile, splitext
from pathlib import Path
from typing import Type, Union, Optional

from allensdk.brain_observatory.behavior.behavior_project_cache.project_cache_base import (
    ProjectCacheBase,
)
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
    VisualBehaviorNeuropixelsProjectCache,
)
from simuran.loaders.base_loader import MetadataLoader
from simuran.recording import Recording


@dataclass
class BaseAllenLoader(MetadataLoader):
    cache_class_type: Type[ProjectCacheBase]
    cache: "ProjectCacheBase"
    cache_directory: Union[str, Path]
    manifest: Optional[str]

    def create_s3_cache(self):
        self.cache = self.cache_class_type.from_s3_cache(cache_dir=self.cache_directory)
        if self.manifest is not None:
            self.cache.load_manifest(self.manifest)

    def create_local_cache(self):
        self.cache = self.cache_class_type.from_local_cache(self.cache_directory)
        if self.manifest is not None:
            self.cache.load_manifest(self.manifest)

    def path_to_nwb(self, recording) -> str:
        name_dict = self._map_class_to_values()
        t, session_name = name_dict["t"], name_dict["session_name"]
        id_ = name_dict["id"]
        manifest_file = self.cache.current_manifest()
        manifest_version = splitext(manifest_file)[0].split("_")[-1][1:]
        id_ = recording.attrs[id_]
        return (
            Path(self.cache.fetch_api.cache._cache_dir)
            / f"visual-behavior-{t}-{manifest_version}"
            / session_name
            / f"{session_name}_{id_}.nwb"
        )

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

    def load_recording(self, recording) -> "Recording":
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

    def _map_class_to_values(self):
        name_dict = {}
        if self.cache_class_type.__name__ == "VisualBehaviorOphysProjectCache":
            name_dict["session_name"] = "behavior_ophys_experiments"
            name_dict["t"] = "ophys"
            name_dict["id"] = "ophys_experiment_id"
            name_dict["unique"] = 1
        elif self.cache_class_type.__name__ == "VisualBehaviorNeuropixelsProjectCache":
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
    Load AIS ophys data from a cache.

    Attributes
    ----------
    cache : VisualBehaviorOphysProjectCache
        The AIS ophys cache to load data from.

    """

    cache: "VisualBehaviorOphysProjectCache" = field(init=False)
    cache_class_type: Type[ProjectCacheBase] = field(
        repr=False, init=False, default=VisualBehaviorOphysProjectCache
    )


@dataclass
class AllenVisualBehaviorLoader(BaseAllenLoader):
    cache: "VisualBehaviorNeuropixelsProjectCache" = field(init=False)
    cache_class_type: Type[ProjectCacheBase] = field(
        repr=False, init=False, default=VisualBehaviorNeuropixelsProjectCache
    )
