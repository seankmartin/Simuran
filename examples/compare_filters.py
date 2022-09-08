from simuran.bridges.mne_bridge import plot_signals


def compare_filters(signals, *filters, **plot_args):
    """
    Plot a comparison of filters.

    Filters are expected to be as tuples like:
    (name, low, high, **kwargs)
    where **kwargs are passed to simuran.eeg.filter

    Returns
    -------
    matplotlib.figure.Figure
        The filtered version of the signals
    """
    ch_names = ["Original"]
    full_sigs = []
    for f in filters:
        fname, low, high, kwargs = f
        for s in signals:
            eeg = s.filter(low, high, inplace=False, **kwargs)
            ch_names.append(fname)
            full_sigs.append(eeg)
    return plot_signals(full_sigs, ch_names=ch_names, **plot_args)


def default_filt_compare(signals, low, high, **plot_args):
    """Compare a FIR filter and and IIR butter filter."""
    plot_args["title"] = plot_args.get(
        "title", f"Filter Comparison -- {signals.source_file}"
    )

    plot_args["duration"] = 5
    butter_dict = {"method": "iir"}

    filter1 = ("Default", low, high, {})
    filter2 = ("Butterworth", low, high, butter_dict)

    compare_filters(signals, filter1, filter2, **plot_args)
