import simuran

try:
    from lfp_atn_simuran.analysis.lfp_clean import LFPClean

    do_analysis = True
except ImportError:
    do_analysis = False

from neurochat.nc_utils import butter_filter


def recording_info():
    def setup_signals():
        """Set up the signals (such as eeg or lfp)."""
        # The total number of signals in the recording
        num_signals = 32

        # What brain region each signal was recorded from
        regions = ["SUB"] * 2 + ["RSC"] * 2 + ["SUB"] * 28

        # If the wires were bundled, or any other kind of grouping existed
        # If no grouping, groups = [i for i in range(num_signals)]
        groups = [0, 0, 1, 1]
        for i in range(2, 9):
            groups.append(i)
            groups.append(i)
            groups.append(i)
            groups.append(i)

        # The sampling rate in Hz of each signal
        sampling_rate = [250] * num_signals
        channel_type = ["eeg"] * num_signals

        # This just passes the information on
        output_dict = {
            "num_signals": num_signals,
            "region": regions,
            "group": groups,
            "sampling_rate": sampling_rate,
            "channel_type": channel_type,
        }

        return output_dict

    def setup_units():
        """Set up the single unit data."""
        # The number of tetrodes, probes, etc - any kind of grouping
        num_groups = 8

        # The region that each group belongs to
        regions = ["SUB"] * num_groups

        # A group number for each group, for example the tetrode number
        groups = [1, 2, 3, 4, 9, 10, 11, 12]

        output_dict = {
            "num_groups": num_groups,
            "region": regions,
            "group": groups,
        }

        return output_dict

    def setup_spatial():
        """Set up the spatial data."""
        arena_size = "default"

        output_dict = {
            "arena_size": arena_size,
        }
        return output_dict

    def setup_loader():
        """
        Set up the loader and keyword arguments for the loader.

        See also
        --------
        simuran.loaders.loader_list.py

        """
        # The type of loader to use, see simuran.loaders.loader_list.py for options
        # For now nc_loader is the most common option
        # loader = "params_only"
        loader = "nc_loader"

        # Keyword arguments to pass to the loader.
        loader_kwargs = {
            "system": "Axona",
            "pos_extension": ".txt",
        }

        output_dict = {
            "loader": loader,
            "loader_kwargs": loader_kwargs,
        }

        return output_dict

    load_params = setup_loader()

    mapping = {
        "signals": setup_signals(),
        "units": setup_units(),
        "spatial": setup_spatial(),
        "loader": load_params["loader"],
        "loader_kwargs": load_params["loader_kwargs"],
    }
    return mapping


def phase_distribution(nc_lfp, spike_times, spatial, theta_min=6, theta_max=10):
    g_data = nc_lfp.phase_dist(spike_times, fwin=(theta_min, theta_max))
    from neurochat.nc_plot import spike_phase
    import matplotlib.pyplot as plt
    figures = spike_phase(g_data)
    for i, f in enumerate(figures):
        f.savefig(f"{i}__phase.png")
        plt.close(f)
    print(nc_lfp.get_results())
    
    phases = nc_lfp.phase_at_events(spike_times, fwin=(theta_min, theta_max))
    _, positions, directions = spatial.get_event_loc(spike_times, keep_zero_idx=True)
    dim_pos = positions[1]
    plt.hist2d(dim_pos, phases, bins=[10, 180])
    plt.savefig("outphase.png")
    plt.close()
    plt.scatter(dim_pos, phases)
    plt.savefig("outscatt.png")
    return

def main(set_file_location, do_analysis=False):
    """Create a single recording for analysis."""
    recording = simuran.Recording(params=recording_info(), base_file=set_file_location)
    if not do_analysis:
        return recording

    else:
        lc_clean = LFPClean(method="avg", visualise=True, show_vis=False)
        result = lc_clean.clean(recording, min_f=None, max_f=None)
        fig = result["fig"]
        fig.savefig("LSR5_01122017_regular.png", dpi=400)

        lc_clean = LFPClean(method="zscore", visualise=True, show_vis=False)
        result = lc_clean.clean(recording, min_f=None, max_f=None)
        fig = result["fig"]
        fig.savefig("LSR5_01122017_zscore.png", dpi=400)


        # result = lc_clean.clean(recording, min_f=None, max_f=None)
        # sub_sig = result["signals"]["SUB"].to_neurochat()
        # recording.spatial.load()
        # spatial = recording.spatial.underlying

        # available_units = recording.get_available_units()
        # for group, units in available_units:
        #     if len(units) != 0:
        #         print("Using tetrode {} unit {}".format(group, units[0]))
        #         idx = recording.units.group_by_property("group", group)[1][0]
        #         spike_obj = recording.units[idx]
        #         spike_obj.load()
        #         spike_obj = spike_obj.underlying
        #         spike_obj.set_unit_no(units[0])
        #         spike_times = spike_obj.get_unit_stamp()
        #         break
        # phase_distribution(sub_sig, spike_times, spatial)


if __name__ == "__main__":
    main_set_file_location = r"D:\SubRet_recordings_imaging\LSubRet5\recording\Small sq up_small sq down\01122017\S1_small sq up\01122017_smallsqdownup_up_1_1.set"
    main(main_set_file_location, True)
