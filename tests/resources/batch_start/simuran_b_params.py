import os

# regex_filters should be a list of regex patterns to match against.
regex_filters = ["^test_this(?:(?!plz_ignore).)+$", "^test_this(?:(?!temp).)+$"]

# Overwrites existing parameter files (simuran_params.py) if they exist.
overwrite = True

# If True, only prints where the parameter files would be written to.
only_check = False

# If True, opens an interactive console to help design your regex_filters.
interactive = False

# Please include either mapping or mapping_file.
# This will determine which parameters are used in proceeding analysis.
mapping = {}  # see default_params.py to set this up

# Absolute path to a file that contains the mapping.
# If left as empty string, will create an absolute path from the relative path.
directory = "__dirname__"
mapping_file = os.path.join(directory, "sim_params.py")

# The basename of the output parameter files.
out_basename = "simuran_params_t.py"

delete_old_files = True

params = {
    "regex_filters": regex_filters,
    "overwrite": overwrite,
    "only_check": only_check,
    "interactive": interactive,
    "mapping": mapping,
    "mapping_file": mapping_file,
    "out_basename": out_basename,
    "delete_old_files": delete_old_files,
}
