"""Module to hold the abstract class setting up information held in a signal."""
import logging
import math
from copy import deepcopy

import mne
import numpy as np
from astropy import units as u
from simuran.core.base_class import BaseSimuran


class BaseSignal(BaseSimuran):
    """
    Describes the base information for a regularly sampled signal.

    For example, LFP or EEG could be represented.

    Attributes
    ----------
    timestamps : array style object
        The timestamps of the signal sampling
    samples : array style object
        The value of the signal at sample points.
        By default, this is assumed to be stored in mV.
    sampling_rate : int
        The sampling rate of the signal in Hz
    region : str
        The brain region that the signal is associated with
    group : object
        An optional value to group on.
        For example, if wires are bundled, this could indicate the bundle number.
    channel : object
        The channel id of the signal.
    channel_type : str
        The type of the signal channel, e.g. eeg.
        Default is "eeg".
    unit : astropy.unit.Unit
        An SI unit measure of the signal. This is set at load time.
    source_file : str
        The path to a source file containing the signal data.

    """

    def __init__(self):
        """See help(BaseSignal)."""
        super().__init__()
        self.timestamps = None
        self.samples = None
        self.sampling_rate = None
        self.region = None
        self.group = None
        self.channel = None
        self.channel_type = "eeg"
        self.conversion = 1.0  # To convert to Volts

    ## TODO design thoughts!
    ## Passing source_file vs full recording??
    def load(self, *args, **kwargs):
        """Load the signal."""
        ## TODO is this needed? If yes, add to other classes
        res = super().load()
        if res == "skip":
            return
        load_result = self.loader.load_signal(self.source_file, **kwargs)
        self.save_attrs(load_result)
        self.last_loaded_source = self.source_file

    @classmethod
    def from_numpy(cls, np_array, sampling_rate):
        """
        Set data from a numpy array, assumed in mV and srate in Hz.

        Parameters
        ----------
        np_array : numpy array
            The data in mV.
        sampling_rate : int
            The sampling rate of the signal in Hz.

        Returns
        -------
        None

        """
        signal = cls()
        signal.samples = np_array
        signal.sampling_rate = sampling_rate
        signal.timestamps = [i / sampling_rate for i in range(len(signal.samples))]
        return signal

    def default_name(self):
        """Get the default name for this signal based on region."""
        name = self.channel_type
        if self.channel is not None:
            name += f" {self.channel}"
        if self.region is not None:
            name = f"{self.region} - {name}"

        return name

    def to_neurochat(self):
        """Convert to NeuroChaT NLfp object."""
        from neurochat.nc_lfp import NLfp

        if self.data is not None and type(self.data) == NLfp:
            return self.data

        lfp = NLfp()
        lfp.set_channel_id(self.channel)
        lfp._timestamp = np.array(self.timestamps * u.mV)
        lfp._samples = np.array(self.samples * u.s)
        lfp._record_info["Sampling rate"] = self.sampling_rate
        return lfp

    def in_range(self, start, stop, step=None):
        """
        Splice samples from second based times.

        Parameters
        ----------
        start : int
            The start time in seconds to grab samples from
        stop : int
            The end time in seconds to grab samples from
        step : int, optional
            The amount to skip, as in normal array splicing.

        Returns
        -------
        np.array
            The spliced array

        """
        start = int(math.floor(start * self.sampling_rate))
        stop = int(math.ceil(stop * self.sampling_rate))
        if step is None:
            return self.samples[start:stop]
        step = int(math.round(self.step * self.sampling_rate))
        return self.samples[start:stop:step]

    def filter(self, low, high, inplace=False, **kwargs):
        """
        Filter the signal.

        Parameters
        ----------
        low : float
            The low frequency for filtering.
        high : float
            The high frequency for filtering.
        inplace : bool, optional
            Whether to perform the operation in place, by default False

        Keyword arguments
        -----------------
        See https://mne.tools/stable/generated/mne.filter.filter_data.html

        Returns
        -------
        simuran.eeg.Eeg
            The filtered signal.

        """
        kwargs["copy"] = not inplace
        if (low is None) or (high is None):
            logging.warning("Invalid filter frequencies")
            return self
        filtered_data = mne.filter.filter_data(
            np.array(self.samples.to(u.V)), self.sampling_rate, low, high, **kwargs
        )
        if not inplace:
            eeg = deepcopy(self)
            eeg.samples = (filtered_data * u.V).to(u.mV)
            return eeg
        else:
            self.samples = (filtered_data * u.V).to(u.mV)
            return self

    def get_duration(self):
        """Get the length of the signal in the unit of timestamps."""
        return max(self.timestamps) - min(self.timestamps)

    def get_start(self):
        """Get the first time recorded"""
        return self.timestamps[0]

    def get_end(self):
        """Get the last time recorded"""
        return self.timestamps[-1]


def convert_signals_to_mne(signals, ch_names=None, verbose=True):
    """
    Convert an iterable of signals to MNE raw array.

    Parameters
    ----------
    signals : Iterable of simuran.base_signal.BaseSignal
        The signals to convert
    ch_names : Iterable of str, optional
        Channel names, by default None

    Returns
    -------
    mne.io.RawArray
        The data converted to MNE format

    """
    verbose = None if verbose else "WARNING"
    
    if ch_names is None:
        ch_names = [sig.default_name() for sig in signals]
    raw_data = np.array([sig.samples * sig.conversion for sig in signals], float)

    sfreq = signals[0].sampling_rate

    ch_types = [sig.channel_type for sig in signals]

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    return mne.io.RawArray(raw_data, info=info, verbose=verbose)
