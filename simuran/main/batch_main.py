"""Run a full analysis set."""
import os

from simuran.main.main import run
from simuran.param_handler import ParamHandler
from neurochat.nc_utils import smooth_1d

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

    # TODO support reloading this pickle dump
    import pickle

    out_dir = os.path.abspath(
        os.path.join(os.path.dirname(run_dict_loc), "..", "sim_results")
    )
    os.makedirs(out_dir, exist_ok=True)
    fn_name = "" if function_to_use is None else os.path.basename(function_to_use)
    pickle_name = os.path.join(
        out_dir,
        os.path.splitext(os.path.basename(run_dict_loc))[0]
        + "--"
        + fn_name
        + "_dump.pickle",
    )
    print("Dumping info to {}".format(pickle_name))
    with open(pickle_name, "wb") as f:
        pickle.dump(all_info, f)

    if after_batch_function is not None:
        after_batch_function(all_info, out_dir)

    return all_info


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
    control_data = []
    lesion_data = []
    for item in info:
        for val in item:
            this_item = list(val.values())[0]
            to_use = this_item
            this_item[1][-10:] = this_item[1][-20:-10]
            to_use[1] = smooth_1d(
                this_item[1].astype(float), kernel_type="hg", kernel_size=5
            )
            if this_item[2][0] == "Control":
                control_data.append(to_use[1])
            else:
                lesion_data.append(to_use[1])
            x_data = to_use[0].astype(float)
            parsed_info.append(to_use)

    lesion_arr = np.array(lesion_data).astype(float)
    control_arr = np.array(control_data).astype(float)

    y_lesion = np.average(lesion_arr, axis=0)
    y_control = np.average(control_arr, axis=0)

    difference = y_control - y_lesion

    data = np.concatenate(parsed_info[:-1], axis=1)
    df = pd.DataFrame(data.transpose(), columns=["frequency", "coherence", "Group"])
    df.replace("Control", "Control (ATN,   N = 6)", inplace=True)
    df.replace("Lesion", "Lesion  (ATNx, N = 5)", inplace=True)
    df[["frequency", "coherence"]] = df[["frequency", "coherence"]].apply(pd.to_numeric)

    sns.lineplot(
        data=df, x="frequency", y="coherence", style="Group", hue="Group", ci=None
    )

    sns.despine()

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Coherence")

    plt.ylim(0, 0.6)

    print("Saving plots to {}".format(out_dir))
    plt.savefig(os.path.join(out_dir, "coherence.png"), dpi=400)

    plt.ylim(0, 1)

    plt.savefig(os.path.join(out_dir, "coherence_full.png"), dpi=400)

    plt.close("all")

    sns.set_style("ticks")
    sns.set_palette("colorblind")

    sns.lineplot(x=x_data, y=difference)

    sns.despine()

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Difference")

    print("Saving to {}".format((os.path.join(out_dir, "difference.pdf"))))
    plt.savefig(os.path.join(out_dir, "difference.pdf"), dpi=400)
