"""
This lists the available loaders in SIMURAN.

Current loaders are:
1. params_only : only loads parameters from files.
2. nc_loader : requires the neurochat package to be installed.
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


def load_params_only():
    from simuran.loaders.base_loader import MetadataLoader

    return MetadataLoader


def load_neurochat():
    try:
        from simuran.loaders.nc_loader import NCLoader

        return NCLoader
    except ModuleNotFoundError:
        module_logger.warning("The NeuroChaT package is not installed.")


def load_allen_ophys():
    try:
        from simuran.loaders.allen_loader import AllenOphysLoader

        return AllenOphysLoader
    except ModuleNotFoundError:
        module_logger.warning("The allensdk package is not installed.")


def load_nwb():
    try:
        from simuran.loaders.nwb_loader import NWBLoader

        return NWBLoader
    except ModuleNotFoundError:
        module_logger.warning("The pynwb module is not installed.")


def supported_loaders():
    return [NWB_NAME, ALLEN_NAME, NEUROCHAT_NAME, BASE_NAME]


def installed_loaders():
    installed = []
    for val in supported_loaders():
        loader = find_loader_class(val)
        if loader is not None:
            installed.append(val)
    return installed_loaders


def options_dict():
    return {
        NWB_NAME: load_nwb,
        ALLEN_NAME: load_allen_ophys,
        NEUROCHAT_NAME: load_neurochat,
        BASE_NAME: load_params_only,
    }


def loader_from_string(value: str, *args, **kwargs) -> "BaseLoader":
    """
    Loader class from string value

    Currently supports:
    "nwb", "neurochat", "allen_ophys"

    args and kwargs are passed to the loader initialiser

    """
    loader_to_use = find_loader_class(value)

    if loader_to_use is None:
        raise ValueError(f"Can't load with uninstalled loader {value}")

    return loader_to_use(*args, **kwargs)


def find_loader_class(value):
    data_loader_fn = options_dict().get(value, None)

    if data_loader_fn is None:
        raise ValueError(
            f"Unrecognised loader {value}, options are {list(options_dict().keys())}"
        )

    return data_loader_fn()
