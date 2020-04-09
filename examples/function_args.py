def run(recording_container, idx):
    arguments = {}
    arguments["nc_power"] = [20]
    arguments["compare_lfp"] = [
        recording_container.base_dir, "all", False, True]
    return arguments
