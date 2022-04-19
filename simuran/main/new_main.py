"""This may be a temp, lets see"""
from typing import Union, Literal
from pathlib import Path
from numpy import rec

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

# TODO maybe not the nicest way to select a loader
params = {
    "loader": "allen_ophys"
}

# This might be just nicer
from simuran.loaders.allen_loader import AllenOphysLoader

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
    # TODO TEMP ?
    cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=input_file_dir)

    # Should support params in multiple formats of metadata
    table = setup_table(input_file_dir)

    # Step 2 - Read a filtered table, can explore with d-tale etc. before continuing (JASP)
    filtered_table = filter_table(table)
    rc = recording_container.from_table(filtered_table, "allen", AllenOphysLoader)
    # TODO I think this step is awkward

    # TODO TEMP let us check a single Allen first

    ## This could be a data class to make it simpler
    recording = Recording()

    recording.set_loader("str" or "cls")

    # This should support different types
    # File
    # Etc.
    recording.set_params(row)

    # This will call load in the background
    # If not already loaded
    recording.get_blah()

    # Alternatively can call
    recording.load()

    # Inspect what data is available
    recording.get_attrs()

    # Perhaps have allen specific functions from the loader??
    recording.print_key_info()

    # For example loop over this and print the df / f
    # At the end of the day this is just a signal
    # Best thing to do is to check how NWB stores data
    # Because NWB stores all nscience data
    # And then can facilitate storing results back to NWB
    # etc. etc.
    # For instance, pynapple just converts to NWB as step1

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
