"""This module provides a container for multiple recording objects."""
from __future__ import annotations

import copy
import os
from collections.abc import Iterable as abcIterable
from dataclasses import dataclass, field
import logging
from pathlib import Path
import pickle
from typing import TYPE_CHECKING, Iterable, Optional, Union, overload
from skm_pyutils.table import df_to_file

import pandas as pd

from simuran.core.base_container import GenericContainer
from simuran.recording import Recording

if TYPE_CHECKING:
    from simuran.loaders.base_loader import BaseLoader

module_logger = logging.getLogger("simuran.recording_container")


@dataclass
class RecordingContainer(GenericContainer):
    """
    A class to hold recording objects.

    Attributes
    ----------
    load_on_fly : bool
        Should information be loaded at the start in bulk, or as needed.
    last_loaded : simuran.recording.Recording
        A reference to the last used recording.
    _last_loaded_idx : int
        The index of the last loaded recording.
    attrs : dict
        Dictionary of metadata.
    invalid_recording_locations : list of int
        Index of recordings that could not be set up.
    table : Dataframe
        A table which describes each recording in the container.
        For example, each row could contain metadata about the session,
        and a path to a source NWB file to load the data for that session.

    """

    load_on_fly: bool = True
    last_loaded: "Recording" = field(default_factory=Recording)
    loader: Optional["BaseLoader"] = field(default=None)
    attrs: dict = field(default_factory=dict)
    invalid_recording_locations: list = field(default_factory=list)
    table: "pd.DataFrame" = field(default_factory=pd.DataFrame)
    _last_loaded_idx: int = field(repr=False, init=False, default=-1)

    @classmethod
    def from_table(
        cls,
        table: "pd.DataFrame",
        loader: Union["BaseLoader", Iterable["BaseLoader"]],
        load_on_fly: bool = True,
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
        load_on_fly : bool, optional
            Whether to load the data for the recording container on the fly.
            Defaults to True (best for memory usage).

        Returns
        -------
        simuran.RecordingContainer

        """
        rc = cls(load_on_fly=load_on_fly)
        rc.loader = loader
        rc.table = table

        for i in range(len(table)):
            if isinstance(rc.loader, abcIterable):
                loader = rc.loader[i]
            recording = Recording()
            module_logger.debug(f"Parsing information from table for row {i}")
            loader.parse_table_row(table, i, recording)
            rc.append(recording)

        return rc

    def load(self) -> None:
        ...
        """Load all recordings."""

    @overload
    def load(self, idx: int) -> "Recording":
        ...
        """Load recording at index idx and return it."""

    def load(self, idx: Optional[int] = None) -> "Recording":
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
        if idx is None:
            if self.load_on_fly:
                raise RuntimeError("Can't bulk load when load_on_fly=True")
            for r in self:
                r.load()
            return
        if self.load_on_fly:
            if self._last_loaded_idx != idx:
                self.last_loaded = copy.copy(self[idx])
                self.last_loaded.load()
                self._last_loaded_idx = idx
            return self.last_loaded
        else:
            self[idx].load()
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
        return [item.results for item in self] if idx is None else self[idx].results

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
                if found:
                    raise ValueError("Found two recordings with the same source")
                found = True
                location = i
        if found:
            return location
        raise LookupError(f"Could not find a recording with the source {source_file}")

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

    def load_iter(self):
        """Iterator through the container that loads data on item retrieval."""
        return RecordingContainerLoadIterator(self)

    def dump(self, filename, results_only=True):
        """
        Dump recording_container to file with pickle.

        Parameters
        ----------
        filename : str or Path
            The output path.
        results_only : bool, optional
            Only save the results

        Returns
        -------
        None

        """
        to_dump = self.get_results() if results_only else self
        with open(filename, "wb") as outfile:
            pickle.dump(to_dump, outfile)

    def save_results_to_table(self, filename=None):
        """
        Dump recording_container to file with pickle.

        Parameters
        ----------
        filename : str or Path
            The output path.
        results_only : bool, optional
            Only save the results

        Returns
        -------
        Dataframe
            The resulting dataframe

        """
        results = self.get_results()
        for res_dict, item in zip(results, self):
            sfile = item.source_file
            if sfile is not None:
                sfile = Path(sfile)
                res_dict.setdefault("Directory", sfile.parent)
                res_dict.setdefault("Filename", sfile.name)
        df = pd.DataFrame.from_dict(results)

        if filename is not None:
            df_to_file(df, filename)

        return df


class RecordingContainerLoadIterator(object):
    """An iterator for loading recording container on the fly."""

    def __init__(self, recording_container: "RecordingContainer"):
        self.recording_container = recording_container
        self.current = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.current += 1
        if self.current < len(self.recording_container):
            return self.recording_container.load(self.current)
        raise StopIteration
