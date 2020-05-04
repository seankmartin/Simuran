from main import run
from simuran.param_handler import ParamHandler


def make_default_dict(add=""):
    param_names = {
        "file_list_name": "file_list{}.txt".format(add),
        "cell_list_name": "cell_list{}.txt".format(add),
        "fn_param_name": "simuran_fn_params{}.py".format(add),
        "base_param_name": "simuran_base_params.py".format(add),
        "batch_param_name": "simuran_batch_params.py".format(add),
        "batch_find_name": "simuran_params.py".format(add),
    }
    return param_names


def main(
        run_dict_list, directory_list,
        default_param_folder=None, check_params=False, idx=None):
    with open("output_log.txt", "w") as f:
        if idx is not None:
            directory = directory_list[idx]
            run_dict = run_dict_list[idx]
            run(
                directory, check_params=check_params,
                default_param_folder=default_param_folder, **run_dict)
            return
        for i, (directory, run_dict) in enumerate(zip(directory_list, run_dict_list)):
            try:
                run(
                    directory, check_params=check_params,
                    default_param_folder=default_param_folder, **run_dict)
            except Exception as e:
                print("ERROR: check output_log.txt for details")
                f.write("Error on {} was {}".format(i, e))


if __name__ == "__main__":
    param_file = r"D:\SubRet_recordings_imaging\muscimol_data\batch.py"
    ph = ParamHandler(in_loc=param_file, name="params")
    dict_l = ph["param_list"]
    dir_l = ph["directory_list"]
    default_param_folder = ph["default_param_folder"]
    check_params = ph["check_params"]
    main(dict_l, dir_l, default_param_folder=default_param_folder,
         check_params=check_params, idx=None)
