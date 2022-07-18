"""The base class sets up information and methods held in most SIMURAN classes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, Union

import rich

from simuran.core.param_handler import ParamHandler

if TYPE_CHECKING:
    from pathlib import Path

    from simuran.loaders.base_loader import BaseLoader


@dataclass
class BaseSimuran(ABC):
    """
    An abstract class which is the base class for most SIMURAN classes.

    This dataclass describes a general framework for any object
    which loads information from a source file.
    The abstract method load must be implemented by subclasses.

    Attributes
    ----------
    attrs : dict or ParamHandler
        Fixed information about this object, e.g. model or session type.
    datetime : datetime.datetime
        The date associated with this object, e.g. recording date.
    tag : str
        An optional tag to describe the object.
        Default "untagged"
    loader : simuran.loader.BaseLoader
        A loader object that is used to load this object.
        The relationship between the loader and this object
        is established in self.load()
    source_file : str
        The path to the source file for this object.
        For instance, an NWB file or an online URL.
    last_loaded_source : str
        The path to the last file this object was loaded from.
    data : Any
        When this object is loaded, complex variables can be stored in data.
        For instance, an xarray object could be set as the data.
        Generally speaking it is where the large (in terms of memory) objects
        are stored after loading.
    results : dict
        A dictionary of results.

    """

    attrs: Union[dict, "ParamHandler"] = field(default_factory=dict)
    datetime: "datetime" = field(default_factory=datetime.now)
    tag: Optional[str] = None
    loader: Optional["BaseLoader"] = field(default=None)
    source_file: Optional[Union[str, "Path"]] = None
    last_loaded_source: Optional[Union[str, "Path"]] = None
    data: Any = None
    results: dict = field(default_factory=dict)

    @abstractmethod
    def load(self) -> None:
        """
        Load the data using the set loader object.

        Skips loading if self.is_loaded().

        Raises
        ------
        ValueError
            If no loader has been set.

        """
        if self.is_loaded():
            return "skip"
        if self.loader is None:
            raise ValueError(
                f"Set a loader in {self.__class__.__name__} before calling load."
            )

    def is_loaded(self) -> bool:
        """
        Return True if the file has been loaded.

        Returns
        -------
        bool
            True if the source file has been loaded.

        """
        return (self.last_loaded_source is not None) and (
            self.last_loaded_source == self.source_file
        )

    def get_attrs(self) -> "dict[str, Any]":
        """Return all attributes of this object"""
        return self.__dict__

    def get_attrs_and_methods(self) -> "list[str]":
        """Return all attributes and methods of this object"""
        class_dir = dir(self)
        return [r for r in class_dir if not r.startswith("_")]

    def inspect(self, methods: bool = False, **kwargs) -> None:  # pragma: no cover
        """
        Inspect this object (see attributes and methods).

        Passes this object into rich.inspect - see this for kwargs.
        Note: You could also try objexplore for this purpose.

        Parameters
        ----------
        methods : bool, optional
            Show the methods, by default False
        **kwargs:
            Keyword arguments to pass into rich.inspect

        Returns
        -------
        None

        """
        rich.inspect(self, methods=methods, **kwargs)


class NoLoader(BaseSimuran):
    def load(self):
        return
