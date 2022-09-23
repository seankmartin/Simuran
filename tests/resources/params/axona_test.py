"""This module holds default parameter values."""

mapping = {
    "signals": {},
    "units": {},
    "spatial": {},
    "loader": "neurochat",
    "loader_kwargs": {"system": "Axona", "pos_extension": ".txt"},
}

# Setting up the signals
num_signals = 1
regions = [
    "CA1",
]
groups = [
    1,
]
mapping["signals"]["num_signals"] = num_signals
mapping["signals"]["region"] = regions
mapping["signals"]["group"] = groups
mapping["signals"]["sampling_rate"] = [250] * num_signals

# Specific to NC
eeg_chan_nums = [i + 1 for i in range(num_signals)]
mapping["signals"]["channels"] = eeg_chan_nums


# Setting up the tetrode data
num_groups = 1
regions = ["CA1"] * num_groups
groups = [
    2,
]
mapping["units"]["num_groups"] = num_groups
mapping["units"]["region"] = regions
mapping["units"]["group"] = groups

# Setting up the spatial data
arena_size = "default"
mapping["spatial"]["arena_size"] = arena_size
