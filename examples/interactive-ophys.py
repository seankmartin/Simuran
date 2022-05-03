# %%
from pathlib import Path

import dtale
import numpy as np
import objexplore
import pandas as pd
import simuran as smr
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)


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


# %%
data_storage_directory = Path(r"D:\AllenBrainObservatory\ophys_data")
cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=data_storage_directory)
behavior_sessions = cache.get_behavior_session_table()
behavior_ophys_sessions = cache.get_ophys_session_table()
behavior_ophys_experiments = cache.get_ophys_experiment_table(as_df=True)

filtered_table = filter_table(behavior_ophys_experiments)
row = filtered_table.iloc[0]
row_as_dict = row.to_dict()
row_as_dict[filtered_table.index.name] = row.name

# %%
recording = smr.Recording()
recording.inspect(methods=True)
all_attrs_and_methods = recording.get_attrs_and_methods()
print(all_attrs_and_methods)

# %% Experiment checking
experiment = cache.get_behavior_ophys_experiment(int(row.name))
print(smr.inspect(experiment))

# %%
loader = smr.loader("allen_ophys")(cache)
recording.loader = loader
recording.metadata = row_as_dict
recording.available = ["signals"]  # This line is silly
recording.load()  # Set back to old load

# %%
recording.inspect()
# recording.show_table(recording.signals.cell_specimen_table)

# %% full container

rc = smr.RecordingContainer.from_table(filtered_table, loader)

# %% working with the container
container_ids = rc.table["ophys_container_id"]

# %%
