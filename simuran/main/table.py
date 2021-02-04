"""This module can convert directory structures into pandas and vice versa."""

import os
from pprint import pprint

import pandas as pd

from skm_pyutils.py_path import get_base_dir_to_files


def dir_to_table(directory):
    """
    Convert directory structure into a table.

    Parameters
    ----------
    directory : str
        The starting directory.

    """
    pass


def table_to_dir(table):
    """
    Convert pandas table structure into directory structure.

    Parameters
    ----------
    table : pandas.DataFrame
        Pandas dataframe containing the information.

    """
    pass


def excel_convert(filename, start_dir, optional_func=None):
    """
    Convert an excel file into a directory structure.

    Parameters
    ----------
    filename : str
        The path to the excel file.
    start_dir : str
        The directory to start the conversion to.
    optional_func : function, optional
        An optional function to apply to the filename.

    """
    df = pd.read_excel(filename)

    os.makedirs(start_dir, exist_ok=True)
    f_out = os.path.join(start_dir, "file_list.txt")
    c_out = os.path.join(start_dir, "cell_list.txt")

    start_dir = os.sep.join(start_dir.split(os.sep)[:-1])
    ffile = open(f_out, "w")
    cfile = open(c_out, "w")
    cfile.write("Recording,Group,Unit\n")

    # directories = df.iloc[:, : df.columns.get_loc("Filename")]
    last_fname = ""
    curr_idx = -1
    for value in df.itertuples():
        directories = value[1 : df.columns.get_loc("Filename") + 1]
        vals = directories[1:]
        # val == val checks for NaN
        vals = [val for val in vals if val == val]
        fname = value.Filename
        if optional_func is not None:
            fname = optional_func(fname)
        if len(vals) != 0:
            path = os.path.join(start_dir, *vals, fname)
            if path != last_fname:
                curr_idx += 1
                last_fname = path
                ffile.write(last_fname.replace("\\", "/") + "\n")
            cstr = "{},{},{}\n".format(curr_idx, value.Group, value.Unit)
            cfile.write(cstr)

    ffile.close()
    cfile.close()


def populate_table_directories(filename, dir_to_start, ext=None, re_filter=None):
    df = pd.read_excel(filename)

    if "Filename" not in df.columns:
        raise ValueError("Filename must be a column of the dataset")

    new_df = df.loc[:, "Filename":].copy()

    def mod_col(item):
        item = item.strip()
        if ext is not None:
            item += ext
        return item

    if ext is not None:
        new_df["Filename"] = new_df["Filename"].apply(mod_col)

    file_dict, no_match, multi_match = get_base_dir_to_files(
        new_df["Filename"].values, dir_to_start, ext=ext, re_filter=re_filter,
    )

    def new_col_maker(item):
        to_use = file_dict.get(item, [])
        if len(to_use) == 1:
            return to_use[0]
        else:
            return ""

    new_col = new_df["Filename"].apply(new_col_maker)

    new_df.insert(0, "Directory", new_col)

    base, out_ext = os.path.splitext(filename)
    out_fname = base + "_filled" + out_ext

    try:
        new_df.to_excel(out_fname, index=False)
    except PermissionError:
        print("Please close {}".format(out_fname))
    print("Wrote excel file to {}".format(out_fname))

    out_fname = base + "_log" + ".txt"
    with open(out_fname, "w") as f:
        f.write("----------Missing files----------\n")
        pprint(no_match, f)
        f.write("\n")
        f.write("----------Multiple Matches--------\n")
        pprint(multi_match, f)
        f.write("\n")
        f.write("----------Full dictionary----------\n")
        pprint(file_dict, f)
    print("Wrote log file to {}".format(out_fname))

    return new_df


if __name__ == "__main__":
    main_out_fname = (
        r"D:\SubRet_recordings_imaging\SIMURAN\cell_lists\CTRL_Lesion_cells.xlsx"
    )
    out_start_dir = r"D:\SubRet_recordings_imaging\SIMURAN\new_folder"
    in_start_dir = r"D:\SubRet_recordings_imaging"

    def opt_func(fnm):
        if fnm.endswith("_"):
            fnm = fnm[:-1]
        return fnm + ".set"

    populate_table_directories(main_out_fname, in_start_dir, ".set", "^CS.*|^LS.*")
    # excel_convert(out_fname, out_start_dir, opt_func, ext=".set")
