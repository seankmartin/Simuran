"""This module holds default parameter values."""

mapping = {
    "signals": {},
    "units": {},
    "spatial": {},
    "loader": "nc_loader",
    "loader_kwargs": {"system": "Axona"}
}

# Setting up the signals
num_signals = 32
regions = ["ACC"] * 2 + ["CLA"] * 28 + ["BLA"] * 2
groups = []
for i in range(16):
    groups.append(i)
    groups.append(i)
mapping["signals"]["num_signals"] = 32
mapping["signals"]["region"] = regions
mapping["signals"]["group"] = groups
mapping["signals"]["sampling_rate"] = [250] * num_signals

# Specific to NC
eeg_chan_nums = [i + 1 for i in range(32)]


# Setting up the tetrode data
num_groups = 16
regions = ["CA1"] * num_groups
groups = [i for i in range(16)]
mapping["units"]["num_groups"] = 16
mapping["units"]["region"] = regions
mapping["units"]["group"] = groups

# Setting up the spatial data
arena_size = "default"
mapping["spatial"]["arena_size"] = arena_size
