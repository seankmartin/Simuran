"""
This lists the available loaders in SIMURAN.
"""
NWB_NAME = "nwb"
ALLEN_NAME = "allen_ophys"
NEUROCHAT_NAME = "neurochat"
BASE_NAME = "params_only"
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from simuran.loaders.base_loader import BaseLoader

module_logger = logging.getLogger("simuran.loaders.loader_list")


def supported_loaders():
    return list(_options_dict().keys())


def installed_loaders():
    installed = []
    for val in supported_loaders():
        loader = find_loader_class(val)
        if loader is not None:
            installed.append(val)
    return installed


def loader_from_string(value: str, *args, **kwargs) -> "BaseLoader":
    """
    Loader class from string value

    Currently supports:
    "nwb", "neurochat", "allen_ophys"

    args and kwargs are passed to the loader initialiser

    """
    loader_to_use = find_loader_class(value.lower())

    if loader_to_use is None:
        raise ValueError(f"Can't load with uninstalled loader {value.lower()}")

    return loader_to_use(*args, **kwargs)


def find_loader_class(value):
    data_loader_fn = _options_dict().get(value, None)

    if data_loader_fn is None:
        raise ValueError(
            f"Unrecognised loader {value}, options are {supported_loaders()}"
        )

    return data_loader_fn()


def _params_only_loader():
    from simuran.loaders.base_loader import MetadataLoader

    return MetadataLoader


def _neurochat_loader():
    try:
        from simuran.loaders.neurochat_loader import NCLoader

        return NCLoader
    except ModuleNotFoundError:
        module_logger.warning("The NeuroChaT package is not installed.")


def _allen_ophys_loader():
    try:
        from simuran.loaders.allen_loader import AllenOphysLoader

        return AllenOphysLoader
    except ModuleNotFoundError:
        module_logger.warning("The allensdk package is not installed.")


def _nwb_loader():
    try:
        from simuran.loaders.nwb_loader import NWBLoader

        return NWBLoader
    except ModuleNotFoundError:
        module_logger.warning("The pynwb module is not installed.")


def _options_dict():
    return {
        NWB_NAME: _nwb_loader,
        ALLEN_NAME: _allen_ophys_loader,
        NEUROCHAT_NAME: _neurochat_loader,
        BASE_NAME: _params_only_loader,
    }
