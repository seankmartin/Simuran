"""This module holds single experiment related information."""
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from simuran.core.base_class import BaseSimuran


@dataclass
class Recording(BaseSimuran):
    """
    Describe a full recording session and holds data.

    This holds single unit information, spatial information,
    EEG information, stimulation information, and
    event information.

    Note that anything you want to store on this object that
    has not been accounted for in attributes, then this can
    be stored on self.info

    Attributes
    ----------
    attrs: dict or ParamHandler
        Fixed information about this object, e.g. model or session type.
    datetime : datetime.datetime
        The date associated with this object, e.g. recording date.
    tag : str
        An optional tag to describe the object.
        Default "untagged"
    loader : simuran.loader.BaseLoader
        A loader object that is used to load this object.
        The relationship between the loader and this object
        is established in self.load()
    source_file : str
        The path to the source file for this object.
        For instance, an NWB file or an online URL.
    last_loaded_source : str
        The path to the last file this object was loaded from.
    data : Any
        When this object is loaded, complex variables can be stored in data.
        For instance, an xarray object could be set as the data.
        Generally speaking it is where the large (in terms of memory) objects
        are stored after loading.
    results : dict
        A dictionary of results.
    available_data : list[str]
        A list of the available data on this recording as a string description.
        E.g. ["spatial:running_speed", "ophys:deltaf/f", "behaviour:lick_times"]
        This can be used in functions explicitly by following types, such
        as those in pynwb, or simply as a helpful flag when debugging/analysing etc.

    See also
    --------
    simuran.base_class.BaseSimuran

    """

    available_data: list = field(default_factory=list)

    def load(self):
        """Load each available attribute."""
        super().load()
        self.loader.load_recording(self)

    def parse_metadata(self):
        """Parse the metadata."""
        self.loader.parse_metadata(self)

    def parse_table_row(self, table, index):
        """Parse the table row."""
        self.loader.parse_table_row(table, index, self)

    def get_name_for_save(self, rel_dir=None):
        """
        Get the name of the recording for saving purposes.

        This is very useful when plotting.
        For example, if the recording is in foo/bar/foo/pie.py
        Then passing rel_dir as foo, would return the name as
        bar--foo--pie

        Parameters
        ----------
        rel_dir, str, optional
            The directory to take the path relative to, default is None.
            If None, it returns the full path with os.sep replaced by --
            and with no extension.

        Returns
        -------
        str
            The name for saving, it has no extension and os.sep replaced by --

        """
        path_sf = Path(self.source_file)
        if rel_dir is None:
            return "--".join(path_sf.with_suffix("").parts)
        name_up_to_rel = path_sf.relative_to(rel_dir).with_suffix("")
        return "--".join(name_up_to_rel.parts)

    def get_np_signals(self):
        """Return a 2D array of signals as a numpy array."""
        return np.array([s.samples for s in self.signals], float)

    def __del__(self):
        if self.loader is not None and hasattr(self.loader, "unload"):
            self.loader.unload(self)
