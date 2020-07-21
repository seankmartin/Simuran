"""This module provides a container for multiple recording objects."""

import os
from copy import deepcopy

from simuran.base_container import AbstractContainer
from simuran.recording import Recording
from skm_pyutils.py_path import get_all_files_in_dir
from skm_pyutils.py_path import get_dirs_matching_regex


class RecordingContainer(AbstractContainer):
    """
    A class to hold recording objects.

    Attributes
    ----------
    load_on_fly : bool
        Should information be loaded at the start in bulk, or as needed.
    last_loaded : simuran.recording.Recording
        A reference to the last used recording.
    last_loaded_idx : int
        The index of the last loaded recording.
    base_dir : str
        The base directory where the recording files are stored.

    Parameters
    ----------
    load_on_fly : bool, optional
        Sets the load_on_fly attribute, by default True
    **kwargs : keyword arguments
        Currently these are not used.

    """

    def __init__(self, load_on_fly=True, **kwargs):
        """See help(RecordingContainer)."""
        super().__init__()
        self.load_on_fly = load_on_fly
        self.last_loaded = Recording()
        self.last_loaded_idx = None
        self.base_dir = None

    # TODO removing subset parameter but probably need it back
    def auto_setup(
        self,
        start_dir,
        param_name="simuran_params.py",
        recursive=True,
        file_regex_filter=None,
        batch_regex_filters=None,
        verbose=False,
    ):
        """
        Automically set up the recording container by finding valid files.

        Parameters
        ----------
        start_dir : str
            The directory to start the search in.
        param_name : str, optional
            The name of the parameter file to look for, by default "simuran_params.py"
        recursive : bool, optional
            Whether to recurse in subdirectories, by default True
        file_regex_filter : str, optional
            A regular expression to filter files by, by default None
        batch_regex_filters : list of str, optional
            A list of regular expressions to filter directories by, by default None
        verbose : bool, optional
            Whether to print extra information, by default False

        Returns
        -------
        list of strings
            The path to the parameter files used for set up.

        """
        fnames = get_all_files_in_dir(
            start_dir,
            ext=".py",
            return_absolute=True,
            recursive=recursive,
            case_sensitive_ext=True,
            re_filter=file_regex_filter,
        )
        dirs = get_dirs_matching_regex(
            start_dir, re_filters=batch_regex_filters, return_absolute=True
        )
        dirs = [d for d in dirs if ("__pycache__" not in d) and (d != "")]
        fnames = [
            fname
            for fname in fnames
            if (os.path.dirname(fname) in dirs)
            and (os.path.basename(fname) == param_name)
        ]
        return self.setup(fnames, start_dir)

    def setup(self, param_files, start_dir=None, verbose=False):
        """
        Set up the recording container.

        Parameters
        ----------
        param_files : list of str
            Each entry should be the path to a parameter file.
        start_dir : str, optional
            The directory to set self.base_dir to, defaults to None.
        verbose : bool, optional
            [description], by default False

        Returns
        -------
        [type]
            [description]
        """
        should_load = not self.load_on_fly
        out_str_load = "Loading" if should_load else "Parsing"
        for i, param_file in enumerate(param_files):
            if verbose:
                print(
                    "{} recording {} of {} at {}".format(
                        out_str_load, i + 1, len(param_files), param_file
                    )
                )
            recording = Recording(param_file=param_file, load=should_load)
            if not recording.valid:
                if verbose:
                    print("Last recording was invalid, not adding to container")
            else:
                self.append(recording)

        if start_dir is not None:
            self.base_dir = start_dir

        return param_files

    def get(self, idx):
        """
        Get the item at the specified index, and load it if not already loaded.

        Parameters
        ----------
        idx : int
            The index of the the item to retrieve.

        Returns
        -------
        simuran.recording.Recording
            The recording at the specified index.

        """
        if self.load_on_fly:
            if self.last_loaded_idx != idx:
                self.last_loaded = deepcopy(self[idx])
                self.last_loaded.load()
                self.last_loaded_idx = idx
            return self.last_loaded
        else:
            return self[idx]

    def get_results(self, idx=None):
        """
        Get the results stored on the objects in the container.

        Parameters
        ----------
        idx : int, optional
            If passed, the index of the item to get the results for, by default None.

        Returns
        -------
        list of dict, or dict
            If idx is None, a list of dictionaries, else a single dictionary.

        """
        return self.data_from_attr_list([("results", None)], idx=idx)

    def get_set_units(self):
        """
        Return all the units that are set in the container.

        Parameters
        ----------
        None

        Returns
        -------
        list of list of int
            The units that are set in the container.

        """
        all_units = []
        for r in self:
            unit_l = []
            for u in r.units:
                unit_l.append(u.units_to_use)
            all_units.append(unit_l)
        return all_units

    def subsample(self, idx_list=None, interactive=False, prop=None, inplace=False):
        """
        Subsample the recording, optionally in place.

        Parameters
        ----------
        idx_list : list of int, optional
            The indices to subsample, by default None
        interactive : bool, optional
            Launch an interactive prompt to subsample, by default False
        prop : str, optional
            An attribute to display in the interactive prompt, by default None
        inplace : bool, optional
            Whether the sampling should be performed in place, by default False

        Returns
        -------
        list of int, or simuran.recording_container.RecordingContainer
            A container with the subsampled items if inplace is False.
            The indices of the items subsampled from the container if inplace is True

        TODO
        ----
        Test with inplace set to False

        """
        if prop is None:
            prop = "source_file"
        return super().subsample(idx_list, interactive, prop, inplace)

    def find_recording_with_source(self, source_file):
        """
        Return the index of the recording in the container with the given source file.

        Parameters
        ----------
        source_file : str
            The source file to search for.

        Returns
        -------
        int
            The index of the recording in the container.

        Raises
        ------
        ValueError
            If two recordings with the same source file are found.
        LookupError
            If no recordings in the container have that source file.

        """
        found = False
        for i, recording in enumerate(self):
            compare = recording.source_file[-len(source_file) :]
            if source_file == compare:
                if not found:
                    found = True
                    location = i
                else:
                    raise ValueError("Found two recordings with the same source")
        if found:
            return location
        raise LookupError(
            "Could not find a recording with the source {}".format(source_file)
        )

    def subsample_by_name(self, source_files, inplace=False):
        """
        Subsample recordings in the container by a set of source filenames.

        Parameters
        ----------
        source_files : list of str
            The source files to subsample to.
        inplace : bool, optional
            Whether to perform the subsampling in place, by default False

        Returns
        -------
        list of int, or simuran.recording_container.RecordingContainer
            A container with the subsampled items if inplace is False.
            The indices of the items subsampled from the container if inplace is True

        TODO
        ----
        Test with inplace set to False

        """
        indexes = [self.find_recording_with_source(s) for s in source_files]
        return self.subsample(
            idx_list=indexes, interactive=False, prop="source_file", inplace=inplace
        )

    def _create_new(self, params):
        """
        Create a new recording with the given parameters.

        Parameters
        ----------
        params : str or dict
            Either a set of parameters or a path to a file listing the parameters.

        Returns
        -------
        simuran.recording.Recording
            The created recording

        """
        if isinstance(params, str):
            recording = Recording(param_file=params)
        else:
            recording = Recording(params=params)
        return recording

    def __str__(self):
        """Call on print."""
        s_files = "\n".join([r.source_file for r in self])
        return "{} with {} elements picked from {}:\n{}".format(
            self.__class__.__name__, len(self), self.base_dir, s_files
        )
