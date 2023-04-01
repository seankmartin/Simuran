from time import perf_counter
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import simuran as smr

from simuran.loaders.allen_loader import AllenOphysLoader
from simuran import AnalysisHandler
from skm_pyutils.plot import GridFig

from utils import get_path_to_allen_ophys_nwb
from summarise_ophys_allen import summarise_single_session

if TYPE_CHECKING:
    from allensdk.brain_observatory.behavior.behavior_project_cache import (
        VisualBehaviorOphysProjectCache,
    )


def _get_mpi(recording: "smr.Recording", plot_summary=False) -> "np.ndarray":
    recording.load()
    dataset = recording.data
    if dataset is None:
        return
    if hasattr(dataset, "max_projection"):  # Allensdk
        mpi = dataset.max_projection.data
    else:  # PyNWB
        mpi = dataset.processing["ophys"]["images"]["max_projection"].data
    if plot_summary:
        try:
            summarise_single_session(recording, cell_id_=1086493025)
        except Exception as e:
            print(e)
    recording.unload()
    return mpi


def get_mpis_simuran(recording_container: "smr.RecordingContainer", plot_summary=False):
    analysis_handler = AnalysisHandler()
    analysis_handler.add_analysis(
        _get_mpi, [(r, plot_summary) for r in recording_container]
    )
    return analysis_handler.run(pbar=True, n_jobs=4)


def get_mpis_allensdk(
    recording_container: "smr.RecordingContainer", plot_summary=False
):
    mpis = []
    for recording in recording_container:
        mpis.append(_get_mpi(recording, plot_summary=plot_summary))
    return mpis


def plot_mpis(
    recording_container: "smr.RecordingContainer",
    output_dir: "Path",
    sm=True,
    plot_summary=False,
):
    if sm:
        mpis = get_mpis_simuran(recording_container, plot_summary=plot_summary)
        oname = "sm_mpis"
    else:
        mpis = get_mpis_allensdk(recording_container, plot_summary=plot_summary)
        oname = "allen_mpis"
    gf = GridFig(len(recording_container), wspace=0.1, hspace=0.1, tight_layout=True)
    for mpi, recording in zip(mpis, recording_container):
        try:
            ax = gf.get_next()
            ax.imshow(mpi, cmap="gray")
            ax.set_axis_off()
            id_ = recording.attrs["ophys_experiment_id"]
            s = recording.attrs["session_number"]
            ax_title = f"ID: {id_}, S: {s}"
            ax.set_title(ax_title)
        except Exception as e:
            print(e)
    name = recording_container.attrs["container_id"]
    out_path = output_dir / oname / f"{name}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gf.fig.savefig(out_path, dpi=400)
    plt.close(gf.fig)


def timeit(name):
    def inner(func):
        def wrapper(*args, **kwargs):
            t1 = perf_counter()
            func(*args, **kwargs)
            t2 = perf_counter()

            with open("timeit.txt", "a+") as f:
                f.write(f"{name} took {t2 - t1:.2f} seconds\n")

        return wrapper

    return inner


@timeit("simuran_time")
def simuran_mpi_plot(recording_container, output_dir, plot_summary=False):
    plot_mpis(recording_container, output_dir, sm=True, plot_summary=plot_summary)


@timeit("allensdk_time")
def allensdk_mpi_plot(recording_container, output_dir, plot_summary=False):
    plot_mpis(recording_container, output_dir, sm=False, plot_summary=plot_summary)


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
    return np_arrays


def main(data_storage_directory, output_directory, manifest):
    loader = AllenOphysLoader(
        local=True, cache_directory=data_storage_directory, manifest=manifest
    )
    cache = loader.cache
    behaviour_table, session_table, experiment_table = get_tables_from_cache(
        cache,
    )

    gcamp_table = filter_table_to_gcamp_behaviour2p(experiment_table)
    experiment_groups_with_fixed_fov = gcamp_table.groupby("ophys_container_id")

    for container_id, table in experiment_groups_with_fixed_fov:
        if len(table) >= 5:
            table["source_file"] = table.apply(
                lambda row: process_source_file(row), axis=1
            )
            nwb_rc = smr.RecordingContainer.from_table(table, loader)
            nwb_rc.attrs["container_id"] = container_id

            allensdk_mpi_plot(nwb_rc, output_directory, plot_summary=True)
            # simuran_mpi_plot(nwb_rc, output_directory, plot_summary=True)
            exit(-1)


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
    manifest = r"visual-behavior-ophys_project_manifest_v1.0.1.json"

    main(main_dir, main_output_dir, manifest)
