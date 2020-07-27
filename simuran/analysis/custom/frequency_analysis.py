import numpy as np


def powers(recording):
    results = {}

    sub_signals = recording.signals.group_by_property("region", "SUB")[0]
    # Remove dead channels
    sub_signals = [s for s in sub_signals if not np.all((s.samples == 0))]
    rsc_signals = recording.signals.group_by_property("region", "RSC")[0]
    rsc_signals = [s for s in rsc_signals if not np.all((s.samples == 0))]
    all_signals = [sub_signals, rsc_signals]
    names = ["sub", "rsc"]

    # For now, lets just take the first non dead channels
    # TODO get averaging or similar working
    for sig_list, name in zip(all_signals, names):
        results["{} delta".format(name)] = np.nan
        results["{} theta".format(name)] = np.nan
        results["{} low gamma".format(name)] = np.nan
        results["{} high gamma".format(name)] = np.nan
        results["{} total".format(name)] = np.nan

        results["{} delta rel".format(name)] = np.nan
        results["{} theta rel".format(name)] = np.nan
        results["{} low gamma rel".format(name)] = np.nan
        results["{} high gamma rel".format(name)] = np.nan

        if len(sig_list) > 0:
            window_sec = 2
            sig_in_use = sig_list[0]
            # TODO find good bands from a paper
            delta_power = sig_in_use.underlying.bandpower(
                [1.5, 4], window_sec=window_sec, band_total=True
            )
            theta_power = sig_in_use.underlying.bandpower(
                [6, 10], window_sec=window_sec, band_total=True
            )
            low_gamma_power = sig_in_use.underlying.bandpower(
                [30, 55], window_sec=window_sec, band_total=True
            )
            high_gamma_power = sig_in_use.underlying.bandpower(
                [65, 90], window_sec=window_sec, band_total=True
            )

            if not (
                delta_power["total_power"]
                == theta_power["total_power"]
                == low_gamma_power["total_power"]
                == high_gamma_power["total_power"]
            ):
                raise ValueError("Unequal total powers")

            results["{} delta".format(name)] = delta_power["bandpower"]
            results["{} theta".format(name)] = theta_power["bandpower"]
            results["{} low gamma".format(name)] = low_gamma_power["bandpower"]
            results["{} high gamma".format(name)] = high_gamma_power["bandpower"]
            results["{} total".format(name)] = delta_power["total_power"]

            results["{} delta rel".format(name)] = delta_power["relative_power"]
            results["{} theta rel".format(name)] = theta_power["relative_power"]
            results["{} low gamma rel".format(name)] = low_gamma_power["relative_power"]
            results["{} high gamma rel".format(name)] = high_gamma_power[
                "relative_power"
            ]

    return results
