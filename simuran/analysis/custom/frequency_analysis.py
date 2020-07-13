import numpy as np


def powers(recording):
    results = {}

    # TODO a good way to do this in different regions
    sub_signals = recording.signals.group_by_property("region", "SUB")
    # Remove dead channels
    sub_signals = [s for s in sub_signals if not np.all((s.samples == 0))]
    rsc_signals = recording.signals.group_by_property("region", "RSC")
    rsc_signals = [s for s in rsc_signals if not np.all((s.samples == 0))]
    all_signals = [sub_signals, rsc_signals]
    names = ["sub", "rsc"]

    # For now, lets just take the first non dead channels
    # TODO get averaging or similar working
    for sig_list, name in zip(all_signals, names):
        if len(sig_list) > 0:
            window_sec = 2
            sig_in_use = sig_list[0]
            theta_power = sig_in_use.underlying.bandpower(
                [5, 11], window_sec=window_sec
            )
            results["{}_theta".format(name)] = theta_power
        else:
            results["{}_theta".format(name)] = np.nan

    return results
