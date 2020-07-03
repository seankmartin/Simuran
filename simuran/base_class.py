"""Module to hold the base class setting up information and methods held in most SIMURAN classes."""

from abc import ABC, abstractmethod
from simuran.loaders.base_loader import BaseLoader


class BaseSimuran(ABC):
    """TODO Put the docstring here."""

    def __init__(self, **kwargs):
        """See help(BaseSimuran) for more info."""
        self.kwargs = kwargs
        self.info = None
        self.date = None
        self.time = None
        self.tag = None
        self.loader = None
        self.source_file = None
        self.last_loaded_source = None
        self.underlying = None
        self.results = {}
        super().__init__()

    def add_info(self, key, name, info):
        if self.info is None:
            self.info = {}
        if not key in self.info.keys():
            self.info[key] = {}
        self.info[key][name] = info

    def get_info(self, key, name):
        if self.info is None:
            raise ValueError("info has not been initialised in {}".format(self))
        return self.info[key][name]

    def does_info_exist(self, name):
        if self.info is not None:
            for item in self.info.values():
                if name in item.keys():
                    return True
        return False

    def setup(self, params):
        self.save_attrs(params)

    def set_loader(self, loader):
        if not isinstance(loader, BaseLoader):
            raise ValueError(
                "Loader set in set_loader should be derived from BaseLoader"
                + " actual class is {}".format(loader.__class__.__name__)
            )
        self.loader = loader

    def set_source_file(self, file):
        self.source_file = file

    @abstractmethod
    def load(self, *args, **kwargs):
        if self.loader is None:
            raise ValueError(
                "Set a loader in {} before calling load.".format(
                    self.__class__.__name__
                )
            )
        if self.loaded():
            return
            # print("Already loaded {} from {}".format(
            #     self.__class__.__name__, self.source_file))

    def loaded(self):
        loaded = (self.last_loaded_source is not None) and (
            self.last_loaded_source == self.source_file
        )
        return loaded

    def data_dict_from_attr_list(self, attr_list, friendly_names=None):
        data_out = {}
        for i, attr_tuple in enumerate(attr_list):
            item = self
            for a in attr_tuple:
                if a is None:
                    break
                if isinstance(a, str):
                    if hasattr(item, a):
                        item = getattr(item, a)
                    else:
                        item = item[a]
                else:
                    item = item[a]
                if callable(item):
                    item = item()
            if isinstance(item, dict):
                for key, value in item.items():
                    data_out[key] = value
            else:
                if friendly_names is None:
                    key = "_".join(attr_tuple)
                else:
                    key = friendly_names[i]
                data_out[key] = item
        return data_out

    def save_attrs(self, attr_dict):
        if attr_dict is not None:
            if hasattr(attr_dict, "items"):
                for key, value in attr_dict.items():
                    setattr(self, key, value)

    def __str__(self):
        """Called on print."""
        return "{} with attributes {}".format(self.__class__.__name__, self.__dict__)
