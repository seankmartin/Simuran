import os

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from skm_pyutils.py_path import make_path_if_not_exists


def get_normalised_diff(s1, s2):
    # MSE of one divided by MSE of main - Normalized squared differnce
    # Symmetric
    return (
        np.sum(np.square(s1 - s2)) /
        (np.sum(np.square(s1) + np.square(s2)) / 2)
    )
    # return np.sum(np.square(s1 - s2)) / np.sum(np.square(s1))  # Non-symmetric


def compare_lfp(
        recording, out_base_dir=None, ch_to_use="all",
        save_result=True, plot=False):
    '''
    Parameters
    ----------
    recording : simuran.Recording
        Recording holding data
    out_base_dir : str, None
        Path for desired output location. Default - Saves output to folder named !LFP in base directory.
    ch: int
        Number of LFP channels in session
    '''

    # Do the actual calcualtion
    if ch_to_use == "all":
        ch_labels = recording.get_signal_channels()
    ch = [i for i in range(len(ch_labels))]

    grid = np.meshgrid(ch, ch, indexing='ij')
    stacked = np.stack(grid, 2)
    pairs = stacked.reshape(-1, 2)
    result_a = np.zeros(shape=pairs.shape[0], dtype=np.float32)

    for i, pair in enumerate(pairs):
        signal1 = recording.signals[pair[0]]
        signal2 = recording.signals[pair[1]]
        res = get_normalised_diff(
            signal1.samples, signal2.samples)
        result_a[i] = res

    # Save out a csv and do plotting
    if out_base_dir is None:
        out_base_dir = os.path.dirname(recording.source_file)
    base_name_part = recording.get_name_for_save(rel_dir=out_base_dir)
    out_base_dir = os.path.join(out_base_dir, "sim_results", "lfp")

    if save_result:
        out_name = base_name_part + "_LFP_Comp.csv"
        out_loc = os.path.join(out_base_dir, out_name)
        make_path_if_not_exists(out_loc)
        print("Saving csv to {}".format(out_loc))
        with open(out_loc, "w") as f:
            headers = [str(i) for i in ch]
            out_str = ",".join(headers)
            f.write(out_str)
            out_str = ""
            for i, (pair, val) in enumerate(zip(pairs, result_a)):
                if i % len(ch) == 0:
                    f.write(out_str + "\n")
                    out_str = ""

                out_str += "{:.2f},".format(val)
            f.write(out_str + "\n")

    if plot:
        out_name = base_name_part + "_LFP_Comp.png"
        out_loc = os.path.join(out_base_dir, "plots", out_name)
        fig = plot_compare_lfp(
            result_a, ch, ch_labels, save=True, save_loc=out_loc)
        return result_a, fig

    return result_a

# TODO create general things for plots such as titles, labels etc.
# So plot functions all set up default things, but these can be changed
# Probably a class to handle this is best
# So any plot function can take the same set of kwargs


def plot_compare_lfp(matrix_data, chans, chan_labels, save=True, save_loc=None):
    ch = len(chans)
    reshaped = np.reshape(matrix_data, newshape=[ch, ch])
    fig, ax = plt.subplots()
    sns.heatmap(reshaped, ax=ax)
    plt.xticks(np.arange(0.5, ch + 0.5), labels=chan_labels, fontsize=8)
    plt.xlabel('LFP Channels')
    plt.yticks(np.arange(0.5, ch + 0.5), labels=chan_labels, fontsize=8)
    plt.ylabel('LFP Channels')
    plt.title('Raw LFP Similarity Index')

    if save:
        save_loc = "lfp_comp.png" if save_loc is None else save_loc
        print("Saving figure to {}".format(save_loc))
        make_path_if_not_exists(save_loc)
        fig.savefig(save_loc, dpi=200,
                    bbox_inches='tight', pad_inches=0.1)
    return fig
