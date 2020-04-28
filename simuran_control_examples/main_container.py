import os
import numpy as np
from copy import copy

from simuran.recording_container import RecordingContainer
from simuran.param_handler import ParamHandler
from simuran.analysis.analysis_handler import AnalysisHandler
from simuran.analysis.lfp_analysis import compare_lfp


def main(rc):
    for i in range(len(rc)):
        r = rc.get(i)
        compare_lfp(r, out_base_dir=rc.base_dir, plot=True)


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
    main(rc)
