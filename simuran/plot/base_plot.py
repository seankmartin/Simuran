"""This module provides functions to interface with matplotlib."""

import os

import matplotlib.pyplot as plt
import seaborn as sns
import skm_pyutils.path


def setup_ax(ax, default, **kwargs):
    """
    Set up an axis object with default parameters that can be overridden.

    In this way, a function can set default for the usual things that should
    be plotted (e.g. plot axis labels), but keyword arguments can overwrite
    any of these.

    Parameters
    ----------
    ax : matplotlib.axes
        The axis object to set up.
    default : dict
        Parameters to use for setting up the axis if not overridden.
        Can contain any of the keys that can be keyword arguments

    Keyword arguments
    -----------------
    xlabel : str
        What to label the x-axis
    ylabel : str
        What to label the y-axis with
    xticks : array like
        x ticks
    xticklabels : array like
        Labels for the x- ticks
    yticks : array like
        y ticks
    yticklabels : array like
        Labels for the y- ticks
    xrotate : float
        The amount to rotate the x labels by
    yrotate : float
        The amount to rotate the y labels by
    labelsize : float
        The text size of the labels

    Returns
    -------
    None

    """
    for key, value in kwargs.items():
        default[key] = value
    ax.set_xlabel(default.get("xlabel", None))
    ax.set_ylabel(default.get("ylabel", None))
    ax.set_title(default.get("title", None))
    if "xticks" in default:
        ax.set_xticks(default.get("xticks"))
    if "xticklabels" in default:
        ax.set_xticklabels(default.get("xticklabels"))
    if "yticks" in default:
        ax.set_yticks(default.get("yticks"))
    if "yticklabels" in default:
        ax.set_yticklabels(default.get("yticklabels"))
    if "xrotate" in default:
        plt.setp(
            ax.get_xticklabels(),
            rotation=default["xrotate"],
            ha="right",
            rotation_mode="anchor",
        )
    if "yrotate" in default:
        plt.setp(
            ax.get_yticklabels(),
            rotation=default["yrotate"],
            ha="right",
            rotation_mode="anchor",
        )
    if "labelsize" in default:
        ax.tick_params(labelsize=default["labelsize"])


def save_simuran_plot(fig, save_location, **kwargs):
    """
    Save a figure using some default settings.

    By default saves both a raster image (bitmap e.g. PNG, JPG)
    and a vector image (e.g. PDF, SVG).
    This can be disabled by setting format to None for the raster
    and vector_format to none for the vector

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The figure to save
    save_location : str
        Where to save the figure to

    Keyword arguments
    -----------------
    dpi : int
        The dots per inch of the output, by default 400
    bbox_inches : str or val
        The size of the bounding box, by default "tight"
    pad_inches : str or val
        The size of the padding, by default 0.1
    verbose : bool
        Whether to print more information, by default False
    out_format : str
        The format to save the output to, by default None,
        which just uses the extension that is on save_location

    Returns
    -------
    str
        The locations saved to

    """
    dpi = kwargs.get("dpi", 400)
    bbox_inches = kwargs.get("bbox_inches", "tight")
    pad_inches = kwargs.get("pad_inches", 0.1)
    verbose = kwargs.get("verbose", False)

    # Save bitmap
    out_format = kwargs.get("format", "png")
    save_locations = []
    if out_format is not None:
        save_location = f"{os.path.splitext(save_location)[0]}.{out_format}"
        dirname, basename = os.path.split(save_location)
        final_path = os.path.join(dirname, out_format, basename)

        if verbose:
            print(f"Saving raster image to {final_path}")

        skm_pyutils.path.make_path_if_not_exists(final_path)
        fig.savefig(
            final_path, dpi=dpi, bbox_inches=bbox_inches, pad_inches=pad_inches
        )
        save_locations.append(final_path)

    # Save vector
    out_format = kwargs.get("vector_format", "pdf")
    if out_format is not None:
        save_location = f"{os.path.splitext(save_location)[0]}.{out_format}"
        dirname, basename = os.path.split(save_location)
        final_path = os.path.join(dirname, out_format, basename)

        if verbose:
            print(f"Saving vector image to {final_path}")

        skm_pyutils.path.make_path_if_not_exists(final_path)
        fig.savefig(
            final_path, dpi=dpi, bbox_inches=bbox_inches, pad_inches=pad_inches
        )
        save_locations.append(final_path)

    return save_locations


def despine():
    """Despine the current plot with trimming."""
    sns.despine(offset=0, trim=True)


def set_plot_style(palette="dark"):
    """Set the seaborn palette and style."""
    sns.set_palette(palette)
    sns.set_context(
        "paper",
        font_scale=1.4,
        rc={"lines.linewidth": 3.2},
    )
