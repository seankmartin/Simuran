import os

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
mapping = {}  # see default_params.py to set this up

# If left as empty string, will create an absolute path from the relative path.
directory = ""
# Absolute path to a file that contains the mapping.
mapping_file = os.path.join(directory, "simuran_base_params.py")

# The basename of the output parameter files.
out_basename = "simuran_params.py"

params = {
    "regex_filters": regex_filters,
    "overwrite": overwrite,
    "only_check": only_check,
    "interactive": interactive,
    "mapping": mapping,
    "mapping_file": mapping_file,
    "out_basename": out_basename,
}
