from pathlib import Path

import numpy as np
import pandas as pd
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
from psutil import virtual_memory


def allen_memory_experiment(
    cache: "VisualBehaviorOphysProjectCache", table: "pd.DataFrame"
):
    for i in range(len(table)):
        id_ = table.iloc[i].name
        print(f"Before loading iteration {i}; {print_memory_usage(as_string=True)}")
        experiment = cache.get_behavior_ophys_experiment(id_)
        print(f"After loading iteration {i}; {print_memory_usage(as_string=True)}")


def main(data_storage_directory):
    cache = VisualBehaviorOphysProjectCache.from_local_cache(data_storage_directory)

    behaviour_table, session_table, experiment_table = get_tables_from_cache(cache)

    gcamp_table = filter_table_to_gcamp_behaviour2p(experiment_table)
    experiment_groups_with_fixed_fov = gcamp_table.groupby("ophys_container_id")

    for container_id, table in experiment_groups_with_fixed_fov:
        print(f"Memory stats before loading SDK: {print_memory_usage(as_string=True)}")
        allen_memory_experiment(cache, table)


def get_tables_from_cache(cache: "VisualBehaviorOphysProjectCache"):
    behaviour_table = cache.get_behavior_session_table(as_df=True)
    session_table = cache.get_ophys_session_table(as_df=True)
    experiment_table = cache.get_ophys_experiment_table(as_df=True)

    return behaviour_table, session_table, experiment_table


def filter_table_to_gcamp_behaviour2p(table: pd.DataFrame) -> pd.DataFrame:
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


def print_memory_usage(as_string: bool = False) -> str:
    str_ = f"RAM memory usage stats: {virtual_memory()}"
    if not as_string:
        print(str_)
    return str_


if __name__ == "__main__":

    # CONFIG
    main_dir = Path(r"D:\AllenBrainObservatory\ophys_data")

    main(main_dir)
