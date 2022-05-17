"""Test BaseSimuran"""

import datetime

import pytest
from simuran.base_class import BaseSimuran
from simuran.loaders.base_loader import MetadataLoader


class BaseClassToTest(BaseSimuran):
    """Needed as Base is ABC"""

    def load(self):
        super().load()
        self.loader.load_recording(self)


def test_raises_loading_exception():
    base_obj = BaseClassToTest()
    with pytest.raises(ValueError):
        base_obj.load()


def test_parameter_load():
    meta_dict = dict((["a", 1], [55, "test_str"]))
    new_dict = dict((["test / test", 551], ["test_again", [1, 1, "b"]]))

    # Make sure not load on creation
    loader = MetadataLoader()
    base_obj = BaseClassToTest(metadata=meta_dict, loader=loader)
    assert not base_obj.is_loaded()

    # Loading first time
    base_obj.load()
    assert meta_dict == base_obj.attrs

    # Faking this for now, can test properly with a real source file
    base_obj.last_loaded_source = "meta_dict"
    base_obj.source_file = "meta_dict"
    assert base_obj.is_loaded()

    # And a new loading
    base_obj.source_file = "new_dict"
    assert not base_obj.is_loaded()
    base_obj.attrs = new_dict

    base_obj.load()
    assert new_dict == base_obj.attrs
