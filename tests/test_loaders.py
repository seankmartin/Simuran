from simuran.loaders.loader_list import (
    installed_loaders,
    loader_from_string,
)
from simuran.loaders.base_loader import MetadataLoader


def test_installed_loaders():
    installed = installed_loaders()
    assert "nwb" in installed
    assert "params_only" in installed
    assert "neurochat" in installed


def test_loader_from_string():
    loader = loader_from_string("params_only")
    assert isinstance(loader, MetadataLoader)
