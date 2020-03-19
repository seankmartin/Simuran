"""This module handles automatic creation of parameter files."""
from skm_pyutils.py_config import read_python
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
