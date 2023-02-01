from collections import OrderedDict
from typing import Callable, TYPE_CHECKING, Tuple, Dict
import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from simuran import Recording
    from pandas import DataFrame


def filter_good_units(unit_table: "DataFrame", sort_: bool = False):
    """
    Filter out all non-desired_units.

    Settings are:
    presence_ratio > 0.9
    contamination < 0.4
    noise_cutoff < 25
    amp_median > 40uV

    TODO also need to verify this filtering
    TODO may be possible to compute our own to match allen

    Parameters
    ----------
    unit_table
    """
    if sort_:
        unit_table = unit_table.sort_values("depth", ascending=True)
    good_unit_filter = (
        (unit_table["presence_ratio"] > 0.9)
        & (unit_table["contamination"] < 0.4)
        & (unit_table["noise_cutoff"] < 25)
        & (unit_table["amp_median"] > 40 * 10**-6)
    )
    return unit_table.loc[good_unit_filter]


def create_spike_train_one(
    recording: "Recording",
    filter_units: bool = True,
    filter_function: Callable[["DataFrame", bool], "DataFrame"] = filter_good_units,
) -> Tuple["DataFrame", Dict[int, np.ndarray]]:
    unit_dfs = []
    spike_train = OrderedDict()
    for k, v in recording.data.items():
        if not k.startswith("probe"):
            continue
        unit_table = v[1]
        unit_table["simuran_id"] = str(k) + unit_table["cluster_id"].astype(str)

        if filter_units:
            unit_table = filter_function(unit_table)
        unit_dfs.append(unit_table)

        spikes = v[0]

        for cluster in unit_table["cluster_id"]:
            spike_train[f"{k}_{cluster}"] = []
        for i in range(len(spikes["depths"])):
            cluster = spikes["clusters"][i]
            if f"{k}_{cluster}" in spike_train:
                spike_train[f"{k}_{cluster}"].append(spikes["times"][i])

        for k2, v2 in spike_train.items():
            spike_train[k2] = np.array(v2).reshape((1, -1))

    unit_table = pd.concat(unit_dfs, ignore_index=True)
    return unit_table, spike_train
