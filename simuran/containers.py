"""This module holds containers to allow for batch processing."""
from abc import ABC, abstractmethod


class AbstractContainer(ABC):
    """TODO Put the docstring here."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super().__init__()

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
    def __getitem__(self, index):
        pass


class ExperimentContainer(AbstractContainer):

    def __init__(self, **kwargs):
        super().__init__()
