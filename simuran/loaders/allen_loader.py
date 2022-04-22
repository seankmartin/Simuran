from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)

from simuran.loaders.base_loader import BaseLoader

# TODO how would this fit in with the Base Loader class?
# TODO work with recording later on
# NOTE I kind of tied together the params and the loader an awful lot
# TODO temp inherit from param

## TODO old way not good so working with this for now
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
