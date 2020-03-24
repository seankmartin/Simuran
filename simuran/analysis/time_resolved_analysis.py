import os
import numpy as np
from simuran.recording import RecordingContainer
from simuran.param_handler import ParamHandler


def time_resolved_check(recording_container):
    for i in range(len(recording_container)):
        recording = recording_container[i]
        unit = recording.units[1]
        unit.load()
        unit.underlying.set_unit_no(1)
        unit.underlying.burst()
    attr_list = [("units", 1, "underlying", "_results", "Propensity to burst")]
    recording_container.save_summary_data(
        os.path.join(recording_container.base_dir,
                     "nc_results", "results.csv"),
        attr_list=attr_list, friendly_names=["Tetrode 3 Unit 1 PtB"])


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
    time_resolved_check(rc)
