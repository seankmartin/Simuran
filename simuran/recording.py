"""This module holds single experiment related information."""
from simuran.base_class import BaseSimuran
from simuran.param_handler import ParamHandler
from simuran.containers import GenericContainer
from simuran.base_signal import AbstractSignal
from simuran.single_unit import SingleUnit
from simuran.spatial import Spatial
from simuran.loaders.loader_list import loaders_dict
from skm_pyutils.py_config import split_dict


class Recording(BaseSimuran):

    def __init__(
            self, params=None, params_file=None, base_file=None, load=True):
        super().__init__()
        self.signals = None
        self.units = None
        self.spatial = None
        self.stimulation = None
        self.available = []
        self.param_handler = None
        self.source_file = base_file
        self.source_files = {}
        if params_file is not None:
            self._setup_from_file(params_file)
        elif params is not None:
            self._setup_from_dict(params)
        if load:
            self.load()

    def load(self, *args, **kwargs):
        for item in self.get_available():
            item.load()

    def get_available(self):
        return [getattr(self, item) for item in self.available]

    def set_base_file(self, base):
        self.source_file = base

    def __repr__(self):
        return ("{} with params {} and source files {}".format(
            self.__class__.__name__, self.param_handler.params,
            self.source_files))

    def _parse_source_files(self):
        source_files = {}
        for item, name in zip(self.get_available(), self.available):
            if isinstance(item, GenericContainer):
                source_files[name] = [s.source_file for s in item]
            else:
                source_files[name] = item.source_file
        self.source_files = source_files

    def _run_analysis(self, fn, **kwargs):
        pass

    def _setup_from_file(self, params_file):
        self.param_handler = ParamHandler(in_loc=params_file)
        self._setup()

    def _setup_from_dict(self, params):
        self.param_handler = ParamHandler(params=params)
        self._setup()

    def _setup(self):
        data_loader_cls = loaders_dict.get(self.param_handler["loader"], None)
        if data_loader_cls is None:
            raise ValueError(
                "Unrecognised loader {}, options are {}".format(
                    self.param_handler["loader"], loaders_dict.keys()))
        else:
            data_loader = data_loader_cls(self.param_handler["loader_kwargs"])
        if self.source_file == None:
            base = self.param_handler["base_fname"]
        else:
            base = self.source_file
        fnames = data_loader.auto_fname_extraction(base)

        # TODO establish what is loaded
        self.signals = GenericContainer(AbstractSignal)
        self.available.append("signals")
        signal_dict = self.param_handler["signals"]
        for i in range(signal_dict["num_signals"]):
            params = split_dict(signal_dict, i)
            self.signals.append_new(params)
            self.signals[-1].set_source_file(fnames["Signal"][i])
            self.signals[-1].set_loader(data_loader)

        self.units = GenericContainer(SingleUnit)
        self.available.append("units")
        units_dict = self.param_handler["units"]
        for i in range(len(fnames["Clusters"])):
            params = split_dict(units_dict, i)
            self.units.append_new(params)
            self.units[-1].set_source_file(
                {"Spike": fnames["Spike"][i],
                 "Clusters": fnames["Clusters"][i]
                 })
            self.units[-1].set_loader(data_loader)

        self.spatial = Spatial()
        self.available.append("spatial")
        self.spatial.set_source_file(fnames["Spatial"])
        self.spatial.set_loader(data_loader)

        self._parse_source_files()
