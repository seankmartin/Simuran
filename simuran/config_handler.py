"""Handles a global level configuration"""

import os

from simuran.param_handler import ParamHandler
from simuran.log_handler import log


def get_default_path(fname="config_path.txt"):
    home = os.path.expanduser("~")
    default_path = os.path.join(home, ".skm_python", fname)
    os.makedirs(os.path.dirname(default_path), exist_ok=True)
    return default_path


def set_config_path(cfg_path, fname="config_path.txt"):
    old_cfg_path = get_config_path(fname)
    if (old_cfg_path != cfg_path) and (old_cfg_path is not None):
        log.warning(
            "A new configuration has been selected -- "
            + "If another instance of SIMURAN is running "
            + "this will change that configuration"
        )

    default_path = get_default_path(fname)
    with open(default_path, "w") as f:
        if cfg_path is None:
            f.write("None")
        else:
            if os.path.exists(cfg_path):
                f.write(os.path.abspath(cfg_path))
            else:
                raise ValueError(f"{cfg_path} does not exist for config")


def get_config_path(fname="config_path.txt"):
    default_path = get_default_path(fname)
    if os.path.exists(default_path):
        with open(default_path, "r") as f:
            cfg_path = f.readline()
            if cfg_path == "None":
                cfg_path = None
    else:
        cfg_path = None
    return cfg_path


def parse_config(fname="config_path.txt"):
    cfg_path = get_config_path(fname)
    if cfg_path is None:
        log.error("Please set a config path before calling parse_cfg")
        return {}
    ph = ParamHandler(in_loc=cfg_path, name="params")
    return ph.params


def clear_config(fname="config_path.txt"):
    fpath = get_default_path(fname)
    if os.path.exists(fpath):
        os.remove(fpath)
