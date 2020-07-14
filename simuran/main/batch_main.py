"""Run a full analysis set."""

from simuran.main.main import run

# TODO this just needs a way to define the relationship between the recordings
# For example, you may want to concatenate them, or take the average of them,
# And then run the analysis


def main(run_dict_list, idx=None, handle_errors=False, **kwargs):
    def get_dict_entry(idx):
        run_dict = run_dict_list[idx]
        batch_param_loc = run_dict.pop("batch_param_loc")
        fn_param_loc = run_dict.pop("fn_param_loc")
        return run_dict, batch_param_loc, fn_param_loc

    if idx is not None:
        run_dict, batch_param_loc, fn_param_loc = get_dict_entry(idx)
        full_kwargs = {**run_dict, **kwargs}
        run(batch_param_loc, fn_param_loc, **full_kwargs)
        return
    for i in range(len(run_dict_list)):
        run_dict, batch_param_loc, fn_param_loc = get_dict_entry(idx)
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
