"""This module hands holding spatial information."""
from dataclasses import dataclass

from simuran.base_class import BaseSimuran


@dataclass
class Spatial(BaseSimuran):
    """
    Hold spatial information.

    Attributes
    ----------
    timestamps : array style object
        The timestamps of the spatial sampling
    positions : tuple of array style object
        The value of the spatial at sample points.
        Stored as (x_array, y_array) in cm units
    speed : array style object
        The speed in cm / s for each time point
    direction : array style object
        The head direction in degrees.
    sampling_rate : int
        The sampling rate of the signal in Hz
    source_file : str
        The path to a source file containing the spatial data.

    """

    def __init__(self):
        """See help(Spatial)."""
        super().__init__()
        self.timestamps = None
        self.position = None
        self.sampling_rate = None
        self.speed = None
        self.direction = None
        self.source_file = "<unknown>"

    def load(self, *args, **kwargs):
        """Load the spatial information."""
        super().load()
        if not self.loaded():
            load_result = self.loader.load_spatial(self.source_file, **kwargs)
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file
