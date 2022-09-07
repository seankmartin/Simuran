import numpy as np
import mne


def convert_signals_to_mne(signals, ch_names=None, verbose=True):
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
    return mne.io.RawArray(raw_data, info=info, verbose=verbose)
