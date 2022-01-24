"""
This lists the available loaders in SIMURAN.

Current loaders are:
1. params_only : only loads parameters from files.
2. nc_loader : requires the neurochat package to be installed.
"""
import sys
import traceback

loaders_dict = {"params_only": "params_only_no_cls"}
try:
    from simuran.loaders.nc_loader import NCLoader

    loaders_dict["nc_loader"] = NCLoader
    loaders_dict["neurochat"] = NCLoader
except ModuleNotFoundError:
    print("INFO: The NeuroChaT package is not installed.")
