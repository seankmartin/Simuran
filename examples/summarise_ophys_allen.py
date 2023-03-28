"""This may be a temp, lets see"""
from pathlib import Path
from typing import Union
from matplotlib import cm
from matplotlib.colors import Normalize

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
from simuran.analysis.analysis_handler import AnalysisHandler
from simuran.recording import Recording
from simuran.loaders.allen_loader import AllenOphysLoader

from skm_pyutils.plot import GridFig

input_file_dir = Path(r"D:\AllenBrainObservatory\ophys_data")
output_dir = Path(r"D:\AllenBrainObservatory\ophys_data\results")
params = {"loader": "allen_ophys"}
manifest = r"visual-behavior-ophys_project_manifest_v1.0.1.json"

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
        "end_time >= @initial_time and start_time <= @final_time"
    )
    max_ = stimulus_presentations_sample["image_index"].max()
    min_ = stimulus_presentations_sample["image_index"].min()
    cmap = cm.autumn_r
    norm = Normalize(vmin=min_, vmax=max_)
    for idx, stimulus in stimulus_presentations_sample.iterrows():
        ax.axvspan(
            stimulus["start_time"],
            stimulus["end_time"],
            color=cmap(norm(stimulus["image_index"])),
            alpha=0.25,
        )


def summarise_single_session(recording):
    allen_dataset = recording.data
    ophys_experiment_id = allen_dataset.ophys_experiment_id
    ## Summary in print
    print(
        f"\n-----------Working on image plane {ophys_experiment_id} "
        f"session {allen_dataset.ophys_session_id}------------"
    )
    print(f"This experiment has metadata {recording.attrs}")
    cell_specimen_table = allen_dataset.cell_specimen_table
    print(
        f"There are {len(cell_specimen_table)} cells "
        f"in this session with IDS {cell_specimen_table.index.array}"
    )
    methods = allen_dataset.list_data_attributes_and_methods()

    ## Plotting per cell information
    timestamps = allen_dataset.ophys_timestamps

    initial_time = 800  # start time in seconds
    final_time = 860  # stop time in seconds

    for cell_id, row in cell_specimen_table.iterrows():
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))

        ax = axes[0]
        ax.imshow(allen_dataset.max_projection, cmap="gray", interpolation="none")
        ax.imshow(row["roi_mask"], cmap="gray", alpha=0.5, interpolation="none")
        ax.set_title("Max projection with ROI mask")

        ax = axes[1]
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

        sns.lineplot(
            ax=ax,
            data=cell_df,
            x="Time (s)",
            y="Normalised magnitude",
            style="Signal",
            hue="Signal",
        )
        plot_stimuli(ax, allen_dataset, initial_time, final_time)
        sns.despine()

        output_path = (
            output_dir
            / "ophys"
            / "CI_plots"
            / f"{cell_id}"
            / f"{ophys_experiment_id}_{cell_id}.png"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    plot_running(ax, allen_dataset, initial_time, final_time)
    plot_pupil(ax, allen_dataset, initial_time, final_time)
    plot_licks(ax, allen_dataset, initial_time, final_time)
    plot_rewards(ax, allen_dataset, initial_time, final_time)
    plot_stimuli(ax, allen_dataset, initial_time, final_time)

    ax.set_yticks([])
    ax.legend(["running speed", "pupil", "licks", "rewards"])
    ax.set_ylabel("Normalised magnitude")
    ax.set_xlabel("Time (s)")

    output_path = output_dir / "ophys" / "CI_plots" / f"{ophys_experiment_id}.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)

    return {"methods": methods}


def establish_analysis(rec):
    ah = AnalysisHandler()
    ah.add_analysis(summarise_single_session, [rec])

    return ah


def main():
    loader = AllenOphysLoader(cache_directory=input_file_dir, manifest=manifest)
    table = loader.cache.get_ophys_experiment_table()

    filtered_table = filter_table(table)

    for idx, row in filtered_table.iterrows():
        row_as_dict = row.to_dict()
        row_as_dict[filtered_table.index.name] = idx
        break
    recording = Recording(loader=loader)
    recording.attrs = row_as_dict
    recording.available = ["signals"]
    recording.load()

    # Step 3 - Iterate over the table performing a fixed function/s with some optional
    # parameters that change
    ah = establish_analysis(recording)
    ah.run()

    # Step 4 - Save output of analysis in multiple formats
    # CSV, straight to JASP etc.
    output_location = "results.csv"
    ah.save_results_to_table(output_location)


if __name__ == "__main__":
    main()
