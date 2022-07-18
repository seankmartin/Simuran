"""Test BaseSimuran"""

import pytest
from simuran.core.base_class import BaseSimuran, NoLoader
from simuran.loaders.base_loader import MetadataLoader


class BaseClassToTest(BaseSimuran):
    """Needed as Base is ABC"""

    def load(self):
        super().load()
        self.loader.load_recording(self)


def create_test_obj(meta_dict):
    loader = MetadataLoader()
    return BaseClassToTest(attrs=meta_dict, loader=loader)


def test_raises_loading_exception():
    base_obj = BaseClassToTest()
    with pytest.raises(ValueError):
        base_obj.load()


def test_parameter_load():
    meta_dict = dict((["a", 1], [55, "test_str"]))
    new_dict = dict((["test / test", 551], ["test_again", [1, 1, "b"]]))
    base_obj = create_test_obj(meta_dict)
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


def test_inpsect():
    d = {"test": "banana"}
    obj = create_test_obj(d)
    attrs = obj.get_attrs()
    assert "attrs" in attrs
    attrs_and_methods = obj.get_attrs_and_methods()
    assert "get_attrs_and_methods" in attrs_and_methods


def test_no_loader():
    no_loader = NoLoader()
    no_loader.load()
    assert not no_loader.is_loaded()


if __name__ == "__main__":
    test_inpsect()
