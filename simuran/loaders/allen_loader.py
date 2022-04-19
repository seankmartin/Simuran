from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)

from simuran.loaders.base_loader import Loader

# TODO how would this fit in with the Base Loader class?
# TODO work with recording later on
# NOTE I kind of tied together the params and the loader an awful lot
class AllenOphysLoader():

    def __init__(self, cache, experiment_id):
        self.experiment_id = experiment_id
        self.cache = cache
        # TODO this is a temp because of how I wrote all this
        self.available = ("signals",)

    def load_signal(self):
        return self.cache.get_behavior_ophys_experiment(
            ophys_experiment_id=self.experiment_id)