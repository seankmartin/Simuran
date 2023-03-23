from typing import Union, Dict, List
from dataclasses import dataclass, field
import numpy as np
from neo.core import SpikeTrain
import quantities


@dataclass
class NeoBridge(object):
    """A class to bridge between other tools and Neo"""

    @staticmethod
    def convert_spikes(
        spikes: Union[Dict[str, np.ndarray], List[np.ndarray]],
        units: quantities.Quantity = quantities.s,
        custom_t_stop: float = None,
        **kwargs
    ) -> List["SpikeTrain"]:
        """
        Convert a list of spike times or dict of spike times to list of SpikeTrain.

        Parameters
        ----------
        spikes: list or dict of spike times
            The times can be lists or np.ndarray
        units: quantities.Quantity
            The time unit.
        custom_t_stop: float
            The t_stop to use for all SpikeTrain objects.
        kwargs: dict
            Additional arguments to pass to neo.SpikeTrain.

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
        if custom_t_stop is not None:
            max_ = custom_t_stop
        else:
            max_ = 0
            for v in to_iter:
                if len(v) == 0:
                    continue
                max_temp = max(v)
                if max_temp > max_:
                    max_ = max_temp
        for v in to_iter:
            l.append(SpikeTrain(v, units=units, t_stop=max_, **kwargs))

        return l
