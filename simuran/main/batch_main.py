"""Run a full analysis set."""

from simuran.main.main import run
from simuran.param_handler import ParamHandler

# TODO this just needs a way to define the relationship between the recordings
# For example, you may want to concatenate them, or take the average of them,
# And then run the analysis

# TODO allow for auto merging
def main(run_dict_list, function_to_use=None, idx=None, handle_errors=False, **kwargs):
    # TODO I'd like to let names have no ext, and auto add .py if not there
    def get_dict_entry(index):
        run_dict = run_dict_list[index]
        batch_param_loc = run_dict.pop("batch_param_loc")
        fn_param_loc = run_dict.pop("fn_param_loc")
        if function_to_use is not None:
            fn_param_loc = function_to_use
        return run_dict, batch_param_loc, fn_param_loc

    if idx is not None:
        run_dict, batch_param_loc, fn_param_loc = get_dict_entry(idx)
        full_kwargs = {**run_dict, **kwargs}
        run(batch_param_loc, fn_param_loc, **full_kwargs)
        return
    for i in range(len(run_dict_list)):
        run_dict, batch_param_loc, fn_param_loc = get_dict_entry(i)
        full_kwargs = {**run_dict, **kwargs}
        if handle_errors:
            with open("output_log.txt", "w") as f:
                try:
                    run(batch_param_loc, fn_param_loc, **full_kwargs)
                except Exception as e:
                    print("ERROR: check output_log.txt for details")
                    f.write("Error on {} was {}\n".format(i, e))
        else:
            run(batch_param_loc, fn_param_loc, **full_kwargs)


def batch_run(
    run_dict_loc, function_to_use=None, idx=None, handle_errors=False, **kwargs
):
    run_dict = ParamHandler(in_loc=run_dict_loc, name="params")
    main(
        run_dict["run_list"],
        function_to_use=function_to_use,
        idx=idx,
        handle_errors=handle_errors,
        **kwargs
    )
