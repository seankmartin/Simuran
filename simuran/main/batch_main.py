"""Run a full analysis set."""
import os
import pickle

from simuran.main.main import run
from simuran.param_handler import ParamHandler
from simuran.main.merge import merge_files, csv_merge


def batch_main(
    run_dict_list,
    function_to_use=None,
    idx=None,
    handle_errors=False,
    save_info=False,
    **kwargs
):
    """
    Start the main control for running multiple simuran.main.main iterations.

    Parameters
    ----------
    run_dict_list : list of dict
        The parameters to use in simuran.main.main in each iteration
    function_to_use : str, optional
        Run this function config on each iteration, by default None
        If None, it should be specified in separate configuration files.
    idx : int, optional
        Instead of running each iteration, just run this index, by default None
    handle_errors : bool, optional
        If True, don't crash on errors, write them to file instead, by default False
    save_info : bool, optional
        If True, pickle the output of the analysis, by default False

    Returns
    -------
    list of tuple or tuple
        Each entry is the output of simuran.main.main

    TODO
    ----
    Allow for extra options, such as merging or concatenating
    All in all, it needs a way to define the relationship between the recordings
    For example, you may want to concatenate them, or take the average of them
    and then run the analysis

    """

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
    overwrite=False,
    merge=True,
    **kwargs
):
    """
    Run batch main, but makes it easier to handle the parameters involved.

    Parameters
    ----------
    run_dict_loc : str
        The path to a file describing the parameters for batch running.
    function_to_use : function, optional
        The function to run analysis with, by default None
    idx : int, optional
        An optional index in the batch to run for, by default None
    handle_errors : bool, optional
        Whether to crash on error or print to file, by default False
    overwrite : bool, optional
        Whether to overwrite an existing pickle of data, by default False
    merge: bool, optional
        Whether to merge output data, by default False

    Returns
    -------
    list of tuples or tuple
        the output of batch_main

    """
    run_dict = ParamHandler(in_loc=run_dict_loc, name="params")
    after_batch_function = run_dict.get("after_batch_fn", None)
    out_dir = os.path.abspath(
        os.path.join(os.path.dirname(run_dict_loc), "..", "sim_results")
    )
    fn_name = (
        "" if function_to_use is None else "--" + os.path.basename(function_to_use)
    )
    pickle_name = os.path.join(
        out_dir,
        os.path.splitext(os.path.basename(run_dict_loc))[0] + fn_name + "_dump.pickle",
    )

    if (idx is None) and os.path.isfile(pickle_name) and (not overwrite):
        with open(pickle_name, "rb") as f:
            all_info = pickle.load(f)
    else:
        all_info = batch_main(
            run_dict["run_list"],
            function_to_use=function_to_use,
            idx=idx,
            handle_errors=handle_errors,
            save_info=(after_batch_function is not None),
            **kwargs,
        )
        os.makedirs(out_dir, exist_ok=True)
        with open(pickle_name, "wb") as f:
            pickle.dump(all_info, f)

        if merge:
            csv_merge(out_dir)
            merge_files(out_dir)

    if after_batch_function is not None:
        after_batch_function(all_info, out_dir)

    return all_info
