from simuran.base_class import BaseSimuran


class Spatial(BaseSimuran):

    def __init__(self):
        super().__init__()

    def load(self, *args, **kwargs):
        super().load()
        load_result = self.loader.load_spatial(self.source_file, **kwargs)
        self.save_attrs(load_result)
