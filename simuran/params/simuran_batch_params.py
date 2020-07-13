"""
simuran_batch_params.py is used to handle the
behaviour of analysis that recourses through child directories.
"""

import os

# Where to start running batch analysis from
start_dir = "__dirname__"

# regex_filters should be a list of regex patterns to match against.
regex_filters = []

# Overwrites existing parameter files (simuran_params.py) if they exist.
overwrite = True

# If True, only prints where the parameter files would be written to.
only_check = False

# If True, opens an interactive console to help design your regex_filters.
interactive = True

# Please include a path to mapping_file, or setup the mapping dictionary.
# This will determine which parameters are used in proceeding analysis.
# mapping directly specifies parameters, so mapping_file is preferred
# TODO does this work properly in main?
mapping = {}  # see default_params.py to set this up

# The magic string __dirname__, is replaced by the directory this file is in
directory = "__dirname__"
# Absolute path to a file that contains the mapping.
mapping_file = os.path.abspath(os.path.join(directory, "simuran_base_params.py"))

# The basename of the output parameter files.
out_basename = "simuran_params.py"

# Should all parameter files be deleted that match out_basename
# And exist in a child directory of the starting directory
delete_old_files = False

params = {
    "start_dir": start_dir,
    "regex_filters": regex_filters,
    "overwrite": overwrite,
    "only_check": only_check,
    "interactive": interactive,
    "mapping": mapping,
    "mapping_file": mapping_file,
    "out_basename": out_basename,
    "delete_old_files": delete_old_files,
}
