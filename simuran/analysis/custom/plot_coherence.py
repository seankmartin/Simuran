import os

import numpy as np
from scipy.signal import coherence
from scipy.signal import welch
import matplotlib.pyplot as plt
import seaborn as sns

from simuran.plot.figure import SimuranFigure


def plot_coherence(x, y, ax, fs=250, group="ATNx"):
    sns.set_style("ticks")
    sns.set_palette("colorblind")

    f, Cxy = coherence(x, y, fs, nperseg=1024)

    sns.lineplot(x=f, y=Cxy, ax=ax)
    sns.despine()

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Coherence")
    plt.ylim(0, 1)

    return np.array([f, Cxy, [group] * len(f)])


def plot_psd(x, ax, fs=250, group="ATNx"):
    f, Pxx = welch(x, fs=fs, nperseg=1024, return_onesided=True, scaling="density",)

    sns.lineplot(f, Pxx, ax=ax)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD")

    return np.array([f, Pxx, [group] * len(f)])


def plot_recording_coherence(recording, figures, base_dir):
    # TODO turn this naming into a helper function
    location = os.path.splitext(recording.source_file)[0]

    name = (
        "--".join(os.path.dirname(location)[len(base_dir + os.sep) :].split(os.sep))
        + "--"
        + os.path.basename(location)
        + "_coherence"
        + ".png"
    )

    # TODO a good way to do this in different regions
    sub_signals = recording.signals.group_by_property("region", "SUB")[0]
    # Remove dead channels
    sub_signals = [s for s in sub_signals if not np.all((s.samples == 0))]
    rsc_signals = recording.signals.group_by_property("region", "RSC")[0]
    rsc_signals = [s for s in rsc_signals if not np.all((s.samples == 0))]

    fig, ax = plt.subplots()
    result = plot_coherence(
        sub_signals[0].samples,
        rsc_signals[0].samples,
        ax,
        sub_signals[0].sampling_rate,
    )

    figures.append(SimuranFigure(fig, name, dpi=400, format="png"))

    fig, ax = plt.subplots()
    plot_psd(sub_signals[0].samples, ax, sub_signals[0].sampling_rate, group="ATNx")

    name = (
        "--".join(os.path.dirname(location)[len(base_dir + os.sep) :].split(os.sep))
        + "--"
        + os.path.basename(location)
        + "_psd_sub"
        + ".png"
    )

    figures.append(SimuranFigure(fig, name, dpi=400, format="png"))

    fig, ax = plt.subplots()
    plot_psd(rsc_signals[0].samples, ax, rsc_signals[0].sampling_rate, group="ATNx")

    name = (
        "--".join(os.path.dirname(location)[len(base_dir + os.sep) :].split(os.sep))
        + "--"
        + os.path.basename(location)
        + "_psd_rsc"
        + ".png"
    )

    figures.append(SimuranFigure(fig, name, dpi=400, format="png"))

    return result
