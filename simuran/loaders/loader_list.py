"""
This lists the available loaders in SIMURAN.

Current loaders are:
1. params_only : only loads parameters from files.
2. nc_loader : requires the neurochat package to be installed.
"""
import sys
import traceback
from typing import Type

from simuran.loaders.base_loader import BaseLoader, ParamLoader

loaders_dict: "dict[str, Type[BaseLoader]]" = {"params_only": ParamLoader}
try:
    from simuran.loaders.nc_loader import NCLoader

    loaders_dict["nc_loader"] = NCLoader
    loaders_dict["neurochat"] = NCLoader
except ModuleNotFoundError:
    print("INFO: The NeuroChaT package is not installed.")

# TODO not quite the right way to check
try:
    from allensdk.brain_observatory.behavior.behavior_project_cache import (
        VisualBehaviorOphysProjectCache,
    )
    from simuran.loaders.allen_loader import AllenOphysLoader

    loaders_dict["allen_ophys"] = AllenOphysLoader
except ModuleNotFoundError:
    print("INFO: The allensdk package is not installed.")


def loader_from_str(value: str) -> Type["BaseLoader"]:
    data_loader_cls = loaders_dict.get(value, None)
    if data_loader_cls is None:
        raise ValueError(
            "Unrecognised loader {}, options are {}".format(
                value,
                list(loaders_dict.keys()),
            )
        )
    return data_loader_cls
