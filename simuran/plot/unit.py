def verify_filtering(units):
    from scipy.ndimage import gaussian_filter1d

    smr.set_plot_style()
    ax = smr.setup_ax(xlabel="log$_{10}$ firing rate (spikes / s)")
    for region, value in region_dict.items():
        data = np.log10(units[units.structure_acronym.isin(value)]['firing_rate'])
        bins = np.linspace(-3, 2, 100)
        histogram, bins = np.histogram(data, bins, density=True)
        ax.plot(bins[:-1], gaussian_filter1d(histogram, 1), c=color_dict[region])
    smr.despine()
    plt.legend(region_dict.keys())
    return ax


def get_brain_regions_units(units, n=20):
    return units["structure_acronym"].value_counts()[:n].index.tolist()


color_dict = {'cortex' : '#08858C',
              'thalamus' : '#FC6B6F',
              'hippocampus' : '#7ED04B',
              'midbrain' : '#FC9DFE'}

def ccf_unit_plot(session_units_channels):
    from matplotlib import pyplot as plt

    fig = plt.figure()
    fig.set_size_inches([14, 8])
    ax = fig.add_subplot(111, projection="3d")

    def plot_probe_coords(probe_group):
        ax.scatter(
            probe_group["left_right_ccf_coordinate"],
            probe_group["anterior_posterior_ccf_coordinate"],
            -probe_group[
                "dorsal_ventral_ccf_coordinate"
            ],  # reverse the z coord so that down is into the brain
        )
        return probe_group["probe_id"].values[0]

    probe_ids = session_units_channels.groupby("probe_id").apply(plot_probe_coords)

    ax.set_zlabel("D/V")
    ax.set_xlabel("Left/Right")
    ax.set_ylabel("A/P")
    ax.legend(probe_ids)
    ax.view_init(elev=55, azim=70)