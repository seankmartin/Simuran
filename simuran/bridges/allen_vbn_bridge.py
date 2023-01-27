from typing import TYPE_CHECKING, Tuple, Dict

import numpy as np

if TYPE_CHECKING:
    from pandas import DataFrame
    from simuran import Recording


# TODO evaulate if this would be better as a Bridge subclass (also check spike-interface)
def filter_good_units(unit_channels: "DataFrame", sort_: bool = True) -> "DataFrame":
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
    unit_channels : pd.DataFrame
        The unit dataframe to filter from, with channel information.
    sort_ : bool
        Whether or not to sort the units, which is by depth.
    """
    if sort_:
        unit_channels = unit_channels.sort_values(
            "probe_vertical_position", ascending=False
        )
    good_unit_filter = (
        (unit_channels["isi_violations"] < 0.4)  # Well isolated units
        & (unit_channels["nn_hit_rate"] > 0.9)  # Well isolated units
        & (
            unit_channels["amplitude_cutoff"] < 0.1
        )  # Units that have most of their activations
        & (unit_channels["presence_ratio"] > 0.9)  # Tracked for 90% of the recording
        # & (unit_channels["quality"] == "good") # Non-artifactual waveform
    )

    return unit_channels.loc[good_unit_filter]


def allen_to_spike_train(
    recording: "Recording", filter_units: bool = True, filter_function=filter_good_units,
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
        units = filter_function(unit_channels)
    else:
        units = session.get_units()
    channels = session.get_channels()
    unit_channels = units.merge(channels, left_on="peak_channel_id", right_index=True)
    if filter_units:
        good_spikes = {k: v for k, v in session.spike_times.items() if k in units.index}
    return unit_channels, good_spikes


def allen_to_trial_passes(recording: "Recording") -> Tuple["DataFrame", Dict[int, np.ndarray]]:
    # See https://allensdk.readthedocs.io/en/latest/_static/examples/nb/aligning_behavioral_data_to_task_events_with_the_stimulus_and_trials_tables.html
    session = recording.data
    stimulus_presentations = session.stimulus_presentations
    active_stimuli = stimulus_presentations[
        stimulus_presentations["active"] & stimulus_presentations["is_change"]
    ]
    passed = active_stimuli["rewarded"]
    trial_times = np.zeros(shape=(len(active_stimuli), 2))
    trial_times[:, 0] = active_stimuli["start_time"]
    trial_times[:, 1] = active_stimuli["end_time"]

    return trial_times, passed

brain_regions_in_structure = {
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