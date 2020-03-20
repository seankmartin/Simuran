"""Module to hold the abstract class setting up information held in a class."""

from abc import ABC, abstractmethod
from simuran.loaders.base_loader import BaseLoader


class BaseSimuran(ABC):
    """TODO Put the docstring here."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.info = None
        self.date = None
        self.time = None
        self.tag = None
        self.loader = None
        self.source_file = None
        self.underlying = None
        super().__init__()

    def add_info(self, key, info, name):
        if self.info is None:
            self.info = {}
        if not key in self.info.keys():
            self.info[key] = {}
        self.info[key][name] = info

    def get_info(self, key, name):
        if self.info is None:
            raise ValueError(
                "info has not been initialised in {}".format(self))
        return self.info[key][name]

    def does_info_exist(self, name):
        if self.info is not None:
            for item in self.info.values():
                if name in item.keys():
                    return True
        return False

    def setup(self, params):
        for key, value in params.items():
            setattr(self, key, value)

    def set_loader(self, loader):
        if not isinstance(loader, BaseLoader):
            raise ValueError(
                "Loader set in set_loader should be derived from BaseLoader" +
                " actual class is {}".format(loader.__class__.__name__))
        self.loader = loader

    def set_source_file(self, file):
        self.source_file = file

    @abstractmethod
    def load(self, *args, **kwargs):
        if self.loader is None:
            raise ValueError(
                "Set a loader in {} before calling load.".format(
                    self.__class__.__name__))

    def __repr__(self):
        """Called on print."""
        return "{} with attributes {}".format(
            self.__class__.__name__, self.__dict__)
