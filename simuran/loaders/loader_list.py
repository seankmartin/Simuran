"""
This lists the available loaders in SIMURAN.

Current loaders are:
1. params_only : only loads parameters from files.
2. nc_loader : requires the neurochat package to be installed.
"""
import sys
import traceback
from typing import Type

from simuran.loaders.base_loader import BaseLoader, MetadataLoader

loaders_dict: "dict[str, Type[BaseLoader]]" = {"params_only": MetadataLoader}
try:
    from simuran.loaders.nc_loader import NCLoader

    loaders_dict["neurochat"] = NCLoader
except ModuleNotFoundError:
    print("INFO: The NeuroChaT package is not installed.")
    # TODO clean this up - it is annoying

# TODO not quite the right way to check
try:
    from simuran.loaders.allen_loader import AllenOphysLoader

    loaders_dict["allen_ophys"] = AllenOphysLoader
except ModuleNotFoundError:
    print("INFO: The allensdk package is not installed.")

try:
    from simuran.loaders.nwb_loader import NWBLoader

    loaders_dict["nwb"] = NWBLoader
except ModuleNotFoundError:
    print("INFO: The pynwb module is not installed.")


def loader_from_str(value: str) -> Type["BaseLoader"]:
    """
    Loader class from string value
    
    Currently supports:
    "nwb", "neurochat", "allen_ophys"
    
    """
    data_loader_cls = loaders_dict.get(value, None)
    if data_loader_cls is None:
        raise ValueError(
            "Unrecognised loader {}, options are {}".format(
                value,
                list(loaders_dict.keys()),
            )
        )
    return data_loader_cls
