from typing import TYPE_CHECKING, Tuple, Dict, Callable, List, Optional, Union
from dataclasses import dataclass, field
from collections import OrderedDict
import ast

import numpy as np
from simuran.core.utils import convert_filter

if TYPE_CHECKING:
    from pandas import DataFrame
    from simuran import Recording


@dataclass
class AllenVBNBridge(object):
    """A class to bridge between Allen VBN and other tools."""

    good_unit_properties: Dict[str, List] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.good_unit_properties) == 0:
            self.good_unit_properties = {
                "isi_violations": ["<", 0.4],
                "nn_hit_rate": [">", 0.9],
                "amplitude_cutoff": ["<", 0.1],
                "presence_ratio": [">", 0.9],
            }

    def filter_good_units(
        self, unit_table: "DataFrame", sort_: bool = False
    ) -> "DataFrame":
        """
        Filter out all non-desired units.

        See https://allensdk.readthedocs.io/en/latest/_static/examples/nb/visual_behavior_neuropixels_quality_metrics.html for more details.

        Settings are:
        isi_violations < 0.4
        nn_hit_rate > 0.9
        amplitude_cutoff < 0.1
        presence_ratio > 0.9

        Parameters
        ----------
        unit_table: pd.DataFrame
            The unit dataframe to filter from, with channel information.
        sort_ : bool
            Whether or not to sort the units, which is by depth.
        """
        if sort_:
            unit_table = unit_table.sort_values(
                "probe_vertical_position", ascending=False
            )
        good_unit_filter_vals = []
        for key, value in self.good_unit_properties.items():
            op, value = value
            filter_part = convert_filter(op)(unit_table[key], value)
            good_unit_filter_vals.append(filter_part)
        good_unit_filter = np.logical_and.reduce(good_unit_filter_vals)

        return unit_table.loc[good_unit_filter]

    def spike_train(
        self,
        recording: "Recording",
        filter_units: bool = True,
        filter_function: Callable[["DataFrame", bool], "DataFrame"] = filter_good_units,
        brain_regions: Optional[List[str]] = None,
    ) -> Tuple["DataFrame", Dict[int, np.ndarray]]:
        """
        Retrieve a spike train for the units in the recording.

        Parameters
        ----------
        recording: simuran.Recording
            The recording to retrieve from.
        filter_units : bool
            Whether to filter out noisy cells, by default True.
        filter_function : function
            The function to use for filtering, by default filter_good_units.
        brain_regions : list of str, optional
            The brain regions to filter by, by default None.

        Returns
        -------
        unit_channels : pd.DataFrame
        spike_train : dict
            Key is unit_id, value is the spike train.
        """
        session = recording.data
        if filter_units:
            units = session.get_units(
                filter_by_validity=True,
                filter_out_of_brain_units=True,
            )
        else:
            units = session.get_units()
        channels = session.get_channels()
        unit_channels = units.merge(
            channels, left_on="peak_channel_id", right_index=True
        )
        if brain_regions is not None:
            unit_channels = unit_channels.loc[
                unit_channels["structure_acronym"].isin(brain_regions)
            ]
        if filter_units:
            unit_channels = filter_function(self, unit_channels)
        good_spikes = OrderedDict(
            (k, v) for k, v in session.spike_times.items() if k in unit_channels.index
        )
        return unit_channels, good_spikes

    @staticmethod
    def trial_info(
        recording: "Recording",
    ) -> Tuple["DataFrame", Dict[int, np.ndarray]]:
        """
        Retrieve the trial information for the recording.

        Parameters
        ----------
        recording: simuran.Recording
            The recording to retrieve from.

        Returns
        -------
        trial_info : dict
            The trial information

        See also
        --------
        https://allensdk.readthedocs.io/en/latest/_static/examples/nb/aligning_behavioral_data_to_task_events_with_the_stimulus_and_trials_tables.html

        """
        session = recording.data
        stimulus_presentations = session.stimulus_presentations
        active_stimuli = stimulus_presentations[
            stimulus_presentations["active"] & stimulus_presentations["is_change"]
        ]
        passed = active_stimuli["rewarded"]
        trial_times = np.zeros(shape=(len(active_stimuli), 2))
        trial_times[:, 0] = active_stimuli["start_time"]
        trial_times[:, 1] = active_stimuli["end_time"]

        trial_info = {
            "trial_times": trial_times,
            "trial_correct": passed,
        }

        return trial_info

    @staticmethod
    def brain_regions_in_structure(
        structure: Optional[str] = None,
    ) -> Union[List[str], Dict[str, List[str]]]:
        """
        Get the brain regions in a structure.

        Parameters
        ----------
        structure : str, optional
            The structure to get the brain regions for, by default None.
            If None, return all brain regions.

        Returns
        -------
        brain_regions : list
            The brain regions in the structure.

        Raises
        ------
        ValueError
            If the structure is not known.

        """

        structures = {
            "cortex": [
                "VISp",
                "VISl",
                "VISrl",
                "VISam",
                "VISpm",
                "VIS",
                "VISal",
                "VISmma",
                "VISmmp",
                "VISli",
            ],
            "thalamus": [
                "LGd",
                "LD",
                "LP",
                "VPM",
                "TH",
                "MGm",
                "MGv",
                "MGd",
                "PO",
                "LGv",
                "VL",
                "VPL",
                "POL",
                "Eth",
                "PoT",
                "PP",
                "PIL",
                "IntG",
                "IGL",
                "SGN",
                "VPL",
                "PF",
                "RT",
            ],
            "hippocampus": [
                "CA1",
                "CA2",
                "CA3",
                "DG",
                "SUB",
                "POST",
                "PRE",
                "ProS",
                "HPF",
            ],
            "midbrain": [
                "MB",
                "SCig",
                "SCiw",
                "SCsg",
                "SCzo",
                "PPT",
                "APN",
                "NOT",
                "MRN",
                "OP",
                "LT",
                "RPF",
                "CP",
            ],
        }

        if structure is None:
            return structures
        else:
            return structures[structure]

    @staticmethod
    def recorded_regions(recording: "Recording") -> List[str]:
        return ast.literal_eval(recording.attrs["structure_acronyms"])
