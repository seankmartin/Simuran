"""This module holds containers to allow for batch processing."""
from abc import ABC, abstractmethod

from simuran.base_signal import AbstractSignal


class AbstractContainer(ABC):
    """TODO Put the docstring here."""

    def __init__(self):
        self.container = []
        super().__init__()

    def group_by_property(self, prop, value):
        group = []
        indices = []
        for i, val in enumerate(self):
            if getattr(val, prop) == value:
                group.append(val)
                indices.append(i)
        return group, indices

    def __getitem__(self, idx):
        return self.container[idx]

    def __len__(self):
        return len(self.container)

    def __iter__(self):
        return iter(self.container)

    def __repr__(self):
        return "{} with {} elements:\n{}".format(
            self.__class__.__name__, len(self), self.container)

    def load(self):
        for item in self:
            item.load()

    def append(self, signal):
        self.container.append(signal)

    def append_new(self, params):
        to_add = self._create_new(params)
        self.append(to_add)

    @abstractmethod
    def _create_new(self, params):
        pass


class GenericContainer(AbstractContainer):

    def __init__(self, cls):
        self.cls = cls
        super().__init__()

    def _create_new(self, params):
        new = self.cls()
        new.setup(params)
        return new
