"""
simuran_multi_params describes running main.py multiple times.

This can support different recordings, functions, etc.
In theory, this could describe a full experiment.
"""


def create_new_entry(batch_param_loc, fn_param_loc, add=""):
    """Create a new entry in the batch dictionary."""

    def make_default_dict(add=""):
        param_names = {}

        # file_list_name is often specific to each analysis
        # as it lists all recordings found under the given regex
        param_names["file_list_name"] = "file_list{}.txt".format(add)

        param_names["cell_list_name"] = "cell_list{}.txt".format(add)

        return param_names

    output_dict = make_default_dict(add=add)

    output_dict["batch_param_loc"] = batch_param_loc
    output_dict["fn_param_loc"] = fn_param_loc

    return output_dict


def set_file_locations():
    """The actual locations to analyse should be set here."""
    import os

    output = []

    output.append(
        (
            os.path.join("__thisdirname__", "simuran_batch_params.py"),
            os.path.join("__thisdirname__", "simuran_fn_params.py"),
            "name_for_cell_and_file_outputs",
        )
    )

    return output


def set_fixed_params(in_dict):
    """The parameters that are general should be set here."""
    in_dict["default_param_folder"] = None

    # Can set a function to run after all analysis here
    # For example, it could plot a summary of all the data
    in_dict["after_batch_fn"] = None

    # If the after batch function needs the full dataset
    # Pass this as true
    # For example, this could be used to concatenate
    # EEG signals that were recorded in two second long trials
    in_dict["keep_all_data"] = False

    # What folders to merge after running, as a list of string folder names
    in_dict["to_merge"] = None

    return in_dict


# Setup the actual parameters
params = {"run_list": []}
params = set_fixed_params(params)

for val in set_file_locations():
    param_dict = create_new_entry(val[0], val[1], val[2])
    params["run_list"].append(param_dict)
