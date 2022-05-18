"""Run analysis handler on recordings. TODO consider class"""
import logging
import multiprocessing
from copy import copy
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
from simuran.analysis.analysis_handler import AnalysisHandler
from simuran.log_handler import log_exception
from simuran.plot.figure import SimuranFigure
from tqdm import tqdm

module_logger = logging.getLogger("simuran.analysis.run_analysis")
main_was_error = False


def run_all_analysis(
    recording_container,
    functions,
    args_fn,
    figures,
    figure_names,
    load_all,
    to_load,
    out_dir,
    cfg,
    num_cpus=1,
    handle_errors=False,
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
    handle_errors : bool, optional
        Whether to raise errors, default is False.

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
                _multiprocessing_func(
                    i,
                    recording_container,
                    functions,
                    args_fn,
                    figures,
                    figure_names,
                    load_all,
                    to_load,
                    out_dir,
                    handle_errors,
                    cfg,
                ),
                callback=final_figs.append,
            )

        pool.close()
        pool.join()

    else:
        base_dir = recording_container.attrs.get("base_dir", None)
        for i in pbar:
            spath = Path(recording_container[i].source_file)
            if base_dir is not None:
                disp_name = spath.relative_to(base_dir)
            else:
                disp_name = spath.stem
            pbar.set_description("Running on {}".format(disp_name))
            figures = _multiprocessing_func(
                i,
                recording_container,
                functions,
                args_fn,
                figures,
                figure_names,
                load_all,
                to_load,
                out_dir,
                handle_errors,
                cfg,
            )

    if args_fn is not None:
        function_args = args_fn(recording_container, i, final_figs)

    analysis_handler = AnalysisHandler()
    for func in functions:
        if isinstance(func, (tuple, list)):
            fn, _ = func
            fn_args = function_args.get(fn.__name__, ([], {}))

            # This allows for multiple runs of the same function
            if isinstance(fn_args, dict):
                for key, value in fn_args.items():
                    cfg_cpy = copy(cfg)
                    args, kwargs = value
                    cfg_cpy.update(kwargs)
                    analysis_handler.add_fn(fn, recording_container, *args, **cfg_cpy)
            else:
                cfg_cpy = copy(cfg)
                args, kwargs = fn_args
                cfg_cpy.update(kwargs)
                analysis_handler.add_fn(fn, recording_container, *args, **cfg_cpy)

    analysis_handler.run_all_fns()
    recording_container.results = copy(analysis_handler.results)

    final_figs = save_figures(
        final_figs, out_dir, figure_names=figure_names, verbose=False
    )

    if main_was_error:
        module_logger.warning("A handled error occurred while loading files")
    return final_figs


def _multiprocessing_func(
    i,
    recording_container,
    functions,
    args_fn,
    figures,
    figure_names,
    load_all,
    to_load,
    out_dir,
    handle_errors,
    cfg,
):
    """This function is run once per recording to analyse."""
    analysis_handler = AnalysisHandler(handle_errors=handle_errors)
    if args_fn is not None:
        function_args = args_fn(recording_container, i, figures)
    else:
        function_args = {}
    if load_all:
        if to_load is not None:
            recording_container[i].available_data = to_load
        if handle_errors:
            try:
                recording = recording_container.load(i)
            except BaseException as e:
                log_exception(
                    e,
                    "Loading recording {} at {}".format(
                        i, recording_container[i].source_file
                    ),
                )
                global main_was_error
                main_was_error = True
                return figures
        else:
            recording = recording_container.load(i)
    else:
        recording = recording_container[i]

    for fn in functions:
        if not isinstance(fn, (tuple, list)):
            fn_args = function_args.get(fn.__name__, ([], {}))

            # This allows for multiple runs of the same function
            if isinstance(fn_args, dict):
                for key, value in fn_args.items():
                    cfg_cpy = copy(cfg)
                    args, kwargs = value
                    cfg_cpy.update(kwargs)
                    analysis_handler.add_fn(fn, recording, *args, **cfg_cpy)
            else:
                args, kwargs = fn_args
                cfg_cpy = copy(cfg)
                cfg_cpy.update(kwargs)
                analysis_handler.add_fn(fn, recording, *args, **cfg_cpy)
    analysis_handler.run_all_fns()
    recording_container[i].results = copy(analysis_handler.results)
    analysis_handler.reset()
    figures = save_figures(figures, out_dir, figure_names=figure_names, verbose=False)

    return figures


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
        if not isinstance(f, SimuranFigure):
            figures[i] = SimuranFigure(figure=f, done=set_done)

    if len(figures) != 0:
        if verbose:
            print("Plotting figures to {}".format(Path(out_dir) / "plots"))

        if len(figure_names) != len(figures):
            for i, f in enumerate(figures):
                if f.filename is None:
                    f.filename = "fig{}.png".format(i)
        else:
            for f, name in zip(figures, figure_names):
                f.filename = name

        for f in figures:
            if f.isdone():
                if verbose:
                    print("Plotting to {}".format(f.filename))
                f.savefig(Path(out_dir) / "plots" / f.filename)
                f.close()

    return [f for f in figures if not f.isdone()]


def save_unclosed_figures(out_dir):
    """Save any figures which were not closed to out_dir and close them."""
    figs = list(map(plt.figure, plt.get_fignums()))
    if len(figs) != 0:
        print("Saving unclosed_plots to {}".format(out_dir))
    for i, f in enumerate(figs):
        output_plot_dir = Path(out_dir) / "unclosed_plots"
        output_plot_dir.mkdir(parents=True, exist_ok=True)
        name = output_plot_dir / "fig_{}.png".format(i)
        f.savefig(name)
        plt.close(f)


def set_output_locations(batch_name, function_config_path, param_config_path):
    """
    Set up the output directory and name based on the input.

    Parameters
    ----------
    batch_name : str
        Path to a configuration file
    function_config_path : str
        Path to the function configuration file
    out_fn_dirname : str, optional
        The name of the output directory function part

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

    if batch_name is None:
        return Path(out_dirname), out_name

    batch_dir = Path(batch_name)

    try:
        start_str = batch_dir.stem
        out_dirname2 = start_str
        if function_config_path is not None:
            out_dirname1 = Path(function_config_path).stem
            start_str = out_dirname1 + "--" + start_str
        else:
            out_dirname1 = whole_time

        out_dirname3 = Path(param_config_path).stem

        out_dir = batch_dir.parent / "sim_results"
        out_dir = out_dir / out_dirname1 / out_dirname2 / out_dirname3
        out_name = "sim_results--" + start_str + ".csv"
    except BaseException:
        out_dir = batch_dir.parent / "sim_results" / out_dirname

    return out_dir.resolve(), out_name
