"""This may be a temp, lets see"""

from simuran.recording_container import RecordingContainer

import pandas as pd

# TODO should this be one level down
from simuran.analysis.analysis_handler import AnalysisHandler

# Pseudo of idea

# Step 1a (optional) - Help to set up table - maybe see table.py

table = pd.DataFrame()

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