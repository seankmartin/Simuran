"""This module holds single experiment related information."""
import os

from simuran.base_class import BaseSimuran
from simuran.param_handler import ParamHandler
from simuran.containers import GenericContainer
from simuran.base_signal import AbstractSignal
from simuran.single_unit import SingleUnit
from simuran.spatial import Spatial
from simuran.loaders.loader_list import loaders_dict
from skm_pyutils.py_config import split_dict


class Recording(BaseSimuran):
    def __init__(self, params=None, param_file=None, base_file=None, load=True):
        super().__init__()
        self.signals = None
        self.units = None
        self.spatial = None
        self.stimulation = None
        self.available = []
        self.param_handler = None
        self.source_file = base_file
        self.source_files = {}
        if param_file is not None:
            self._setup_from_file(param_file, load=load)
        elif params is not None:
            self._setup_from_dict(params, load=load)

    def load(self, *args, **kwargs):
        for item in self.get_available():
            item.load()

    def get_available(self):
        return [getattr(self, item) for item in self.available]

    def set_base_file(self, base):
        self.source_file = base

    def get_signal_channels(self, as_idx=False):
        num_sigs = self.param_handler["signals"]["num_signals"]
        if as_idx:
            return [i for i in range(num_sigs)]
        default_chans = [i + 1 for i in range(num_sigs)]
        chans = self.param_handler["signals"].get("channels", default_chans)
        return chans

    def get_name_for_save(self, rel_dir=None):
        if rel_dir is None:
            base_name_part, _ = os.path.splitext(os.path.basename(self.source_file))
        else:
            name_up_to_rel = self.source_file[len(rel_dir + os.sep) :]
            base_name_part, _ = os.path.splitext(name_up_to_rel)
            base_name_part = base_name_part.replace(os.sep, "--")
        return base_name_part

    def get_available_units(self):
        l = []
        for i, unit in enumerate(self.units):
            l.append([unit.group, unit.get_available_units()])
        return l

    def get_set_units(self):
        return [unit.units_to_use for unit in self.units]

    def _parse_source_files(self):
        source_files = {}
        for item, name in zip(self.get_available(), self.available):
            if isinstance(item, GenericContainer):
                source_files[name] = [s.source_file for s in item]
            else:
                source_files[name] = item.source_file
        self.source_files = source_files

    def _setup_from_file(self, param_file, load=True):
        self.param_handler = ParamHandler(in_loc=param_file)
        self._setup(load=load)

    def _setup_from_dict(self, params, load=True):
        self.param_handler = ParamHandler(params=params)
        self._setup(load=load)

    def _setup(self, load=True):
        if self.source_file == None:
            default_base_val = None
            if self.param_handler.location is not None:
                default_base_val = os.path.dirname(self.param_handler.location)
            base = self.param_handler.get("base_fname", default_base_val)

            if base is None:
                raise ValueError("Must set a base file in Recording setup")
        else:
            base = self.source_file

        data_loader_cls = loaders_dict.get(self.param_handler.get("loader", None), None)
        if data_loader_cls is None:
            raise ValueError(
                "Unrecognised loader {}, options are {}".format(
                    self.param_handler.get("loader", None), list(loaders_dict.keys())
                )
            )
        elif data_loader_cls == "params_only_no_cls":
            data_loader = None
            load = False
        else:
            data_loader = data_loader_cls(self.param_handler["loader_kwargs"])
            chans = self.get_signal_channels()
            groups = self.param_handler["units"]["group"]
            fnames, base = data_loader.auto_fname_extraction(
                base, sig_channels=chans, unit_groups=groups
            )
            if fnames is None:
                self.valid = False
                return
            self.source_file = base

        # TODO this could possibly have different classes for diff loaders
        self.signals = GenericContainer(AbstractSignal)
        if "signals" in self.param_handler.keys():
            self.available.append("signals")
            signal_dict = self.param_handler["signals"]
            for i in range(signal_dict["num_signals"]):
                params = split_dict(signal_dict, i)
                self.signals.append_new(params)
                if data_loader is not None:
                    self.signals[-1].set_source_file(fnames["Signal"][i])
                    self.signals[-1].set_loader(data_loader)

        if "units" in self.param_handler.keys():
            self.units = GenericContainer(SingleUnit)
            self.available.append("units")
            units_dict = self.param_handler["units"]
            for i in range(units_dict["num_groups"]):
                params = split_dict(units_dict, i)
                self.units.append_new(params)
                if data_loader is not None:
                    self.units[-1].set_source_file(
                        {"Spike": fnames["Spike"][i], "Clusters": fnames["Clusters"][i]}
                    )
                    self.units[-1].set_loader(data_loader)

        if "spatial" in self.param_handler.keys():
            self.spatial = Spatial()
            self.available.append("spatial")
            if data_loader is not None:
                self.spatial.set_source_file(fnames["Spatial"])
                self.spatial.set_loader(data_loader)

        self._parse_source_files()

        if load:
            self.load()

        self.valid = True

    def __str__(self):
        return "{} with params {} and source files {}".format(
            self.__class__.__name__, self.param_handler.params, self.source_files
        )
