"""This module handles automatic creation of parameter files."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from skm_pyutils.config import read_json, read_python, read_yaml, convert_dict_to_string
import yaml
import json

DEFAULT = object()


@dataclass
class ParamHandler(object):
    """
    A wrapper around a dictionary describing parameters.

    Provides loaders for this and helper functions.

    Attributes
    ----------
    dictionary : dict
        The dictionary of underlying parameters
    source_file : Path
        The path to the file containing the parameters.
    name : str
        The name of the variable describing the parameters, default is "params".
        This is only used if in_loc is not None.
    dirname_replacement : str
        The directory name to replace __dirname__ by.
        By default, replaces it by dirname(param_file)

    """

    attrs: dict = field(default_factory=dict)
    source_file: Optional[Union[str, "Path"]] = None
    name: str = "params"
    dirname_replacement: str = ""

    def __post_init__(self):
        if self.source_file is not None:
            self.source_file = Path(self.source_file)
            self.read()

    def write(self, out_loc):
        """
        Write the parameters out to a python file.

        Parameters
        ----------
        out_loc : str
            The path to write to

        Returns
        -------
        None

        """
        ext = Path(out_loc).suffix
        with open(out_loc, "w") as f:
            if ext == ".py":
                out_str = self.to_str()
                f.write(out_str)
            elif ext in (".yml", ".yaml"):
                yaml.dump(self.attrs, f)
            elif ext == ".json":
                json.dump(self.attrs, f)

    def read(self):
        """
        Read the parameters.

        Returns
        -------
        None

        """
        if self.source_file.suffix == ".py":
            self.attrs = read_python(
                self.source_file, dirname_replacement=self.dirname_replacement
            )[self.name]
        elif self.source_file.suffix in [".yaml", ".yml"]:
            self.attrs = read_yaml(self.source_file)
        elif self.source_file.suffix == ".json":
            self.attrs = read_json(self.source_file)

    def to_str(self):
        """
        Convert the underlying parameters dictionary to string.

        Can be useful for printing or writing to a file.
        Does not overwrite default __str__ as the output is quite verbose.

        Returns
        -------
        str
            The string representation of the dict.

        """
        return convert_dict_to_string(self.attrs, self.name)

    def clear(self):
        """Remove all items from the dictionary."""
        self.attrs.clear()

    def keys(self):
        """Return all keys in the parameters."""
        return self.attrs.keys()

    def values(self):
        """Return all values in the parameters."""
        return self.attrs.values()

    def items(self):
        """Return key, value pairs in the parameters."""
        return self.attrs.items()

    def get(self, key, default=None):
        """
        Retrieve the value of key from the parameters.

        This mimics regular dictionary get.

        Parameters
        ----------
        key : str
            The key to retrieve
        default : object, optional
            What to return if the key is not found, default is None

        Returns
        -------
        object
            The value of the key

        """
        return self.attrs.get(key, default)

    def update(self, dict_):
        """
        Update attrs with dict_

        Parameters
        ----------
        dict_ : dict
            The dictionary to update with

        Returns
        -------
        None

        """
        self.attrs.update(dict_)

    def pop(self, key, default=DEFAULT):
        """
        Pop key from dictionary, optionally with default value

        Parameters
        ----------
        key : Any
            The key to pop
        default : Any
            If provided, the default value to get

        Returns
        -------
        Any
            The value of the key

        """
        if default is DEFAULT:
            self.attrs.pop(key)
        else:
            self.attrs.pop(key, default)

    def setdefault(self, key, value=DEFAULT):
        """
        Return the value of the key. If the key does not exist, set it to value.

        Parameters
        ----------
        key : Any
            The key to pop
        value : Any
            If provided, the default value to set

        Returns
        -------
        Any
            The value of the key

        """
        if value is DEFAULT:
            return self.attrs.setdefault(key)
        else:
            return self.attrs.setdefault(key, value)

    def __getitem__(self, key):
        """Return the value of key."""
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def __contains__(self, key):
        return key in self.attrs

    def __len__(self):
        return len(self.attrs)
