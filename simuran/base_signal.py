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

    def setup(self, params):
        for key, value in params.items():
            setattr(self, key, value)

    def __repr__(self):
        return "{} with attributes {}".format(
            self.__class__.__name__, self.__dict__)

    # Alternatively
    # def __getattr__(self, key):
    #     return self.params.get(key, None)
