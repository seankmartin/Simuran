from typing import Union, Dict, List
import numpy as np
from neo.core import SpikeTrain
import quantities


def convert_spikes_to_train(
    spikes: Union[Dict[str, np.ndarray], List[np.ndarray]],
    units: quantities.Quantity = quantities.s,
) -> List["SpikeTrain"]:
    """
    Convert a list of spike times or dict of spike times to list of SpikeTrain.

    Parameters
    ----------
    spikes: list or dict of spike times
        The times can be lists or np.ndarray
    units: quantities.Quantity
        The time unit.

    Returns
    -------
    list
        list of neo.SpikeTrain objects

    """
    l = []
    if hasattr(spikes, "values"):
        to_iter = spikes.values()
    else:
        to_iter = spikes
    max_ = 0
    for v in to_iter:
        if len(v) == 0:
            continue
        max_temp = max(v)
        if max_temp > max_:
            max_ = max_temp
    for v in to_iter:
        l.append(SpikeTrain(v, units=units, t_stop=max_))

    return l
