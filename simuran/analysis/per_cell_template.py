"""This contains a template function for performing per cell stats."""
from copy import deepcopy

import numpy as np


def stat_per_cell(recording):
    """Template function for performing per cell stats."""
    # How many results expected in a row?
    NUM_RESULTS = 5

    output = {}
    # To avoid overwriting what has been set to analyse
    all_analyse = deepcopy(recording.get_set_units())

    # Unit contains probe/tetrode info, to_analyse are list of cells
    for unit, to_analyse in zip(recording.units, all_analyse):

        # Two cases for empty list of cells
        if to_analyse is None:
            continue
        if len(to_analyse) == 0:
            continue

        unit.load()
        # Loading can overwrite units_to_use, so reset these after load
        unit.units_to_use = to_analyse
        out_str_start = str(unit.group)
        no_data_loaded = unit.underlying is None
        available_units = unit.underlying.get_unit_list()

        for cell in to_analyse:
            name_for_save = out_str_start + "_" + str(cell)
            output[name_for_save] = [np.nan] * NUM_RESULTS

            # Check to see if this data is ok
            if no_data_loaded:
                continue
            if cell not in available_units:
                continue

            unit.underlying.set_unit_no(cell)
            # Do analysis on that unit
            results = np.ones(NUM_RESULTS)
            output[name_for_save] = results
            unit.underlying.reset_results()

    return output
