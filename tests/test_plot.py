import os

from simuran.plot.figure import SimuranFigure
from simuran.plot.base_plot import despine, set_plot_style, setup_ax
from matplotlib import pyplot as plt


def test_figure():
    fig, ax = plt.subplots()

    sm_fig = SimuranFigure(fig=fig, filename="test.png")
    assert not sm_fig.isdone()
    despine()
    set_plot_style()
    setup_ax(ax, {})

    sm_fig.save()
    for key, fname in sm_fig.output_filenames.items():
        assert os.path.exists(fname)
        os.remove(fname)

    sm_fig.close()
    assert len(plt.get_fignums()) == 0
