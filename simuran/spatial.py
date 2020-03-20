from simuran.base_class import BaseSimuran


class Spatial(BaseSimuran):

    def __init__(self):
        super().__init__()

    def load(self, *args, **kwargs):
        super().load()
        self.underlying = self.loader.load_spatial(self.source_file, **kwargs)
