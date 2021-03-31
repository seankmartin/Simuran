import mne
import numpy as np
from astropy import units as u


def convert_signals_to_mne(signals, ch_names=None):
    if ch_names is None:
        ch_names = [lfp.default_name() for lfp in signals]
    raw_data = np.array([lfp.get_samples().to(u.V) for lfp in signals], float)

    sfreq = signals[0].get_sampling_rate()

    ch_types = [lfp.get_channel_type() for lfp in signals]

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(raw_data, info=info)

    return raw