from dataclasses import dataclass
from os.path import isfile, splitext
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from allensdk.brain_observatory.behavior.behavior_project_cache import (
        VisualBehaviorOphysProjectCache,
    )

from simuran.loaders.base_loader import BaseLoader
from simuran.recording import Recording
from simuran.spatial import Spatial


@dataclass
class AllenOphysLoader(BaseLoader):
    """
    Load AIS ophys data from a cache.

    Attributes
    ----------
    cache : VisualBehaviorOphysProjectCache
        The AIS ophys cache to load data from.

    """

    cache: "VisualBehaviorOphysProjectCache"

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

    def parse_table_row(self, table, index, recording=None) -> "Recording":
        """Move information from row into recording."""
        recording = Recording() if recording is None else recording
        row = table.iloc[index]
        row_as_dict = row.to_dict()
        row_as_dict[table.index.name] = row.name
        recording.loader = self
        recording.metadata = row_as_dict
        recording.available = ["data", "spatial"]
        recording.source_file = self.path_to_nwb(recording)
        recording.metadata["downloaded"] = isfile(recording.source_file)
        return recording

    def load_recording(self, recording) -> "Recording":
        ophys_experiment_id = recording.metadata["ophys_experiment_id"]
        try:
            experiment = self.cache.get_behavior_ophys_experiment(ophys_experiment_id)
        except FileNotFoundError:
            fpath = self.path_to_nwb(recording)
            print(f"Please download {fpath} before trying to load it.")
            return recording
        recording.data = experiment
        recording.spatial = Spatial()
        recording.spatial.data = experiment.running_speed
        return recording

    def load_signal(self, recording):
        return self.cache.get_behavior_ophys_experiment(
            ophys_experiment_id=recording.ophys_experiment_id
        )

    def load_single_unit(self, *args, **kwargs):
        return

    def load_spatial(self, *args, **kwargs):
        return

    def auto_fname_extraction(self, *args, **kwargs):
        return

    def index_files(self, folder, **kwargs):
        return
