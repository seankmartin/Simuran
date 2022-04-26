"""This may be a temp, lets see"""
from typing import Union, Literal, TYPE_CHECKING
from pathlib import Path

import numpy as np
import seaborn as sns
import pandas as pd
from skm_pyutils.py_table import df_from_file
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
import dtale
from icecream import ic
from skm_pyutils.py_plot import GridFig
import matplotlib.pyplot as plt

# TODO should this be one level down
from simuran.recording_container import RecordingContainer
from simuran.analysis.analysis_handler import AnalysisHandler
from simuran.recording import Recording

# Pseudo of idea
input_file_dir = Path(r"D:\AllenBrainObservatory\ophys_data")
output_dir = Path(r"D:\AllenBrainObservatory\ophys_data\results")

# TODO maybe not the nicest way to select a loader
from simuran.loaders.loader_list import loaders_dict

params = {"loader": "allen_ophys"}

# This might be just nicer
from simuran.loaders.allen_loader import AllenOphysLoader

if TYPE_CHECKING:
    from simuran.loaders.base_loader import BaseLoader

# Step 1a (optional) - Help to set up table - maybe see table.py
def setup_table(input_file_dir: Union[str, Path]) -> pd.DataFrame:
    cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=input_file_dir)
    experiments = cache.get_ophys_experiment_table()
    # dtale.show(experiments).open_browser()
    return experiments


# Step 1b filter the table
def filter_table(table: pd.DataFrame, inplace: bool = True) -> pd.DataFrame:
    """
    _summary_

    Parameters
    ----------
    table : pd.DataFrame
        _description_
    inplace : bool, optional
        _description_, by default True

    Returns
    -------
    pd.DataFrame
        _description_
    """
    genotype = "Slc17a7-IRES2-Cre/wt;Camk2a-tTA/wt;Ai93(TITL-GCaMP6f)/wt"
    # Alternatively
    values = {
        "project_code": ["VisualBehaviorMultiscope"],
        "full_genotype": [genotype],
    }
    filters = []
    for k, v in values.items():
        filters.append(table[k].isin(v))
    full_mask = np.logical_and.reduce(np.array(filters))
    filtered_table = table[full_mask]
    return filtered_table


# function to plot running speed
def plot_running(ax, dataset, initial_time, final_time):
    running_sample = dataset.running_speed.query(
        "timestamps >= @initial_time and timestamps <= @final_time"
    )
    ax.plot(
        running_sample["timestamps"],
        running_sample["speed"] / running_sample["speed"].max(),
        "--",
        color="gray",
        linewidth=1,
    )


# function to plot pupil diameter
def plot_pupil(ax, dataset, initial_time, final_time):
    pupil_sample = dataset.eye_tracking.query(
        "timestamps >= @initial_time and timestamps <= @final_time"
    )
    ax.plot(
        pupil_sample["timestamps"],
        pupil_sample["pupil_width"] / pupil_sample["pupil_width"].max(),
        color="gray",
        linewidth=1,
    )


# function to plot licks
def plot_licks(ax, dataset, initial_time, final_time):
    licking_sample = dataset.licks.query(
        "timestamps >= @initial_time and timestamps <= @final_time"
    )
    ax.plot(
        licking_sample["timestamps"],
        np.zeros_like(licking_sample["timestamps"]),
        marker="o",
        markersize=3,
        color="black",
        linestyle="none",
    )


# function to plot rewards
def plot_rewards(ax, dataset, initial_time, final_time):
    rewards_sample = dataset.rewards.query(
        "timestamps >= @initial_time and timestamps <= @final_time"
    )
    ax.plot(
        rewards_sample["timestamps"],
        np.zeros_like(rewards_sample["timestamps"]),
        marker="d",
        color="blue",
        linestyle="none",
        markersize=12,
        alpha=0.5,
    )


def plot_stimuli(ax, dataset, initial_time, final_time):
    stimulus_presentations_sample = dataset.stimulus_presentations.query(
        "stop_time >= @initial_time and start_time <= @final_time"
    )
    for idx, stimulus in stimulus_presentations_sample.iterrows():
        ax.axvspan(
            stimulus["start_time"],
            stimulus["stop_time"],
            color=stimulus["color"],
            alpha=0.25,
        )


def summarise_single_session(allen_dataset):

    ## Summary in print
    print(
        f"\n-----------Working on image plane {allen_dataset.ophys_experiment_id} "
        f"session {allen_dataset.ophys_session_id}------------"
    )
    print(f"This experiment has metadata {allen_dataset.metadata}")
    cell_specimen_table = allen_dataset.cell_specimen_table
    print(cell_specimen_table)
    print(
        f"There are {len(cell_specimen_table)} cells "
        f"in this session with IDS {cell_specimen_table.index.array}"
    )
    methods = allen_dataset.list_data_attributes_and_methods()
    print(f"The available information is {methods}")

    ## Stimulus and trial information
    # stimulus_table = allen_dataset.stimulus_presentations
    # trials_table = allen_dataset.trials

    ## Plotting per cell information
    timestamps = allen_dataset.ophys_timestamps

    # create a list of all unique stimuli presented in this experiment
    unique_stimuli = [
        stimulus
        for stimulus in allen_dataset.stimulus_presentations["image_name"].unique()
    ]

    # create a colormap with each unique image having its own color
    colormap = {
        image_name: sns.color_palette()[image_number]
        for image_number, image_name in enumerate(np.sort(unique_stimuli))
    }
    colormap["omitted"] = (1, 1, 1)  # set omitted stimulus to white color

    # add the colors for each image to the stimulus presentations table in the dataset
    allen_dataset.stimulus_presentations[
        "color"
    ] = allen_dataset.stimulus_presentations["image_name"].map(
        lambda image_name: colormap[image_name]
    )

    initial_time = 820  # start time in seconds
    final_time = 860  # stop time in seconds

    for cell_id, row in cell_specimen_table.iterrows():
        gf = GridFig(2, 2, traverse_rows=False, size_multiplier_x=10)

        ax = gf.get_next()
        ax.imshow(allen_dataset.max_projection, cmap="gray")
        ax.set_title("Max projection")

        ax = gf.get_next()
        ax.imshow(row["roi_mask"])
        ax.set_title(f"ROI for {cell_id}")

        ax = gf.get_next()

        dff = np.array(allen_dataset.dff_traces.loc[cell_id, "dff"])
        events = np.array(allen_dataset.events.loc[cell_id, "events"])
        filtered_events = np.array(allen_dataset.events.loc[cell_id, "filtered_events"])

        y = np.concatenate(
            [
                dff / dff.max(),
                events / events.max(),
                filtered_events / filtered_events.max(),
            ]
        )
        x = np.concatenate([timestamps, timestamps, timestamps])
        z = np.concatenate(
            [
                ["DFF"] * len(timestamps),
                ["Events"] * len(timestamps),
                ["Filtered Events"] * len(timestamps),
            ]
        )

        cell_df = pd.DataFrame([x, y, z]).T
        cell_df.columns = ["Time (s)", "Normalised magnitude", "Signal"]
        cell_df = cell_df.query(
            "`Time (s)` >= @initial_time and `Time (s)` <= @final_time", inplace=False
        )

        sns.lineplot(ax=ax, data=cell_df, x="Time (s)", y="Normalised magnitude", style="Signal", hue="Signal")
        plot_stimuli(ax, allen_dataset, initial_time, final_time)
        sns.despine()

        ax = gf.get_next()
        plot_running(ax, allen_dataset, initial_time, final_time)
        plot_pupil(ax, allen_dataset, initial_time, final_time)
        plot_licks(ax, allen_dataset, initial_time, final_time)
        plot_rewards(ax, allen_dataset, initial_time, final_time)
        plot_stimuli(ax, allen_dataset, initial_time, final_time)

        ax.set_yticks([])
        ax.legend(["running speed", "pupil", "licks", "rewards"])
        ax.set_ylabel("Normalised magnitude")
        ax.set_xlabel("Time (s)")

        fig = gf.fig
        output_path = output_dir / "ophys" / "CI_plots" / f"{cell_id}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

    return {"methods": methods}


def establish_analysis(rec):
    # Temp fn here
    def print_info(recording, *args, **kwargs):
        print(recording)
        print(*args, **kwargs)
        return vars(recording)

    ah = AnalysisHandler()
    ah.add_fn(summarise_single_session, rec.signals)
    ah.add_fn(print_info, rec)

    return ah


# TODO move this out of here
def loader_from_str(value: str) -> "BaseLoader":
    data_loader_cls = loaders_dict.get(value, None)
    if data_loader_cls is None:
        raise ValueError(
            "Unrecognised loader {}, options are {}".format(
                value,
                list(loaders_dict.keys()),
            )
        )
    return data_loader_cls


def main():
    # TODO TEMP ?
    cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=input_file_dir)

    # Should support params in multiple formats of metadata
    table = setup_table(input_file_dir)

    # Step 2 - Read a filtered table, can explore with d-tale etc. before continuing (JASP)
    filtered_table = filter_table(table)
    # rc = RecordingContainer.from_table(filtered_table, "allen", AllenOphysLoader)
    # TODO I think this step is awkward

    # TODO TEMP let us check a single Allen first

    ## This could be a data class to make it simpler
    for idx, row in filtered_table.iterrows():
        row_as_dict = row.to_dict()
        row_as_dict[filtered_table.index.name] = idx
        break

    recording = Recording()
    recording.loader = AllenOphysLoader(cache=cache)
    # loader2 = loader_from_str("allen_ophys")(cache=cache)

    # TODO This should support different types, file, dict, series, etc
    recording.set_metadata(row_as_dict)

    # TODO this should come with params / loader setting
    recording.available = ["signals"]
    print(recording)

    ## TODO is there a setup step? for recording to set paths?

    # This will call load in the background
    # If not already loaded
    # recording.get_blah()

    # Alternatively can call
    recording.new_load()

    # Inspect what data is available
    # print(recording.get_attrs())

    # Perhaps have allen specific functions from the loader??
    # recording.print_key_info()
    print(recording.signals.__dict__)

    # For example loop over this and print the df / f
    # At the end of the day this is just a signal
    # Best thing to do is to check how NWB stores data
    # Because NWB stores all nscience data
    # And then can facilitate storing results back to NWB
    # etc. etc.
    # For instance, pynapple just converts to NWB as step1

    # Step 3 - Iterate over the table performing a fixed function/s with some optional
    # parameters that change
    ah = establish_analysis(recording)
    ah.run_all_fns()

    # Step 4 - Save output of analysis in multiple formats
    # CSV, straight to JASP etc.
    output_location = "results.csv"
    ah.save_results(output_location)

    # Step 5 - Support to view figures and tables from within the program

    # TODO no support for that yet

    # What about interactions between objects in recordings?


if __name__ == "__main__":
    main()
