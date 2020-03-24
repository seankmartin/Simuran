"""This module handles automatic creation of parameter files."""
import os

from skm_pyutils.py_config import read_python
from skm_pyutils.py_path import get_dirs_matching_regex
from typing import Iterable


class ParamHandler:
    def __init__(self, params=None, in_loc=None):
        self.params = params
        self.location = None
        if in_loc is not None:
            self.read(in_loc)
            self.location = in_loc

    def set_param_dict(self, params):
        self.params = params

    def write(self, out_loc):
        if self.params is None:
            raise ValueError()
        with open(out_loc, "w") as f:
            f.write("mapping = {\n")
            for k, v in self.params.items():
                f.write("\t{}:".format(self._val_to_str(k)))
                if isinstance(v, dict):
                    f.write("\n\t\t{\n")
                    for k2, v2 in v.items():
                        f.write("\t\t {}: {},\n".format(
                            self._val_to_str(k2), self._val_to_str(v2)))
                    f.write("\t\t},\n")
                else:
                    f.write(" {},\n".format(
                        self._val_to_str(v)))
            f.write("\t}")

    def read(self, in_loc):
        self.params = read_python(in_loc)["mapping"]

    def get(self, key, default=None):
        if key in self.params.keys():
            return self[key]
        else:
            return default

    def set_default_params(self):
        self.location = os.path.join(
            os.path.dirname(__file__), "default_params.py")
        self.read(self.location)

    def batch_write(
            self, start_dir, re_filter=None, check_only=False,
            return_absolute=True):
        dirs = get_dirs_matching_regex(
            start_dir, re_filter=re_filter, return_absolute=return_absolute)

        if check_only:
            print("Would write parameters to the following dirs")
            for d in dirs:
                print(d)
        return dirs

    def interactive_refilt(self, start_dir):
        re_filt = ""
        dirs = []
        while True:
            this_re_filt = input(
                "Please enter the regex to test or quit or qt to move on:\n")
            done = (
                (this_re_filt.lower() == "quit") or
                (this_re_filt.lower() == "qt"))
            if done:
                break
            if this_re_filt == "":
                re_filt = None
            else:
                re_filt = this_re_filt
            dirs = self.batch_write(
                start_dir, re_filter=re_filt, check_only=True,
                return_absolute=False)
        print("The final regex was: {}".format(re_filt))
        return re_filt, dirs

    def __getitem__(self, key):
        return self.params[key]

    def __repr__(self):
        return ("{} with params {} from {}".format(
            self.__class__.__name__, self.params, self.location))

    @staticmethod
    def _val_to_str(val):
        if not isinstance(val, Iterable) or isinstance(val, str):
            return "\'{}\'".format(val)
        else:
            return val
