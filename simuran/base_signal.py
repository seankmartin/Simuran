"""Module to hold the abstract class setting up information held in a signal."""

from simuran.base_class import BaseSimuran


class AbstractSignal(BaseSimuran):
    """TODO Put the docstring here."""

    def __init__(self):
        self.timestamps = None
        self.samples = None
        self.sampling_rate = None
        self.region = None
        self.group = None
        super().__init__()

    def load(self, *args, **kwargs):
        super().load()
        if not self.loaded():
            load_result = self.loader.load_signal(self.source_file, **kwargs)
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file

    def get_duration(self):
        return self.timestamps[-1] - self.timestamps[0]

    def get_sampling_rate(self):
        return self.sampling_rate

    def get_timestamps(self):
        return self.timestamps

    def get_samples(self):
        return self.samples
