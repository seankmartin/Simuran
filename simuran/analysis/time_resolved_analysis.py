import os
import numpy as np
from simuran.recording import RecordingContainer
from simuran.param_handler import ParamHandler


def time_resolved_check(recording_container):
    pass


if __name__ == "__main__":
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR7_muscimol\2_03082018"
    ph = ParamHandler()
    ph.set_default_params()
    # ph.batch_write(os.path.join(in_dir, ".."), check_only=True)
    ph.interactive_refilt(
        r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR7_muscimol")
    # ".*\\(?:(?!nc).)+$"
