import os
import numpy as np
import csv
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
        "temp.csv", attr_list=attr_list,
        friendly_names=["Tetrode 3 Unit 1 PtB"])


def one_time_setup(in_dir):
    ph = ParamHandler(
        in_loc=r"E:\Repos\SIMURAN\examples\musc_params.py")
    re_filts = ['^t(?:(?!\\\\nc).)+$',
                '^t(?:(?!\\\\final).)+$', '^t(?:(?!\\\\data).)+$']
    ph.batch_write(
        os.path.join(in_dir), re_filters=re_filts,
        check_only=False, overwrite=True)


def test_analysis():
    in_dir = r"D:\SubRet_recordings_imaging\muscimol_data\CanCSR7_muscimol\2_03082018"
    one_time_setup(in_dir)
    ParamHandler.clear_params(os.path.join(in_dir, "t6_tmaze"))
    rc = RecordingContainer()
    rc.auto_setup(in_dir, recursive=True)

    def sort_fn(x):
        comp = x.source_file[len(rc.base_dir + os.sep) + 1:]
        order = int(comp.split("_")[0])
        return order

    rc.sort(sort_fn, reverse=False)
    time_resolved_check(rc)
    with open("temp.csv", "r") as cf:
        reader = csv.reader(cf, delimiter=",")
        cols = [row[1][:6] for row in reader][1:]
        vals = ["0.067497404",
                "0.027263875",
                "0.014662757",
                "0.011589404",
                "0.030674847",
                "0.049013748",
                "0.08045977",
                "0.065048099",
                "0.087336245",
                "0.115936695",
                "0.091756624",
                "0.073743017",
                "0.08306538",
                "0.075157516",
                "0.030627871",
                "0.081031308"
                ]
        vals = [val[:6] for val in vals]
        assert cols == vals
    os.remove("temp.csv")


if __name__ == "__main__":
    test_analysis()
