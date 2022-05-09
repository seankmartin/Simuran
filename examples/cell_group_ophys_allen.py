from pathlib import Path
from typing import TYPE_CHECKING

import dtale
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import simuran as smr
from icecream import ic

# TODO can this be a member of smr directly? Should it be?
from simuran.loaders.allen_loader import AllenOphysLoader
from simuran.loaders.nwb_loader import NWBLoader
from skm_pyutils.py_log import print_memory_usage
from skm_pyutils.py_plot import GridFig

from utils import get_path_to_allen_ophys_nwb

if TYPE_CHECKING:
    from allensdk.brain_observatory.behavior.behavior_project_cache import (
        VisualBehaviorOphysProjectCache,
    )


def plot_mpis(recording_container: "smr.RecordingContainer", output_dir: "Path"):
    name = recording_container.metadata["container_id"]
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
        print(mpi)
        ax.imshow(mpi, cmap="gray")
        id_ = recording.metadata["ophys_experiment_id"]
        s = recording.metadata["session_number"]
        ax_title = f"ID: {id_}, S: {s}"
        ax.set_title(ax_title)
        recording.nwb_io.close()
    out_path = output_dir / "mpis" / f"{name}.png"
    gf.fig.savefig(out_path, dpi=400)
    plt.close(gf.fig)


def recording_memory_experiment(recording_container: "smr.RecordingContainer"):
    for i in range(len(recording_container)):
        recording = recording_container.load(i)
        print(f"After loading iteration {i}; {print_memory_usage(as_string=True)}")


def no_smr_memory_experiment(
    cache: "VisualBehaviorOphysProjectCache", table: "pd.DataFrame"
):
    for i in range(len(table)):
        id_ = table.iloc[i].name
        experiment = cache.get_behavior_ophys_experiment(id_)
        print(f"After loading iteration {i}; {print_memory_usage(as_string=True)}")


def no_allen_sdk_experiment(recording_container: "smr.RecordingContainer"):
    for i in range(len(recording_container)):
        recording = recording_container.load(i)
        print(f"After loading iteration {i}; {print_memory_usage(as_string=True)}")
        mpi = recording.data.processing["ophys"]["images"]["max_projection"]
        print(mpi)
        recording.nwb_io.close()


def process_source_file(row):
    id_ = row.name
    return get_path_to_allen_ophys_nwb(id_)


def main(
    data_storage_directory,
    output_directory,
    verbose=False,
):
    loader = AllenOphysLoader.from_local_cache(data_storage_directory)
    nwb_loader = NWBLoader()
    cache = loader.cache

    behaviour_table, session_table, experiment_table = get_tables_from_cache(
        cache, verbose
    )

    gcamp_table = filter_table_to_gcamp_behaviour2p(experiment_table)
    experiment_groups_with_fixed_fov = gcamp_table.groupby("ophys_container_id")

    print(f"Memory usage before loading: {print_memory_usage(as_string=True)}")
    for container_id, table in experiment_groups_with_fixed_fov:
        table["source_file"] = table.apply(lambda row: process_source_file(row), axis=1)
        rc = smr.RecordingContainer.from_table(table, loader)
        rc.metadata["container_id"] = container_id

        nwb_rc = smr.RecordingContainer.from_table(table, nwb_loader)
        nwb_rc.metadata["container_id"] = container_id
        no_allen_sdk_experiment(nwb_rc)
        # no_smr_memory_experiment(cache, table)
        # recording_memory_experiment(rc)

        plot_mpis(nwb_rc, output_directory)


def get_tables_from_cache(
    cache: "VisualBehaviorOphysProjectCache", verbose: bool = False
):
    behaviour_table = cache.get_behavior_session_table(as_df=True)
    session_table = cache.get_ophys_session_table(as_df=True)
    experiment_table = cache.get_ophys_experiment_table(as_df=True)

    if verbose:
        dtale.show(behaviour_table)
        dtale.show(session_table)
        dtale.show(experiment_table).open_browser()
        inp = input("Press Enter to continue...")

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


if __name__ == "__main__":

    # CONFIG
    main_dir = Path(r"D:\AllenBrainObservatory\ophys_data")
    main_output_dir = main_dir / "results"
    main_output_dir.mkdir(parents=True, exist_ok=True)

    main_verbose = False

    main(main_dir, main_output_dir, main_verbose)
