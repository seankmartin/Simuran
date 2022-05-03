# %%
from pathlib import Path

import dtale
import matplotlib.pyplot as plt
import numpy as np
import objexplore
import pandas as pd
import simuran as smr
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
from skm_pyutils.py_plot import GridFig

# %%
OUTPUT_DIR = Path(r"D:\AllenBrainObservatory\ophys_data\results")


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


def plot_mpis(recording_container):
    name = recording_container.metadata["container_id"]
    gf = GridFig(len(recording_container))
    for recording in recording_container:
        dataset = recording.signals.data
        ax = gf.get_next()
        ax.imshow(dataset.max_projection.data, cmap="gray")
        ax.set_title(name)
    out_path = OUTPUT_DIR / "mpis" / f"{name}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gf.fig.savefig(out_path, dpi=400)
    plt.close(gf.fig)


# %%
data_storage_directory = Path(r"D:\AllenBrainObservatory\ophys_data")
cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=data_storage_directory)
behavior_sessions = cache.get_behavior_session_table()
behavior_ophys_sessions = cache.get_ophys_session_table()
behavior_ophys_experiments = cache.get_ophys_experiment_table(as_df=True)
filtered_table = filter_table(behavior_ophys_experiments)

loader = smr.loader("allen_ophys")(cache)

# %% Let us test tables etc.
group_obj = filtered_table.groupby("ophys_container_id")

for g in group_obj:
    name, df = g
    rc = smr.RecordingContainer.from_table(df, loader)
    rc.metadata["container_id"] = name
    plot_mpis(rc)

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
# %% working with the container
container_ids = rc.table["ophys_container_id"]
