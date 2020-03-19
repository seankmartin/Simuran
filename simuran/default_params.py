"""This module holds default parameter values."""

mapping = {
    "signals": {}
}
num_signals = 32
regions = ["ACC"] * 2 + ["CLA"] * 28 + ["BLA"] * 2
groups = []
for i in range(16):
    groups.append(i)
    groups.append(i)
mapping["signals"]["region"] = regions
mapping["signals"]["group"] = groups
mapping["signals"]["num_signals"] = 32
