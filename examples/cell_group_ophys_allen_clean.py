from pathlib import Path

import numpy as np
import pandas as pd
import simuran as smr
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
from skm_pyutils.py_log import print_memory_usage

from utils import get_path_to_allen_ophys_nwb


def allen_memory_experiment(
    cache: "VisualBehaviorOphysProjectCache", table: "pd.DataFrame"
):
    for i in range(len(table)):
        id_ = table.iloc[i].name
        experiment = cache.get_behavior_ophys_experiment(id_)
        print(f"After loading iteration {i}; {print_memory_usage(as_string=True)}")


def no_allen_sdk_experiment(recording_container: "smr.RecordingContainer"):
    for i in range(len(recording_container)):
        recording = recording_container.load(i)
        mpi = recording.data.processing["ophys"]["images"]["max_projection"]
        recording.nwb_io.close()
        print(f"After loading iteration {i}; {print_memory_usage(as_string=True)}")


def process_source_file(row):
    id_ = row.name
    return get_path_to_allen_ophys_nwb(id_)


def main(
    data_storage_directory,
    output_directory,
    verbose=False,
):
    cache = VisualBehaviorOphysProjectCache.from_local_cache(data_storage_directory)
    nwb_loader = smr.loader("nwb")()

    behaviour_table, session_table, experiment_table = get_tables_from_cache(
        cache, verbose
    )

    gcamp_table = filter_table_to_gcamp_behaviour2p(experiment_table)
    experiment_groups_with_fixed_fov = gcamp_table.groupby("ophys_container_id")

    for container_id, table in experiment_groups_with_fixed_fov:
        table["source_file"] = table.apply(lambda row: process_source_file(row), axis=1)

        # Loading using NWB
        nwb_rc = smr.RecordingContainer.from_table(table, nwb_loader)
        nwb_rc.metadata["container_id"] = container_id
        print(f"Memory stats before loading NWB: {print_memory_usage(as_string=True)}")
        no_allen_sdk_experiment(nwb_rc)

        # Loading using AllenSDK
        print(f"Memory stats before loading SDK: {print_memory_usage(as_string=True)}")
        allen_memory_experiment(cache, table)


def get_tables_from_cache(
    cache: "VisualBehaviorOphysProjectCache", verbose: bool = False
):
    behaviour_table = cache.get_behavior_session_table(as_df=True)
    session_table = cache.get_ophys_session_table(as_df=True)
    experiment_table = cache.get_ophys_experiment_table(as_df=True)

    if verbose:
        import dtale

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
