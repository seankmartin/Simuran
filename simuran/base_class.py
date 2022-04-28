"""The base class sets up information and methods held in most SIMURAN classes."""

import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Union

import dtale
import rich

from simuran.loaders.base_loader import BaseLoader, ParamLoader
from simuran.loaders.loader_list import loader_from_str


@dataclass
class BaseSimuran(ABC):
    """
    An abstract class which is the base class for most SIMURAN classes.

    This class describes a general framework for any object
    which loads information from a source file.

    The abstract method load must be implemented by subclasses.

    Attributes
    ----------
    kwargs : dict
        Any extra keyword arguments to store on this object.
    info : dict
        Store any extra information on this object.
    datetime : datetime.datetime
        The datetime stored on the object.
        Can be used for filtering purposes.
        For example, to get recordings performed on a specific day.
    tag : str
        An optional tag to describe the object.
    loader : simuran.loader.Loader
        A loader object that is used to load the object.
    source_file : str
        The path to the source file for this object.
    last_loaded_source : str
        The path to the last file this object was loaded from.
    underlying : object
        When self.loader is called, the underlying object
        can be stored in this object under this name.
    results : dict
        A dictionary of results.

    """

    def __init__(self):
        """See help(BaseSimuran) for more info."""
        super().__init__()
        self.metadata = {}
        self.datetime = datetime.datetime.now()
        self.tag = None
        self.loader = ParamLoader()
        self.source_file = None
        self.last_loaded_source = None
        self.data = None
        self.results = {}

    @abstractmethod
    def load(self, *args, **kwargs):
        """
        Load the data using the set loader object.

        Parameters
        ----------
        *args : list
            Positional arguments
        **kwargs : dict
            Keyword arguments

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If no loader has been set.

        """
        if self.loader is None:
            raise ValueError(
                "Set a loader in {} before calling load.".format(
                    self.__class__.__name__
                )
            )
        if self.is_loaded():
            return

    # TODO flesh out the properties
    @property
    def loader(self) -> "BaseLoader":
        return self._loader

    @loader.setter
    def loader(self, value: Union[str, "BaseLoader"]) -> None:
        """
        Set the loader object.

        Parameters
        ----------
        value : simuran.loader.Loader or str
            Loader object to set.

        Raises
        ------
        TypeError
            The passed loader is not a simuran.loader.Loader.
        ValueError
            The passed loader (str) is not a valid option.

        """
        if isinstance(value, str):
            value = loader_from_str(value)
        if not isinstance(value, BaseLoader) and value is not None:
            raise TypeError(
                "Loader set in set_loader should be derived from BaseLoader"
                + " actual class is {}".format(value.__class__.__name__)
            )
        self._loader = value

    def is_loaded(self) -> bool:
        """
        Return True if the file has been loaded.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True if the source file has been loaded.

        """
        loaded = (self.last_loaded_source is not None) and (
            self.last_loaded_source == self.source_file
        )
        return loaded

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve the value of key from the attributes.

        This mimics regular dictionary get, but on attributes.

        Parameters
        ----------
        key : str
            The attribute to retrieve
        default : object, optional
            What to return if the key is not found, default is None

        Returns
        -------
        object
            The value of the key

        """
        if hasattr(self, key):
            return self.key  # type: ignore
        else:
            return default

    def save_attributes(self, attr_dict: dict) -> None:
        """
        Store all the keys in attr_dict as attributes.

        If attr_dict is passed as None, nothing happens.

        Parameters
        ----------
        attr_dict : dict
            A dictionary of key/value pairs to be stored as attributes.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            Input is not a dictionary.

        """
        if attr_dict is not None:
            if hasattr(attr_dict, "items"):
                for key, value in attr_dict.items():
                    setattr(self, key, value)
            else:
                raise TypeError("Input is not a dictionary")

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
        if friendly_names is not None:
            if len(friendly_names) != len(attr_list):
                raise ValueError("friendly_names and attr_list must be the same")

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
                    if key is None:
                        key = "_".join(attr_tuple)
                data_out[key] = item
        return data_out

    def get_attrs(self) -> "dict[str, Any]":
        return self.__dict__

    def get_attrs_and_methods(self) -> "list[str]":
        class_dir = dir(self)
        attrs_and_methods = [r for r in class_dir if not r.startswith("_")]
        return attrs_and_methods

    def explore(self, methods: bool = False, **kwargs) -> None:
        """Note: could also try objexplore"""
        rich.inspect(self, methods=methods, **kwargs)
        # objexplore.explore(self)

    @staticmethod
    def rich_explore(obj, methods: bool = False, **kwargs) -> None:
        rich.inspect(obj, methods=methods, **kwargs)

    @staticmethod
    def show_interactive_table(table, notebook=False) -> None:
        ## TODO maybe should have a config for notebook version
        if notebook:
            dtale.show(table)
        else:
            dtale.show(table).open_browser()

    def __str__(self) -> str:
        """Call on print."""
        return "{} with attributes {}".format(self.__class__.__name__, self.__dict__)
