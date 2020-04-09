import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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


def save_simuran_plot(fig, save_location=None, name=None, **kwargs):
    if save_location is None and name is None:
        raise ValueError('save_location and name cannot be both None')

    dpi = kwargs.get('dpi', 400)
    bbox_inches = kwargs.get('bbox_inches', 'tight')
    pad_inches = kwargs.get('pad_inches', 0.1)
    verbose = kwargs.get('verbose', False)

    if verbose:
        print("Saving figure to {}".format(save_location))
    skm_pyutils.py_path.make_path_if_not_exists(save_location)
    fig.savefig(save_location, dpi=dpi,
                bbox_inches=bbox_inches, pad_inches=pad_inches)


def plot_compare_lfp(
        matrix_data, chans, save=True, save_loc=None, **kwargs):
    ch = len(chans)
    default = {
        'title': "LFP Similarity",
        'xlabel': 'LFP Channels',
        'ylabel': 'LFP Channels',
        'xticks': np.arange(0.5, ch + 0.5),
        'xticklabels': chans,
        'yticks': np.arange(0.5, ch + 0.5),
        'yticklabels': chans,
        'labelsize': 6
    }

    fig, ax = plt.subplots()
    reshaped = np.reshape(matrix_data, newshape=[ch, ch])
    sns.heatmap(reshaped, ax=ax)
    setup_ax(ax, default, **kwargs)
    # plt.gca().invert_yaxis()

    if save:
        save_loc = "lfp_comp.png" if save_loc is None else save_loc
        save_simuran_plot(fig, save_loc, **kwargs)
    return fig
