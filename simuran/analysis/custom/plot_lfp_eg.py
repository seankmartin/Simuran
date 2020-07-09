import os

from bvmpc.lfp_odict import LfpODict
from bvmpc.lfp_plot import plot_lfp
from simuran.plot.figure import SimuranFigure


def main(recording, figures, base_dir):
    location = os.path.splitext(recording.source_file)[0]
    lfp_odict = LfpODict(location, filt_params=(True, 1.5, 90))
    lfp_figs = plot_lfp("", lfp_odict, filt=True, return_figs=True)
    for item in lfp_figs:
        figure, name = item
        name = (
            "--".join(os.path.dirname(location)[len(base_dir + os.sep) :].split(os.sep))
            + "--"
            + name
        )
        figures.append(SimuranFigure(figure, name, dpi=5, format="png"))
