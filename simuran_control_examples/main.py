import simuran.recording
import simuran.analysis.lfp_analysis


def setup_params():
    """This module holds default parameter values."""
    mapping = {
        "signals": {},
        "units": {},
        "loader": "nc_loader",
        "loader_kwargs": {"system": "Axona"},
        "base_fname": r"D:\Ham\Batch_3\A13_CAR-SA5\CAR-SA5_20200212\CAR-SA5_2020-02-12.set",
    }

    # Setting up the signals
    num_signals = 16
    regions = ["ACC"] * 2 + ["CLA"] * 12 + ["BLA"] * 2
    groups = []
    for i in range(int(num_signals // 2)):
        groups.append(i)
        groups.append(i)
    mapping["signals"]["num_signals"] = num_signals
    mapping["signals"]["region"] = regions
    mapping["signals"]["group"] = groups
    mapping["signals"]["sampling_rate"] = [250] * num_signals

    # Specific to NC
    eeg_chan_nums = [i + 1 for i in range(num_signals)]
    mapping["signals"]["channels"] = eeg_chan_nums

    # Setting up the tetrode data
    num_groups = 0
    regions = ["CA1"] * num_groups
    groups = [i for i in range(1, 5)] + [i for i in range(9, 13)]
    mapping["units"]["num_groups"] = num_groups
    mapping["units"]["region"] = regions
    mapping["units"]["group"] = groups

    return mapping


def main(r):
    simuran.analysis.lfp_analysis.compare_lfp(r, plot=True)
    print([s.region for s in r.signals])


if __name__ == "__main__":
    r = simuran.recording.Recording(params=setup_params(), load=True)
    main(r)
