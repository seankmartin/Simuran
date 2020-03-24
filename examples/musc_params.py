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
regions = ["RSC"] * 2 + ["SUB"] * 30
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
mapping["signals"]["channels"] = eeg_chan_nums

# Setting up the tetrode data
num_groups = 7
regions = ["SUB"] * num_groups
groups = [i for i in range(2, 5)] + [i for i in range(9, 13)]
mapping["units"]["num_groups"] = num_groups
mapping["units"]["region"] = regions
mapping["units"]["group"] = groups

# Setting up the spatial data
arena_size = "default"
mapping["spatial"]["arena_size"] = arena_size
