import simuran.analysis.lfp_analysis


def nc_power(recording, lfp_channel):
    signal = recording.signals[lfp_channel]
    signal.load()
    lfp = signal.underlying
    result = lfp.bandpower_ratio(
        [5, 11], [1.5, 4], 4, first_name="Theta", second_name="Delta"
    )
    return lfp.get_results()


functions = [nc_power, simuran.analysis.lfp_analysis.compare_lfp]
