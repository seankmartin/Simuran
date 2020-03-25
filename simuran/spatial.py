from simuran.base_class import BaseSimuran


class Spatial(BaseSimuran):

    def __init__(self):
        super().__init__()

    def load(self, *args, **kwargs):
        super().load()
        if not self.loaded():
            load_result = self.loader.load_spatial(self.source_file, **kwargs)
            self.save_attrs(load_result)
            self.last_loaded_source = self.source_file
