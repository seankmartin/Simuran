"""This may be a temp, lets see"""
import pandas as pd
from skm_pyutils.py_table import df_from_file

# TODO should this be one level down
from simuran.recording_container import RecordingContainer
from simuran.analysis.analysis_handler import AnalysisHandler

# Pseudo of idea

# TODO params from elsewhere?
index_location = os.path.join(temp_storage_location, "index.csv")

nc_loader_kwargs = {
    "system": "Axona",
    "pos_extension": ".pos"
}

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
    "cfg_base_dir" : "/content/drive/My Drive/NeuroScience/ATN_CA1",

    # STA
    "number_of_shuffles_sta": 5
}

# Step 1a (optional) - Help to set up table - maybe see table.py
table = df_from_file(index_location)

## Series of help on selecting from the dataframe - see
# https://pandas.pydata.org/docs/user_guide/indexing.html
# https://pandas.pydata.org/docs/user_guide/basics.html#dt-accessor
# Easiest way to filter is probably like this

values = {"col1": ["options"], "col2": ["options"]}
table.isin(values) # or not with table.~isin
row_mask = table.isin(values).any() # or not with table.~isin
filtered = table[row_mask]

# Alternatively, you can query

var = "b"
table[(table["a"] == 1) & table[(table[var] == 2)]]
table.query("a == 1 & @var == 2")

# Can expand the table with metadata
expand_table(table)
filtered_table = table[]

# Step 2 - Read a filtered table, can explore with d-tale etc. before continuing (JASP)

recording_container = RecordingContainer.from_table(
    table, "neurochat", param_dir, load=False)

# Step 3 - Iterate over the table performing a fixed function/s with some optional 
# parameters that change

# Temp fn here
def print_info(recording, *args, **kwargs):
    print(recording)
    print(*args, **kwargs)
    return recording.source_file

ah = AnalysisHandler()
ah.add_fn(print_info)

# Step 4 - Save output of analysis in multiple formats
# CSV, straight to JASP etc.

output_location = "results.csv"
ah.save_results(output_location)

# Step 5 - Support to view figures and tables from within the program

# TODO no support for that yet

# Should support params in multiple formats of metadata

# IMPORTANT NEED TO BRANCH HERE.

# What about interactions between objects in recordings?