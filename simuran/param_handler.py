"""This module handles automatic creation of parameter files."""
import os
from pprint import pformat

from skm_pyutils.py_config import read_python
from skm_pyutils.py_path import get_dirs_matching_regex
from skm_pyutils.py_path import get_all_files_in_dir
from typing import Iterable


class ParamHandler:
    def __init__(self, params=None, in_loc=None):
        self.set_param_dict(params)
        self.location = None
        if in_loc is not None:
            self.read(in_loc)
            self.location = in_loc

    def set_param_dict(self, params):
        self.params = params

    def params_to_str(self):
        if self.params is None:
            raise ValueError()
        out_str = ""
        out_str += ("mapping = {\n")
        for k, v in self.params.items():
            out_str += ("\t{}:".format(self._val_to_str(str(k))))
            if isinstance(v, dict):
                out_str += ("\n\t\t{\n")
                for k2, v2 in v.items():
                    out_str += ("\t\t {}: {},\n".format(
                        self._val_to_str(str(k2)), self._val_to_str(v2)))
                out_str += ("\t\t},\n")
            else:
                out_str += (" {},\n".format(
                    self._val_to_str(v)))
        out_str += ("\t}")
        return out_str

    def write(self, out_loc, out_str=None):
        with open(out_loc, "w") as f:
            if out_str is None:
                out_str = self.params_to_str()
            f.write(out_str)

    def read(self, in_loc):
        self.set_param_dict(read_python(in_loc)["mapping"])

    def get(self, key, default=None):
        if key in self.params.keys():
            return self[key]
        else:
            return default

    def set_default_params(self):
        self.location = os.path.join(
            os.path.dirname(__file__), "params", "default_params.py")
        self.read(self.location)

    def batch_write(
            self, start_dir, re_filters=None, fname="simuran_params.py",
            overwrite=True, check_only=False, return_absolute=True):
        dirs = get_dirs_matching_regex(
            start_dir, re_filters=re_filters, return_absolute=return_absolute)

        if check_only:
            print("Would write parameters to the following dirs")
            for d in dirs:
                print(d)
            return dirs

        out_str = self.params_to_str()
        for d in dirs:
            write_loc = os.path.join(d, fname)
            print("Writing params to {}".format(write_loc))
            self.write(write_loc, out_str=out_str)

    @staticmethod
    def clear_params(start_dir, recursive=True):
        fnames = get_all_files_in_dir(
            start_dir, ext=".py", recursive=recursive)
        for fname in fnames:
            if os.path.basename(fname) == "simuran_params.py":
                print("Removing {}".format(fname))
                os.remove(fname)

    def interactive_refilt(self, start_dir):
        re_filt = ""
        dirs = []
        while True:
            this_re_filt = input(
                "Please enter the regexes seperated by SIM_SEP to test or quit / qt to move on:\n")
            done = (
                (this_re_filt.lower() == "quit") or
                (this_re_filt.lower() == "qt"))
            if done:
                break
            if this_re_filt == "":
                re_filt = None
            else:
                re_filt = this_re_filt.split(" SIM_SEP ")
            dirs = self.batch_write(
                start_dir, re_filters=re_filt, check_only=True,
                return_absolute=False)
        print("The final regex was: {}".format(re_filt))
        return re_filt, dirs

    def __getitem__(self, key):
        return self.params[key]

    def __repr__(self):
        return ("{} from {} with params:\n{}".format(
            self.__class__.__name__, self.location,
            pformat(self.params, width=200)))

    @staticmethod
    def _val_to_str(val):
        if isinstance(val, str):
            return "\'{}\'".format(val)
        else:
            return val