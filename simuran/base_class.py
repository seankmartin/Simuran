"""The base class sets up information and methods held in most SIMURAN classes."""

from abc import ABC, abstractmethod
import datetime

import rich
import dtale

from simuran.loaders.base_loader import BaseLoader, ParamLoader


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

    def __init__(self, **kwargs):
        """See help(BaseSimuran) for more info."""
        super().__init__()
        self.kwargs = kwargs
        self.info = {}
        self.datetime = datetime.datetime.now()
        self.tag = None
        self.loader = None
        self.source_file = None
        self.last_loaded_source = None
        self.underlying = None
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
        if self.loaded():
            return

    def save_attrs(self, attr_dict):
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

    # TODO convert to property
    def set_metadata(self, params):
        """
        Store all the keys in params as attributes.

        Parameters
        ----------
        params : dict
            A dictionary of key/value pairs to be stored as attributes.

        Returns
        -------
        None

        """
        self.save_attrs(params)

    def add_info(self, key, name, info):
        """
        Store information so self.info[key][name] = info.

        Parameters
        ----------
        key : str
            The first key in the dictionary to store information to.
        name : str
            The second key in the dictionary to store information to.
        info : object
            The information to store

        Returns
        -------
        None

        """
        if key not in self.info.keys():
            self.info[key] = {}
        self.info[key][name] = info

    def get_info(self, key, name):
        """
        Retrieve self.info[key][name].

        Parameters
        ----------
        key : str
            The first key in the dictionary to retrieve information from.
        name : str
            The second key in the dictionary to retrieve information from.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            The key and name are not in self.info.

        """
        if key in self.info.keys():
            if name in self.info[key].keys():
                return self.info[key][name]
        raise ValueError("info has not been initialised in {}".format(self))

    def does_info_exist(self, name):
        """
        Check if name exists in any sub dictionaries in self.info.

        Parameters
        ----------
        name : str
            The string to check for.

        Returns
        -------
        bool
            Whether name exists in any sub dictionaries.

        """
        for item in self.info.values():
            if name in item.keys():
                return True
        return False

    # TODO flesh out the properties
    @property
    def loader(self):
        return self._loader

    @loader.setter
    def loader(self, value):
        """
        Set the loader object.

        Parameters
        ----------
        loader : simuran.loader.Loader
            Loader object to set.

        Raises
        ------
        TypeError
            The passed loader is not a simuran.loader.Loader.

        """
        if not isinstance(value, BaseLoader) and value is not None:
            raise TypeError(
                "Loader set in set_loader should be derived from BaseLoader"
                + " actual class is {}".format(value.__class__.__name__)
            )
        self._loader = value

    def set_source_file(self, file):
        """
        Set the source file.

        Parameters
        ----------
        file : str
            [description]

        """
        self.source_file = file

    def loaded(self):
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

    def get(self, key, default=None):
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
            return self.key
        else:
            return default

    def data_dict_from_attr_list(self, attr_list, friendly_names=None):
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
        friendly_names : list, optional
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

    def get_attrs(self):
        return self.__dict__

    def get_attrs_and_methods(self):
        class_dir = dir(self)
        attrs_and_methods = [r for r in class_dir if not r.startswith("_")]
        return attrs_and_methods

    def explore(self, methods=False, **kwargs):
        """Note: could also try objexplore"""
        rich.inspect(self, methods=methods, **kwargs)
        # objexplore.explore(self)

    @staticmethod
    def rich_explore(obj, methods=False, **kwargs):
        rich.inspect(obj, methods=methods, **kwargs)

    @staticmethod
    def show_interactive_table(table):
        ## TODO maybe should have a config for notebook version
        dtale.show(table).open_browser()

    def __str__(self):
        """Call on print."""
        return "{} with attributes {}".format(self.__class__.__name__, self.__dict__)
