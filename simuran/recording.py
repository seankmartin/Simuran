"""This module holds single experiment related information."""
import logging
import os
from dataclasses import dataclass
from typing import Union

import astropy.units as u
import numpy as np
from skm_pyutils.py_config import split_dict

from simuran.base_class import BaseSimuran
from simuran.base_container import GenericContainer
from simuran.base_signal import BaseSignal
from simuran.eeg import Eeg, EegArray
from simuran.param_handler import ParamHandler
from simuran.single_unit import SingleUnit
from simuran.spatial import Spatial


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
    signals : list of simuran.base_signal.BaseSignal
        The signals in the recording.
    units : list of simuran.single_unit.SingleUnit
        The single units in the recording.
    spatial : list of simuran.spatial.Spatial
        The spatial information in the recording.
    stimulation : list of TODO
        The stimulation, events, and stimuli in the recording.
    available : list of strings
        Each value in the list should be present if the information is available.
        E.g. available = ["signals", "spatial"] would indicate
        that this recording has EEG information and spatial information only.
    param_handler : simuran.param_handler.ParamHandler
        Parameters which describe the information in the recording.
    source_file : str
        The path to the underlying source file describing the recording.
        When recordings have many source files, this should be either
        the directory where they are all located, or a file listing them.
    source_files : dict
        A dictionary describing the source files for each attribute.

    Parameters
    ----------
    params : dict, optional
        Direct parameters which describe the recording, default is None
        See simuran.params.simuran_base_params for what can be passed.
    param_file : str, optional
        The path to a file which contains parameters, default is None
    base_file : str, optional
        Sets the value of self.source_file, default is None
    load : bool, optional
        Whether to load the recording on initialisation, default is True

    See also
    --------
    simuran.base_class.BaseSimuran

    """

    def load(self):
        """Load each available attribute."""
        super().load()
        self.loader.load_recording(self)

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

    def _parse_source_files(self):
        """
        Set the value of self.source_files based on the parameters.

        This only functions for things that have been set as available.

        """
        source_files = {}
        for item, name in zip(self.get_available(), self.available):
            if isinstance(item, GenericContainer):
                source_files[name] = [s.source_file for s in item]
            else:
                source_files[name] = item.source_file
        self.source_files = source_files

    def setup_from_file(self, param_file, load=True):
        """
        Set up this recording from a source parameter file.

        Parameters
        ----------
        param_file : str
            The parameter file to setup from.
        load : bool, optional
            Whether the information should be loaded, by default True

        Returns
        -------
        None

        """
        self.param_handler = ParamHandler(source_file=param_file)
        self._setup(load=load)

    def setup_from_dict(self, params, load=True):
        """
        Set up this recording from a dictionary of parameters.

        Parameters
        ----------
        params : dict
            The parameters to setup from.
        load : bool, optional
            Whether the information should be loaded, by default True

        Returns
        -------
        None

        """
        self.param_handler = ParamHandler(params=params)
        self._setup(load=load)
