import os

import mne
import numpy as np
from astropy import units as u
from simuran.core.base_container import GenericContainer
from simuran.core.base_signal import BaseSignal


class Eeg(BaseSignal):
    """EEG class. Provides extra functionality on top of base signal."""

    def __init__(self, samples=None, sampling_rate=None, signal=None):
        """See help(Eeg)"""
        super().__init__()
        ## TODO also use copy method here
        if signal is not None:
            self.samples = signal.samples
            self.sampling_rate = signal.sampling_rate
            self.timestamps = signal.timestamps
            self.region = signal.region
            self.group = signal.group
            self.channel = signal.channel
            self.channel_type = signal.channel_type
            self.attrs = signal.attrs
            self.datetime = signal.datetime
            self.tag = signal.tag
            self.loader = signal.loader
            self.source_file = signal.source_file
            self.last_loaded_source = signal.last_loaded_source
            self.data = signal.data
            self.results = signal.results
        if samples is not None and sampling_rate is not None:
            self.from_numpy(samples, sampling_rate)

    def default_name(self):
        """Get the default name for this signal based on region."""
        name = ""
        if self.channel is not None:
            name += f"{self.channel}"
        if self.region is not None:
            name = f"{self.region} - {name}"

        return name

    def compare_filters(self, *filters, **plot_args):
        """
        Plot a comparison of filters.

        Filters are expected to be as tuples like:
        (name, low, high, **kwargs)
        where **kwargs are passed to simuran.eeg.filter

        Returns
        -------
        matplotlib.figure.Figure
            The filtered version of the signals
        """
        eeg_array = EegArray()
        eeg_array.append(self)
        ch_names = ["Original"]
        for f in filters:
            fname, low, high, kwargs = f
            eeg = self.filter(low, high, inplace=False, **kwargs)
            eeg_array.append(eeg)
            ch_names.append(fname)
        return eeg_array.plot(ch_names=ch_names, **plot_args)

    def default_filt_compare(self, low, high, **plot_args):
        """Compare a FIR filter and and IIR butter filter."""
        plot_args["title"] = plot_args.get(
            "title", f"Filter Comparison -- {self.source_file}"
        )

        plot_args["duration"] = 5
        butter_dict = {"method": "iir"}

        filter1 = ("Default", low, high, {})
        filter2 = ("Butterworth", low, high, butter_dict)

        self.compare_filters(filter1, filter2, **plot_args)

    def __str__(self):
        """Convert to string representation"""
        return f"EEG signal at {self.sampling_rate}Hz with {len(self.samples)} samples"


class EegArray(GenericContainer):
    """Hold a set of EEG signals."""

    def __init__(self):
        """See help(EegArray)"""
        super().__init__(cls=Eeg)

    def convert_signals_to_mne(self, ch_names=None, verbose=True, bad_chans=None):
        """
        Convert an iterable of signals to MNE raw array.

        Parameters
        ----------
        signals : Iterable of simuran.base_signal.BaseSignal
            The signals to convert
        ch_names : Iterable of str, optional
            Channel names, by default None
        bad_chans : list of object, optional
            A list of SIMURAN channels that are bad.

        Returns
        -------
        mne.io.RawArray
            The data converted to MNE format

        """
        verbose = None if verbose else "WARNING"
        signals = self
        if ch_names is None:
            ch_names = [eeg.default_name() for eeg in signals]
        raw_data = np.array([eeg.get_samples().to(u.V) for eeg in signals], float)

        sfreq = signals[0].get_sampling_rate()

        ch_types = [eeg.get_channel_type() for eeg in signals]

        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
        raw = mne.io.RawArray(raw_data, info=info, verbose=verbose)

        mne_bad = []
        if bad_chans is not None:
            for i in bad_chans:
                mne_bad.extend(
                    raw.info["ch_names"][j]
                    for j in range(len(signals))
                    if signals[j].channel == i
                )

        raw.info["bads"] = mne_bad

        return raw

    def plot(
        self,
        title=None,
        ch_names=None,
        lowpass=None,
        highpass=None,
        start=0,
        duration=100,
        proj=False,
        show=True,
        bad_chans=None,
        **kwargs,
    ):
        """
        Plot signals through MNE interface.

        Parameters
        ----------
        signals : Iterable of simuran.base_signal.BaseSignal
            The signals to plot.
        title : str, optional
            The name of the plot title, by default None
        ch_names : Iterable of string, optional
            The names of the channels, by default None
        lowpass : float, optional
            The lowpass of the signal, by default None
        highpass : float, optional
            The highpass of the signal, by default None
        start : float, optional
            Where to start the plot from (in s), by default 0
        duration : int, optional
            How long to plot for (in s), by default 100
        proj : bool, optional
            Whether to project the signals, by default False
        show : bool, optional
            Whether to show the plot in interactive mode, by default True
        bad_chans : list of int, optional
            The bad channels in the array (plotted in red) - by channel.

        Keyword arguments
        -----------------
        See https://mne.tools/stable/generated/mne.io.Raw.html?highlight=raw%20plot#mne.io.Raw.plot

        Returns
        -------
        matplotlib.figure.Figure
            The raw traces in a figure instance.

        """
        signals = self
        mne_array = self.convert_signals_to_mne(
            ch_names=ch_names, verbose=False, bad_chans=bad_chans
        )

        n_channels = kwargs.get("n_channels", len(signals))
        kwargs["duration"] = duration
        kwargs["start"] = start
        kwargs["n_channels"] = n_channels
        kwargs["scalings"] = kwargs.get("scalings", None)
        if title is None:
            title = os.path.basename(signals[0].get_source_file())
        kwargs["title"] = title
        kwargs["show"] = show
        kwargs["block"] = show
        kwargs["lowpass"] = lowpass
        kwargs["highpass"] = highpass
        kwargs["clipping"] = kwargs.get("clipping", None)
        kwargs["proj"] = proj
        kwargs["group_by"] = kwargs.get("group_by", "original")
        kwargs["remove_dc"] = kwargs.get("remove_dc", False)
        kwargs["show_options"] = kwargs.get("show_options", False)

        if kwargs["scalings"] is None:
            scalings = dict(
                mag=1e-12,
                grad=4e-11,
                eeg=20e-6,
                eog=150e-6,
                ecg=5e-4,
                emg=1e-3,
                ref_meg=1e-12,
                misc=1e-3,
                stim=1,
                resp=1,
                chpi=1e-4,
                whitened=1e2,
            )
            max_val = 1.8 * np.max(np.abs(mne_array.get_data(stop=duration)))
            scalings["eeg"] = max_val
            kwargs["scalings"] = scalings
        return mne_array.plot(verbose="ERROR", **kwargs)
