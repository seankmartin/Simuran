"""Holds a custom figure class."""
import os

import matplotlib.pyplot as plt

from simuran.plot.base_plot import save_simuran_plot


class SimuranFigure(object):
    """
    A custom figure class that holds a figure and filename.

    It also has helper methods, and support for saving only when ready.

    Attributes
    ----------
    figure : matplotlib.figure.Figure
        The underlying figure object.
    filename : str
        The filename that the figure will be saved to.
    kwargs : dict
        Extra keyword arguments used for saving.
    done : bool
        Whether this figure is ready to save or not.
    closed : bool
        Whether the underlying mpl figure has been closed.
    """

    def __init__(self, figure=None, filename=None, done=False, **kwargs):
        """Holds a figure as well as a filename."""
        self.figure = figure
        self.filename = filename
        self.kwargs = kwargs
        self.done = done
        self.closed = False

    def __del__(self):
        """On deletion, closes the underlying figure."""
        self.close()

    def set_done(self, done):
        """Set the value of self.done."""
        self.done = done

    def set_filename(self, filename):
        """Set the value of self.filename."""
        self.filename = filename

    def get_filename(self):
        """Get the filename that will be saved to."""
        out_format = self.kwargs.get("format", None)
        if out_format is not None:
            filename = os.path.splitext(self.filename)[0] + "." + out_format
        else:
            filename = self.filename
        return filename

    def set_figure(self, figure):
        """Set the value of self.figure."""
        self.figure = figure

    def set_kwargs(self, **kwargs):
        """Update self.kwargs."""
        for key, val in kwargs.items():
            self.kwargs[key] = val

    def savefig(self, filename=None, **kwargs):
        """
        Call simuran.plot.base_plot.save_simuran_plot to save this figure.

        The underlying figure object is saved to filename,
        and any kwargs are passed to simuran.plot.base_plot.save_simuran_plot

        Parameters
        ----------
        filename : str, optional
            Overrides self.filename if passed.
        kwargs : keyword arguments
            simuran.plot.base_plot.save_simuran_plot for support kwargs
        
        Returns
        -------
        None

        """
        if filename is None:
            filename = self.filename
        keyword_args = self.kwargs.copy()
        for key, val in kwargs.items():
            keyword_args[key] = val
        save_simuran_plot(self.figure, filename, **keyword_args)

    def save(self, filename=None, **kwargs):
        """Alias for savefig."""
        self.savefig(filename, **kwargs)

    def close(self):
        """Close the underlying figure if not closed."""
        if not self.closed:
            plt.close(self.figure)
            self.closed = True

    def isdone(self):
        """Return if this figure is ready for saving."""
        return self.done or self.closed
