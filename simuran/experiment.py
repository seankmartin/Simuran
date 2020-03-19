"""This module holds single experiment related information."""
from simuran.base_class import BaseSimuran
from simuran.param_handler import ParamHandler


class Experiment(BaseSimuran):

    def __init__(self, params=None, params_file=None):
        self.signals = None
        self.units = None
        self.spatial = None
        self.stimulation = None
        self.param_handler = None
        if params_file is not None:
            self._setup_from_file(params_file)
        elif params is not None:
            self._setup_from_dict(params)
        super().__init__()

    def __repr__(self):
        return ("Experiment with params: {}".format(
            self.param_handler.params))

    def _run_analysis(self, fn, **kwargs):
        pass

    def _setup_from_file(self, params_file):
        # Parse the params file and load the data and store param location
        self.param_handler = ParamHandler(in_loc=params_file)
        # The params file should describe the signals, units, etc.
        # The params file should be python code, similar to how spike sorting works.

    def _setup_from_dict(self, params):
        self.param_handler = ParamHandler(params=params)
