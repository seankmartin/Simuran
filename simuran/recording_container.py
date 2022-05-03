"""This module provides a container for multiple recording objects."""
from __future__ import annotations

import csv
import os
import pathlib
from collections.abc import Iterable as abcIterable
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Type, Union

import pandas as pd
from skm_pyutils.py_log import FileLogger, FileStdoutLogger
from skm_pyutils.py_path import get_all_files_in_dir, get_dirs_matching_regex

from simuran.base_container import AbstractContainer
from simuran.loaders.base_loader import BaseLoader, ParamLoader
from simuran.loaders.loader_list import loader_from_str
from simuran.recording import Recording

# TODO make this easier
log = FileStdoutLogger()
file_log = FileLogger("simuran_cli")


@dataclass
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
    invalid_recording_locations : list of str
        Paths to recordings that could not be set up.

    Parameters
    ----------
    load_on_fly : bool, optional
        Sets the load_on_fly attribute, by default True
    **kwargs : keyword arguments
        Currently these are not used.

    """

    load_on_fly: bool = True
    last_loaded: "Recording" = field(default_factory=Recording)
    loader: "BaseLoader" = field(default_factory=ParamLoader)
    metadata: dict = field(default_factory=dict)
    table: "pd.DataFrame" = field(default_factory=pd.DataFrame)

    def __init__(self, load_on_fly=True, **kwargs):
        """See help(RecordingContainer)."""
        super().__init__()
        self.load_on_fly = load_on_fly
        self.last_loaded = Recording()

    @classmethod
    def from_table(
        cls,
        table: "pd.DataFrame",
        loader: Union["BaseLoader", Iterable["BaseLoader"]],
    ) -> RecordingContainer:
        """
        Create a Recording container from a pandas dataframe.

        Parameters
        ----------
        df : pandas.DataFrame
            The dataframe to load from.
        loader :
        param_dir : str
            A path to the directory containing parameter files
        load : bool, optional
            Whether to load the data for the recording container.
            Defaults to False.

        Returns
        -------
        simuran.RecordingContainer

        """
        rc = cls(load_on_fly=True)
        rc.loader = loader
        rc.table = table

        for i in range(len(table)):
            if isinstance(rc.loader, abcIterable):
                loader = rc.loader[i]
            recording = Recording()
            loader.parse_row(table.iloc[i], recording)
            rc.append(recording)

        return rc

    # TODO perhaps these are move to their own place
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
        Automatically set up the recording container by finding valid files.

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
        return self.setup(fnames, start_dir, verbose=verbose)

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
            Whether to print more information, by default False

        Returns
        -------
        list of str
            The param_files that were loaded from

        """
        should_load = not self.load_on_fly
        out_str_load = "Loading" if should_load else "Parsing"
        good_param_files = []
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
                    log.print(
                        "WARNING: Recording from {} was invalid, not adding to container".format(
                            param_file
                        )
                    )
                file_log.warning("Recording from {} was invalid".format(param_file))
                self.invalid_recording_locations.append(param_file)
            else:
                self.append(recording)
                good_param_files.append(param_file)

        if start_dir is not None:
            self.base_dir = start_dir

        return good_param_files

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

    def get_invalid_locations(self):
        """
        Get a list of invalid locations (can not be loaded)

        For example, these recordings could have invalid mappings.

        Returns
        -------
        list
            These are in index form.

        """
        return self.invalid_recording_locations

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
            if os.path.normpath(source_file) == os.path.normpath(compare):
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

        """
        indexes = [self.find_recording_with_source(s) for s in source_files]
        return self.subsample(
            idx_list=indexes, interactive=False, prop="source_file", inplace=inplace
        )

    def select_cells(self, cell_location, do_cell_picker=False, overwrite=False):
        """
        Select cells to use from a file or interactive prompt.

        Parameters
        ----------
        cell_location : str
            Path to a file to save choice to or read choice from.
        do_cell_picker : bool, optional
            Whether to launch an interactive prompt to pick cells, by default False.
        overwrite : bool, optional
            Whether to overwrite an existing file, by default False.

        Returns
        -------
        None

        """
        if ((not os.path.isfile(cell_location)) or overwrite) and do_cell_picker:
            print("Starting unit select helper")
            units_to_use = self.pick_cells(cell_location)
            self.set_chosen_cells(units_to_use, cell_location)
        else:
            print("Loading cells from {}".format(cell_location))
            self.load_cells(cell_location)

    def load_cells(self, cell_location):
        """
        Load cells from a csv file at the given location.

        Parameters
        ----------
        cell_location : str
            Path to a csv file listing the cells to use.

        Returns
        -------
        None

        Raises
        ------
        FileNotFoundError
            If the file passed does not exist.

        """
        if not os.path.isfile(cell_location):
            raise FileNotFoundError(
                "No cell list available at {}.".format(cell_location)
            )
        with open(cell_location, "r") as f:
            if f.readline().strip().lower() != "all":
                reader = csv.reader(f, delimiter=",")
                for row in reader:
                    row = [x.strip() for x in row]
                    row[1:] = [int(x) for x in row[1:]]
                    try:
                        row[0] = int(row[0])
                        recording = self[row[0]]
                    except ValueError:
                        recording = self[
                            self.find_recording_with_source(os.path.normpath(row[0]))
                        ]
                    record_unit_idx = recording.units.group_by_property(
                        "group", row[1]
                    )[1][0]
                    recording.units[record_unit_idx].units_to_use = row[2:]

    def pick_cells(self, cell_location):
        """
        Launch an interactive prompt to select cells in this container.

        The chosen cells are saved to cell_location.

        1. Enter the word all to select every single unit.
        2. Enter a single number to select that unit from everything.
        3. Enter <group>_<unit-num> to analyse one unit.
        4. Enter Idx: Unit, Unit, Unit | Idx, Unit, Unit, ... for anything

        Parameters
        ----------
        cell_location : str
            The path to a file to save the selected cells to.

        Raises
        ------
        LookupError
            If any unit in the user input is not found.

        Returns
        -------
        list of tuple
            Each tuple is layed out as
            Recording container index, single unit group at that index, group units

        """
        total, all_cells, _ = self.print_units()
        final_units = []
        input_str = (
            "Please enter the units to analyse, the input options are:\n"
            + "\t 1. Enter the word all to select every single unit.\n"
            + "\t 2. Enter a single number to select that unit from everything.\n"
            + "\t 3. Enter <group>_<unit-num> to analyse one unit.\n"
            + "\t 4. Enter Idx: Unit, Unit, Unit | Idx: Unit, Unit, ... "
            + "to select anything\n"
        )

        user_inp = input(input_str)
        while user_inp == "":
            print("No user input entered, please enter something.\n")
            user_inp = input(input_str)

        # Handle option 1
        if user_inp == "all":
            with open(cell_location, "w") as f:
                f.write("all")
            return

        # Handle option 2 and 3
        try:
            parts = user_inp.strip().split("_")
            if len(parts) == 2:
                group, unit_number = parts
                group = int(group.strip())
                unit_number = int(unit_number.strip())
                unit_spec_list = [
                    [i, [unit_number]]
                    for i in range(total)
                    if all_cells[i][1][0] == group
                ]
            else:
                value = int(user_inp.strip())
                unit_spec_list = [[i, [value]] for i in range(total)]

        # Handle option 4
        except BaseException:
            unit_spec_list = []
            unit_specifications = user_inp.split("|")
            for u in unit_specifications:
                parts = u.split(":")
                idx = int(parts[0].strip())
                units = [int(x.strip()) for x in parts[1].split(",")]
                unit_spec_list.append([idx, units])

        # Use the result option 2, 3, or 4
        for u in unit_spec_list:
            for val in u[1]:
                if val not in all_cells[u[0]][1][1]:
                    raise LookupError(
                        "{}: {} not in {}".format(u[0], val, all_cells[u[0]][1][1])
                    )
            # Recording container index, single unit group at that index, group units
            final_units.append([all_cells[u[0]][0], all_cells[u[0]][1][0], u[1]])

        return final_units

    def set_chosen_cells(self, final_units, cell_location):
        """
        Set the cells available to final_units, and write chosen to cell_location.

        Parameters
        ----------
        final_units : list of tuple
            Each tuple should be layed out as
            Recording container index, single unit group at that index, group units
        cell_location : str
            Path to a file to write the choice to

        Returns
        -------
        None

        """
        with open(cell_location, "w") as f:
            max_num = max([len(u[2]) for u in final_units])
            unit_as_string = ["Unit_{}".format(i) for i in range(max_num)]
            unit_str = ",".join(unit_as_string)
            f.write("Recording,Group,{}\n".format(unit_str))
            for u in final_units:
                units_as_str = [str(val) for val in u[2]]
                unit_str = ",".join(units_as_str)
                recording = self[u[0]]
                f.write(
                    "{},{},{}\n".format(
                        os.path.normpath(
                            os.path.relpath(
                                recording.source_file,
                                self.base_dir,
                            )
                        ),
                        u[1],
                        unit_str,
                    )
                )
                record_unit_idx = recording.units.group_by_property("group", u[1])[1][0]
                recording.units[record_unit_idx].units_to_use = u[2]
            print("Saved cells to {}".format(cell_location))

    def print_units(self, f=None):
        """
        Print all the units in this container, optionally to a file.

        Also returns all the units found.

        Parameters
        ----------
        f : file, optional
            An open writable file, by default None

        Returns
        -------
        total : int
            The total number of groups in this container
        all_cells : list of tuples
            The first item in the tuple is the index of the recording in the container,
            The second item in the tuple is some of the units found for that recording,
            which is a tuple consisting of (group, units_in_group).
        printed : str
            The string which was printed

        """
        total = 0
        all_cells = []
        full_str = []
        for i in range(len(self)):
            was_available = self[i].available
            self[i].available = ["units"]
            recording = self.get(i)
            available_units = recording.get_available_units()
            ## TODO many files could have same name, use join on --
            out_str = "--------{}: {}--------\n".format(
                i, os.path.basename(recording.source_file)
            )
            self[i].available = was_available
            full_str.append(out_str)
            if f is not None:
                f.write(out_str)
            else:
                print(out_str, end="")

            any_units = False
            for available_unit in available_units:
                if len(available_unit[1]) != 0:
                    out_str = "    {}: Group {} with Units {}\n".format(
                        total, available_unit[0], available_unit[1]
                    )
                    full_str.append(out_str)
                    if f is not None:
                        f.write(out_str)
                    else:
                        print(out_str, end="")
                    all_cells.append([i, available_unit])
                    total += 1
                    any_units = True

            if not any_units:
                out_str = "    NONE\n"
                full_str.append(out_str)
                if f is not None:
                    f.write(out_str)
                else:
                    print(out_str, end="")

        final_str = "".join(full_str)
        return total, all_cells, final_str

    def set_all_units_on(self):
        """Flag all cells as to be analysed."""
        for i in range(len(self)):
            was_available = self[i].available
            self[i].available = ["units"]
            recording = self.get(i)
            available_units = recording.get_available_units()
            self[i].available = was_available
            for j in range(len(recording.units)):
                self[i].units[j].units_to_use = available_units[j][1]

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
        picked_location = (
            self.base_dir if self.base_dir is not None else "custom locations"
        )
        s_files = "\n".join([r.source_file for r in self])
        return "{} with {} elements picked from {}:\n{}".format(
            self.__class__.__name__, len(self), picked_location, s_files
        )
