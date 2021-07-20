"""Handles a global level configuration"""

import os
import logging

from simuran.param_handler import ParamHandler


def get_default_path(fname="config_path.txt"):
    home = os.path.expanduser("~")
    default_path = os.path.join(home, ".skm_python", fname)
    os.makedirs(os.path.dirname(default_path), exist_ok=True)
    return default_path


def set_config_path(cfg_path, fname="config_path.txt"):
    old_cfg_path = get_config_path(fname)
    if (old_cfg_path != cfg_path) and (old_cfg_path is not None):
        logging.warning(
            "A new configuration has been selected -- "
            + "If another instance of SIMURAN is running "
            + "this will change that configuration"
        )

    default_path = get_default_path(fname)
    with open(default_path, "w") as f:
        f.write(cfg_path)


def get_config_path(fname="config_path.txt"):
    default_path = get_default_path(fname)
    if os.path.exists(default_path):
        with open(default_path, "r") as f:
            cfg_path = f.readline()
    else:
        cfg_path = None
    return cfg_path


def parse_config(fname="config_path.txt"):
    cfg_path = get_config_path(fname)
    if cfg_path is None:
        logging.error("Please set a config path before calling parse_cfg")
    ph = ParamHandler(in_loc=cfg_path, name="params")
    return ph.params


def clear_config(fname="config_path.txt"):
    fpath = get_default_path(fname)
    if os.path.exists(fpath):
        os.remove(fpath)


if __name__ == "__main__":
    from pprint import pprint
    main_cfg_path = r"E:\Repos\lfp_atn\lfp_atn_simuran\configs\default.py"
    set_config_path(main_cfg_path)
    pprint(parse_config())
    clear_config()
