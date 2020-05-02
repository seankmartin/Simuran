import neurochat.nc_plot as ncplot
import matplotlib.pyplot as plt

# TODO log these exceptions - also maybe build them into analysis handler?? Nah prob not


def frate(recording, tetrode_num, unit_num):
    try:
        units, _ = recording.units.group_by_property("group", tetrode_num)
        unit = units[0]
        unit.load()
        spike = unit.underlying
        spike.set_unit_no(unit_num)
        return (spike.get_unit_spikes_count() / spike.get_duration())
    except:
        return -1


def place_field(recording, grid_fig, tetrode_num, unit_num):
    try:
        units, _ = recording.units.group_by_property("group", tetrode_num)
        unit = units[0]
        unit.load()
        spike = unit.underlying
        spike.set_unit_no(unit_num)
        spatial = recording.spatial
        spatial.load()
        place_data = spatial.underlying.place(spike.get_unit_stamp())
        ncplot.loc_rate(place_data, ax=grid_fig.get_next())
        plt.close()
        ncplot.loc_spike(place_data, ax=grid_fig.get_next())
        plt.close()
        wave_data = spike.wave_property()
        ncplot.largest_waveform(wave_data, ax=grid_fig.get_next())
        plt.close()
    except:
        grid_fig.get_next()
        grid_fig.get_next()
        grid_fig.get_next()


def place_field_file(recording, grid_fig):
    try:
        available_units = recording.get_set_units()
        unit_num = -1
        for i, a_unit in enumerate(available_units):
            if len(a_unit) != 0:
                if unit_num != -1:
                    raise ValueError(
                        "There are two set units for {}, {}".format(
                            recording, a_unit))
                unit = recording.units[i]
                unit_num = a_unit[0]
        if unit_num == -1:
            print("Warning: no set units for {}".format(recording))
            return
        unit.load()
        spike = unit.underlying
        spike.set_unit_no(unit_num)
        spatial = recording.spatial
        spatial.load()
    except:
        grid_fig.get_next()
        grid_fig.get_next()
        grid_fig.get_next()
        return
    place_data = spatial.underlying.place(spike.get_unit_stamp())
    ncplot.loc_rate(place_data, ax=grid_fig.get_next())
    plt.close()
    ncplot.loc_spike(place_data, ax=grid_fig.get_next())
    plt.close()
    wave_data = spike.wave_property()
    ncplot.largest_waveform(wave_data, ax=grid_fig.get_next())
    plt.close()


def count_cells(recording):
    output = {}
    for val in [1, 2, 3, 4, 9, 10, 11, 12]:
        output[str(val)] = 0

    try:
        for unit in recording.units:
            spike = unit.underlying
            if spike is None:
                continue
            num = len(spike.get_unit_list())
            output[str(unit.group)] = num
        return output

    except Exception as e:
        print("Error on {} was {}".format(recording, e))
        return output
