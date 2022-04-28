"""Holds a custom figure class."""
import os

import matplotlib.pyplot as plt

from simuran.plot.base_plot import save_simuran_plot
from simuran.log_handler import log


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
        self._output_filenames = {}
        self.kwargs = kwargs
        self.done = done
        self.closed = False

    def __del__(self):
        """On deletion, closes the underlying figure."""
        self.close()

    @property
    def output_filenames(self):
        """Get the filenames that will be saved to."""
        self._output_filenames = {}

        # raster image
        out_format = self.kwargs.get("format", "png")
        if out_format is not None:
            filename = os.path.splitext(self.filename)[0] + "." + out_format
            self._output_filenames["raster"] = filename

        # vector image
        out_format = self.kwargs.get("vector_format", "pdf")
        if out_format is not None:
            filename = os.path.splitext(self.filename)[0] + "." + out_format
            self._output_filenames["vector"] = filename

        return self._output_filenames

    @output_filenames.setter
    def output_filenames(self, value):
        self._output_filenames = value

    def update_kwargs(self, **kwargs):
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
            self.closed = True
            if self.figure is None:
                return
            try:
                plt.close(self.figure)
            except BaseException:
                if hasattr(self.figure, "close"):
                    self.figure.close()
                elif hasattr(self.figure, "_close"):
                    self.figure._close(None)
                else:
                    if self.filename is None:
                        log.warning("Unable to close figure")
                    else:
                        log.warning("Unable to close {}".format(self.filename))
                    self.closed = False

    def isdone(self):
        """Return if this figure is ready for saving."""
        return self.done or self.closed
