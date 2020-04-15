import os

import matplotlib.pyplot as plt

import skm_pyutils.py_path


def setup_ax(ax, default, **kwargs):
    for key, value in kwargs.items():
        default[key] = value
    ax.set_xlabel(default.get('xlabel', None))
    ax.set_ylabel(default.get('ylabel', None))
    ax.set_title(default.get('title', None))
    if 'xticks' in default:
        ax.set_xticks(default.get('xticks'))
    if 'xticklabels' in default:
        ax.set_xticklabels(default.get('xticklabels'))
    if 'yticks' in default:
        ax.set_yticks(default.get('yticks'))
    if 'yticklabels' in default:
        ax.set_yticklabels(default.get('yticklabels'))
    if 'xrotate' in default:
        plt.setp(
            ax.get_xticklabels(), rotation=default['xrotate'],
            ha="right", rotation_mode="anchor")
    if 'yrotate' in default:
        plt.setp(
            ax.get_yticklabels(), rotation=default['yrotate'],
            ha="right", rotation_mode="anchor")
    if 'labelsize' in default:
        ax.tick_params(labelsize=default['labelsize'])


def save_simuran_plot(fig, save_location, **kwargs):
    dpi = kwargs.get('dpi', 400)
    bbox_inches = kwargs.get('bbox_inches', 'tight')
    pad_inches = kwargs.get('pad_inches', 0.1)
    verbose = kwargs.get('verbose', False)
    out_format = kwargs.get('format', "png")

    save_location = os.path.splitext()[0] + "." + out_format

    if verbose:
        print("Saving figure to {}".format(save_location))
    skm_pyutils.py_path.make_path_if_not_exists(save_location)
    fig.savefig(save_location, dpi=dpi,
                bbox_inches=bbox_inches, pad_inches=pad_inches)
