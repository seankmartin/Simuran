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
        regions = ["RSC"] * 2 + ["SUB"] * 30

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


def main(set_file_location):
    """Create a single recording for analysis."""
    recording = simuran.Recording(params=recording_info(), base_file=set_file_location)
    print(recording.signals[0].get_source_file())

    result = LFPClean.clean_lfp_signals(recording, verbose=True, vis=True, append_avg=True)
    # eeg_sigs = recording.get_eeg_signals()
    # filter_ = [10, 1.5, 100, "bandpass"]
    # butter_filter(eeg_sigs[0].samples, eeg_sigs[0].sampling_rate, *filter_)
    # eeg_sigs[0].default_filt_compare(1.5, 100)


if __name__ == "__main__":
    main_set_file_location = r"D:\SubRet_recordings_imaging\LSubRet5\recording\Small sq up_small sq down\01122017\S1_small sq up\01122017_smallsqdownup_up_1_1.set"
    main(main_set_file_location)
