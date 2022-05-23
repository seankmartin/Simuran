"""This module can convert directory structures into pandas and vice versa."""

import logging
import os
import pickle
from pathlib import Path
from pprint import pprint
from typing import Any, Callable, Optional, Union

import pandas as pd
from skm_pyutils.log import get_default_log_loc
from skm_pyutils.path import get_all_files_in_dir, get_base_dir_to_files
from skm_pyutils.table import (df_from_file, df_subset_from_rows, df_to_file,
                               list_to_df)

from simuran.analysis.analysis_handler import AnalysisHandler
from simuran.core.log_handler import log_exception, print
from simuran.core.param_handler import ParamHandler
from simuran.loaders.base_loader import BaseLoader
from simuran.recording import Recording
from simuran.recording_container import RecordingContainer

module_logger = logging.getLogger("simuran.table")


def dir_to_table(directory, cell_id="cell_list", file_id="file_list", ext=".txt"):
    """
    Convert directory structure into a table.

    Parameters
    ----------
    directory : str
        The starting directory.
    cell_id : str, optional
        The starting string to any cell list file.
        Defaults to "cell_list"
    file_id : str, optional
        The starting string to any file list file.
        Defaults to "file_list"
    ext : str, optional
        The extension of the files.
        defaults to ".txt"

    Returns
    -------
    df : pandas.DataFrame
        The dataframe of the directory information.

    """
    txt_files = get_all_files_in_dir(
        directory, ext=ext, recursive=True, return_absolute=False
    )
    d = {}
    for f in txt_files:
        basename = os.path.basename(f)
        if basename.startswith(cell_id):
            l = len(cell_id) + 1
            ok = "cell"
        elif basename.startswith(file_id):
            l = len(file_id) + 1
            ok = "file"
        else:
            continue
        k = (
            os.path.dirname(f).replace(os.sep, "--")
            + "--"
            + os.path.splitext(basename)[0][l:]
        )
        if k not in d:
            d[k] = {}
        d[k][ok] = os.path.join(directory, f)

    saved_info = []
    for k, v in d.items():
        cell_loc = v.get("cell", None)
        file_loc = v.get("file", None)
        if (cell_loc is None) or (file_loc is None):
            continue
        if k.startswith("--"):
            start_dir = None
        else:
            start_dir = (os.sep).join(k.split("--")[:-1])

        with open(file_loc, "r") as f:
            if start_dir is not None:
                files = [
                    os.path.join(directory, start_dir, name.strip())
                    for name in f.readlines()
                ]
            else:
                files = [
                    os.path.join(directory, name.strip()) for name in f.readlines()
                ]

        with open(cell_loc, "r") as f:
            for line in f.readlines()[1:]:
                (idx, g, r) = line.split(",")
                fname = files[int(idx)]
                dirname, basename = os.path.split(fname)
                saved_info.append([dirname, basename, int(g), int(r)])

    df = list_to_df(saved_info, headers=["Directory", "Filename", "Group", "Unit"])
    return df


def process_paths_from_df(df):
    """
    Turn a dataframe of cells into a SIMURAN compatible list.

    It is assumed that the dataframe is grouped by filename

    Parameters
    ----------
    df : pandas.DataFrame
        Pandas dataframe containing the information.

    Returns
    -------
    file_list : list
        The list of files to use
    cell_list : list
        A list of tuples containing for each cell the information
        (file_index, tetrode group number, unit number)
    mapping_list : list
        A list of mapping files

    """
    last_fname = ""
    curr_idx = -1
    file_list = []
    cell_list = []
    mapping_list = []

    for value in df.itertuples():
        directories = value[1 : df.columns.get_loc("Filename") + 1]
        # TODO ensure same functionality as val == val check
        vals = [val for val in directories if not pd.isna(val)]
        fname = value.Filename
        if len(vals) != 0:
            path = os.path.join(*vals, fname)
        else:
            path = fname
        if path != last_fname:
            curr_idx += 1
            last_fname = path
            file_list.append(path)
            mapping_list.append(value.Mapping)
        cell_list.append((curr_idx, value.Group, value.Unit))

    return file_list, cell_list, mapping_list


def data_convert(filename, start_dir, optional_func=None):
    """
    Convert a data file into a directory structure.

    It is assumed that the data is grouped by filename.

    Parameters
    ----------
    filename : str
        The path to the data file (excel, csv).
    start_dir : str
        The directory to start the conversion to.
    optional_func : function, optional
        An optional function to apply to the filename.

    """
    df = df_from_file(filename)

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
        # TODO ensure same functionality as val == val check
        vals = [val for val in vals if not pd.isna(val)]
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
    """
    Find the directories that match given filenames in filename.

    Parameters
    ----------
    filename : str
        The path to a data file (excel, csv) describing the filenames to search for.
        "Filename" must be a column of this excel file.
    dir_to_start : str
        The directory to start the search in
    ext : str, optional
        A file extension to look for
    re_filter : str, optional
        A regular expression to match filenames to

    Returns
    -------
    pandas.DataFrame
        The original dataframe with an added Directory column.

    """
    df = df_from_file(filename)

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
        new_df["Filename"].values,
        dir_to_start,
        ext=ext,
        re_filter=re_filter,
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
        df_to_file(new_df, out_fname)
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


def index_ephys_files(
    start_dir: Union[str, Path],
    loader: "BaseLoader",
    output_path: str = "",
    overwrite: bool = True,
    post_process_fn: Optional[Callable[[str, Any], "pd.DataFrame"]] = None,
    post_process_kwargs: Optional[dict] = None,
    loader_index_kwargs: Optional[dict] = None,
):
    """
    Create a dataframe from ephys files found in folder.

    The loader passed defines how to populate the table with information.

    Parameters
    ----------
    start_dir : str or Path
        Path to folder containing the files to index.
    loader : BaseLoader
        The loader to use for the file population.
    output_path : str, optional
        path to file to save results to if provided.
    overwrite : bool, optional
        Whether to overwrite an existing output, by default True.
    post_process_fn : function, optional
        An optional function to apply to the indexed data files.
        Should take (dataframe, **kwargs as parameters)
        If preferred, can manually post process and save the dataframe.
    post_process_kwargs : dict, optional
        Keyword arguments passed to post_process_fn.
    loader_index_kwargs : dict, optional
        Keyword arguments passed to loader.index_files()

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with all discovered files.

    """
    post_process_kwargs = {} if post_process_kwargs is None else post_process_kwargs
    loader_index_kwargs = {} if loader_index_kwargs is None else loader_index_kwargs
    if (overwrite is False) and os.path.exists(output_path):
        module_logger.warning(
            f"{output_path} exists, so loading this table - "
            + "please delete to reindex or pass overwrite as True."
        )
        return df_from_file(output_path)

    results_df = loader.index_files(start_dir, **loader_index_kwargs)

    if post_process_fn is not None:
        results_df = post_process_fn(results_df, **post_process_kwargs)

    if output_path != "":
        df_to_file(results_df, output_path)

    return results_df


def recording_container_from_file(filename, base_dir, load=False):
    """
    Create a simuran.RecordingContainer from filename.

    It is assumed that filename is in a structure like this
    parent:
        - tables/filename
        - recording_mappings/mapping_files

    Parameters
    ----------
    filename : str
        The filename to load from.
    base_dir : str
        The base directory of the recording container
    load : bool, optional
        Whether to load the data for the recording container.
        Defaults to False.

    Returns
    -------
    simuran.RecordingContainer

    """
    df = df_from_file(filename)
    param_dir = os.path.abspath(os.path.join(os.path.dirname(filename), ".."))
    rc = recording_container_from_df(df, base_dir, param_dir, load=load)
    return rc


def recording_container_from_df(df, base_dir, param_dir, load=False):
    """
    Create a Recording container from a pandas dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to load from.
    base_dir : str
        The base directory of the recording container
    param_dir : str
        A path to the directory containing parameter files
    load : bool, optional
        Whether to load the data for the recording container.
        Defaults to False.

    Returns
    -------
    simuran.RecordingContainer

    """
    needed = ["Filename", "Mapping"]
    for need in needed:
        if need not in df.columns:
            raise ValueError(f"{need} is a required column")

    has_folder = "Directory" in df.columns

    rc = RecordingContainer()

    for row in df.itertuples():
        fname = row.Filename
        if has_folder:
            dirname = row.Directory
            fname = os.path.join(dirname, fname)
        base_dir = os.path.abspath(os.path.join(param_dir, "..", "recording_mappings"))
        if row.Mapping != "NOT_EXIST":
            mapping_f = os.path.join(base_dir, row.Mapping)
            if not os.path.exists(mapping_f):
                mapping_f = os.path.join(param_dir, row.Mapping)
            if not os.path.exists(mapping_f):
                raise ValueError(f"{mapping_f} could not be found in {param_dir}")
            recording = Recording(param_file=mapping_f, base_file=fname, load=load)
            rc.append(recording)

    rc.base_dir = base_dir
    return rc


def main_analyse_cell_list(params, dirname_replacement, overwrite=False):
    if isinstance(params, dict):
        ph = ParamHandler(
            params=params,
        )
        default = "sim_results__"
    else:
        ph = ParamHandler(
            source_file=params, name="params", dirname_replacement=dirname_replacement
        )
        default = os.path.join(
            os.path.dirname(params),
            "..",
            "sim_results",
            os.path.splitext(os.path.basename(params))[0],
        )
    out_dir = ph.get("out_dir", None)
    if out_dir is None:
        out_dir = default

    cfg = parse_config()
    cfg.update(ph.get("fn_kwargs", {}))
    return analyse_cell_list(
        filename=ph["cell_list_path"],
        fn_to_use=ph["function_to_run"],
        headers=ph["headers"],
        after_fn=ph.get("after_fn", None),
        out_dir=out_dir,
        fn_args=ph.get("fn_args", []),
        fn_kwargs=cfg,
        overwrite=ph.get("overwrite", overwrite),
    )
