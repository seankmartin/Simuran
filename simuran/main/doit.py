"""This module contains helpers for creating doit tasks."""

import os
import shutil
import pprint

from doit.tools import title_with_actions

from simuran.main.single_main import modify_path
from simuran.param_handler import ParamHandler


def create_task(
    batch_file,
    analysis_functions=[],
    num_workers=1,
    dirname="",
    cfg_path="",
    reason="",
    overwrite=True,
    save=True,
):
    """
    Create a doit task.

    Parameters
    ----------
    batch_file : str
        The path to file to use for batch running SIMURAN.
    analysis_functions : list, optional
        List of strings of python files containing dependent functions, by default []
    num_workers : int, optional
        The number of workers to use for the task, by default 1
    dirname : str, optional
        The directory name to replace __dirname__ by in SIMURAN.
    cfg_path : str, optional
        The path to the configuration file.
    reason : str, optional
        A description of the reason for running the task.
    overwrite : bool, optional
        Whether to overwrite the existing results. By default True.
    save : bool, optional
        Whether to save the run to SUMATRA logs. By default True.

    Returns
    -------
    dict
        A python doit dictionary.

    """
    modify_path(
        os.path.abspath(os.path.join(os.path.dirname(batch_file), "..", "analysis")),
        verbose=False,
    )
    run_dict = ParamHandler(
        in_loc=batch_file, name="params", dirname_replacement=dirname
    )
    dependencies = []

    for run_dict in run_dict["run_list"]:
        batch_param_loc = os.path.abspath(run_dict["batch_param_loc"])
        if batch_param_loc not in dependencies:
            in_dir = os.path.dirname(batch_param_loc)
            dependencies.append(batch_param_loc)
            new_params = ParamHandler(in_loc=batch_param_loc, name="params")
            if new_params["mapping_file"] not in dependencies:
                dependencies.append(new_params["mapping_file"])
        function_loc = os.path.abspath(run_dict["fn_param_loc"])
        if function_loc not in dependencies:
            dependencies.append(function_loc)

    for fname in analysis_functions:
        path = os.path.abspath(
            os.path.join(os.path.dirname(in_dir), "..", "analysis", fname)
        )
        if os.path.isfile(path):
            dependencies.append(path)

    in_dir = os.path.dirname(batch_file)
    targets = [
        os.path.join(
            in_dir,
            "..",
            "sim_results",
            "pickles",
            os.path.splitext(os.path.basename(batch_file))[0] + "_dump.pickle",
        )
    ]
    if overwrite:
        overwrite_part = "-o "
    else:
        overwrite_part = ""
    if save:
        save_part = ""
    else:
        save_part = "-ns "
    action = f"simuran -r -m {overwrite_part}{save_part}-n {num_workers}"
    if dirname != "":
        action += f" --dirname {dirname}"
    if cfg_path != "":
        action += f" --config {cfg_path}"
    if reason != "":
        action += f' --reason "{reason}"'
    action += f" {batch_file}"

    def clean():
        run_dict_ = ParamHandler(in_loc=batch_file, name="params")
        for run_dict_i in run_dict_["run_list"]:
            function_loc_ = os.path.abspath(run_dict_i["fn_param_loc"])
            to_remove = os.path.join(
                os.path.dirname(batch_file),
                "..",
                "sim_results",
                os.path.splitext(os.path.basename(function_loc_))[0],
            )
            if os.path.isdir(to_remove):
                print("Removing folder {}".format(to_remove))
                shutil.rmtree(to_remove)

        for fname_ in targets:
            if os.path.isfile(fname_):
                print("Removing file {}".format(fname_))
                os.remove(fname_)

    return {
        "file_dep": dependencies,
        "targets": targets,
        "actions": [action],
        "clean": [clean],
        "title": title_with_actions,
        "verbosity": 0,
        "doc": action,
    }


def create_list_task(
    batch_file,
    analysis_functions=[],
    num_workers=1,
    dirname="",
    cfg_path="",
    reason="",
    overwrite=True,
    save=True,
):
    """
    Create a doit task.

    Parameters
    ----------
    batch_file : str
        The path to file to use for batch running SIMURAN.
    analysis_functions : list, optional
        List of strings of python files containing dependent functions, by default []
    num_workers : int, optional
        The number of workers to use for the task, by default 1
    dirname : str, optional
        The directory name to replace __dirname__ by in SIMURAN.
    cfg_path : str, optional
        The path to the configuration file.
    reason : str, optional
        A description of the reason for running the task.
    overwrite : bool, optional
        Whether to overwrite the existing results. By default True.
    save : bool, optional
        Whether to save the run to SUMATRA logs. By default True.

    Returns
    -------
    dict
        A python doit dictionary.

    """
    modify_path(
        os.path.abspath(os.path.join(os.path.dirname(batch_file), "..", "analysis")),
        verbose=False,
    )
    run_dict = ParamHandler(
        in_loc=batch_file, name="params", dirname_replacement=dirname
    )
    dependencies = [batch_file, run_dict["cell_list_path"]]

    in_dir = os.path.dirname(batch_file)
    for fname in analysis_functions:
        path = os.path.abspath(
            os.path.join(os.path.dirname(in_dir), "..", "analysis", fname)
        )
        if os.path.isfile(path):
            dependencies.append(path)

    targets = [
        os.path.join(
            batch_file,
            "..",
            "sim_results",
            "pickles",
            os.path.splitext(os.path.basename(batch_file))[0] + "_dump.pickle",
        )
    ]
    if overwrite:
        overwrite_part = "-o "
    else:
        overwrite_part = ""
    if save:
        save_part = ""
    else:
        save_part = "-ns "
    action = f"simuran -l {overwrite_part}{save_part}-n {num_workers}"
    if dirname != "":
        action += f" --dirname {dirname}"
    if cfg_path != "":
        action += f" --config {cfg_path}"
    if reason != "":
        action += f' --reason "{reason}"'
    action += f" {batch_file}"

    def clean():
        to_remove = os.path.join(
            os.path.dirname(batch_file),
            "..",
            "sim_results",
            os.path.splitext(os.path.basename(batch_file))[0],
        )
        if os.path.isdir(to_remove):
            print("Removing folder {}".format(to_remove))
            shutil.rmtree(to_remove)

        for fname_ in targets:
            if os.path.isfile(fname_):
                print("Removing file {}".format(fname_))
                os.remove(fname_)

    return {
        "file_dep": dependencies,
        "targets": targets,
        "actions": [action],
        "clean": [clean],
        "title": title_with_actions,
        "verbosity": 0,
        "doc": action,
    }


if __name__ == "__main__":
    pprint.pprint(
        create_task(
            "/media/sean/Elements/SubRet_recordings_imaging/SIMURAN/multi_runs/coherence_atnx.py",
            ["plot_coherence.py"],
            4,
        )
    )
