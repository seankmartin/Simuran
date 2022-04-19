"""This may be a temp, lets see"""
from typing import Union, Literal
from pathlib import Path

import pandas as pd
from skm_pyutils.py_table import df_from_file
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
import dtale

# TODO should this be one level down
from simuran.recording_container import RecordingContainer
from simuran.analysis.analysis_handler import AnalysisHandler

# Pseudo of idea

input_file_dir = Path(
    r"D:\AllenBrainObservatory\ophys_data\visual-behavior-ophys-1.0.1"
)

# TODO params from elsewhere?
index_location = input_file_dir / "index.csv"

nc_loader_kwargs = {"system": "Axona", "pos_extension": ".pos"}

clean_kwargs = {
    "pick_property": "group",
    "channels": ["LFP"],
}

# Here is where per file params?
all_params = {
    # Cleaning params
    "clean_method": "pick_zscore",
    "clean_kwargs": clean_kwargs,
    # Filtering params
    "fmin": 1,
    "fmax": 100,
    "theta_min": 6,
    "theta_max": 10,
    "delta_min": 1.5,
    "delta_max": 4,
    "fmax_plot": 40,
    # Plotting params
    "psd_scale": "decibels",
    "image_format": "png",
    # Path setup
    "cfg_base_dir": "/content/drive/My Drive/NeuroScience/ATN_CA1",
    # STA
    "number_of_shuffles_sta": 5,
}

# Step 1a (optional) - Help to set up table - maybe see table.py
def setup_table(input_file_dir: Union[str, Path]) -> pd.DataFrame:
    cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=input_file_dir)
    experiments = cache.get_ophys_experiment_table()
    dtale.show(experiments, subprocess=False)
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
    # Alternatively
    # values = {"col1": ["options"], "col2": ["options"]}
    # table.isin(values) # or not with table.~isin
    # row_mask = table.isin(values).any() # or not with table.~isin
    # filtered = table[row_mask]
    genotype = "Slc17a7-IRES2-Cre/wt;Camk2a-tTA/wt;Ai93(TITL-GCaMP6f)/wt"
    query_ = (
        "project_code == VisualBehaviorMultiscope" "&" f"full_genotype == {genotype}"
    )
    if inplace:
        table.query(query_, inplace=True)
        return table
    else:
        return table.query(query_, inplace=False)


def establish_analysis():
    # Temp fn here
    def print_info(recording, *args, **kwargs):
        print(recording)
        print(*args, **kwargs)
        return recording.source_file

    ah = AnalysisHandler()
    ah.add_fn(print_info)

    return ah


def main():
    # Should support params in multiple formats of metadata
    table = setup_table(input_file_dir)

    # Step 2 - Read a filtered table, can explore with d-tale etc. before continuing (JASP)
    filtered_table = filter_table(table)
    rc = recording_container.from_table(filtered_table, "allen")
    # TODO I think this step is awkward

    # Step 3 - Iterate over the table performing a fixed function/s with some optional
    # parameters that change
    ah = establish_analysis()
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
