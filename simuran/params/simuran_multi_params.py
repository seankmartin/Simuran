"""
simuran_multi_params describes running main.py for multiple
different recordings, functions, etc.
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

        # These will often stay the same since the parameters that describe the
        # layout of a recording don't often change
        param_names["base_param_name"] = "simuran_base_params.py"
        param_names["batch_find_name"] = "simuran_params.py"

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
            os.path.join("__dirname__", "simuran_batch_params.py"),
            os.path.join("__dirname__", "simuran_fn_params.py"),
            "name_for_cell_and_file_outputs",
        )
    )

    return output


def set_fixed_params(in_dict):
    """The parameters that are general should be set here."""
    in_dict["default_param_folder"] = None

    return in_dict


# Setup the actual parameters
params = {"run_list": []}
params = set_fixed_params(params)

for val in set_file_locations():
    param_dict = create_new_entry(val[0], val[1], val[2])
    params["run_list"].append(param_dict)
