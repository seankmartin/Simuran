"""Module to hold the abstract class setting up information held in a signal."""

from simuran.base_class import BaseSimuran


class AbstractSignal(BaseSimuran):
    """TODO Put the docstring here."""

    def __init__(self):
        self.sampling_rate = None
        self.timestamps = None
        self.region = None
        self.group = None
        super().__init__()

    def load(self, *args, **kwargs):
        super().load()
        self.underlying = self.loader.load_signal(self.source_file, **kwargs)
