import os
import shutil
import subprocess
import csv
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
        select_recordings=None, figures=[], figure_names=[],
        cell_list_name="cell_list.txt",
        file_list_name="file_list.txt",
        print_all_cells=True):

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
        # TODO this does not work properly at the moment
        if param_handler["overwrite"] and (not param_handler["only_check"]):
            batch_setup.clear_params(location, to_remove=param_name)
            dirs = batch_setup.write_batch_params(
                verbose_params=verbose_batch_params)

    # Setup the recording_container
    # TODO only parse things to be selected
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
        print("Sorting the container")
        recording_container.sort(sort_container_fn, reverse=reverse_sort)

    # TODO if file is empty run again
    in_dir = location if os.path.isdir(location) else os.path.dirname(location)
    if print_all_cells:
        help_out_loc = os.path.join(in_dir, "all_cells.txt")
        if not os.path.isfile(help_out_loc):
            print("Printing all units to {}".format(help_out_loc))
            total = 0
            with open(help_out_loc, "w") as f:
                for i in range(len(recording_container)):
                    recording_container[i].available = ["units"]
                    recording = recording_container.get(i)
                    available_units = recording.get_available_units()
                    f.write("----{}----\n".format(
                        os.path.basename(recording.source_file)))
                    for l in available_units:
                        if len(l[1]) != 0:
                            f.write("        " +
                                    "{}: Group {} with Units {}\n".format(
                                        total, l[0], l[1]))
                            total += 1
        else:
            print("All units already available at {}".format(help_out_loc))

    if select_recordings is not None:
        if not os.path.isdir(location):
            raise ValueError("Can't select recordings with only one")
        if select_recordings == True:
            select_location = os.path.join(
                recording_container.base_dir, file_list_name)
            if not os.path.isfile(select_location):
                idx_list = recording_container.subsample(interactive=True)
                print("Selected {} for processing, saved to {}".format(
                    recording_container.get_property("source_file"),
                    select_location))
                with open(select_location, "w") as f:
                    out_str = ""
                    for recording in recording_container:
                        name = recording.source_file
                        name = name[len(location + os.sep):]
                        out_str = "{}\n".format(name)
                        f.write(out_str)
            else:
                with open(select_location, "r") as f:
                    name_list = [x.strip() for x in f.readlines()]
                    recording_container.subsample_by_name(name_list)
        else:
            all_idx = True
            for val in select_recordings:
                if isinstance(val, str):
                    all_idx = False
            if all_idx:
                recording_container.subsample(idx_list=select_recordings)
            else:
                recording_container.subsample_by_name(select_recordings)

    # TODO move cell picking helper
    # TODO provide loaders with get list of cell only methods
    # TODO get this to work from saved list of cells
    cell_location = os.path.join(in_dir, cell_list_name)
    if not os.path.isfile(cell_location):
        print("Start unit select helper")
        total = 0
        ok = []
        for i in range(len(recording_container)):
            recording_container[i].available = ["units"]
            recording = recording_container.get(i)
            available_units = recording.get_available_units()
            print("--------{}--------".format(
                os.path.basename(recording.source_file)))
            for l in available_units:
                if len(l[1]) != 0:
                    print("    {}: Group {} with Units {}".format(
                        total, l[0], l[1]))
                    ok.append([i, l])
                    total += 1
        user_inp = input(
            "Please enter the units to analyse or enter the word all or num\n" +
            "Format: Idx: Unit, Unit, Unit | Idx: Unit, Unit, Unit\n")
        if user_inp == "":
            raise ValueError("No user input entered")
        if user_inp != "all":
            final_units = []
            try:
                parts = user_inp.strip().split("_")
                if len(parts) == 2:
                    group, unit_number = parts
                    group = int(group.strip())
                    unit_number = int(unit_number.strip())
                    unit_spec_list = [
                        [i, [unit_number, ]]
                        for i in range(total)
                        if ok[i][1][0] == group]
                else:
                    value = int(user_inp.strip())
                    unit_spec_list = [[i, [value, ]] for i in range(total)]
            except:
                unit_spec_list = []
                unit_specifications = user_inp.split("|")
                for u in unit_specifications:
                    parts = u.split(":")
                    idx = int(parts[0].strip())
                    units = [int(x.strip()) for x in parts[1].split(",")]
                    unit_spec_list.append([idx, units])
            for u in unit_spec_list:
                for val in u[1]:
                    if val not in ok[u[0]][1][1]:
                        raise ValueError("{}: {} not in {}".format(
                            u[0], val, ok[u[0]][1][1]))
                final_units.append([ok[u[0]][0], ok[u[0]][1][0], u[1]])
        with open(cell_location, "w") as f:
            max_num = max([len(u[2]) for u in final_units])
            unit_as_string = ["Unit_{}".format(i) for i in range(max_num)]
            unit_str = ",".join(unit_as_string)
            f.write("Recording,Group,{}\n".format(unit_str))
            for u in final_units:
                units_as_str = [str(val) for val in u[2]]
                unit_str = ",".join(units_as_str)
                f.write("{},{},{}\n".format(u[0], u[1], unit_str))
                recording = recording_container[u[0]]
                record_unit_idx = recording.units.group_by_property(
                    "group", u[1])[1][0]
                recording.units[record_unit_idx].units_to_use = u[2]
        print("Saved cells to {}".format(cell_location))
    else:
        print("Loading cells from {}".format(cell_location))
        with open(cell_location, "r") as f:
            reader = csv.reader(f, delimiter=",")
            next(reader)
            for row in reader:
                row = [int(x.strip()) for x in row]
                recording = recording_container[row[0]]
                record_unit_idx = recording.units.group_by_property(
                    "group", row[1])[1][0]
                recording.units[record_unit_idx].units_to_use = row[2:]

    analysis_handler = simuran.analysis.analysis_handler.AnalysisHandler()
    pbar = tqdm(range(len(recording_container)))
    for i in pbar:
        if args_fn is not None:
            function_args = args_fn(recording_container, i, figures)
        disp_name = recording_container[i].source_file[
            len(recording_container.base_dir + os.sep):]
        # Can include [fn.__name__ for fn in functions] below
        pbar.set_description("Running on {}".format(disp_name))
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


def run(
        in_dir, file_list_name="file_list.txt", cell_list_name="cell_list.txt",
        fn_param_name="simuran_fn_params.py",
        base_param_name="simuran_base_params.py",
        batch_param_name="simuran_batch_params.py",
        batch_find_name="simuran_params.py",
        default_param_folder=None,
        check_params=False):

    # TODO extract this into another function
    # TODO get different defaults. EG for NC.
    here = os.path.dirname(__file__)
    if default_param_folder is None:
        default_param_folder = os.path.join(here, "..", "params")
    default_param_names = {
        "fn": os.path.join(default_param_folder, "simuran_fn_params.py"),
        "base": os.path.join(default_param_folder, "simuran_base_params.py"),
        "batch": os.path.join(default_param_folder, "simuran_batch_params.py")
    }

    param_names = {
        "fn": fn_param_name,
        "base": base_param_name,
        "batch": batch_param_name}

    # TODO put this in another file
    t_editor = "notepad++"
    # t_editor = "code"
    new = False
    for key, value in param_names.items():
        full_name = os.path.join(in_dir, value)
        if not os.path.isfile(full_name):
            sim_p = default_param_names[key]
            shutil.copy(sim_p, full_name)
            args = [t_editor, full_name]
            print("Running {}".format(args))
            subprocess.run(args)
            new = True
        elif check_params:
            args = [t_editor, full_name]
            print("Running {}".format(args))
            subprocess.run(args)
    if check_params:
        full_name = os.path.join(in_dir, file_list_name)
        if os.path.isfile(full_name):
            args = [t_editor, full_name]
            print("Running {}".format(args))
            subprocess.run(args)
    if new or check_params:
        cont = input("Do you wish to continue with this setup? (y/n)\n")
        if cont.lower() == "n":
            exit(0)

    # TODO probably put this in main
    fn_param_loc = os.path.join(in_dir, fn_param_name)
    if not os.path.isfile(fn_param_loc):
        raise ValueError(
            "Please create a file listing params at {}".format(
                fn_param_loc))
    setup_ph = simuran.param_handler.ParamHandler(
        in_loc=fn_param_loc, name="fn_params")
    list_of_functions = setup_ph["run"]
    save_list = setup_ph["save"]
    args_fn = setup_ph.get("args", None)
    friendly_names = setup_ph.get("names", None)
    figures = setup_ph.get("figs", [])
    figure_names = setup_ph.get("fignames", [])
    sort_fn = setup_ph.get("sorting", None)

    main(
        in_dir, list_of_functions, save_list,
        args_fn=args_fn, do_batch_setup=True, sort_container_fn=sort_fn,
        verbose_batch_params=False, load_all=True, to_load=["units"],
        select_recordings=True, friendly_names=friendly_names,
        figures=figures, figure_names=figure_names,
        param_name=batch_find_name, batch_name=batch_param_name,
        cell_list_name=cell_list_name,
        file_list_name=file_list_name)


if __name__ == "__main__":
    # in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR7_muscimol\2_03082018"
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR8_muscimol\05102018"
    # in_dir = r"D:\ATNx_CA1"
    run(in_dir)
