import os
import numpy as np
from copy import copy

from simuran.recording_container import RecordingContainer
from simuran.param_handler import ParamHandler
from simuran.analysis.analysis_handler import AnalysisHandler


def burst(recording, tetrode_idx, unit_num):
    unit = recording.units[tetrode_idx]
    unit.load()
    unit.underlying.set_unit_no(unit_num)
    unit.underlying.burst()
    return unit.underlying.get_results()


def my_burst(recording, tetrode_idx, unit_num):
    unit = recording.units[tetrode_idx]
    unit.load()
    unit_stamps = unit.timestamps[np.where(unit.unit_tags == unit_num)]
    isi = np.diff(unit_stamps)
    below_thresh = (isi < 0.005)
    in_burst = False
    num_bursts = 0
    for val in below_thresh:
        if val:
            if not in_burst:
                num_bursts += 2
                in_burst = True
            else:
                num_bursts += 1
        else:
            in_burst = False
    return num_bursts / len(unit_stamps)


def time_resolved_check(recording_container):
    ah = AnalysisHandler()
    for i in range(len(recording_container)):
        recording = recording_container[i]
        ah.add_fn(burst, recording, 1, 1)
        ah.add_fn(my_burst, recording, 1, 1)
        ah.run_all_fns()
        recording.results = copy(ah.results)
        ah.reset()
    attr_list = [("results", "values", 0, "Propensity to burst")]
    attr_list.append(("results", "values", 1))
    recording_container.save_summary_data(
        os.path.join(recording_container.base_dir,
                     "nc_results", "results.csv"),
        attr_list=attr_list, friendly_names=[
            "Tetrode 3 Unit 1 PtB", "My burst"])


def one_time_setup(in_dir):
    ph = ParamHandler(
        in_loc=r"E:\Repos\SIMURAN\examples\musc_params.py")
    # re_filts = ['.*\\\\(?:(?!nc).)+$',
    #             '.*\\\\(?:(?!final).)+$', '.*\\\\(?:(?!data).)+$']
    re_filts = ['^t(?:(?!\\\\nc).)+$',
                '^t(?:(?!\\\\final).)+$', '^t(?:(?!\\\\data).)+$']
    # ph.interactive_refilt(in_dir)
    ph.batch_write(
        os.path.join(in_dir), re_filters=re_filts,
        check_only=False, overwrite=True)


if __name__ == "__main__":
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR7_muscimol\2_03082018"
    # one_time_setup(in_dir)
    # ParamHandler.clear_params(os.path.join(in_dir, "t6_tmaze"))
    # exit(-1)
    rc = RecordingContainer()
    rc.auto_setup(in_dir, recursive=True)

    def sort_fn(x):
        comp = x.source_file[len(rc.base_dir + os.sep) + 1:]
        order = int(comp.split("_")[0])
        return order

    rc.sort(sort_fn, reverse=False)
    print(rc)
    time_resolved_check(rc)
