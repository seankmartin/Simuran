from typing import TYPE_CHECKING

import numpy as np
from neurochat.nc_lfp import NLfp

if TYPE_CHECKING:
    from simuran.core.base_signal import BaseSignal


def signal_to_neurochat(signal: "BaseSignal"):
    """Convert BaseSignal to NeuroChaT NLfp object."""

    if signal.data is not None and type(signal.data) == NLfp:
        return signal.data

    lfp = NLfp()
    lfp.set_channel_id(signal.channel)
    signal.fill_timestamps()
    lfp._timestamp = np.array(signal.timestamps)
    # Neurochat assumes mV signal
    lfp._samples = np.array(signal.samples) * signal.conversion * 1000
    lfp._record_info["Sampling rate"] = signal.sampling_rate
    lfp._record_info["No of samples"] = len(signal.samples)
    return lfp
