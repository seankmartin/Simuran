from main import run


def make_default_dict():
    param_names = {
        "file_list_name": "file_list.txt",
        "cell_list_name": "cell_list.txt",
        "fn_param_name": "simuran_fn_params.py",
        "base_param_name": "simuran_base_params.py",
        "batch_param_name": "simuran_batch_params.py",
        "batch_find_name": "simuran_params.py",
    }
    return param_names


def main(run_dict_list, directory_list):
    for directory, run_dict in zip(directory_list, run_dict_list):
        run(directory, **run_dict)


if __name__ == "__main__":
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR8_muscimol\05102018"
    dict_l = [make_default_dict(), ]
    dir_l = [in_dir, ]
    main(dict_l, dir_l)
