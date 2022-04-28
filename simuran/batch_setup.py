"""This module assists with writing parameters needed for batch analysis."""


import os
import shutil
from pprint import pformat

from simuran.param_handler import ParamHandler
from skm_pyutils.py_path import get_all_files_in_dir


class BatchSetup(object):
    """
    Help managing parameters for running batch operations.

    Parameters
    ----------
    in_dir : str
        Sets attribute in_dir.
    fpath : str
        Either the full path to a parameter file, or just
        the name of the parameter file relative to in_dir.
        This should describe how batch_setup will behave.
    ph : simuran.params.ParamHandler
        A param handler that holds the configuration.
    dirname_replacement : str
        What to replace "__dirname__" by in config files

    Attributes
    ----------
    in_dir : str
        The path to the directory to start batch operations in.
    fpath : str
        The path to the parameter file describing the behaviour.
    only_check : bool
        Whether files should actually be written out,
        or just have the paths that would be written to printed out.
    dirname_replacement : str
        What to replace "__dirname__" by in config files
    _bad_file : bool
        True if the file passed is not valid, or not passed.

    Example
    -------
    .. highlight:: python
    .. code-block:: python

        batch_setup = BatchSetup(directory, fpath="params.py")
        batch_setup.interactive_refilt()
        print(batch_setup)
        batch_setup.write_batch_params()
    """

    def __init__(self, in_dir, fpath="simuran_batch_params.py", dirname_replacement=""):
        """See help(BatchSetup)."""
        super().__init__()
        self.in_dir = in_dir
        if not os.path.isfile(fpath):
            if os.path.isfile(os.path.join(self.in_dir, fpath)):
                self.file_loc = os.path.join(self.in_dir, fpath)
        else:
            self.file_loc = fpath
        self.dirname_replacement = dirname_replacement
        self.setup()
        self.only_check = False

    def set_only_check(self, val):
        """
        Set the value of only_check.

        Parameters
        ----------
        val : bool
            The value to set.

        Returns
        -------
        None

        """
        self.only_check = val

    def setup(self):
        """Call on initialisation."""
        self.ph = ParamHandler(
            in_loc=self.file_loc,
            name="params",
            dirname_replacement=self.dirname_replacement,
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

    def start(self):
        """Start the main control function."""
        if self.ph["interactive"]:
            print("Interactive mode selected")
            self.interactive_refilt()
        self.write_batch_params(verbose_params=True)

    def interactive_refilt(self):
        """Launch an interactive prompt to design REGEX filters for batch operation."""
        if self._bad_file:
            new_ph = ParamHandler(params=self.ph["mapping"])
        else:
            new_ph = ParamHandler(in_loc=self.ph["mapping_file"])
        regex_filts, _ = new_ph.interactive_refilt(
            self.in_dir, self.ph["regex_filters"]
        )
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
        """
        Write parameters to the established locations in setup.

        If verbose_params is True, prints the files that would be written to.

        Parameters
        ----------
        verbose_params : bool, optional
            Whether to write the parameters in short or long format, default is False.
            E.g. if params = [1, 2, 3] * 2, verbose_params set to True would write
            [1, 2, 3, 1, 2, 3], while false would write params = [1, 2, 3] * 2
        verbose : bool, optional
            Whether to print out extra information during execution, default is False.

        Returns
        -------
        list
            A list of directories that were written to.

        Raises
        ------
        ValueError
            If a non-existent file is attempted to be written.
            Can only occur in non verbose_params mode.

        """
        check_only = self.ph["only_check"] or self.only_check
        overwrite = self.ph["overwrite"]
        re_filts = self.ph["regex_filters"]
        delete_old_files = self.ph.get("delete_old_files", False)

        if delete_old_files and not check_only:
            BatchSetup.clear_params(self.in_dir, to_remove=self.ph["out_basename"])

        if verbose_params and not check_only:
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
        """
        Remove all files with the name to_remove from start_dir.

        Parameters
        ----------
        start_dir : str
            Where to start removing files from
        to_remove : str, optional
            The name of the files to remove, by default "simuran_params.py"
        recursive : bool, optional
            Whether to recursive through child directories, by default True
        verbose : bool, optional
            Whether to print the files that were deleted, by default False

        Returns
        -------
        None

        """
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
        """
        Find all directories that have to_find in them.

        Parameters
        ----------
        start_dir : str
            Where to start the search from.
        to_find : str, optional
            What filename to find, by default "simuran_params.py"
        recursive : bool, optional
            Whether to recurse through child directories, by default True

        Returns
        -------
        list
            Paths to each of the files found.
        """
        fnames = get_all_files_in_dir(start_dir, ext=".py", recursive=recursive)

        def keep_file(filename):
            return ("__pycache__" not in filename) and (
                os.path.basename(filename) == to_find
            )

        return [fname for fname in fnames if keep_file(fname)]

    @staticmethod
    def get_params_matching_pattern(
        start_dir, re_filter=".*simuran.*params", recursive=True
    ):
        """
        Find all files matching a regex pattern.

        Parameters
        ----------
        start_dir : str
            Where to start the search from.
        re_filter : str, optional
            A regular expression pattern, by default ".*simuran.*params"
        recursive : bool, optional
            Whether to recurse into subdirectories, by default True

        Returns
        -------
        list
            Paths to the files found.

        """
        fnames = get_all_files_in_dir(
            start_dir, ext=".py", recursive=recursive, re_filter=re_filter
        )

        def keep_file(filename):
            return "__pycache__" not in filename

        return [fname for fname in fnames if keep_file(fname)]

    @staticmethod
    def copy_params(
        from_dir, to_dir, re_filter=".*simuran.*params", recursive=True, test_only=False
    ):
        """
        Copy all parameters matching a regex between directories.

        Parameters
        ----------
        from_dir : str
            Path to the directory to copy from.
        to_dir : str
            Path to the directory to copy to.
        re_filter : str, optional
            A regular expression pattern, by default ".*simuran.*params"
        recursive : bool, optional
            Whether to recurse into subdirectories, by default True
        test_only : bool, optional
            If True, it only prints what would be copied, by default False

        Returns
        -------
        None

        """
        files = BatchSetup.get_params_matching_pattern(
            from_dir, re_filter=re_filter, recursive=recursive
        )

        for f in files:
            file_without_base = f[len(from_dir + os.sep) :]
            dest = os.path.join(to_dir, file_without_base)

            if test_only:
                print("Would copy {} to {}".format(f, dest))
            else:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy(f, dest)

    def __str__(self):
        """Call on print."""
        return "{} from {} with parameters:\n {} ".format(
            self.__class__.__name__, self.file_loc, pformat(self.ph.params, width=200)
        )
