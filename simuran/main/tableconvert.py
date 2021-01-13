"""This module can convert directory structures into pandas and vice versa."""

import os


import pandas as pd
import numpy as np


def dir_to_table(dir):
    """
    Convert directory structure into a table.

    Parameters
    ----------
    dir : str
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

    f_out = os.path.join(start_dir, "file_list.txt")
    c_out = os.path.join(start_dir, "cell_list.txt")
    ffile = open(f_out, "w")
    cfile = open(c_out, "w")
    cfile.write("Recording,Group,Unit\n")

    directories = df.iloc[:, : df.columns.get_loc("Filename")]
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


if __name__ == "__main__":
    out_fname = r"D:\SubRet_recordings_imaging\SIMURAN\CTRL_Lesion_cells.xlsx"
    out_start_dir = r"D:\SubRet_recordings_imaging\SIMURAN\new_folder"

    def opt_func(fnm):
        if fnm.endswith("_"):
            fnm = fnm[:-1]
        return fnm + ".set"

    excel_convert(out_fname, out_start_dir, opt_func)
