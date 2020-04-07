import os
from copy import copy

import simuran.batch_setup
import simuran.recording
import simuran.analysis.analysis_handler


def main(
        location, functions, attributes_to_save, do_batch_setup=False,
        friendly_names=None, sort_container_fn=None, reverse_sort=False,
        param_name="simuran_params.py", batch_name="simuran_batch_params.py",
        verbose_batch_params=False):

    # Do batch setup if requested.
    if do_batch_setup:
        if not os.path.isdir(location):
            raise ValueError(
                "Please provide a directory, entered {}".format(location))
        batch_setup = simuran.batch_setup.BatchSetup(
            location, fname=batch_name)
        batch_setup.write_batch_params(verbose_params=verbose_batch_params)

    # Setup the recording_container
    recording_container = simuran.recording.RecordingContainer()
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

    analysis_handler = simuran.analysis.analysis_handler.AnalysisHandler()
    for i in range(len(recording_container)):
        # Load the data if it is not already loaded.
        recording = recording_container.get(i)
        # TODO get the function list to work well.
        for fn in functions:
            analysis_handler.add_fn(*fn)
        analysis_handler.run_all_fns()
        recording.results = copy(analysis_handler.results)
        analysis_handler.reset()
    out_loc = os.path.join(recording_container.base_dir,
                           "nc_results", "results.csv")
    recording_container.save_summary_data(
        out_loc, attr_list=attributes_to_save, friendly_names=friendly_names)


if __name__ == "__main__":
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR7_muscimol\2_03082018"

    # Example sorting
    def sort_fn(x):
        comp = x.source_file[len(in_dir + os.sep) + 1:]
        order = int(comp.split("_")[0])
        return order

    main(in_dir, [], [], sort_container_fn=sort_fn)
