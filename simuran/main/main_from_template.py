"""main using old as templates"""
import logging
import site
from pathlib import Path
from typing import Optional, Union

import typer
from rich import print
from simuran.log_handler import establish_main_logger
from simuran.param_handler import ParamHandler

logger = logging.getLogger("simuran")
establish_main_logger(logger)


def main(
    data_config: Union[dict, "ParamHandler"],
    param_config: Union[dict, "ParamHandler"],
    function_config: Union[dict, "ParamHandler"],
    data_filter: Optional[Union[dict, "ParamHandler"]] = None,
    dummy: bool = False,
):
    print(data_config)
    print(param_config)
    print(function_config)
    print(data_filter)


def cli_entry(
    datatable_filepath: str,
    config_filepath: str,
    function_filepath: str,
    dummy: bool = False,
    data_filterpath: Optional[str] = None,
):
    possible_analysis_directories = [
        Path(datatable_filepath).parent.parent / "Scripts",
        Path.cwd() / "scripts",
    ]
    for site_dir in possible_analysis_directories:
        if site_dir.is_dir():
            logger.debug(f"Added {site_dir} to path")
            site.addsitedir(site_dir)

    data_params = ParamHandler(source_file=datatable_filepath, name="params")
    config_params = ParamHandler(source_file=config_filepath, name="params")
    function_params = ParamHandler(source_file=function_filepath, name="fn_params")
    data_filter = ParamHandler(source_file=data_filterpath, name="params")
    main(data_params, config_params, function_params, data_filter, dummy)


if __name__ == "__main__":
    typer.run(cli_entry)()
