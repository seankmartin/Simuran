from typing import Dict, Optional, Union, List

import numpy as np


def bin_spike_train(
    spike_train: Union[Dict[int, np.ndarray], List[np.ndarray]],
    bin_step: float = 0.1,
    bin_overlap: float = 0.0,
    t_start: float = 0,
    t_stop: Optional[float] = None,
    bin_type: str = "count",
    smooth: bool = False,
) -> np.ndarray:
    """
    Bin a spike train.

    Parameters
    ----------
    spike_train : np.ndarray
        The spike train to bin.
    bin_step : float
        The size of the bins in seconds.
    bin_overlap : float, optional
        The overlap between bins in seconds, by default 0.
    t_start : float, optional
        The start time of the spike train, by default 0.
    t_stop : float, optional
        The end time of the spike train, by default None.
    bin_type : str, optional
        The type of binning to do, by default "count".
        Options are "count", "rate", "binary".

    Returns
    -------
    np.ndarray
        The binned spike train.
    """
    if isinstance(spike_train, dict):
        spike_train = list(spike_train.values())
    if t_stop is None:
        t_stop = max(st[-1] for st in spike_train)
    bin_size = bin_step + (2 * bin_overlap)
    bin_centres = np.arange(t_start, t_stop, bin_step)
    bin_starts = bin_centres - (bin_size / 2)
    bin_ends = bin_centres + (bin_size / 2)

    binned_train = []
    for train in spike_train:
        last_index = np.searchsorted(train, bin_ends, side="right")
        first_index = np.searchsorted(train, bin_starts, side="left")
        hist = last_index - first_index
        if smooth:
            hist = np.convolve(hist, np.ones(3) / 3, mode="same")
        if bin_type == "rate":
            hist = hist / bin_size
        elif bin_type == "binary":
            hist = np.where(hist > 0, 1, 0)
        elif bin_type != "count":
            raise ValueError("Unknown bin_type: {}".format(bin_type))

        binned_train.append(hist)

    return np.array(binned_train)
