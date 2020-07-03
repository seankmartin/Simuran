import os
import shutil
from pprint import pformat

from simuran.param_handler import ParamHandler
from skm_pyutils.py_path import get_all_files_in_dir


class BatchSetup(object):
    """
    Example usage is:

    batch_setup = BatchSetup(directory)
    print(batch_setup)
    batch_setup.write_batch_params()
    """

    def __init__(self, in_dir, fname="simuran_batch_params.py"):
        self.in_dir = in_dir
        self.fname = fname
        self.file_loc = os.path.join(self.in_dir, self.fname)
        self.setup()

    def setup(self):
        self.ph = ParamHandler(in_loc=self.file_loc, name="params")
        if os.path.dirname(self.ph["mapping_file"]) == "":
            self.ph.params["mapping_file"] = os.path.join(
                self.in_dir, self.ph["mapping_file"]
            )
        self._bad_file = self.ph["mapping_file"] is None
        if not self._bad_file:
            self._bad_file = not os.path.isfile(self.ph["mapping_file"])
        if self.ph["mapping"] == {} and self._bad_file:
            raise ValueError(
                "Please pass either a valid mapping file "
                + "or a parameter mapping, "
                + "currently:\n {} and {} respectively\n".format(
                    self.ph["mapping_file"], self.ph["mapping"]
                )
            )
        if self.ph["interactive"]:
            print("Interactive mode selected")
            self.interactive_refilt()

    def interactive_refilt(self):
        regex_filts, _ = self.ph.interactive_refilt(self.in_dir)
        neuro_file = open(self.file_loc, "r")
        temp_file = open("temp.txt", "w")
        for line in neuro_file:

            if line.startswith("regex_filters ="):
                line = "regex_filters = " + str(regex_filts) + "\n"
                print("Set the regex filters to: " + line)
                temp_file.write(line)
            elif line.startswith("interactive ="):
                line = "interactive = False\n"
                temp_file.write(line)
            else:
                temp_file.write(line)

        neuro_file.close()
        temp_file.close()

        os.remove(self.file_loc)
        shutil.move("temp.txt", self.file_loc)
        self.setup()

    def write_batch_params(self, verbose_params=False, verbose=False):
        """If verbose_params is True, writes the result of executing code."""
        check_only = self.ph["only_check"]
        overwrite = self.ph["overwrite"]
        re_filts = self.ph["regex_filters"]

        if verbose_params:
            if self._bad_file:
                new_ph = ParamHandler(params=self.ph["mapping"])
            else:
                new_ph = ParamHandler(in_loc=self.ph["mapping_file"])
            dirs = new_ph.batch_write(
                self.in_dir,
                re_filters=re_filts,
                fname=self.ph["out_basename"],
                check_only=check_only,
                overwrite=overwrite,
                verbose=verbose,
            )
        else:
            fname = self.ph["mapping_file"]
            if self._bad_file:
                raise ValueError("Can't copy non-existant file {}".format(fname))
            dirs = self.ph.batch_write(
                self.in_dir,
                re_filters=re_filts,
                fname=self.ph["out_basename"],
                check_only=check_only,
                overwrite=overwrite,
                exact_file=fname,
                verbose=verbose,
            )
        return dirs

    @staticmethod
    def clear_params(
        start_dir, to_remove="simuran_params.py", recursive=True, verbose=False
    ):
        fnames = BatchSetup.get_param_locations(
            start_dir, to_find=to_remove, recursive=recursive
        )
        for fname in fnames:
            if os.path.basename(fname) == to_remove:
                if verbose:
                    print("Removing {}".format(fname))
                os.remove(fname)

    @staticmethod
    def get_param_locations(start_dir, to_find="simuran_params.py", recursive=True):
        fnames = get_all_files_in_dir(start_dir, ext=".py", recursive=recursive)

        def keep_file(filename):
            return (not "__pycache__" in filename) and (
                os.path.basename(filename) == to_find
            )

        return [fname for fname in fnames if keep_file(fname)]

    def __str__(self):
        return "{} from {} with parameters:\n {} ".format(
            self.__class__.__name__, self.file_loc, pformat(self.ph.params, width=200)
        )
