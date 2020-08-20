"""This module is the main control for the simuran package."""

import os
import shutil
import subprocess
import site
import sys
import time
import multiprocessing
from copy import copy
from datetime import datetime

from tqdm import tqdm

import simuran.batch_setup
import simuran.recording_container
import simuran.recording
import simuran.analysis.analysis_handler
import simuran.param_handler
import simuran.plot.figure

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt4agg")


def save_figures(figures, out_dir, figure_names=[], verbose=False, set_done=False):
    """
    Save all figures to the output directory if they are ready.

    Parameters
    ----------
    figures : list of matplotlib.figure.Figure or simuran.plot.figure.SimuranFigure
        The figures to save.
    out_dir : str
        The output directory to save the figures to.
    figure_names : list of str, optional
        Names for each of the figures, by default [].
        If empty, uses fig+iteration as name, unless the figure at iteration,
        is a SimuranFigure with a name set.
    verbose : bool, optional
        Whether to print more information, by default False
    set_done : bool, optional
        If converting to a SimuranFigure, set whether the figure is ready for output.

    Returns
    -------
    list of simuran.plot.figure.SimuranFigure
        All the figures that were not ready to be saved.

    """
    for i, f in enumerate(figures):
        if not isinstance(f, simuran.plot.figure.SimuranFigure):
            figures[i] = simuran.plot.figure.SimuranFigure(figure=f, done=set_done)

    if len(figures) != 0:
        if verbose:
            print("Plotting figures to {}".format(os.path.join(out_dir, "plots")))

        if len(figure_names) != len(figures):
            for i, f in enumerate(figures):
                if f.filename is None:
                    f.set_filename("fig{}.png".format(i))
        else:
            for f, name in zip(figures, figure_names):
                f.set_filename(name)

        for f in figures:
            if f.isdone():
                if verbose:
                    print("Plotting to {}".format(f.get_filename()))
                f.savefig(os.path.join(out_dir, "plots", f.get_filename()))
                f.close()

    return [f for f in figures if not f.isdone()]


def save_unclosed_figures(out_dir):
    """Save any figures which were not closed to out_dir and close them."""
    figs = list(map(plt.figure, plt.get_fignums()))
    for i, f in enumerate(figs):
        f.savefig(os.path.join(out_dir, "unclosed_plots", "fig_{}.png".format(i)))
        f.close()


def check_input_params(location, batch_name):
    """
    Check the configuration parameters and create a batch setup.

    Parameters
    ----------
    location : str
        Where the main control will run, either a file or a directory.
    batch_name : str
        The path to a config file listing the configuration.

    Returns
    -------
    simuran.batch_setup.BatchSetup or None
        The created batch setup object based on the configuration.

    Raises
    ------
    FileNotFoundError
        The input location must be a file or a directory.
    ValueError
        The parameter file has the only_params loader set.

    """
    if os.path.isdir(location):
        batch_setup = simuran.batch_setup.BatchSetup(location, fpath=batch_name)
        full_param_loc = batch_setup.ph.get("mapping_file", "")

        record_params = simuran.param_handler.ParamHandler(
            in_loc=full_param_loc, name="mapping"
        )
        return batch_setup
    elif os.path.isfile(location):
        record_params = simuran.param_handler.ParamHandler(
            in_loc=location, name="mapping"
        )
        return None
    else:
        raise FileNotFoundError("location must be a file or a directory")

    if record_params["loader"] == "params_only":
        raise ValueError("The only params loader is not supported for loading files")


def modify_path(path_dir, verbose=False):
    """
    Add a folder to path and process any .pth files in it.

    Parameters
    ----------
    path_dir : str
        Path to the directory to add to python path.
    verbose : bool, optional
        Whether to print the new path, by default False

    Returns
    -------
    None

    """
    if os.path.isdir(path_dir):
        if verbose:
            print("Adding {} to path".format(path_dir))
        site.addsitedir(path_dir)
    elif verbose:
        print("WARNING: {} does not exist, not adding to path".format(path_dir))
    if verbose:
        print("The path is now:")
        for line in sys.path:
            print(line)


def batch_control_setup(batch_setup, only_check, do_interactive=True, verbose=False):
    """
    Perform the batch setup operation for main.

    Parameters
    ----------
    batch_setup : simuran.batch_setup.BatchSetup
        The object to perform the batch setup with.
    only_check : bool
        Whether to write files or just check where they would be written.
    do_interactive : bool, optional
        Whether to launch an interactive prompt for regex design, by default True
    verbose : bool, optional
        Whether to print more information, by default False

    Returns
    -------
    bool
        Whether files were written or not, True if they were written.

    """
    batch_setup.set_only_check(only_check)

    if batch_setup.ph["interactive"] or do_interactive:
        print(
            "Interactive mode selected, starting REGEX design at {}".format(
                batch_setup.ph["start_dir"]
            )
        )
        batch_setup.interactive_refilt()

    print("Running batch setup from {}".format(batch_setup.file_loc))
    batch_setup.write_batch_params(verbose_params=True, verbose=verbose)
    if batch_setup.ph["only_check"]:
        print(
            "Done checking batch setup. "
            + "Change only_check to False in {} to run".format(batch_setup.file_loc)
        )
    elif only_check:
        print("Done checking batch setup. " + "Pass only_check as False in main to run")

    return not (batch_setup.ph["only_check"] or only_check)


def container_setup(
    location, batch_params=None, sort_container_fn=None, reverse_sort=False
):
    """
    Set up the recording_container for the main control.

    Parameters
    ----------
    location : str
        The directory or file to run on
    batch_params : dict, optional
        Parameters for running if a directory is passed, by default None
    sort_container_fn : function, optional
        A function to sort the container with, by default None
    reverse_sort : bool, optional
        Whether to reverse the sorting, by default False

    Returns
    -------
    simuran.recording_container.RecordingContainer
        The recording container object with filenames setup

    Raises
    ------
    FileNotFoundError
        The location passed is not a file or a directory
    FileNotFoundError
        No recordings were found at the given location

    """
    recording_container = simuran.recording_container.RecordingContainer()
    if os.path.isdir(location):
        recording_container.auto_setup(
            location,
            param_name=batch_params["out_basename"],
            recursive=True,
            batch_regex_filters=batch_params["regex_filters"],
        )
    elif os.path.isfile(location):
        recording = simuran.recording.Recording(param_file=location, load=False)
        recording_container.append(recording)
    else:
        raise FileNotFoundError(
            "Please provide a valid location, entered {}".format(location)
        )

    if len(recording_container) == 0:
        raise FileNotFoundError("No recordings found in {}".format(location))

    if sort_container_fn is not None:
        print("Sorting the container")
        recording_container.sort(sort_container_fn, reverse=reverse_sort)

    return recording_container


def write_cells_in_container(
    recording_container, in_dir, name="all_cells.txt", overwrite=True
):
    """
    Write all the cells available in this container to a file.

    Parameters
    ----------
    recording_container : simuran.recording_container.RecordingContainer
        The container to write the cells for.
    location : str
        A directory to write to
    name : str, optional
        The name of the file to write, by default "all_cells.txt"
    overwrite : bool, optional
        Whether to overwrite an existing file, by default True

    Returns
    -------
    None

    """
    help_out_loc = os.path.join(in_dir, "all_cells.txt")
    if (not os.path.isfile(help_out_loc)) or overwrite:
        print("Printing all units to {}".format(help_out_loc))
        with open(help_out_loc, "w") as f:
            recording_container.print_units(f)
    else:
        print(
            "All units already available at {}, delete this to update".format(
                help_out_loc
            )
        )


def subsample_container(
    recording_container, select_recordings, file_list_name, overwrite=True
):
    """
    Subsample the main recording container.

    Parameters
    ----------
    recording_container : simuran.recording_container.RecordingContainer
        The recording container to subsample
    select_recordings : list or bool
        If a list, it should be a list of indices or names of recordings to use.
        If a bool, True indicates to launch an interactive prompt, False passes.
        If None is passed, it also passes.
    file_list_name : str
        The name of the file to save choices to, or load from if it exists.
    overwrite : bool, optional
        Whether to overwrite an existing file.

    Returns
    -------
    None

    """
    if len(recording_container) <= 1:
        return

    if (select_recordings is not None) and (select_recordings is not False):
        if select_recordings is True:
            select_location = os.path.join(recording_container.base_dir, file_list_name)
            if (not os.path.isfile(select_location)) or overwrite:
                recording_container.subsample(interactive=True, inplace=True)
                print(
                    "Selected {} for processing, saved to {}".format(
                        recording_container.get_property("source_file"), select_location
                    )
                )
                with open(select_location, "w") as f:
                    out_str = ""
                    for recording in recording_container:
                        name = recording.source_file
                        name = name[len(recording_container.base_dir + os.sep) :]
                        out_str = "{}\n".format(name)
                        f.write(out_str)
            else:
                print(
                    "Loading recordings from {}, delete this to update".format(
                        select_location
                    )
                )
                with open(select_location, "r") as f:
                    name_list = [x.strip() for x in f.readlines() if x.strip() != ""]
                    recording_container.subsample_by_name(name_list)
        else:
            all_idx = True
            for val in select_recordings:
                if isinstance(val, str):
                    all_idx = False
            if all_idx:
                recording_container.subsample(idx_list=select_recordings, inplace=True)
            else:
                recording_container.subsample_by_name(select_recordings, inplace=True)


def set_output_locations(batch_name, function_config_path):
    """
    Set up the output directory and name based on the input.

    Parameters
    ----------
    batch_name : str
        Path to a configuration file
    function_config_path : str
        Path to the function configuration file

    Returns
    -------
    out_dir : str
        The path to the output directory
    out_name : str
        The name of the results file to use

    """
    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")
    out_name = "sim_results_" + current_time + ".csv"
    whole_time = now.strftime("%Y-%m-%d--%H-%M-%S")
    out_dirname = whole_time

    try:
        start_str = os.path.splitext(os.path.basename(batch_name))[0]
        out_dirname2 = start_str
        if function_config_path is not None:
            out_dirname1 = os.path.splitext(os.path.basename(function_config_path))[0]
            start_str = (
                os.path.splitext(os.path.basename(function_config_path))[0]
                + "--"
                + start_str
            )

        else:
            out_dirname1 = whole_time

        out_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(batch_name),
                "..",
                "sim_results",
                out_dirname1,
                out_dirname2,
            )
        )
        out_name = "sim_results--" + start_str + ".csv"
    except BaseException:
        out_dir = os.path.abspath(
            os.path.join(os.path.dirname(batch_name), "..", "sim_results", out_dirname)
        )

    return out_dir, out_name


def multiprocessing_func(
    i,
    recording_container,
    functions,
    args_fn,
    figures,
    figure_names,
    load_all,
    to_load,
    out_dir,
):
    analysis_handler = simuran.analysis.analysis_handler.AnalysisHandler()
    if args_fn is not None:
        function_args = args_fn(recording_container, i, figures)
    if load_all:
        recording_container[i].available = to_load
        recording = recording_container.get(i)
    else:
        recording = recording_container[i]
    for fn in functions:
        # TODO get this right
        if not isinstance(fn, (tuple, list)):
            fn_args = function_args.get(fn.__name__, ([], {}))

            # This allows for multiple runs of the same function
            if isinstance(fn_args, dict):
                for key, value in fn_args.items():
                    args, kwargs = value
                    analysis_handler.add_fn(fn, recording, *args, **kwargs)
            else:
                args, kwargs = fn_args
                analysis_handler.add_fn(fn, recording, *args, **kwargs)
    analysis_handler.run_all_fns()
    recording_container[i].results = copy(analysis_handler.results)
    analysis_handler.reset()
    figures = save_figures(figures, out_dir, figure_names=figure_names, verbose=False)

    return figures


def run_all_analysis(
    recording_container,
    functions,
    args_fn,
    figures,
    figure_names,
    load_all,
    to_load,
    out_dir,
    num_cpus=1,
):
    """
    Run all of the analysis functions on the recording container.

    Parameters
    ----------
    recording_container : simuran.recording_container.RecordingContainer
        The recording container to run the analysis on.
    functions : list of functions
        The functions to run
    args_fn : function
        A function to retrive the arguments to use for the functions.
    figures : list of matplotlib.figure.Figure or simuran.plot.figure.SimuranFigure
        The figures to plot
    figure_names : list of str
        The names of the figures
    load_all : bool
        Whether to load the full recording or load as needed
    to_load : list of str
        The items to load if load_all is True
    out_dir : str
        The directory to save the figures to
    num_cpus : int, optional
        The number of CPUs to use, default is 1.

    Returns
    -------
    figures : list of simuran.plot.figure.SimuranFigure
        The figures to plot
    figure_names : list of str
        The names of the figures to plot

    """
    pbar = tqdm(range(len(recording_container)))

    final_figs = []
    if num_cpus > 1:
        pool = multiprocessing.get_context("spawn").Pool(num_cpus)
        print(
            "Launching {} workers for {} iterations".format(
                num_cpus, len(recording_container)
            )
        )
        for i in pbar:
            pool.apply_async(
                multiprocessing_func(
                    i,
                    recording_container,
                    functions,
                    args_fn,
                    figures,
                    figure_names,
                    load_all,
                    to_load,
                    out_dir,
                ),
                callback=final_figs.append,
            )

        pool.close()
        pool.join()

    else:
        for i in pbar:
            disp_name = os.path.relpath(
                recording_container[i].source_file, recording_container.base_dir
            )
            pbar.set_description("Running on {}".format(disp_name))
            multiprocessing_func(
                i,
                recording_container,
                functions,
                args_fn,
                figures,
                figure_names,
                load_all,
                to_load,
                out_dir,
            ),

    if args_fn is not None:
        function_args = args_fn(recording_container, i, final_figs)

    analysis_handler = simuran.analysis.analysis_handler.AnalysisHandler()
    for func in functions:
        if isinstance(func, (tuple, list)):
            fn, _ = func
            fn_args = function_args.get(fn.__name__, ([], {}))

            # This allows for multiple runs of the same function
            if isinstance(fn_args, dict):
                for key, value in fn_args.items():
                    args, kwargs = value
                    analysis_handler.add_fn(fn, recording_container, *args, **kwargs)
            else:
                args, kwargs = fn_args
                analysis_handler.add_fn(fn, recording_container, *args, **kwargs)

    analysis_handler.run_all_fns()
    recording_container.results = copy(analysis_handler.results)

    final_figs = save_figures(
        final_figs, out_dir, figure_names=figure_names, verbose=False
    )

    return final_figs


def setup_default_params(
    default_param_folder,
    batch_param_loc,
    fn_param_loc,
    base_param_name,
    text_editor,
    check_params,
):
    """
    Set up the default parameters from the folder given.

    Parameters
    ----------
    default_param_folder : str
        The path to a folder containing default parameters.
    batch_param_loc : str
        The path to a config file listing the program behaviour.
    fn_param_loc : str
        The path to a config file listing the functions that should be run.
    base_param_name : str
        The name of the base parameter file to use.
        Will be overwritten by the setting in batch_param_loc if exists.
    text_editor : str
        The text editor to use for editing the default parameters.
    check_params : bool
        Whether to check the parameters.

    Returns
    -------
    should_quit : bool
        True if execution should be halted.
    param_names : dict
        The "fn", "base", and "batch" parameter locations.
    in_dir : str
        The path to the directory that execution should start in.

    Raises
    ------
    FileNotFoundError
        Any of the default parameters do not exist.

    """
    should_quit = False
    default_param_names = {
        "fn": os.path.join(default_param_folder, "simuran_fn_params.py"),
        "base": os.path.join(default_param_folder, "simuran_base_params.py"),
        "batch": os.path.join(default_param_folder, "simuran_batch_params.py"),
    }
    for name in default_param_names.values():
        if not os.path.isfile(name):
            raise FileNotFoundError(
                "Default parameters do not exist at {}".format(name)
            )

    in_dir = os.path.dirname(batch_param_loc)
    param_names = {
        "fn": fn_param_loc,
        "base": os.path.abspath(os.path.join(in_dir, base_param_name)),
        "batch": batch_param_loc,
    }

    if os.path.isfile(param_names["batch"]):
        batch_handler = simuran.param_handler.ParamHandler(
            in_loc=param_names["batch"], name="params"
        )
        param_names["base"] = batch_handler.get("mapping_file", param_names["base"])
        in_dir = batch_handler.get("start_dir", in_dir)

    if in_dir != "":
        os.makedirs(in_dir, exist_ok=True)
    new = False
    made_files = []
    for key, value in param_names.items():
        full_name = value
        made_files.append(False)
        if not os.path.isfile(full_name):
            sim_p = default_param_names[key]
            shutil.copy(sim_p, full_name)
            made_files[-1] = True
            args = [text_editor, full_name]
            subprocess.run(args)
            new = True
        elif check_params:
            args = [text_editor, full_name]
            subprocess.run(args)

    if new or check_params:
        cont = input("Do you wish to continue with this setup? (y/n)\n")
        if cont.lower() == "n":
            delete_these = input(
                "Do you wish to delete the created setup files? (y/n)\n"
            )
            if delete_these.lower() == "y":
                for (key, value), made in zip(param_names.items(), made_files):
                    full_name = value
                    if os.path.isfile(full_name) and made:
                        os.remove(full_name)
            should_quit = True

    return should_quit, param_names, in_dir


def main(
    location,
    functions,
    attributes_to_save,
    args_fn=None,
    do_batch_setup=False,
    verbose=False,
    friendly_names=None,
    sort_container_fn=None,
    reverse_sort=False,
    param_name="simuran_params.py",
    batch_name="simuran_batch_params.py",
    load_all=True,
    to_load=["signals", "spatial", "units"],
    select_recordings=None,
    figures=[],
    figure_names=[],
    cell_list_name="cell_list.csv",
    file_list_name="file_list.txt",
    print_all_cells=True,
    do_cell_picker=True,
    decimals=3,
    function_config_path=None,
    only_check=False,
    should_modify_path=True,
    num_cpus=1,
):
    """
    Run the main control functionality.

    Also helps to set up files.

    Parameters
    ----------
    location : str
        The path to the directory or file to consider for analysis.
    functions : list
        A list of functions to perform on each recording.
    attributes_to_save : list
        A list of attributes to save from the results.
    args_fn : function, optional
        A function which returns the arguments to use for each
        function in functions for each recording.
        The default value None indicates default parameters will be used.
    do_batch_setup : bool, optional
        Whether to write new parameter files (default False).
    verbose : bool, optional
        Whether to print extra information about batch parameters (default False).
    friendly_names : list of strings, optional
        A list of names to save attributes_to_save under.
    sort_container_fn : function, optional
        A function to sort the recording container with.
    reverse_sort : bool, optional
        Reverses the sorting if sort_container_fn is provided.
    param_name : str, optional
        Which filename to look for which holds recording information.
    batch_name : str, optional
        Which filename to look for which holds batch information.
    load_all : bool, optional
        Whether to load information about each recording (default True).
    to_load : list of strings, optional
        Which items to load on the recording.
        Should be a subset of ["signals", "spatial", "units"]
    select_recordings : list of integers or strings, or bool, or None, optional
        If None, all recordings are used (default option).
        If True, an interactive console is launched to help pick recordings to consider.
        These chosen recordings are saved to disk and will be used if True is passed.
        If list, then the list of recordings used are the ones at those indices,
        or strings matched.
    figures : list, optional
        A list of figures to plot recordings into.
    figure_names : list of strings, optional
        Plotting names for each figure.
    cell_list_name : string, optional
        The filename to look for that describes the cells to consider.
        If this does not exist, an interactive prompt is shown to help make it.
    file_list_name : string, optional
        The filename to look for that describes the files to consider.
    print_all_cells : bool, optional
        Whether to save a file containing all the cells found (default True).
    do_cell_picker : bool, optional
        Whether to start a cell picking helper (default True).
    decimals : int, optional
        The number of decimals to round to in output (default 3).
    function_config_path : str, optional
        The path to a function configuration file (default None).
        At the moment, this is parsed in run.
        This is only used for naming purposes, currently.
    only_check : bool, optional
        Only checks what would run if True (default False)
    should_modify_path : bool, optional
        If True, the directory batch_script_dir/../analysis
        is added to path, by default True.
    num_cpus : int, optional
        The number of worker CPUs to launch, by default 1.

    Returns
    -------
    results : list of dict
        The results obtained from the analysis for each recording in the container.
    recording_container : simuran.recording_container.RecordingContainer
        The container that was used to obtain the results.

    Raises
    ------
    ValueError
        If do_batch_setup is True, but location is not a directory.
        If select_recordings is not None, but location is not a directory.
    FileNotFoundError
        If a valid location is not passed.
        If no recordings are found in the location passed
    LookupError
        Non-existant cells are tried to be selected.

    """
    in_dir = location if os.path.isdir(location) else os.path.dirname(location)
    batch_setup = check_input_params(location, batch_name)
    batch_params = batch_setup.ph
    out_dir, out_name = set_output_locations(batch_name, function_config_path)
    out_loc = os.path.join(out_dir, out_name)

    if should_modify_path:
        site_dir = os.path.abspath(
            os.path.join(os.path.dirname(batch_setup.file_loc), "..", "analysis")
        )
        modify_path(site_dir, verbose=verbose)

    if do_batch_setup:
        # TODO let the interactive be controllable
        if not batch_control_setup(
            batch_setup, only_check, do_interactive=False, verbose=verbose
        ):
            return [], []

    recording_container = container_setup(
        location, batch_params, sort_container_fn, reverse_sort
    )

    if print_all_cells:
        write_cells_in_container(recording_container, in_dir, overwrite=False)

    subsample_container(
        recording_container, select_recordings, file_list_name, overwrite=False
    )

    cell_location = os.path.join(in_dir, cell_list_name)
    # TODO improve this to load the info from write cells.
    if os.path.isfile(cell_location) or do_cell_picker:
        recording_container.select_cells(
            cell_location, do_cell_picker=do_cell_picker, overwrite=False
        )

    start_time = time.monotonic()
    recording_container.output_dir = out_dir
    figures = run_all_analysis(
        recording_container,
        functions,
        args_fn,
        figures,
        figure_names,
        load_all,
        to_load,
        out_dir,
        num_cpus=num_cpus,
    )

    recording_container.save_summary_data(
        out_loc,
        attr_list=attributes_to_save,
        friendly_names=friendly_names,
        decimals=decimals,
    )

    figures = save_figures(
        figures, out_dir, figure_names=figure_names, verbose=False, set_done=True
    )
    save_unclosed_figures(out_dir)

    results = recording_container.data_from_attr_list(
        attributes_to_save, friendly_names=friendly_names, decimals=decimals
    )

    print(
        "Operation completed in {:.2f}mins".format((time.monotonic() - start_time) / 60)
    )

    return results, recording_container


def run(
    batch_param_loc,
    fn_param_loc,
    file_list_name="file_list.txt",
    cell_list_name="cell_list.csv",
    base_param_name="simuran_base_params.py",
    batch_param_name="simuran_batch_params.py",
    batch_find_name="simuran_params.py",
    default_param_folder=None,
    check_params=False,
    text_editor="nano",
    do_batch_setup=True,
    do_cell_picker=True,
    verbose=False,
    only_check=False,
    should_modify_path=True,
    num_cpus=1,
):
    """
    Run main more readily without having to set as many params.

    The basic purpose of this function is to help set up the correct
    configuration files and setting the paths to those configuration files.

    The main function has the same functionality without using configuration files
    if that is preferred.

    Parameters
    ----------
    batch_param_loc : str
        The path to a config file listing the batch behaviour.
        If it does not exist, it will be created with the default params.
    fn_param_loc : str
        The path to a config file listing the function parameters.
        If it does not exist, it will be created with the default params.
    file_list_name : str, optional
        The name of the file listing the files to consider.
    cell_list_name : str, optional
        The name of the file listing the cells to consider.
    base_param_name : str, optional
        The name of the file list base parameters.
    batch_param_name : str, optional
        The name of the file listing batch parameters.
    batch_find_name : str, optional
        The name of the file listing recording parameters.
    default_param_folder : str or None, optional
        The folder to look for default parameters in.
        This is used for creating new parameter files,
        the defaults are used as a template.
    check_params : bool, optional
        Whether to print the selected parameters (default False).
    text_editor : str or None, optional
        The text editor to use (default nano).
    do_batch_setup : bool, optional
        Whether to write new parameter files (default True).
    do_cell_picker : bool, optional
        Whether to launch a cell picker (default True).
    verbose : bool, optional
        Whether to print extra information about batch parameters (default False).
    only_check : bool, optional
        Only checks what would run if True (default False)
    should_modify_path : bool, optional
        If True, the directory batch_script_dir/../analysis
        is added to path, by default True.
    num_cpus : int, optional
        The number of worker CPUs to launch, by default 1.

    Returns
    -------
    results : list of dict
        The results obtained from the analysis for each recording in the container.
    recording_container : simuran.recording_container.RecordingContainer
        The container that was used to obtain the results.

    Raises
    ------
    FileNotFoundError
        If the batch configuration path or function config path are invalid.

    """
    here = os.path.dirname(__file__)
    if default_param_folder is None:
        default_param_folder = os.path.join(here, "..", "params")
    should_quit, param_names, in_dir = setup_default_params(
        default_param_folder,
        batch_param_loc,
        fn_param_loc,
        base_param_name,
        text_editor,
        check_params,
    )
    if should_quit:
        return [], []

    if os.path.isfile(param_names["fn"]):
        if should_modify_path:
            site_dir = os.path.abspath(
                os.path.join(os.path.dirname(batch_param_loc), "..", "analysis")
            )
            modify_path(site_dir, verbose=verbose)
            should_modify_path = False
        setup_ph = simuran.param_handler.ParamHandler(
            in_loc=param_names["fn"], name="fn_params"
        )
        list_of_functions = setup_ph["run"]
        save_list = setup_ph["save"]
        args_fn = setup_ph.get("args", None)
        friendly_names = setup_ph.get("names", None)
        figures = setup_ph.get("figs", [])
        figure_names = setup_ph.get("fignames", [])
        sort_fn = setup_ph.get("sorting", None)
        to_load = setup_ph.get("to_load", ["signals", "spatial", "units"])
        load_all = setup_ph.get("load_all", True)
        select_recordings = setup_ph.get("select_recordings", True)
    else:
        raise FileNotFoundError(
            "Please create a file listing params at {}".format(fn_param_loc)
        )

    if os.path.isfile(param_names["batch"]):
        batch_handler = simuran.param_handler.ParamHandler(
            in_loc=param_names["batch"], name="params"
        )
        in_dir = batch_handler.get("start_dir", in_dir)
    else:
        raise FileNotFoundError(
            "Please create a file listing batch behaviour at {}".format(
                param_names["batch"]
            )
        )

    return main(
        in_dir,
        list_of_functions,
        save_list,
        args_fn=args_fn,
        sort_container_fn=sort_fn,
        friendly_names=friendly_names,
        figure_names=figure_names,
        figures=figures,
        param_name=os.path.basename(param_names["base"]),
        batch_name=param_names["batch"],
        cell_list_name=cell_list_name,
        file_list_name=file_list_name,
        to_load=to_load,
        load_all=load_all,
        select_recordings=select_recordings,
        do_batch_setup=do_batch_setup,
        do_cell_picker=do_cell_picker,
        verbose=verbose,
        function_config_path=fn_param_loc,
        only_check=only_check,
        should_modify_path=should_modify_path,
        num_cpus=num_cpus,
    )
