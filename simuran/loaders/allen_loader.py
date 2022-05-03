import re

from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
from simuran.loaders.base_loader import BaseLoader
from simuran.spatial import Spatial


class AllenOphysLoader(BaseLoader):
    def __init__(self, cache):
        self.cache = cache

    def parse_table_row(self, table, index, recording) -> None:
        """Move information from row into recording."""
        row = table.iloc[index]
        row_as_dict = row.to_dict()
        row_as_dict[table.index.name] = row.name
        recording.loader = self
        recording.metadata = row_as_dict
        recording.available = ["signals"]

    ## TODO experimenting with a new idea here
    def load_recording(self, recording) -> None:
        ophys_experiment_id = recording.metadata["ophys_experiment_id"]
        experiment = self.cache.get_behavior_ophys_experiment(ophys_experiment_id)
        recording.data = experiment
        recording.spatial = Spatial()
        recording.spatial.data = experiment.running_speed

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
