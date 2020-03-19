"""This module holds single experiment related information."""
from simuran.base_class import BaseSimuran


class Experiment(BaseSimuran):

    def __init__(self, **kwargs):
        self.signals = None
        self.units = None
        self.spatial = None
        self.stimulation = None
        super().__init__()

    def __repr__(self):
        print("This is an Experiment")

    def _run_analysis(self, fn, **kwargs):
        pass

    def setup(self, params_file):
        # Parse the params file and load the data and store param location

        # The params file should describe the signals, units, etc.
        # The params file should be python code, similar to how spike sorting works.
        pass
