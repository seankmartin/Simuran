"""Run a full analysis set."""
import os

from simuran.main.main import run
from simuran.param_handler import ParamHandler

# TODO this just needs a way to define the relationship between the recordings
# For example, you may want to concatenate them, or take the average of them,
# And then run the analysis

# TODO allow for auto merging
def main(
    run_dict_list,
    function_to_use=None,
    idx=None,
    handle_errors=False,
    save_info=False,
    **kwargs
):
    # TODO I'd like to let names have no ext, and auto add .py if not there
    def get_dict_entry(index):
        run_dict = run_dict_list[index]
        batch_param_loc = run_dict.pop("batch_param_loc")
        fn_param_loc = run_dict.pop("fn_param_loc")
        if function_to_use is not None:
            fn_param_loc = function_to_use
        return run_dict, os.path.abspath(batch_param_loc), os.path.abspath(fn_param_loc)

    if idx is not None:
        run_dict, batch_param_loc, fn_param_loc = get_dict_entry(idx)
        full_kwargs = {**run_dict, **kwargs}
        info = run(batch_param_loc, fn_param_loc, **full_kwargs)
        return info

    all_info = []
    for i in range(len(run_dict_list)):
        print(
            "--------------------SIMURAN Batch Iteration {}--------------------".format(
                i
            )
        )
        run_dict, batch_param_loc, fn_param_loc = get_dict_entry(i)
        full_kwargs = {**run_dict, **kwargs}
        if handle_errors:
            with open("output_log.txt", "w") as f:
                try:
                    info = run(batch_param_loc, fn_param_loc, **full_kwargs)
                    all_info.append(info)
                except Exception as e:
                    print("ERROR: check output_log.txt for details")
                    f.write("Error on {} was {}\n".format(i, e))
        else:
            info = run(batch_param_loc, fn_param_loc, **full_kwargs)

        if save_info:
            all_info.append(info)

    return all_info


def batch_run(
    run_dict_loc,
    function_to_use=None,
    idx=None,
    handle_errors=False,
    after_batch_function=None,
    **kwargs
):

    # TODO for now, I am very lazily putting after_batch function here
    # Remember to change this!
    after_batch_function = plot_all_lfp

    run_dict = ParamHandler(in_loc=run_dict_loc, name="params")
    all_info = main(
        run_dict["run_list"],
        function_to_use=function_to_use,
        idx=idx,
        handle_errors=handle_errors,
        save_info=(after_batch_function is not None),
        **kwargs,
    )

    if after_batch_function is not None:
        # TODO support reloading this pickle dump
        import pickle

        out_dir = os.path.abspath(
            os.path.join(os.path.dirname(run_dict_loc), "..", "sim_results")
        )
        os.makedirs(out_dir, exist_ok=True)
        pickle_name = os.path.join(
            out_dir,
            os.path.splitext(os.path.basename(run_dict_loc))[0] + "_dump.pickle",
        )
        print("Dumping info to {}".format(pickle_name))
        with open(pickle_name, "wb") as f:
            pickle.dump(all_info, f)
        after_batch_function(all_info, out_dir)


def plot_all_lfp(info, out_dir):
    # TODO this is only temp here, should not be here in general
    import numpy as np
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)

    sns.set_style("ticks")
    sns.set_palette("colorblind")

    # TODO this should be a helper probably
    parsed_info = []
    for item in info:
        for val in item:
            parsed_info.append(list(val.values())[0])

    data = np.concatenate(parsed_info, axis=1)
    df = pd.DataFrame(data.transpose(), columns=["frequency", "coherence", "group"])
    df[["frequency", "coherence"]] = df[["frequency", "coherence"]].apply(pd.to_numeric)

    sns.lineplot(data=df, x="frequency", y="coherence", style="group", hue="group")

    sns.despine()

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Coherence")

    plt.savefig(os.path.join(out_dir, "coherence.png"), dpi=400)
