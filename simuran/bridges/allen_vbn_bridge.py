from typing import TYPE_CHECKING, Tuple, Dict, Callable, List, Optional
from collections import OrderedDict

import numpy as np

if TYPE_CHECKING:
    from pandas import DataFrame
    from simuran import Recording


def filter_good_units(unit_table: "DataFrame", sort_: bool = False) -> "DataFrame":
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
        unit_table = unit_table.sort_values("probe_vertical_position", ascending=False)
    good_unit_filter = (
        (unit_table["isi_violations"] < 0.4)  # Well isolated units
        & (unit_table["nn_hit_rate"] > 0.9)  # Well isolated units
        & (
            unit_table["amplitude_cutoff"] < 0.1
        )  # Units that have most of their activations
        & (unit_table["presence_ratio"] > 0.9)  # Tracked for 90% of the recording
        # & (unit_channels["quality"] == "good") # Non-artifactual waveform
    )

    return unit_table.loc[good_unit_filter]


def allen_spike_train(
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
        The function to use for filtering, be default filter_good_units.

    Returns
    -------
    unit_channels : pd.DataFrame
    spike_train : dict
        Key is unit_id, value is the spike train.
    """
    session = recording.data
    if filter_units:
        # Removes noisy waveforms and units not in a brain area
        units = session.get_units(
            filter_by_validity=True,
            filter_out_of_brain_units=True,
        )
        if brain_regions is not None:
            units = units.loc[units["structure_acronyms"].isin(brain_regions)]
        units = filter_function(units)
    else:
        units = session.get_units()
    channels = session.get_channels()
    unit_channels = units.merge(channels, left_on="peak_channel_id", right_index=True)
    if filter_units:
        good_spikes = OrderedDict(
            (k, v) for k, v in session.spike_times.items() if k in units.index
        )
    return unit_channels, good_spikes


def allen_trial_info(
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


def get_brain_regions_to_structure_dict():
    return {
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
        "hippocampus": ["CA1", "CA2", "CA3", "DG", "SUB", "POST", "PRE", "ProS", "HPF"],
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


def allen_recorded_regions(recording: "Recording") -> List[str]:
    return recording.attrs["structure_acronyms"]
