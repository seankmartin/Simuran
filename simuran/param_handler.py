"""This module handles automatic creation of parameter files."""
import os
import shutil
from pprint import pformat

from skm_pyutils.py_config import read_python
from skm_pyutils.py_path import get_dirs_matching_regex


class ParamHandler(object):
    """
    A wrapper around a dictionary describing parameters.

    Provides loaders for this and helper functions.

    Attributes
    ----------
    params : dict
        The dictionary of underlying parameters
    location : str
        The path to the file containing the parameters.
    _param_name : str
        If reading a Python file, the name of the variable
        in that file which describes all the parameters.

    Parameters
    ----------
    params : dict, optional
        If passed, directly defines a dictionary of parameters.
    in_loc : str, optional
        If passed, a path to a file describing the parameters.
    name : str, optional
        The name of the variable describing the parameters, default is "mapping".
        This is only used if in_loc is not None.
    dirname_replacement : str, optional
        The directory name to replace __dirname__ by.
        By default, replaces it by dirname(param_file)

    """

    def __init__(
        self, params=None, in_loc=None, name="mapping", dirname_replacement=""
    ):
        """See help(ParamHandler)."""
        super().__init__()
        self.set_param_dict(params)
        self.location = ""
        self._param_name = name
        if in_loc is not None:
            self.read(in_loc, dirname_replacement=dirname_replacement)
            self.location = in_loc

    def set_param_dict(self, params):
        """
        Set the parameter dictionary.

        Parameters
        ----------
        params : dict
            The parameters to set

        Returns
        -------
        None

        """
        self.params = params

    def params_to_str(self):
        """
        Convert the underlying parameters dictionary to string.

        Can be useful for printing or writing to a file.

        Returns
        -------
        str
            The string representation of the string.

        """
        if self.params is None:
            raise ValueError()
        out_str = ""
        out_str += "mapping = {\n"
        for k, v in self.params.items():
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

    def write(self, out_loc, out_str=None):
        """
        Write the parameters out to a file.

        Parameters
        ----------
        out_loc : str
            The path to write to
        out_str : str, optional
            A custom string to write, by default None,
            which calls self.params_to_str()

        Returns
        -------
        None

        """
        with open(out_loc, "w") as f:
            if out_str is None:
                out_str = self.params_to_str()
            f.write(out_str)

    def read(self, in_loc, dirname_replacement=""):
        """
        Read the parameters from in_loc.

        Parameters
        ----------
        in_loc : str
            Path to a file to read parameters from.
        dirname_replacement : str, optional
            What to replace __dirname__ by in files, by default "".

        Returns
        -------
        None

        """
        param_dict = read_python(in_loc, dirname_replacement=dirname_replacement)[
            self._param_name
        ]
        self.set_param_dict(param_dict)

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
        if key in self.keys():
            return self[key]
        else:
            return default

    def set_default_params(self):
        """Set the default parameters in SIMURAN."""
        self.location = os.path.join(
            os.path.dirname(__file__), "params", "default_params.py"
        )
        self.read(self.location)

    def batch_write(
        self,
        start_dir,
        re_filters=None,
        fname="simuran_params.py",
        overwrite=True,
        check_only=False,
        return_absolute=True,
        exact_file=None,
        verbose=False,
    ):
        """
        Write the parameters out to a set of files.

        Parameters
        ----------
        start_dir : str
            Where to start the write operation from.
        re_filters : list, optional
            A list of regular expressions to match, by default None
        fname : str, optional
            The filename to write to, by default "simuran_params.py"
        overwrite : bool, optional
            Should existing files be overwritten, by default True
        check_only : bool, optional
            If true, don't do any writing, by default False
        return_absolute : bool, optional
            Should absolute or relative filenames be returned, by default True
        exact_file : str, optional
            Path to a file to copy, by default None
        verbose : bool, optional
            Whether to print more information, by default False

        Returns
        -------
        list of str
            The directories written to

        Raises
        ------
        ValueError
            If exact_file is passed but does not exist.

        """
        dirs = get_dirs_matching_regex(
            start_dir, re_filters=re_filters, return_absolute=return_absolute
        )
        dirs = [d for d in dirs if ("__pycache__" not in d) and (d != "")]

        if check_only:
            if exact_file is None:
                print("Would write parameters:")
                print(pformat(self.params, width=200))
                print("to:")
                for d in dirs:
                    print(d)
                return dirs
            else:
                print("Would copy {} to:".format(exact_file))
                for d in dirs:
                    print(d)
                return dirs

        if exact_file is None:
            out_str = self.params_to_str()
        for d in dirs:
            write_loc = os.path.join(d, fname)

            if exact_file is None:
                if verbose:
                    print("Writing params to {}".format(write_loc))
                if overwrite or not os.path.isfile(write_loc):
                    self.write(write_loc, out_str=out_str)
            else:
                if not os.path.isfile(exact_file):
                    raise ValueError(
                        "{} is not a valid file location".format(exact_file)
                    )
                if verbose:
                    print("Copying from {} to {}".format(exact_file, write_loc))
                if overwrite or not os.path.isfile(write_loc):
                    shutil.copy(exact_file, write_loc)

        return dirs

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
        if starting_filt is []:
            starting_filt = None
        dirs = self.batch_write(
            start_dir, re_filters=starting_filt, check_only=True, return_absolute=False
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
            dirs = self.batch_write(
                start_dir, re_filters=re_filt, check_only=True, return_absolute=False
            )

        if re_filt == "":
            re_filt = starting_filt
            if re_filt is None:
                re_filt = []

        print("The final regex was: {}".format(re_filt))
        return re_filt, dirs

    def keys(self):
        """Return all keys in the parameters."""
        return self.params.keys()

    def vals(self):
        """Return all values in the parameters."""
        return self.params.vals()

    def items(self):
        """Return key, value pairs in the parameters."""
        return self.params.items()

    def set_param_name(self, name):
        """
        Set the value of _param_name.

        Parameters
        ----------
        name : str
            The name to set.

        Returns
        -------
        None

        """
        self._param_name = name

    def __getitem__(self, key):
        """Return the value of key."""
        return self.params[key]

    def __str__(self):
        """Call on print."""
        return "{} from {} with params:\n{}".format(
            self.__class__.__name__, self.location, pformat(self.params, width=200)
        )

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
