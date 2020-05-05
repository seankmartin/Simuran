import os
import shutil
import numpy as np

from main import run

from simuran.param_handler import ParamHandler
from skm_pyutils.py_path import get_all_files_in_dir


def merge(in_dict, out_dir, all_result_ext=None):
    all_file_loc = os.path.join(out_dir, "all_results_merged")
    os.makedirs(all_file_loc, exist_ok=True)
    for location, value in in_dict.items():
        d = os.path.join(location, "sim_results")
        dirs = [os.path.join(d, o) for o in os.listdir(d)
                if os.path.isdir(os.path.join(d, o))][::-1]
        dirs_to_use = dirs[:value]
        for d in dirs_to_use:
            name = d[len(out_dir) - 11:]
            name = "--".join(name.split(os.sep))
            copy_location = os.path.join(out_dir, name)
            print("Copying {} to {}".format(d, copy_location))
            all_files = get_all_files_in_dir(
                d, ext=all_result_ext,
                recursive=True, return_absolute=True)

            all_names = ["--".join(f[len(out_dir) - 11:].split(os.sep))
                         for f in all_files]
            for f, o_name in zip(all_files, all_names):
                out_name = os.path.join(all_file_loc, o_name)
                shutil.copy(f, out_name)
            shutil.copytree(d, copy_location, dirs_exist_ok=True)


def csv_merge(
        in_dir, keep_headers=True, insert_newline=True, stats=True,
        delim=",", data_start_col=1):
    csv_files = get_all_files_in_dir(in_dir, ext="csv", recursive=True)
    o_name = os.path.join(in_dir, "merge.csv")
    if os.path.isfile(o_name):
        csv_files = csv_files[1:]
    with open(o_name, "w") as output:
        for i, f in enumerate(csv_files):
            print("Merging {} into {}".format(f, o_name))
            with open(f, 'r') as open_file:
                lines = open_file.readlines()
                if keep_headers or (i == 0):
                    for line in lines:
                        output.write(line)
                else:
                    for line in lines[1:]:
                        output.write(line)

                if stats:
                    split_up = [line.split(",")[data_start_col:]
                                for line in lines[1:]]
                    data = np.zeros(shape=(len(split_up), len(split_up[0])))
                    for i, row in enumerate(split_up):
                        data[i] = np.array([float(val.strip()) for val in row])
                    avg = np.mean(data, axis=0)
                    std = np.std(data, axis=0)
                    avg_str = (
                        "Average," +
                        ",".join(str(val) for val in avg)[:-1] + "\n")
                    std_str = (
                        "Std," +
                        ",".join(str(val) for val in std)[:-1] + "\n")
                    output.write(avg_str)
                    output.write(std_str)

                if insert_newline:
                    output.write('\n')


if __name__ == "__main__":
    param_file = r"D:\SubRet_recordings_imaging\muscimol_data\batch.py"
    out_dir = r"D:\SubRet_recordings_imaging\muscimol_data\sim_results"
    os.makedirs(out_dir, exist_ok=True)
    ph = ParamHandler(in_loc=param_file, name="params")
    dir_l = ph["directory_list"]
    in_dict = {}
    for val in dir_l:
        if val not in in_dict.keys():
            in_dict[val] = 1
        else:
            in_dict[val] += 1
    merge(in_dict, out_dir, all_result_ext="png")
    csv_merge(out_dir)
