from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import simuran as smr

from simuran.loaders.allen_loader import AllenOphysLoader
from simuran.loaders.nwb_loader import NWBLoader
from skm_pyutils.log import print_memory_usage
from skm_pyutils.plot import GridFig

from utils import get_path_to_allen_ophys_nwb

if TYPE_CHECKING:
    from allensdk.brain_observatory.behavior.behavior_project_cache import (
        VisualBehaviorOphysProjectCache,
    )


def plot_mpis(recording_container: "smr.RecordingContainer", output_dir: "Path"):
    name = recording_container.attrs["container_id"]
    gf = GridFig(len(recording_container))
    for i in range(len(recording_container)):
        recording = recording_container.load(i)
        print(f"After loading iteration {i}; {print_memory_usage(as_string=True)}")
        dataset = recording.data
        if dataset is None:
            return
        ax = gf.get_next()
        if hasattr(dataset, "max_projection"):  # Allensdk
            mpi = dataset.max_projection.data
        else:  # PyNWB
            mpi = dataset.processing["ophys"]["images"]["max_projection"].data

        ## For NWB
        ax.imshow(mpi, cmap="gray")
        id_ = recording.attrs["ophys_experiment_id"]
        s = recording.attrs["session_number"]
        ax_title = f"ID: {id_}, S: {s}"
        ax.set_title(ax_title)
    out_path = output_dir / "mpis" / f"{name}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gf.fig.savefig(out_path, dpi=400)
    plt.close(gf.fig)


def process_source_file(row):
    id_ = row.name
    return get_path_to_allen_ophys_nwb(id_)


def array_of_ci_events(
    recording_container: "smr.RecordingContainer",
) -> "list[np.ndarray]":
    np_arrays = []
    for recording in recording_container:
        recording.load()
        ci_events = recording.data.processing["ophys"]["event_detection"].data.value
        np_arrays.append(ci_events)
    # Might be able to get this to work with padding? Lets see if worth
    # xray = xr.DataArray()
    return np_arrays


def main(
    data_storage_directory,
    output_directory,
):
    loader = AllenOphysLoader.from_local_cache(data_storage_directory)
    nwb_loader = NWBLoader()
    cache = loader.cache

    behaviour_table, session_table, experiment_table = get_tables_from_cache(
        cache,
    )

    gcamp_table = filter_table_to_gcamp_behaviour2p(experiment_table)
    experiment_groups_with_fixed_fov = gcamp_table.groupby("ophys_container_id")

    print(f"Memory usage before loading: {print_memory_usage(as_string=True)}")
    for container_id, table in experiment_groups_with_fixed_fov:
        if len(table) >= 5:
            table["source_file"] = table.apply(
                lambda row: process_source_file(row), axis=1
            )
            nwb_rc = smr.RecordingContainer.from_table(table, loader)
            nwb_rc.attrs["container_id"] = container_id

            plot_mpis(nwb_rc, output_directory)


def get_tables_from_cache(cache: "VisualBehaviorOphysProjectCache"):
    behaviour_table = cache.get_behavior_session_table(as_df=True)
    session_table = cache.get_ophys_session_table(as_df=True)
    experiment_table = cache.get_ophys_experiment_table(as_df=True)
    return behaviour_table, session_table, experiment_table


def filter_table_to_gcamp_behaviour2p(table: pd.DataFrame) -> pd.DataFrame:
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


if __name__ == "__main__":

    # CONFIG
    main_dir = Path(r"D:\AllenBrainObservatory\ophys_data")
    main_output_dir = main_dir / "results"
    main_output_dir.mkdir(parents=True, exist_ok=True)

    main(main_dir, main_output_dir)
