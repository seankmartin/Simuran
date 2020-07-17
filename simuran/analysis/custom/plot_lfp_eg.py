import os

import numpy as np

from bvmpc.lfp_odict import LfpODict
from bvmpc.lfp_plot import plot_lfp
from simuran.plot.figure import SimuranFigure


def get_normalised_diff(s1, s2):
    return np.sum(np.square(s1 - s2)) / (np.sum(np.square(s1) + np.square(s2)) / 2)


def main(recording, figures, base_dir):
    location = os.path.splitext(recording.source_file)[0]
    lfp_odict = LfpODict(
        location,
        filt_params=(True, 1.5, 90),
        channels=[i + 1 for i in range(len(recording.signals))],
    )
    lfp_figs = plot_lfp("", lfp_odict, filt=True, return_figs=True)
    for item in lfp_figs:
        figure, name = item
        name = (
            "--".join(os.path.dirname(location)[len(base_dir + os.sep) :].split(os.sep))
            + "--"
            + name
        )
        figures.append(SimuranFigure(figure, name, dpi=40, format="png", done=True))

    sub_signals = recording.signals.group_by_property("region", "SUB")[0]
    sub_signals = [s for s in sub_signals if not np.all((s.samples == 0))]
    rsc_signals = recording.signals.group_by_property("region", "RSC")[0]
    rsc_signals = [s for s in rsc_signals if not np.all((s.samples == 0))]

    results = {
        "sub": get_normalised_diff(sub_signals[0].samples, sub_signals[1].samples),
        "rsc": get_normalised_diff(rsc_signals[0].samples, rsc_signals[1].samples),
    }

    return results
