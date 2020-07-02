from simuran.base_class import BaseSimuran


class SingleUnit(BaseSimuran):
    def __init__(self):
        super().__init__()
        self.timestamps = None
        self.unit_tags = None
        self.waveforms = None
        self.available_units = []
        self.units_to_use = []

    def load(self, *args, **kwargs):
        super().load(*args, **kwargs)
        if not self.loaded():
            load_result = self.loader.load_single_unit(
                self.source_file["Spike"], self.source_file["Clusters"], **kwargs
            )
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file

    def get_available_units(self):
        return self.available_units
