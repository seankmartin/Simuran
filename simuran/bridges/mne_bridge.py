import os

import numpy as np
import mne


def convert_signals_to_mne(signals, ch_names=None, verbose=True, bad_chans=None):
    """
    Convert an iterable of signals to MNE raw array.

    Parameters
    ----------
    signals : Iterable of simuran.base_signal.BaseSignal
        The signals to convert
    ch_names : Iterable of str, optional
        Channel names, by default None
    verbose : bool
        Whether to print verbose messages, default True
    bad_chans : list of object, optional
        A list of SIMURAN channels that are bad / noisy by index.

    Returns
    -------
    mne.io.RawArray
        The data converted to MNE format

    """
    verbose = None if verbose else "WARNING"

    if ch_names is None:
        ch_names = [sig.default_name() for sig in signals]
    raw_data = np.array(
        [np.array(sig.samples) * sig.conversion for sig in signals], float
    )
    sfreq = signals[0].sampling_rate
    ch_types = [sig.channel_type for sig in signals]

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(raw_data, info=info, verbose=verbose)

    if bad_chans is not None:
        raw.info["bads"] = bad_chans

    return raw


def default_scalings():
    return dict(
        mag=1e-12,
        grad=4e-11,
        eeg=2e-05,
        eog=0.00015,
        ecg=0.0005,
        emg=0.001,
        ref_meg=1e-12,
        misc=0.001,
        stim=1,
        resp=1,
        chpi=0.0001,
        whitened=100.0,
    )


def plot_signals(
    signals,
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

    Directly using mne.plot() on converted data is also feasible.
    This function merely sets up some default values for that plot.
    And explicitly names some of the most commonly used kwargs.

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
    mne_array = convert_signals_to_mne(
        signals, ch_names=ch_names, verbose=False, bad_chans=bad_chans
    )

    n_channels = kwargs.get("n_channels", len(signals))
    kwargs["duration"] = duration
    kwargs["start"] = start
    kwargs["n_channels"] = n_channels
    kwargs["scalings"] = kwargs.get("scalings")
    if title is None:
        title = (
            None
            if signals[0].source_file is None
            else os.path.basename(signals[0].source_file)
        )
    kwargs["title"] = title
    kwargs["show"] = show
    kwargs["block"] = show
    kwargs["lowpass"] = lowpass
    kwargs["highpass"] = highpass
    kwargs["clipping"] = kwargs.get("clipping")
    kwargs["proj"] = proj
    kwargs["group_by"] = kwargs.get("group_by", "original")
    kwargs["remove_dc"] = kwargs.get("remove_dc", False)
    kwargs["show_options"] = kwargs.get("show_options", False)

    if kwargs["scalings"] is None:
        scalings = default_scalings()
        max_val = 1.8 * np.max(np.abs(mne_array.get_data(stop=duration)))
        scalings["eeg"] = max_val
        kwargs["scalings"] = scalings
    return mne_array.plot(verbose="ERROR", **kwargs)
