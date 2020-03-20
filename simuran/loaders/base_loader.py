"""The base loading class in SIMURAN."""

from abc import ABC, abstractmethod


class BaseLoader(ABC):

    def __init__(self, load_params={}):
        self.signal = None
        self.spatial = None
        self.single_unit = None
        self.source_filenames = {}
        self.load_params = load_params
        super().__init__()

    @abstractmethod
    def load_signal(self, *args, **kwargs):
        pass

    @abstractmethod
    def load_single_unit(self, *args, **kwargs):
        pass

    @abstractmethod
    def load_spatial(self, *args, **kwargs):
        pass

    @abstractmethod
    def auto_fname_extraction(self, basefname, **kwargs):
        pass
