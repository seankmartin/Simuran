"""This module hands holding spatial information."""

from simuran.base_class import BaseSimuran


class Spatial(BaseSimuran):
    """
    Hold spatial information.

    TODO
    ----
    This is a barebones implementation of the spatial information.

    """

    def __init__(self):
        """See help(Spatial)."""
        super().__init__()

    def load(self, *args, **kwargs):
        """Load the spatial information."""
        super().load()
        if not self.loaded():
            load_result = self.loader.load_spatial(self.source_file, **kwargs)
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file
