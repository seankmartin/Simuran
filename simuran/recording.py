"""This module holds single experiment related information."""
import os
from dataclasses import dataclass, field

import astropy.units as u
import numpy as np

from simuran.base_class import BaseSimuran
from simuran.eeg import Eeg, EegArray


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

    def get_available(self):
        """Get the available attributes."""
        return [getattr(self, item) for item in self.available]

    def set_base_file(self, base):
        """Set the source file of this recording."""
        self.source_file = base

    def get_signal_channels(self, as_idx=False):
        """
        Get the channel of each signal in the recording.

        Parameters
        ----------
        as_idx : bool, optional
            If true, just returns [i for i in range(num_signals)]

        Returns
        -------
        list
            The channels found. Returns None if no channels are set.

        """
        if self.signals is None:
            if self.param_handler.get("signals", None) is not None:
                num_sigs = self.param_handler["signals"]["num_signals"]
                if as_idx:
                    return [i for i in range(num_sigs)]
                default_chans = [i + 1 for i in range(num_sigs)]
                chans = self.param_handler["signals"].get("channels", default_chans)
                return chans
            else:
                return None
        else:
            chans = []
            if as_idx:
                return [i for i in range(len(self.signals))]
            for s in self.signals:
                if s.channel is not None:
                    chans.append(s.channel)
                else:
                    return [i for i in range(len(self.signals))]
            return chans

    def get_unit_groups(self):
        """
        Get the groups of the units.

        For example, the list of tetrodes in the recording.
        Or the IDs of the sites on a ephys probe.

        Returns
        -------
        list
            The found groups. Returns None if none are set yet.
        """
        if self.units is None:
            if self.param_handler.get("units", None) is not None:
                groups = self.param_handler["units"]["group"]
                return groups
            else:
                return None
        else:
            groups = set([unit.group for unit in self.units])

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
        if rel_dir is None:
            base_name_part, _ = os.path.splitext(os.path.basename(self.source_file))
        else:
            name_up_to_rel = self.source_file[len(rel_dir + os.sep) :]
            base_name_part, _ = os.path.splitext(name_up_to_rel)
            base_name_part = base_name_part.replace(os.sep, "--")
        return base_name_part

    def get_available_units(self):
        """
        Get the list of available units.

        Returns
        -------
        list
            list of tuple(group, list of units)

        """
        all_units = []
        for i, unit in enumerate(self.units):
            all_units.append([unit.group, unit.get_available_units()])
        return all_units

    def load_available_neurochat_units(self):
        """
        Load and return the available neurochat units.

        Returns
        -------
        generator
            generator of SingleUnit instances.

        """
        available_units = self.get_available_units()
        non_zero_units = [(g, u) for (g, u) in available_units if len(u) != 0]
        for group, units in non_zero_units:
            print("Using tetrode {} unit {}".format(group, units[0]))
            idx = self.units.group_by_property("group", group)[1][0]
            unit = self.units[idx]
            unit.load()
            spike_obj = unit.underlying
            spike_obj.set_unit_no(units[0])
            yield spike_obj

    def get_set_units(self):
        """Get the units which are set for analysis."""
        return [unit.units_to_use for unit in self.units]

    def get_set_units_as_dict(self):
        """Get the units which are set as a dictionary"""
        groups = [unit.group for unit in self.units]
        units = self.get_set_units()
        out_dict = {}

        for g, u in zip(groups, units):
            out_dict[g] = u

        return out_dict

    def get_signals(self):
        """Get the signals."""
        return self.signals

    def get_eeg_signals(self, copy=True):
        """
        Get the eeg signals as an EegArray.

        Parameters
        ----------
        copy : bool, optional
            Whether to copy the retrieved signals, by default True.

        Returns
        -------
        simuran.eeg.EegArray
            The signals as an EegArray.

        """
        inplace = not copy
        eeg_array = EegArray()
        _, eeg_idxs = self.signals.group_by_property("channel_type", "eeg")
        eeg_sigs = self.signals.subsample(idx_list=eeg_idxs, inplace=inplace)
        if inplace:
            eeg_sigs = self.signals
        eeg_array.set_container([Eeg(signal=eeg) for eeg in eeg_sigs])

        return eeg_array

    def get_np_signals(self):
        """Return a 2D array of signals as a numpy array."""
        return np.array([s.samples for s in self.signals], float)

    def get_unit_signals(self):
        """Return a 2D array of signals with units."""
        return np.array([s.samples.to(u.mV) for s in self.signals], float) * u.mV

    def __del__(self):
        if self.loader is not None:
            if hasattr(self.loader, "unload"):
                self.loader.unload(self)
