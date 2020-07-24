def plot_all_lfp(info, out_dir):
    import os

    import numpy as np
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    from neurochat.nc_utils import smooth_1d

    os.makedirs(out_dir, exist_ok=True)

    sns.set_style("ticks")
    sns.set_palette("colorblind")

    # TODO this should be a helper probably
    parsed_info = []
    control_data = []
    lesion_data = []
    for item in info:
        for val, _ in item:
            this_item = list(val.values())[0]
            to_use = this_item
            this_item[1][-10:] = this_item[1][-20:-10]
            to_use[1] = smooth_1d(
                this_item[1].astype(float), kernel_type="hg", kernel_size=5
            )
            if this_item[2][0] == "Control":
                control_data.append(to_use[1])
            else:
                lesion_data.append(to_use[1])
            x_data = to_use[0].astype(float)
            parsed_info.append(to_use)

    lesion_arr = np.array(lesion_data).astype(float)
    control_arr = np.array(control_data).astype(float)

    y_lesion = np.average(lesion_arr, axis=0)
    y_control = np.average(control_arr, axis=0)

    difference = y_control - y_lesion

    data = np.concatenate(parsed_info[:-1], axis=1)
    df = pd.DataFrame(data.transpose(), columns=["frequency", "coherence", "Group"])
    df.replace("Control", "Control (ATN,   N = 6)", inplace=True)
    df.replace("Lesion", "Lesion  (ATNx, N = 5)", inplace=True)
    df[["frequency", "coherence"]] = df[["frequency", "coherence"]].apply(pd.to_numeric)

    sns.lineplot(
        data=df, x="frequency", y="coherence", style="Group", hue="Group", ci=None
    )

    sns.despine()

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Coherence")

    plt.ylim(0, 0.6)

    print("Saving plots to {}".format(out_dir))
    plt.savefig(os.path.join(out_dir, "coherence.png"), dpi=400)

    plt.ylim(0, 1)

    plt.savefig(os.path.join(out_dir, "coherence_full.png"), dpi=400)

    plt.close("all")

    sns.set_style("ticks")
    sns.set_palette("colorblind")

    sns.lineplot(x=x_data, y=difference)

    sns.despine()

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Difference")

    print("Saving to {}".format((os.path.join(out_dir, "difference.pdf"))))
    plt.savefig(os.path.join(out_dir, "difference.pdf"), dpi=400)
