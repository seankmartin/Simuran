"""This module handles automatic creation of parameter files."""
from skm_pyutils.py_config import read_python
from typing import Iterable


class ParamHandler:
    def __init__(self, params=None):
        self.params = params

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

    @staticmethod
    def _val_to_str(val):
        if not isinstance(val, Iterable) or isinstance(val, str):
            print("{} is not iterable".format(val))
            return "\'{}\'".format(val)
        else:
            return val
