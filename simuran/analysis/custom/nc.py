def frate(recording, tetrode_num, unit_num):
    units, _ = recording.units.group_by_property("group", tetrode_num)
    unit = units[0]
    unit.load()
    spike = unit.underlying
    spike.set_unit_no(unit_num)
    return (spike.get_unit_spikes_count() / spike.get_duration())
