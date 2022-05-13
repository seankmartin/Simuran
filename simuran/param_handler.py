"""This module handles automatic creation of parameter files."""
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from typing import Optional, Union

from skm_pyutils.py_config import read_json, read_python, read_yaml
from skm_pyutils.py_path import get_dirs_matching_regex


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
        The name of the variable describing the parameters, default is "mapping".
        This is only used if in_loc is not None.
    dirname_replacement : str
        The directory name to replace __dirname__ by.
        By default, replaces it by dirname(param_file)

    """

    attrs: dict = field(default_factory=dict)
    source_file: Optional[Union[str, "Path"]] = None
    name: str = "mapping"
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
        with open(out_loc, "w") as f:
            out_str = self.to_str()
            f.write(out_str)

    def read(self):
        """
        Read the parameters.

        TODO
        ----
        Support more than just .py params.

        Returns
        -------
        None

        """
        if self.source_file.suffix == ".py":
            self.attrs = read_python(
                self.source_file, dirname_replacement=self.dirname_replacement
            )[self.name]
        elif self.source_file.suffix == ".yaml":
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
        out_str = ""
        out_str += f"{self.name}" + " = {\n"
        for k, v in self.attrs.items():
            out_str += "\t{}:".format(self._val_to_str(str(k)))
            if isinstance(v, dict):
                out_str += "\n\t\t{\n"
                for k2, v2 in v.items():
                    out_str += "\t\t {}: {},\n".format(
                        self._val_to_str(str(k2)), self._val_to_str(v2)
                    )
                out_str += "\t\t},\n"
            else:
                out_str += " {},\n".format(self._val_to_str(v))
        out_str += "\t}"
        return out_str

    def set_default_params(self):
        """Set the default parameters in SIMURAN."""
        self.source_file = os.path.join(
            os.path.dirname(__file__), "params", "default_params.py"
        )
        self.read()

    def write_to_directories(
        self,
        start_dir,
        re_filters=None,
        fname="simuran_params.py",
        overwrite=True,
        dummy=False,
        return_absolute=True,
        exact_file=None,
        verbose=False,
        format_output=False,
    ):
        """
        Write the parameters out to a set of files.

        Parameters
        ----------
        start_dir : str
            Where to start the write operation from.
        re_filters : list, optional
            A list of regular expressions to match, by default None
            Picks up directories from this regex.
        fname : str, optional
            The filename to write to, by default "simuran_params.py"
        overwrite : bool, optional
            Should existing files be overwritten, by default True
        dummy : bool, optional
            If true, don't do any writing, by default False
        return_absolute : bool, optional
            Should absolute or relative filenames be returned, by default True
        verbose : bool, optional
            Whether to print more information, by default False
        format_output : bool, optional
            Print the formatted version of the source file instead of copying,
            by default False

        Returns
        -------
        list of str
            The paths written to

        Raises
        ------
        ValueError
            If exact_file is passed but does not exist.

        """

        def remove_empty_dirs_and_caches(dir_list: "list[str]") -> "list[str]":
            possible_dirs = [
                d for d in dir_list if ("__pycache__" not in d) and (d != "")
            ]

            # Exclude empty directories
            dirs = []
            for d in possible_dirs:
                filenames = next(os.walk(d), (None, None, []))[2]
                if len(filenames) > 0:
                    dirs.append(d)

            return dirs

        matched_dirs = get_dirs_matching_regex(
            start_dir, re_filters=re_filters, return_absolute=return_absolute
        )
        filtered_dirs = remove_empty_dirs_and_caches(matched_dirs)
        write_locs = [os.path.join(d, fname) for d in filtered_dirs]

        if dummy:
            locations = pformat(self.write_locs, width=200)
            if self.source_file is None:
                params = pformat(self.params, width=200)
                print(f"Would write metadata:\n{params}\nto:\n{locations}")
            else:
                print(f"Would copy {self.source_file} to locations:\n{locations}")
        else:
            for write_loc in write_locs:
                if (self.source_file is None) or format_output:
                    if verbose:
                        print("Writing params to {}".format(write_loc))
                    if overwrite or not os.path.isfile(write_loc):
                        self.write(write_loc)
                else:
                    if verbose:
                        print(f"Copying from {self.source_file} to {write_loc}")
                    if not os.path.isfile(self.source_file):
                        raise ValueError(f"{self.source_file} does not exist")
                    if overwrite or not os.path.isfile(write_loc):
                        shutil.copy(exact_file, write_loc)

        return write_locs

    def interactive_refilt(self, start_dir, starting_filt=None):
        """
        Launch an interactive prompt to select regex filters.

        Parameters
        ----------
        start_dir : str
            Where to start the search from.

        Returns
        -------
        re_filt : list of str
            The final list of regex filters chosen by the user.
        dirs : list of str
            The final list of directories that would be written to.

        """
        re_filt = ""
        if starting_filt == []:
            starting_filt = None
        dirs = self.write_to_directories(
            start_dir, re_filters=starting_filt, dummy=True, return_absolute=False
        )
        while True:
            this_re_filt = input(
                "Please enter the regexes seperated by SIM_SEP to test or"
                + " ok to continue with the current selection"
                + ", or exit to kill the whole program:\n"
            )
            if this_re_filt.lower().strip() == "exit":
                exit(-1)
            done = this_re_filt.lower().strip() == "ok"
            if done:
                break
            if this_re_filt == "":
                re_filt = None
            else:
                re_filt = this_re_filt.split(" SIM_SEP ")
            dirs = self.write_to_directories(
                start_dir, re_filters=re_filt, dummy=True, return_absolute=False
            )

        if re_filt == "":
            re_filt = starting_filt
            if re_filt is None:
                re_filt = []

        print("The final regex was: {}".format(re_filt))
        return re_filt, dirs

    @staticmethod
    def _val_to_str(val):
        """
        Convert a value to a string.

        One caveat, if a string is passed, it returns
        the original string wrapped in quotes.

        Parameters
        ----------
        val : object
            The value to convert

        Returns
        -------
        str
            The value as a string.

        """
        if isinstance(val, str):
            return "'{}'".format(val)
        else:
            return val

    ## Below this point mimics regular dictionary operations
    ## Equivalent to self.dictionary.blah() = self.blah()

    def keys(self):
        """Return all keys in the parameters."""
        return self.attrs.keys()

    def vals(self):
        """Return all values in the parameters."""
        return self.attrs.vals()

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

    def __getitem__(self, key):
        """Return the value of key."""
        return self.attrs[key]

    def __setitem__(self, key, value):
        self.attrs[key] = value
