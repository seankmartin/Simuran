"""This module holds single experiment related information."""
from simuran.base_class import BaseSimuran
from simuran.param_handler import ParamHandler
from simuran.containers import SignalContainer
from skm_pyutils.py_config import split_dict


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
        return ("{} with params: {}".format(
            self.__class__.__name__, self.param_handler.params))

    def _run_analysis(self, fn, **kwargs):
        pass

    def _setup_from_file(self, params_file):
        self.param_handler = ParamHandler(in_loc=params_file)
        self._setup()

    def _setup_from_dict(self, params):
        self.param_handler = ParamHandler(params=params)
        self._setup()

    def _setup(self):
        # The params file should describe the signals, units, etc.
        self.signals = SignalContainer()
        signal_dict = self.param_handler["signals"]
        for i in range(signal_dict["num_signals"]):
            params = split_dict(signal_dict, i)
            self.signals.append_new(params)
        # The params file should be python code, similar to how spike sorting works.
