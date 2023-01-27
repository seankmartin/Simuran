from collections import OrderedDict

def filter_good_one_units(recording):
    # TODO also need to verify this filtering
    # TODO may be possible to compute our own to match allen
    results = {}
    for k, v in recording.data.items():
        if not k.startswith("probe"):
            continue
        unit_table = v[1]
        conditions = (
            (unit_table["presence_ratio"] > 0.9)
            & (unit_table["contamination"] < 0.4)
            & (unit_table["noise_cutoff"] < 25)
            & (unit_table["amp_median"] > 40 * 10**-6)
        )
        results[k] = unit_table.loc[conditions]
    return results

def create_spike_train_one(recording, good_unit_dict=None):
    results = {}
    for k, v in recording.data.items():
        if not k.startswith("probe"):
            continue

        spikes, clusters_df = v
        spike_train = OrderedDict()
        if good_unit_dict is None:
            index = clusters_df.index
        else:
            if isinstance(good_unit_dict[k], list):
                index = good_unit_dict[k]
            else:
                index = good_unit_dict[k].index
        for val in index:
            spike_train[val] = []
        for i in range(len(spikes["depths"])):
            cluster = spikes["clusters"][i]
            if cluster in spike_train:
                spike_train[cluster].append(spikes["times"][i])

        for k2, v2 in spike_train.items():
            spike_train[k2] = np.array(v2).reshape((1, -1))

        results[k] = spike_train

    return results