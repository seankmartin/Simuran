"""This module provides support for holding single unit or spiking information."""

from simuran.base_class import BaseSimuran


class SingleUnit(BaseSimuran):
    """
    Hold information for single unit.

    Attributes
    ----------
    timestamps : array style object
        The timestamps of the data.
    unit_tags : array style object
        Lists all the tags of each unit in the data set.
    waveforms : array style object
        Lists the waveforms of each unit in the data set.
    available_units : array style object
        Lists the available units (or units that should be loaded).
    units_to_use : array style object
        Lists the units that should be analysed.

    TODO
    ----
    I'm not sure the interface to single unit is the cleanest.

    """

    def __init__(self):
        """See help(SingleUnit)."""
        super().__init__()
        self.timestamps = None
        self.unit_tags = None
        self.waveforms = None
        self.available_units = []
        self.units_to_use = None

    def load(self, *args, **kwargs):
        """Load the object."""
        super().load(*args, **kwargs)
        if not self.loaded():
            load_result = self.loader.load_single_unit(
                self.source_file["Spike"], self.source_file["Clusters"], **kwargs
            )
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file

    def get_available_units(self):
        """
        Retrieve the available units.

        Returns
        -------
        array style object
            The available units in the object.

        """
        return self.available_units
