import os

from simuran.base_signal import BaseSignal
from simuran.base_container import GenericContainer

import mne
import numpy as np
from astropy import units as u
import scipy.signal as sg


class Eeg(BaseSignal):
    """EEG class."""

    def __init__(self, samples=None, sampling_rate=None, signal=None):
        super().__init__()
        if signal is not None:
            self.samples = signal.samples
            self.sampling_rate = signal.sampling_rate
            self.timestamps = signal.timestamps
            self.source_file = signal.source_file
            self.region = signal.region
            self.group = signal.group
            self.channel = signal.channel
            self.channel_type = signal.channel_type
            self.source_file = signal.source_file
            self.kwargs = signal.kwargs
            self.info = signal.info
            self.datetime = signal.datetime
            self.tag = signal.tag
            self.loader = signal.loader
            self.last_loaded_source = signal.last_loaded_source
            self.underlying = signal.underlying
            self.results = signal.results
        if samples is not None and sampling_rate is not None:
            self.from_numpy(samples, sampling_rate)

    def default_name(self):
        """Default name based on region."""
        name = ""
        if self.channel is not None:
            name += "{}".format(self.channel)
        if self.region is not None:
            name = "{} - {}".format(self.region, name)

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
            "title", "Filter Comparison -- {}".format(self.source_file)
        )
        plot_args["duration"] = 5
        butter_dict = {"method": "iir"}

        filter_ = (0, low, high, "bandpass")
        nc_iir = {
            "order": butter_filter(self.sampling_rate, *filter_),
            "ftype": "butter",
        }
        nc_dict = {"method": "iir", "iir_params": nc_iir}
        filter1 = ("Default", low, high, {})
        filter2 = ("Butterworth", low, high, butter_dict)
        filter3 = ("NeuroChaT", low, high, nc_dict)

        self.compare_filters(filter1, filter2, filter3, **plot_args)

    def __str__(self):
        return "EEG signal at {}Hz with {} samples".format(
            self.sampling_rate, len(self.samples)
        )


class EegArray(GenericContainer):
    """Hold EEG signals."""

    def __init__(self):
        super().__init__(Eeg)

    def convert_signals_to_mne(self, ch_names=None, verbose=True):
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
        if not verbose:
            verbose = "WARNING"
        else:
            verbose = None

        signals = self
        if ch_names is None:
            ch_names = [eeg.default_name() for eeg in signals]
        raw_data = np.array([eeg.get_samples().to(u.V) for eeg in signals], float)

        sfreq = signals[0].get_sampling_rate()

        ch_types = [eeg.get_channel_type() for eeg in signals]

        info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
        raw = mne.io.RawArray(raw_data, info=info, verbose=verbose)

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
        **kwargs
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

        Keyword arguments
        -----------------
        See https://mne.tools/stable/generated/mne.io.Raw.html?highlight=raw%20plot#mne.io.Raw.plot

        Returns
        -------
        matplotlib.figure.Figure
            The raw traces in a figure instance.

        """
        signals = self
        mne_array = self.convert_signals_to_mne(ch_names=ch_names, verbose=False)

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
        fig = mne_array.plot(verbose="ERROR", **kwargs)

        return fig


def butter_filter(Fs, *args):
    """
    Filter using bidirectional zero-phase shift Butterworth filter.

    Parameters
    ----------
    x : ndarray
        Data or signal to filter
    Fs : Sampling frequency
    *kwargs
        Arguments with filter paramters

    Returns
    -------
    ndarray
        Filtered signal

    """
    gstop = 20  # minimum dB attenuation at stopabnd
    gpass = 3  # maximum dB loss during ripple
    for arg in args:
        if isinstance(arg, str):
            filttype = arg
    if filttype == "lowpass" or filttype == "highpass":
        wp = args[1] / (Fs / 2)
        if wp > 1:
            wp = 1
            if filttype == "lowpass":
                print("Butterworth filter critical frequency Wp is capped at 1")
            else:
                exit(-1)

    elif filttype == "bandpass":
        if len(args) < 4:
            exit(-1)
        else:
            wp = np.array(args[1:3]) / (Fs / 2)
            if wp[0] >= wp[1]:
                exit(-1)
            if wp[0] == 0 and wp[1] >= 1:
                exit(-1)
            elif wp[0] == 0:
                wp = wp[1]
                filttype = "lowpass"
            elif wp[1] >= 1:
                wp = wp[0]
                filttype = "highpass"

    if filttype == "lowpass":
        ws = min([wp + 0.1, 1])
    elif filttype == "highpass":
        ws = max([wp - 0.1, 0.01 / (Fs / 2)])
    elif filttype == "bandpass":
        ws = np.zeros_like(wp)
        ws[0] = max([wp[0] - 0.1, 0.01 / (Fs / 2)])
        ws[1] = min([wp[1] + 0.1, 1])

    min_order, min_wp = sg.buttord(wp, ws, gpass, gstop)

    return min_order
