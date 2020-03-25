from simuran.base_class import BaseSimuran


class SingleUnit(BaseSimuran):

    def __init__(self):
        super().__init__()

    def load(self, *args, **kwargs):
        super().load()
        load_result = self.loader.load_single_unit(
            self.source_file["Spike"], self.source_file["Clusters"], **kwargs)
        self.save_attrs(load_result)
