"""This module holds containers to allow for batch processing."""
from abc import ABC, abstractmethod
from collections import OrderedDict
from simuran.base_signal import AbstractSignal


class AbstractContainer(ABC):
    """TODO Put the docstring here."""

    def __init__(self, **kwargs):
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

    @abstractmethod
    def __repr__(self):
        """Called on print."""
        pass

    @abstractmethod
    def __iter__(self):
        """Iterate through the container."""
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __getitem__(self, key):
        pass


class ExperimentContainer(AbstractContainer):

    def __init__(self, **kwargs):
        super().__init__()


class SignalContainer(AbstractContainer):

    def __init__(self, **kwargs):
        super().__init__()
        self.container = OrderedDict()

    def __getitem__(self, key):
        if type(key) is int:
            return list(self.container.values())[key]
        return self.container.get(key, None)

    def __len__(self):
        return len(self.container)

    def __iter__(self):
        return self.container.values()

    def __repr__(self):
        return "{} with {} elements:\n{}".format(
            self.__class__.__name__, len(self), self.container)

    def append(self, signal, key=None):
        if key is None:
            key = len(self)
        self.container[key] = signal

    def append_new(self, params, key=None):
        signal = AbstractSignal()
        signal.setup(params)
        self.append(signal, key=key)
