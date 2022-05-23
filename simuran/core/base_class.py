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

    # TODO test with raw data (not from file)
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

    # TODO this might be better in pyutils
    def data_dict_from_attr_list(
        self, attr_list: list, friendly_names: Union["list[str]", None] = None
    ):
        """
        From a list of attributes, return a dictionary.

        Each item in attr_list should be a tuple containing
        attributes, keys, or None.
        The elements of the tuple are then accessed iteratively, like
        self.tuple_el1.tuple_el2...
        If the element is an attribute, it is directly retrieved.
        If the element is a key in a dictionary, that is retrieved.
        If the element is None, it indicates a break.
        (This last option can be used to get functions without calling them,
        or to get a full dictionary instead of pulling out the key, value pairs.)

        The output also depends on what is retrieved, if a dictionary or a function.
        Functions are called with no arguments.
        Dictionaries have key value pairs, that are stored in the output dictionary.
        Both of these can be avoided by passing the last element of the tuple as None.

        As an example:
        self.results = {"addition": {"1 + 1": 2}}
        self.data.running_speed = [0.5, 1.4, 1.5]
        attr_list = [("results", "addition", None)]
        this_fn(attr_list) = {"results_addition": {"1 + 1" = 2}}
        attr_list = [("results", "addition"), ("data", "running_speed")]
        this_fn(attr_list) = {"1 + 1": 2, "data_running_speed": [0.5, 1.4, 1.5]}

        Parameters
        ----------
        attr_list : list
            The list of attributes to retrieve.
        friendly_names : list of str, optional
            What to name each retrieved attribute, (default None).
            Must be the same size as attr_list or None.

        Returns
        -------
        dict
            The retrieved attributes.

        Raises
        ------
        ValueError
            attr_list and friendly_names are not the same size.

        """
        if friendly_names is not None and len(friendly_names) != len(attr_list):
            raise ValueError("friendly_names and attr_list must be the same length")

        data_out = {}
        for i, attr_tuple in enumerate(attr_list):
            item = self
            for a in attr_tuple:
                if a is None:
                    break
                item = (
                    getattr(item, a)
                    if isinstance(a, str) and hasattr(item, a)
                    else item[a]
                )
                if callable(item):
                    item = item()
            if isinstance(item, dict):
                for key, value in item.items():
                    data_out[key] = value
            else:
                non_none_attrs = [x for x in attr_tuple if x is not None]
                if friendly_names is None:
                    key = "_".join(non_none_attrs)
                else:
                    key = friendly_names[i]
                    if key is None:
                        key = "_".join(non_none_attrs)
                data_out[key] = item
        return data_out

    def get_attrs(self) -> "dict[str, Any]":
        """Return all attributes of this object"""
        return self.__dict__

    def get_attrs_and_methods(self) -> "list[str]":
        """Return all attributes and methods of this object"""
        class_dir = dir(self)
        return [r for r in class_dir if not r.startswith("_")]

    def inspect(self, methods: bool = False, **kwargs) -> None:
        """
        Inspect this object (see attributes and methods).

        Really just passes this object into rich.inspect.
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
        pass
