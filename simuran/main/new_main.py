"""This may be a temp, lets see"""
from typing import Union, Literal, TYPE_CHECKING
from pathlib import Path
import numpy as np

import pandas as pd
from skm_pyutils.py_table import df_from_file
from allensdk.brain_observatory.behavior.behavior_project_cache import (
    VisualBehaviorOphysProjectCache,
)
import dtale
from icecream import ic

# TODO should this be one level down
from simuran.recording_container import RecordingContainer
from simuran.analysis.analysis_handler import AnalysisHandler
from simuran.recording import Recording

# Pseudo of idea
input_file_dir = Path(r"D:\AllenBrainObservatory\ophys_data")

# TODO maybe not the nicest way to select a loader
from simuran.loaders.loader_list import loaders_dict

params = {"loader": "allen_ophys"}

# This might be just nicer
from simuran.loaders.allen_loader import AllenOphysLoader

if TYPE_CHECKING:
    from simuran.loaders.base_loader import BaseLoader

# Step 1a (optional) - Help to set up table - maybe see table.py
def setup_table(input_file_dir: Union[str, Path]) -> pd.DataFrame:
    cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=input_file_dir)
    experiments = cache.get_ophys_experiment_table()
    # dtale.show(experiments).open_browser()
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


def establish_analysis(rec):
    # Temp fn here
    def print_info(recording, *args, **kwargs):
        print(recording)
        print(*args, **kwargs)
        return vars(recording)

    ah = AnalysisHandler()
    ah.add_fn(print_info, rec)

    return ah


# TODO move this out of here
def loader_from_str(value: str) -> "BaseLoader":
    data_loader_cls = loaders_dict.get(value, None)
    if data_loader_cls is None:
        raise ValueError(
            "Unrecognised loader {}, options are {}".format(
                value,
                list(loaders_dict.keys()),
            )
        )
    return data_loader_cls


def main():
    # TODO TEMP ?
    cache = VisualBehaviorOphysProjectCache.from_s3_cache(cache_dir=input_file_dir)

    # Should support params in multiple formats of metadata
    table = setup_table(input_file_dir)

    # Step 2 - Read a filtered table, can explore with d-tale etc. before continuing (JASP)
    filtered_table = filter_table(table)
    # rc = RecordingContainer.from_table(filtered_table, "allen", AllenOphysLoader)
    # TODO I think this step is awkward

    # TODO TEMP let us check a single Allen first

    ## This could be a data class to make it simpler
    for idx, row in filtered_table.iterrows():
        row_as_dict = row.to_dict()
        row_as_dict[filtered_table.index.name] = idx
        break

    recording = Recording()
    recording.loader = AllenOphysLoader(cache=cache)
    # loader2 = loader_from_str("allen_ophys")(cache=cache)

    # TODO This should support different types, file, dict, series, etc
    recording.set_metadata(row_as_dict)

    # TODO this should come with params / loader setting
    recording.available = ["signals"]
    print(recording)

    ## TODO is there a setup step? for recording to set paths?

    # This will call load in the background
    # If not already loaded
    # recording.get_blah()

    # Alternatively can call
    recording.new_load()

    # Inspect what data is available
    # print(recording.get_attrs())

    # Perhaps have allen specific functions from the loader??
    # recording.print_key_info()
    print(recording.signals.__dict__)

    # For example loop over this and print the df / f
    # At the end of the day this is just a signal
    # Best thing to do is to check how NWB stores data
    # Because NWB stores all nscience data
    # And then can facilitate storing results back to NWB
    # etc. etc.
    # For instance, pynapple just converts to NWB as step1

    # Step 3 - Iterate over the table performing a fixed function/s with some optional
    # parameters that change
    ah = establish_analysis(recording)
    ah.run_all_fns()
    print(ah.results)

    # Step 4 - Save output of analysis in multiple formats
    # CSV, straight to JASP etc.
    output_location = "results.csv"
    ah.save_results(output_location)

    # Step 5 - Support to view figures and tables from within the program

    # TODO no support for that yet

    # What about interactions between objects in recordings?


if __name__ == "__main__":
    main()
