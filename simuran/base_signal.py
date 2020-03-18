"""Module to hold the abstract class setting up information held in a signal."""

from abc import ABC, abstractmethod


class BaseSignal(ABC):
    """TODO Put the docstring here."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        super().__init__()

    @abstractmethod
    def __repr__(self):
        """Called on print."""
        pass
