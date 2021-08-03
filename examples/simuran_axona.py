from site import addsitedir
import os
from copy import copy
import logging
from pprint import pformat

import simuran
from simuran.main.single_main import save_figures
from lfp_atn_simuran.analysis.frequency_analysis import powers

HERE = os.path.dirname(os.path.abspath(__file__))
lib_folder = os.path.abspath(os.path.join(HERE, ".."))
addsitedir(lib_folder)

from index_axona_files import clean_data

def analyse_container(rc, out_dir):
    # More simple
    for recording in rc:
        # Recording has signals, single_units, spatial

        # signals
        signals = recording.signals
        for i in range(len(signals)):
            signals[i].load()
        
        # spatial
        recording.spatial.load()

        # Do the analysis
        neurochat_spatial = recording.spatial.underlying

        for i in range(len(signals)):
            neurochat_lfp = signals[i].underlying


    # This could also be performed without SIMURAN functions
    # Just by looping over the container and grabbing what you need
    # However, you would lose some functionality such as error checking
    figures = []
    # This function should take (recording, *args, **kwargs)
    fn_to_use = powers
    fn_args = [rc.base_dir, figures]
    fn_kwargs = simuran.parse_config()
    ah = simuran.AnalysisHandler(handle_errors=True)
    os.makedirs(out_dir, exist_ok=True)
    bad_idx = []
    for i in range(len(rc)):
        try:
            recording = rc.get(i)
        except BaseException as e:
            simuran.log_exception(
                e, "Loading recording {} at {}".format(i, rc[i].source_file),
            )
            rc.invalid_recording_locations.append(rc[i].source_file)
            bad_idx.append(i)
            continue
        ah.add_fn(fn_to_use, recording, *fn_args, **fn_kwargs)
        ah.run_all_fns()
        rc[i].results = copy(ah.results)
        ah.reset()
        figure_names = []
        figures = save_figures(figures, out_dir, figure_names, set_done=True)

    bname = os.path.basename(main_out_dir)

    # Indicate what should be saved from the analysis
    # save_list = [("results", "powers")] would save everything
    base_list = ["results", "powers"]
    friendly_names = [
        "SUB delta",
        "SUB theta",
        "SUB low gamma",
        "SUB high gamma",
        "SUB total",
        "SUB delta rel",
        "SUB theta rel",
        "RSC delta",
        "RSC theta",
        "RSC low gamma",
        "RSC high gamma",
        "RSC total",
        "RSC delta rel",
        "RSC theta rel",
    ]
    save_list = [base_list + [fname] for fname in friendly_names]

    # You can name each of these outputs
    output_names = friendly_names

    # Throw away bad data (could not be loaded)
    good_idx = [i for i in range(len(rc)) if i not in bad_idx]
    new_rc = rc.subsample(idx_list=good_idx, inplace=False)

    new_rc.save_summary_data(
        os.path.join(out_dir, f"{bname}_results.csv"),
        attr_list=save_list,
        friendly_names=output_names,
    )

    if len(rc.get_invalid_locations()) > 0:
        logging.warning(
            pformat(
                "Loaded {} recordings and skipped loading from {} locations:\n {}".format(
                    len(rc),
                    len(rc.get_invalid_locations()),
                    rc.get_invalid_locations(),
                )
            )
        )

    return new_rc.get_results()


def main(folder, data_out_path, param_dir, out_dir):

    # 1. Parse all the files in the directory
    df = simuran.index_ephys_files(
        folder,
        loader_name="neurochat",
        out_loc=data_out_path,
        post_process_fn=clean_data,
        overwrite=False,
        loader_kwargs={"system": "Axona"},
    )

    # 1a. Filter out the data you want

    # 2. Process this into a recording container
    rc = simuran.recording_container_from_df(df, folder, param_dir, load=False)
    recording = rc[0]
    print(recording)
    exit(-1)

    # 3. Do analysis on this container
    results = analyse_container(rc, out_dir)

    return results


if __name__ == "__main__":
    # You can change the path to all the indexed files here
    main_out_loc = r"E:\Repos\lfp_atn\lfp_atn_simuran\cell_lists\index.csv"
    main_folder = r"D:\SubRet_recordings_imaging"
    main_param_dir = r"E:\Repos\lfp_atn\lfp_atn_simuran\recording_mappings"
    main_out_dir = r"E:\Repos\lfp_atn\lfp_atn_simuran\sim_results\power_results"

    main(main_folder, main_out_loc, main_param_dir, main_out_dir)
