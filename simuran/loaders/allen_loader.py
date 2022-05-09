from dataclasses import dataclass
from os.path import isfile, splitext
from pathlib import Path

from allensdk.brain_observatory.behavior.behavior_project_cache import \
    VisualBehaviorOphysProjectCache
from simuran.loaders.base_loader import MetadataLoader
from simuran.recording import Recording
from simuran.spatial import Spatial


@dataclass
class AllenOphysLoader(MetadataLoader):
    """
    Load AIS ophys data from a cache.

    Attributes
    ----------
    cache : VisualBehaviorOphysProjectCache
        The AIS ophys cache to load data from.

    """

    cache: "VisualBehaviorOphysProjectCache"

    @classmethod
    def from_s3_cache(cls, cache_directory):
        s3_cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=cache_directory)
        return cls(cache=s3_cache)

    @classmethod
    def from_local_cache(cls, cache_directory):
        local_cache = VisualBehaviorOphysProjectCache.from_local_cache(cache_directory)
        return cls(cache=local_cache)

    def path_to_nwb(self, recording) -> str:
        manifest_file = self.cache.current_manifest()
        manifest_version = splitext(manifest_file)[0].split("_")[-1][1:]
        id_ = recording.metadata["ophys_experiment_id"]
        fname = (
            Path(self.cache.fetch_api.cache._cache_dir)
            / f"visual-behavior-ophys-{manifest_version}"
            / "behavior_ophys_experiments"
            / f"behavior_ophys_experiment_{id_}.nwb"
        )
        return fname

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
        # TODO expand this
        recording.available_data = ["ophys", "spatial", "licks"]
        recording.source_file = self.path_to_nwb(recording)
        recording.metadata["downloaded"] = isfile(recording.source_file)

    def load_recording(self, recording) -> "Recording":
        ophys_experiment_id = recording.metadata["ophys_experiment_id"]
        try:
            experiment = self.cache.get_behavior_ophys_experiment(ophys_experiment_id)
        except FileNotFoundError:
            fpath = self.path_to_nwb(recording)
            print(f"Please download {fpath} before trying to load it.")
            return recording
        recording.data = experiment
        # TODO is this needed?
        recording.spatial = Spatial()
        recording.spatial.data = experiment.running_speed
        return recording

    def load_signal(self, recording):
        return self.cache.get_behavior_ophys_experiment(
            ophys_experiment_id=recording.ophys_experiment_id
        )
