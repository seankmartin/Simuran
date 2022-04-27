from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)

from simuran.loaders.base_loader import BaseLoader

class AllenOphysLoader(BaseLoader):
    def __init__(self, cache):
        self.cache = cache

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
