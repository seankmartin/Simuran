"""Holds a custom figure class."""
import os

import matplotlib.pyplot as plt

from simuran.plot.base_plot import save_simuran_plot


class SimuranFigure(object):
    """A custom figure class."""

    def __init__(self, figure=None, filename=None, done=False, **kwargs):
        """Holds a figure as well as a filename."""
        self.figure = figure
        self.filename = filename
        self.kwargs = kwargs
        self.done = done
        self.closed = False

    def __del__(self):
        self.close()

    def set_done(self, done):
        self.done = done

    def set_filename(self, filename):
        self.filename = filename

    def get_filename(self):
        out_format = self.kwargs.get("format", None)
        if out_format is not None:
            filename = os.path.splitext(self.filename)[0] + "." + out_format
        else:
            filename = self.filename
        return filename

    def set_figure(self, figure):
        self.figure = figure

    def set_kwargs(self, **kwargs):
        for key, val in kwargs.items():
            self.kwargs[key] = val

    def savefig(self, filename=None, **kwargs):
        if filename is None:
            filename = self.filename
        keyword_args = self.kwargs.copy()
        for key, val in kwargs.items():
            keyword_args[key] = val
        save_simuran_plot(self.figure, filename, **keyword_args)

    def save(self, filename=None, **kwargs):
        self.savefig(filename, **kwargs)

    def close(self):
        if not self.closed:
            plt.close(self.figure)
            self.closed = True

    def isdone(self):
        return self.done or self.closed
