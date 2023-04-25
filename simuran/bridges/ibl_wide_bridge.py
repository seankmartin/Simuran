from collections import OrderedDict
from typing import Callable, TYPE_CHECKING, Tuple, Dict, Optional, List, Union
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from brainbox.behavior.training import get_signed_contrast

if TYPE_CHECKING:
    from simuran import Recording
    from pandas import DataFrame


@dataclass
class IBLWideBridge(object):
    """A class to bridge between IBL and other tools."""

    good_unit_properties: Dict[str, List] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.good_unit_properties) == 0:
            self.good_unit_properties = {
                "presence_ratio": [">", 0.9],
                "contamination": ["<", 0.4],
                "noise_cutoff": ["<", 25],
                "amp_median": [">", 40 * 10**-6],
            }

    def filter_good_units(
        self, unit_table: "DataFrame", sort_: bool = False
    ) -> "DataFrame":
        """
        Filter out all non-desired_units.

        Settings are:
        presence_ratio > 0.9
        contamination < 0.4
        noise_cutoff < 25
        amp_median > 40uV

        Parameters
        ----------
        unit_table : pd.DataFrame
            The unit dataframe to filter from, with channel information.
        sort_ : bool
            Whether or not to sort the units, which is by depth.

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

    def spike_train(
        self,
        recording: "Recording",
        filter_units: bool = True,
        filter_function: Callable[
            ["IBLWideBridge", "DataFrame", bool], "DataFrame"
        ] = filter_good_units,
        brain_regions: Optional[List[str]] = None,
    ) -> Tuple["DataFrame", Dict[int, np.ndarray]]:
        """
        Retrieve a spike train for the units in the recording.

        Parameters
        ----------
        recording
            The recording to retrieve from.
        filter_units : bool
            Whether to filter out noisy cells, by default True.
        filter_function : function
            The function to use for filtering, be default filter_good_units.

        Returns
        -------
        unit_table, spike_train
            The unit table and spike train.

        """
        unit_dfs = []
        spike_train = OrderedDict()
        for k, v in recording.data.items():
            if not k.startswith("probe"):
                continue
            unit_table = v[1].copy()
            if brain_regions is not None:
                unit_table = unit_table.loc[unit_table["acronym"].isin(brain_regions)]
            unit_table.loc["simuran_id"] = str(k) + unit_table["cluster_id"].astype(str)

            if filter_units:
                unit_table = filter_function(self, unit_table)
            unit_dfs.append(unit_table)

            spikes = v[0]

            for cluster in unit_table["cluster_id"]:
                spike_train[f"{k}_{cluster}"] = []
            for i in range(len(spikes["clusters"])):
                cluster = spikes["clusters"][i]
                if f"{k}_{cluster}" in spike_train:
                    spike_train[f"{k}_{cluster}"].append(spikes["times"][i])

            for k2, v2 in spike_train.items():
                spike_train[k2] = np.array(v2).reshape((1, -1))

        unit_table = pd.concat(unit_dfs, ignore_index=True)
        return unit_table, spike_train

    @staticmethod
    def trial_info(recording: "Recording") -> dict:
        """
        Convert a one recording to a trial information dict.

        Parameters
        ----------
        recording : Recording
            The recording to convert.

        Returns
        -------
        result_dict : dict
            The trial passes dict.

        """
        result_dict = {}
        trials = recording.data["trials"]

        # https://int-brain-lab.github.io/iblenv/notebooks_external/loading_trials_data.html
        result_dict["trial_contrasts"] = get_signed_contrast(trials)
        result_dict["trial_correct"] = np.array(
            [True if t == 1 else False for t in trials["feedbackType"]]
        )

        trial_starts = trials["stimOn_times"]
        trial_ends = trials["response_times"]
        result_dict["trial_times"] = [(x, y) for x, y in zip(trial_starts, trial_ends)]

        return result_dict

    @staticmethod
    def recorded_regions(recording: "Recording") -> List[str]:
        vals = []
        for k, v in recording.data.items():
            if not k.startswith("probe"):
                continue
            unit_table = v[1]
            vals.extend(unit_table["acronym"].unique())
        return list(set(vals))
