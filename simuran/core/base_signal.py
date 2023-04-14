"""Module to hold the abstract class setting up information held in a signal."""
import logging
from dataclasses import dataclass, field
import math
from copy import deepcopy
from typing import Optional, Iterable, Any

import mne
import numpy as np
from simuran.core.base_class import BaseSimuran


@dataclass
class BaseSignal(BaseSimuran):
    """
    Describes the base information for a regularly sampled signal.

    For example, LFP or EEG could be represented.

    Attributes
    ----------
    timestamps : array style object
        The timestamps of the signal sampling in seconds
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
    conversion : float
        The conversion rate to Volts for samples
        self.samples * self.conversion is in Volts

    See also
    --------
    simuran.core.base_class.BaseSimuran

    """

    timestamps: Optional[Iterable[float]] = None
    samples: Iterable[float] = field(default_factory=list)
    sampling_rate: Optional[float] = None
    region: Optional[str] = None
    group: Any = None
    channel: Any = None
    channel_type: str = "misc"
    conversion: int = 1.0

    def load(self, *args, **kwargs):
        """Load the signal."""
        if super().load() == "skip":
            return
        load_result = self.loader.load_signal(self.source_file, *args, **kwargs)
        self.__dict__.update(load_result.__dict__)
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
        signal.fill_timestamps()
        signal.conversion = 0.001
        return signal

    def default_name(self, starting_name=None):
        """
        Get the default name for this signal based on region.

        Parameters
        ----------
        starting_name : str, optional
            By default None, which starts with the chan type.

        Returns
        -------
        str
            The name of the channel as {region} - {starting_name} {channel}
        """
        if starting_name is None:
            name = self.channel_type
        if self.channel is not None:
            name += f" {self.channel}"
        if self.region is not None:
            name = f"{self.region} - {name}"

        return name

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
        step = int(step * self.sampling_rate)
        return self.samples[start:stop:step]

    def filter(self, low=None, high=None, inplace=False, **kwargs):
        """
        Filter the signal.

        Parameters
        ----------
        low : float, optional
            The low frequency for filtering. Default None.
        high : float, optional
            The high frequency for filtering. Default None.
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
        if (low is None) and (high is None):
            logging.warning("Invalid filter frequencies")
            return self
        filtered_data = (
            mne.filter.filter_data(
                np.array(self.get_samples_in_volts()),
                self.sampling_rate,
                low,
                high,
                **kwargs,
            )
            / self.conversion
        )
        if not inplace:
            eeg = deepcopy(self)
            eeg.samples = filtered_data
            return eeg
        else:
            self.samples = filtered_data
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

    def get_samples_in_volts(self):
        return np.array(self.samples) * self.conversion

    def fill_timestamps(self):
        if self.timestamps is not None:
            return
        if self.sampling_rate is None:
            raise ValueError("Must set a sampling rate before setting time stamps")
        self.timestamps = np.array(
            [i / self.sampling_rate for i in range(len(self.samples))]
        )


@dataclass
class Eeg(BaseSignal):
    """A signal of channel_type eeg"""

    channel_type: str = "eeg"
