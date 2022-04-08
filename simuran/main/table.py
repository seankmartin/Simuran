"""This module can convert directory structures into pandas and vice versa."""

import os
import pickle
from pprint import pprint
import pandas as pd

from skm_pyutils.py_path import (
    get_base_dir_to_files,
    get_all_files_in_dir,
)
from skm_pyutils.py_table import (
    list_to_df,
    df_from_file,
    df_to_file,
    df_subset_from_rows,
)
from skm_pyutils.py_log import get_default_log_loc

from simuran.log_handler import log_exception, print
from simuran.loaders.loader_list import loaders_dict
from simuran.recording import Recording
from simuran.recording_container import RecordingContainer
from simuran.analysis.analysis_handler import AnalysisHandler
from simuran.param_handler import ParamHandler
from simuran.config_handler import parse_config, get_config_path


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


def analyse_cell_list(
    filename,
    fn_to_use,
    headers,
    after_fn=None,
    out_dir=None,
    fn_args=None,
    fn_kwargs=None,
    overwrite=False,
):
    """
    Run a function on all cells listed in an excel file.

    Parameters
    ----------
    filename : str
        The path to the excel file.
    fn_to_use : function
        The function to run on all cells.
        The first argument of this function must be recording.
        The keys returned from the function used must be group_unit.
    headers : str
        The headers to use for the resulting data.
    after_fn : function, optional
        An optional function to apply to resulting data.
    out_dir : str, optional
        Where to store the output data.
    fn_args : tuple, optional
        The arguments to pass to fn_to_use.
    fn_kwargs : dict, optional
        The keyword arguments to pass to the function.
    overwrite : bool, optional
        Whether to overwrite an existing result.
        By default, False.

    Returns
    -------
    pandas.DataFrame
        Dataframe containing the results per cell.

    TODO
    ----
    Support multiprocessing.

    """
    if out_dir is None:
        out_dir = os.path.dirname(filename)
    if fn_args is None:
        fn_args = []
    if fn_kwargs is None:
        fn_kwargs = {}

    orig_df = df_from_file(filename)
    base, ext = os.path.splitext(os.path.basename(filename))
    res_name = "_" + fn_to_use.__name__ + "_results"
    out_fname = os.path.join(out_dir, base + res_name + ext)
    cfg_path = get_config_path()
    try:
        cfg_name = os.path.splitext(os.path.basename(cfg_path))[0]
    except BaseException:
        cfg_name = None
    cfg_fin = "--" + cfg_name if cfg_name is not None else ""
    pickle_name = os.path.abspath(
        os.path.join(out_dir, "..", "pickles", base + res_name + cfg_fin + "_dump.pickle")
    )
    if os.path.exists(pickle_name) and not overwrite:
        print(
            f"{pickle_name} exists already, please delete to run or pass overwrite as True"
        )
        with open(pickle_name, "rb") as f:
            df = pickle.load(f)
        if after_fn is not None:
            after_fn(df, (out_dir, os.path.basename(filename)), **fn_kwargs)
        return df

    nrows_original = len(orig_df)

    file_list, cell_list, mapping_list = process_paths_from_df(orig_df)

    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(filename), "..", "recording_mappings")
    )
    mapping_list = [os.path.join(base_dir, fname) for fname in mapping_list]

    rc = RecordingContainer()

    n_not_loaded = 0
    bad_idx = []
    log_loc = get_default_log_loc("simuran_table.log")
    for i, (fname, map_name) in enumerate(zip(file_list, mapping_list)):
        try:
            recording = Recording(param_file=map_name, base_file=fname, load=False)
        except BaseException as ex:
            n_not_loaded += 1
            log_exception(
                ex, "Unable to load recording {}".format(fname), location=log_loc,
            )
            bad_idx.append(i)
            recording = Recording()
        rc.append(recording)
    if n_not_loaded != 0:
        print(f"Unable to load {n_not_loaded} recordings")

    skipped = []
    for i, info in enumerate(cell_list):
        row_info = orig_df.iloc[i]
        file_idx, group_no, cell_no = info
        if file_idx in bad_idx:
            skipped.append(i)
            continue

        record_unit_idx = rc[file_idx].units.group_by_property("group", group_no)[1][0]
        if rc[file_idx].units[record_unit_idx].units_to_use is None:
            rc[file_idx].units[record_unit_idx].units_to_use = []
        rc[file_idx].units[record_unit_idx].units_to_use.append(cell_no)
        rc[file_idx].units[record_unit_idx].info[cell_no] = row_info

    if len(skipped) != 0:
        print(f"Unable to analyse {len(skipped)} cells due to recording problems")
    unskipped = [i for i in range(len(orig_df)) if i not in skipped]
    orig_df_subset = df_subset_from_rows(orig_df, unskipped)

    ah = AnalysisHandler()
    used_recs = []
    for i, recording in enumerate(rc):
        if i not in bad_idx:
            ah.add_fn(fn_to_use, recording, *fn_args, **fn_kwargs)
            used_recs.append(recording.source_file)
    ah.run_all_fns(pbar=True)

    if len(ah.results.items()) == 0:
        raise RuntimeError(
            f"Unable to analyse any cells, see {log_loc} for more information."
        )

    result_list = []
    last_order = -1

    for i, (key, val) in enumerate(ah.results.items()):
        if i != 0:
            order = int(key.split("_")[-1])
            if order < last_order:
                raise RuntimeError("Not evaluating in ascending order.")
            last_order = order
        fname = used_recs[i]
        dirname, basename = os.path.split(fname)
        first = []
        for result_key, result_val in val.items():
            group, unit = result_key.split("_")
            group, unit = int(group), int(unit)
            first = [dirname, basename, group, unit, *result_val]
            result_list.append(first)

    if len(headers) != len(result_list[0]):
        headers = ["Directory", "Filename", "Group", "Unit",] + headers
    df = list_to_df(in_list=result_list, headers=headers)
    nrows_new = len(df)

    if nrows_new != nrows_original:
        print("WARNING: Not all cells were correctly analysed.")
        print(f"Analysed {nrows_new} cells out of {nrows_original} cells.")
        print("Please evaluate the result with caution.")
    for name, _ in orig_df.iteritems():
        if name not in df.columns:
            df[name] = orig_df_subset[name]

    df_to_file(df, out_fname)

    os.makedirs(os.path.dirname(pickle_name), exist_ok=True)
    with open(pickle_name, "wb") as f:
        pickle.dump(df, f)

    if after_fn is not None:
        ## TODO extra info should really be a dict
        after_fn(df, (out_dir, os.path.basename(filename)), **fn_kwargs)

    return df


def index_ephys_files(
    start_dir,
    loader_name,
    out_loc=None,
    overwrite=True,
    post_process_fn=None,
    post_process_kwargs=None,
    loader_kwargs=None,
    **kwargs,
):
    """
    Create a dataframe from ephys files found in folder.

    This function recursively scan folder for Axona .set files and return
    a pandas dataframe with ['filename', 'folder', 'time', 'duration']
    columns

    TODO
    ----
    expand this to use loaders for different formats

    Parameters
    ----------
    start_dir : str
        Path to folder containing the files to index.
    loader_name : str
        The loader to use for the file population.
    out_loc : str, optional
        path to file to save results to if provided.
    overwrite : bool, optional
        Whether to overwrite an existing output, by default True.
    post_process_fn : function, optional
        An optional function to apply to the indexed data files.
        Should take (dataframe, **kwargs as parameters)
    post_process_kwargs : dict, optional
        Keyword arguments passed to post_process_fn.
    loader_kwargs : dict, optional
        Keyword arguments passed to post_process_fn.

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe with all discovered files.

    """
    if out_loc is None:
        out_loc = ""

    if (overwrite is False) and os.path.exists(out_loc):
        print(
            f"{out_loc} exists, so loading this - "
            + "please delete to reindex or pass overwrite as True."
        )
        return df_from_file(out_loc)

    if post_process_kwargs is None:
        post_process_kwargs = {}
    if loader_kwargs is None:
        loader_kwargs = {}

    data_loader_cls = loaders_dict.get(loader_name)
    if data_loader_cls is None:
        raise ValueError(
            "Unrecognised loader {}, options are {}".format(
                loader_name, list(loaders_dict.keys())
            )
        )
    data_loader = data_loader_cls(loader_kwargs)
    results_df = data_loader.index_files(start_dir, **kwargs)

    if post_process_fn is not None:
        results_df = post_process_fn(results_df, **post_process_kwargs)

    if out_loc != "":
        df_to_file(results_df, out_loc)

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
        ph = ParamHandler(params=params,)
        default = "sim_results__"
    else:
        ph = ParamHandler(
            in_loc=params, name="params", dirname_replacement=dirname_replacement
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
