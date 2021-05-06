"""Module to hold the abstract class setting up information held in a signal."""
import math
from copy import deepcopy

from simuran.base_class import BaseSimuran

import mne
import numpy as np
from astropy import units as u


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
        self.source_file = "<unknown>"

    def load(self, *args, **kwargs):
        """Load the signal."""
        super().load()
        if not self.loaded():
            load_result = self.loader.load_signal(self.source_file, **kwargs)
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file

    def from_numpy(self, np_array, sampling_rate):
        """Set data from a numpy array. - assumed in mV and srate in Hz"""
        if not hasattr(np_array, "unit"):
            self.samples = np_array * u.mV
        else:
            self.samples = np_array
        self.sampling_rate = sampling_rate
        self.timestamps = [i / sampling_rate for i in range(len(self.samples))] * u.s

    def default_name(self):
        """Default name based on region."""
        name = self.channel_type
        if self.channel is not None:
            name += " {}".format(self.channel)
        if self.region is not None:
            name = "{} - {}".format(self.region, name)

        return name

    def to_neurochat(self):
        """Convert to NeuroChaT NLfp object."""
        from neurochat.nc_lfp import NLfp

        if self.underlying is not None:
            if type(self.underlying) == NLfp:
                # TODO check this works
                return self.underlying
        lfp = NLfp()
        lfp.set_channel_id(self.channel)
        lfp._timestamp = np.array(self.timestamps * u.mV)
        lfp._samples = np.array(self.samples * u.s)
        lfp._record_info["Sampling rate"] = self.sampling_rate
        return lfp

    def in_range(self, start, stop, step=None):
        """Splice samples from second based times."""
        start = int(math.floor(start * self.sampling_rate))
        stop = int(math.ceil(stop * self.sampling_rate))
        if step is not None:
            step = int(math.round(self.step * self.sampling_rate))
            return self.samples[start:stop:step]
        else:
            return self.samples[start:stop]

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

    def get_sampling_rate(self):
        """Return the sampling rate."""
        return self.sampling_rate

    def get_timestamps(self):
        """Return the timestamps."""
        return self.timestamps

    def get_samples(self):
        """Return the samples."""
        return self.samples

    def get_channel(self):
        """Return the channel."""
        return self.channel

    def get_channel_type(self):
        """Return the channel type."""
        return self.channel_type

    def get_source_file(self):
        """Return the name of the source file."""
        return self.source_file

    def set_duration(self, duration):
        """Set the value of self.duration."""
        self.duration = duration

    def set_samples(self, samples):
        """Set the value of self.samples."""
        self.samples = samples

    def set_sampling_rate(self, sampling_rate):
        """Set the value of self.sampling_rate."""
        self.sampling_rate = sampling_rate

    def set_timestamps(self, timestamps):
        """Set the value of self.timestamps."""
        self.timestamps = timestamps

    def set_channel(self, channel):
        """Set the value of self.channel."""
        self.channel = channel

    def set_channel_type(self, channel_type):
        """Set the value of self.channel_type."""
        self.channel_type = channel_type

    def set_source_file(self, source_file):
        """Set the value of self.source_file."""
        self.source_file = source_file

    def set_region(self, region):
        """Set the value of self.region."""
        self.region = region


def convert_signals_to_mne(signals, ch_names=None):
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
    if ch_names is None:
        ch_names = [sig.default_name() for sig in signals]
    raw_data = np.array([sig.get_samples().to(u.V) for sig in signals], float)

    sfreq = signals[0].get_sampling_rate()

    ch_types = [sig.get_channel_type() for sig in signals]

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(raw_data, info=info)

    return raw
