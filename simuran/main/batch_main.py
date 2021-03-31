"""Run a full analysis set."""
import os
import pickle
import time
import multiprocessing

from skm_pyutils.py_log import log_exception

from simuran.main.main import run, modify_path
from simuran.param_handler import ParamHandler
from simuran.main.merge import merge_files, csv_merge


def get_dict_entry(run_dict_list, function_to_use, index):
    run_dict = run_dict_list[index]
    batch_param_loc = run_dict.pop("batch_param_loc")
    fn_param_loc = run_dict.pop("fn_param_loc")
    if function_to_use is not None:
        fn_param_loc = function_to_use
    return run_dict, os.path.abspath(batch_param_loc), os.path.abspath(fn_param_loc)


def multiprocessing_func(
    i, run_dict_list, function_to_use, kwargs, handle_errors, save_info, keep_container,
):
    # TODO printing would have to be stored and done at the end
    print(
        "--------------------SIMURAN Batch Iteration {}--------------------".format(i)
    )
    run_dict, batch_param_loc, fn_param_loc = get_dict_entry(
        run_dict_list, function_to_use, i
    )
    full_kwargs = {**run_dict, **kwargs}
    if handle_errors:
        try:
            results, recording_container = run(
                batch_param_loc, fn_param_loc, **full_kwargs
            )
        except BaseException as e:
            log_exception(
                e, "Running batch on iteration {} using {}".format(i, batch_param_loc),
            )
    else:
        results, recording_container = run(batch_param_loc, fn_param_loc, **full_kwargs)

    if save_info:
        if keep_container:
            to_use = recording_container
        else:
            if type(recording_container) is list:
                to_use = []
            else:
                to_use = recording_container.get_property("source_file")
    else:
        to_use = None

    return i, results, to_use


def batch_main(
    run_dict_list,
    function_to_use=None,
    idx=None,
    handle_errors=False,
    save_info=False,
    keep_container=False,
    num_cpus=4,
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
        If True, append the output of analysis to a list, by default False
    keep_container : bool, optional
        If True, keeps the container made in main, by default False
        False just keeps the results and the filenames
    num_cpus : int, optional
        The number of worker CPUs to launch, by default 4.
        Enter 1 to disable multiprocessing.

    Returns
    -------
    tuple of lists or tuple
        A single tuple is returned if idx is not None
        Otherwise, tuple[0] is the list of results
        while tuple[1] is the name of the recording,
        or the recording container, depending on the configuration.

    """
    all_info = []

    if idx is not None:
        run_dict, batch_param_loc, fn_param_loc = get_dict_entry(idx)
        full_kwargs = {**run_dict, **kwargs}
        info = run(batch_param_loc, fn_param_loc, **full_kwargs)
        return info

    if num_cpus > 1:
        pool = multiprocessing.get_context("spawn").Pool(num_cpus)

        print(
            "Launching {} workers for {} iterations".format(
                num_cpus, len(run_dict_list)
            )
        )
        for i in range(len(run_dict_list)):
            pool.apply_async(
                multiprocessing_func,
                args=(
                    i,
                    run_dict_list,
                    function_to_use,
                    kwargs,
                    handle_errors,
                    save_info,
                    keep_container,
                ),
                callback=all_info.append,
            )

        pool.close()
        pool.join()
        all_info = sorted(all_info, key=lambda x: x[0])
        final_res = ([], [])
        for item in all_info:
            final_res[0].append(item[1])
            final_res[1].append(item[2])

    else:
        print("Starting a loop over {} iterations".format(len(run_dict_list)))
        final_res = ([], [])
        for i in range(len(run_dict_list)):
            info = multiprocessing_func(
                i,
                run_dict_list,
                function_to_use,
                kwargs,
                handle_errors,
                save_info,
                keep_container,
            )
            final_res[0].append(info[1])
            final_res[1].append(info[2])

    return final_res


def batch_run(
    run_dict_loc,
    function_to_use=None,
    idx=None,
    handle_errors=False,
    overwrite=False,
    merge=True,
    num_cpus=4,
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
    num_cpus : int, optional
        The number of worker CPUs to launch, by default 4.
        Enter 1 to disable multiprocessing.

    Returns
    -------
    list of tuples or tuple
        the output of batch_main

    Raises
    ------
    ValueError
        More CPUs than available were entered.

    """
    if num_cpus > multiprocessing.cpu_count():
        raise ValueError(
            "Entered more CPUs than available, detected {}.".format(
                multiprocessing.cpu_count()
            )
        )

    start_time = time.monotonic()
    dirname = kwargs.get("dirname", "")
    run_path_to_use = os.path.dirname(run_dict_loc) if dirname == "" else dirname
    modify_path(
        os.path.abspath(os.path.join(run_path_to_use, "..", "analysis")),
        verbose=kwargs.get("verbose", False),
    )
    run_dict = ParamHandler(
        in_loc=run_dict_loc, name="params", dirname_replacement=dirname
    )
    after_batch_function = run_dict.get("after_batch_fn", None)
    keep_container = run_dict.get("keep_all_data", False)
    to_merge = run_dict.get("to_merge", [])
    if isinstance(to_merge, str):
        to_merge = [to_merge]
    out_dir = os.path.abspath(os.path.join(run_path_to_use, "..", "sim_results"))
    fn_name = (
        ""
        if function_to_use is None
        else "--" + os.path.splitext(os.path.basename(function_to_use))[0]
    )
    pickle_name = os.path.join(
        out_dir,
        "pickles",
        os.path.splitext(os.path.basename(run_dict_loc))[0] + fn_name + "_dump.pickle",
    )
    if (
        (idx is None)
        and (not kwargs.get("only_check", False))
        and os.path.isfile(pickle_name)
        and (not overwrite)
    ):
        print(
            "Loading data from {}, please delete it to run instead".format(pickle_name)
        )
        with open(pickle_name, "rb") as f:
            all_info = pickle.load(f)
    else:
        all_info = batch_main(
            run_dict["run_list"],
            function_to_use=function_to_use,
            idx=idx,
            handle_errors=handle_errors,
            save_info=(not kwargs.get("only_check", False)),
            keep_container=keep_container,
            should_modify_path=False,
            num_cpus=num_cpus,
            **kwargs,
        )
        if not kwargs.get("only_check", False) and (idx is None):
            os.makedirs(os.path.dirname(pickle_name), exist_ok=True)
            with open(pickle_name, "wb") as f:
                pickle.dump(all_info, f)

            if merge:
                print("--------------------Merging results--------------------")
                if len(to_merge) == 0:
                    print("Merging everything in {}".format(out_dir))
                    csv_merge(out_dir)
                    merge_files(out_dir)
                else:
                    for folder in to_merge:
                        print(
                            "Merging in the folder {}".format(
                                os.path.join(out_dir, folder)
                            )
                        )
                        csv_merge(os.path.join(out_dir, folder))
                        merge_files(os.path.join(out_dir, folder))
    if (
        (not kwargs.get("only_check", False))
        and (after_batch_function is not None)
        and (after_batch_function != "save")
    ):
        print("Running {}".format(after_batch_function.__name__))
        after_batch_function(
            all_info,
            extra_info=(
                out_dir,
                os.path.splitext(os.path.basename(run_dict_loc))[0] + fn_name,
            ),
        )

    print(
        "Batch operation completed in {:.2f}mins".format(
            (time.monotonic() - start_time) / 60
        )
    )

    return all_info
