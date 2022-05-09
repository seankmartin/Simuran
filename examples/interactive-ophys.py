# %%
%load_ext autoreload
%autoreload 2

# %%
from pathlib import Path
from urllib.parse import urljoin

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
import simuran as smr
from allensdk.brain_observatory.behavior.behavior_project_cache import \
    VisualBehaviorOphysProjectCache
from skm_pyutils.py_plot import GridFig
from tqdm import tqdm

# %%
OUTPUT_DIR = Path(r"D:\AllenBrainObservatory\ophys_data\results")
HERE = Path(__file__).parent.absolute()
MANIFEST_VERSION = "1.0.1"
DATA_STORAGE_DIRECTORY = Path(r"D:\AllenBrainObservatory\ophys_data")

# %% File path functions
def get_behavior_ophys_experiment_url(ophys_experiment_id: int) -> str:
    hostname = "https://visual-behavior-ophys-data.s3-us-west-2.amazonaws.com/"
    object_key = f"visual-behavior-ophys/behavior_ophys_experiments/behavior_ophys_experiment_{ophys_experiment_id}.nwb"
    return urljoin(hostname, object_key)


def get_path_to_nwb(experiment_id):
    fname = (
        DATA_STORAGE_DIRECTORY
        / f"visual-behavior-ophys-{MANIFEST_VERSION}"
        / "behavior_ophys_experiments"
        / f"behavior_ophys_experiment_{experiment_id}.nwb"
    )
    return fname


def manual_download(experiment_id):
    url = get_behavior_ophys_experiment_url(experiment_id)
    response = requests.get(url, stream=True)
    fname = get_path_to_nwb(experiment_id)

    with open(fname, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)


# %%
def filter_table(table: pd.DataFrame) -> pd.DataFrame:
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


def plot_mpis(recording_container: "smr.RecordingContainer"):
    name = recording_container.metadata["container_id"]
    gf = GridFig(len(recording_container))
    for i in range(len(recording_container)):
        recording = recording_container.load(i)
        dataset = recording.data
        if dataset is None:
            return
        ax = gf.get_next()
        ax.imshow(dataset.max_projection.data, cmap="gray")
        id_ = recording.metadata["ophys_experiment_id"]
        s = recording.metadata["session_number"]
        ax_title = f"ID: {id_}, S: {s}"
        ax.set_title(ax_title)
    out_path = OUTPUT_DIR / "mpis" / f"{name}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gf.fig.savefig(out_path, dpi=400)
    plt.close(gf.fig)


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
    if allen_dataset is None:
        return

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

    exp_id = allen_dataset.ophys_experiment_id
    sess_id = allen_dataset.ophys_session_id
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
        output_path = (
            OUTPUT_DIR / "CI_plots" / f"E{exp_id}" / f"S{sess_id}_C{cell_id}.png"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300)
        plt.close(fig)

    return {"methods": methods}


# %%
data_storage_directory = Path(r"D:\AllenBrainObservatory\ophys_data")
loader = smr.loader("allen_ophys").from_s3_cache(data_storage_directory)
cache = loader.cache
behavior_sessions = cache.get_behavior_session_table()
behavior_ophys_sessions = cache.get_ophys_session_table()
behavior_ophys_experiments = cache.get_ophys_experiment_table(as_df=True)
filtered_table = filter_table(behavior_ophys_experiments)

#%% Checking behavior sessions
behavior_id = behavior_ophys_experiments["behavior_session_id"].loc[filtered_table.iloc[2].name]
behaviour_session = cache.get_behavior_session(behavior_id)
print(behaviour_session)

# %% Clearing the cache
cache.fetch_api.cache.cache_clear()
experiment = cache.get_behavior_ophys_experiment(filtered_table.iloc[0].name)
experiment.cache_clear()

# %% Manual allen loading
nwb_loader = smr.loader("nwb")()
recording = smr.Recording(
    source_file=get_path_to_nwb(filtered_table.iloc[0].name), loader=nwb_loader
)
recording.load()
print(recording.data)

# %% Let us test tables etc.
group_obj = filtered_table.groupby("ophys_container_id")

for g in group_obj:
    name, df = g
    rc = smr.RecordingContainer.from_table(df, loader)
    ## RC needs genericcontainer to be dataclass - look tomorrow
    rc.metadata["container_id"] = name
    plot_mpis(rc)
    # for r in rc:
    #     summarise_single_session(r.data)
    # break

# %% Explore the RC
rc.inspect()

# %% explore cache
print(cache.current_manifest())
# print(cache.data_path(1085673715))
# smr.inspect(cache, methods="True")
# smr.inspect(cache.fetch_api.cache, methods="True")
print(cache.fetch_api.cache.file_id_column)
print(filtered_table["file_id"].iloc[0])
# print(cache.fetch_api.cache.data_path(filtered_table["file_id"].iloc[0]))

# %%

local_cache = VisualBehaviorOphysProjectCache.from_local_cache(data_storage_directory)
smr.inspect(local_cache)
print(behavior_sessions.iloc[5].name)
print(local_cache.fetch_api.cache._cache_dir)
# local_cache.get_behavior_session(behavior_sessions.iloc[5].name)
local_cache.get_behavior_ophys_experiment(behavior_ophys_experiments.iloc[-1].name)

# %%

loader = smr.loader("allen_ophys")(local_cache)
r = loader.parse_table_row(behavior_ophys_experiments, -1)
print(r.metadata)
r.load()
print(r.data)
r = loader.parse_table_row(behavior_ophys_experiments, 1)
print(r.metadata)
r.load()
print(r.data)

# %%
