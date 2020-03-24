import os
import numpy as np
from simuran.recording import RecordingContainer
from simuran.param_handler import ParamHandler


def time_resolved_check(recording_container):
    pass


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
    one_time_setup(in_dir)
    rc = RecordingContainer()
    rc.auto_setup(in_dir, recursive=True)
    time_resolved_check(rc)
