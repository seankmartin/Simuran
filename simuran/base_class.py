"""Module to hold the abstract class setting up information held in a class."""

from abc import ABC, abstractmethod


class BaseSimuran(ABC):
    """TODO Put the docstring here."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.info = None
        self.date = None
        self.time = None
        self.tag = None
        super().__init__()

    @abstractmethod
    def __repr__(self):
        """Called on print."""
        pass

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
