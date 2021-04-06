import os

import mne
import numpy as np
from astropy import units as u


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
        ch_names = [lfp.default_name() for lfp in signals]
    raw_data = np.array([lfp.get_samples().to(u.V) for lfp in signals], float)

    sfreq = signals[0].get_sampling_rate()

    ch_types = [lfp.get_channel_type() for lfp in signals]

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(raw_data, info=info)

    return raw


def plot(
    signals,
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

    Returns
    -------
    matplotlib.figure.Figure
        The raw traces in a figure instance.

    """
    mne_array = convert_signals_to_mne(signals, ch_names=ch_names,)

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
    kwargs["show_options"] = kwargs.get("show_options", True)

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
        max_val = 1.2 * np.max(np.abs(mne_array.get_data(stop=15)[0]))
        scalings["eeg"] = max_val
        kwargs["scalings"] = scalings

    fig = mne_array.plot(**kwargs)

    return fig
