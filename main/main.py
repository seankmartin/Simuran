import os
from copy import copy
from datetime import datetime

from tqdm import tqdm
import simuran.batch_setup
import simuran.recording_container
import simuran.analysis.analysis_handler
import simuran.param_handler

# TODO this is only on my PC
import matplotlib
matplotlib.use('Qt4agg')


def main(
        location, functions, attributes_to_save,
        args_fn=None, do_batch_setup=False, friendly_names=None,
        sort_container_fn=None, reverse_sort=False,
        param_name="simuran_params.py", batch_name="simuran_batch_params.py",
        verbose_batch_params=False, load_all=False,
        to_load=["signals, spatial, units"],
        select_recordings=None, figures=[], figure_names=[]):

    # Do batch setup if requested.
    if do_batch_setup:
        if not os.path.isdir(location):
            raise ValueError(
                "Please provide a directory, entered {}".format(location))
        batch_setup = simuran.batch_setup.BatchSetup(
            location, fname=batch_name)
        print("Running batch setup {}".format(batch_setup))
        param_handler = simuran.param_handler.ParamHandler(
            in_loc=os.path.join(location, batch_name), name="params")
        if param_handler["overwrite"] and (not param_handler["only_check"]):
            batch_setup.clear_params(location, to_remove=param_name)
            dirs = batch_setup.write_batch_params(
                verbose_params=verbose_batch_params)
        if param_handler["only_check"]:
            print("Was only checking params so exiting.")
            return

    # Setup the recording_container
    recording_container = simuran.recording_container.RecordingContainer()
    if os.path.isdir(location):
        recording_container.auto_setup(
            location, param_name=param_name, recursive=True)
    elif os.path.isfile(location):
        recording_container.auto_setup(
            os.path.dirname(location), param_name=param_name,
            recursive=False)
    else:
        raise ValueError(
            "Please provide a valid location, entered {}".format(location))

    if sort_container_fn is not None:
        recording_container.sort(sort_container_fn, reverse=reverse_sort)

    if select_recordings is not None:
        if select_recordings == True:
            select_location = os.path.join(
                recording_container.base_dir, "file_list.txt")
            if not os.path.isfile(select_location):
                idx_list = recording_container.subsample(interactive=True)
                print("Selected {} for processing, saved to {}".format(
                    recording_container.get_property("source_file"),
                    select_location))
                with open(select_location, "w") as f:
                    out_str = ""
                    for val in idx_list:
                        out_str = "{} {}".format(out_str, val)
                    f.write(out_str[1:])
            else:
                with open(select_location, "r") as f:
                    idx_list = [int(x) for x in f.read().strip().split(" ")]
                    recording_container.subsample(idx_list=idx_list)
        else:
            recording_container.subsample(idx_list=select_recordings)

    analysis_handler = simuran.analysis.analysis_handler.AnalysisHandler()
    pbar = tqdm(range(len(recording_container)))
    for i in pbar:
        if args_fn is not None:
            function_args = args_fn(recording_container, i, figures)
        disp_name = recording_container[i].source_file[
            len(recording_container.base_dir + os.sep):]
        pbar.set_description(
            "Running {} on {}".format(
                [fn.__name__ for fn in functions], disp_name))
        if load_all:
            recording_container[i].available = to_load
            recording = recording_container.get(i)
        else:
            recording = recording_container[i]
        for fn in functions:
            fn_args = function_args.get(fn.__name__, [])

            # This allows for multiple runs of the same function
            if isinstance(fn_args, dict):
                for key, value in fn_args.items():
                    analysis_handler.add_fn(fn, recording, *value)
            else:
                analysis_handler.add_fn(fn, recording, *fn_args)
        analysis_handler.run_all_fns()
        recording_container[i].results = copy(analysis_handler.results)
        analysis_handler.reset()
    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")
    out_name = "sim_results_" + current_time + ".csv"
    whole_time = now.strftime("%Y-%m-%d--%H-%M-%S")
    out_dir = os.path.join(recording_container.base_dir,
                           "sim_results", whole_time)
    out_loc = os.path.join(out_dir, out_name)
    recording_container.save_summary_data(
        out_loc, attr_list=attributes_to_save, friendly_names=friendly_names)

    for f, name in zip(figures, figure_names):
        f.savefig(os.path.join(out_dir, "plots", name))


if __name__ == "__main__":
    # in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR7_muscimol\2_03082018"
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR8_muscimol\05102018"

    # Example sorting TODO also put this with the data
    def sort_fn(x):
        comp = x.source_file[len(in_dir + os.sep) + 1:]
        order = int(comp.split("_")[0])
        return order

    # Quick fix for these needs to be expanded upon
    fn_param_loc = os.path.join(in_dir, "simuran_fn_params.py")
    if not os.path.isfile(fn_param_loc):
        raise ValueError(
            "Please create a file listing params at {}".format(
                fn_param_loc))
    setup_ph = simuran.param_handler.ParamHandler(
        in_loc=fn_param_loc, name="fn_params")
    list_of_functions = setup_ph["run"]
    args_fn = setup_ph["args"]
    save_list = setup_ph["save"]
    friendly_names = setup_ph["names"]
    figures = setup_ph["figs"]
    figure_names = setup_ph["fignames"]

    main(
        in_dir, list_of_functions, save_list,
        args_fn=args_fn, do_batch_setup=True, sort_container_fn=sort_fn,
        verbose_batch_params=True, load_all=True, to_load=[],
        select_recordings=True, friendly_names=friendly_names,
        figures=figures, figure_names=figure_names)
