"""main using old as templates"""
print("Starting application...")

import logging
import site
from pathlib import Path
from typing import Union

import click_spinner

with click_spinner.spinner():
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
    dummy: bool = False,
):
    print(data_config)
    print(param_config)
    print(function_config)


def cli_entry(
    data_descriptor_filepath: str,
    config_filepath: str,
    function_filepath: str,
    dummy: bool = False,
):
    possible_analysis_directories = [
        Path(data_descriptor_filepath).parent.parent / "Scripts",
        Path.cwd() / "scripts",
    ]
    for site_dir in possible_analysis_directories:
        if site_dir.is_dir():
            logger.debug(f"Added {site_dir} to path")
            site.addsitedir(site_dir)

    data_params = ParamHandler(source_file=data_descriptor_filepath, name="params")
    config_params = ParamHandler(source_file=config_filepath, name="params")
    function_params = ParamHandler(source_file=function_filepath, name="fn_params")
    main(data_params, config_params, function_params, dummy)


if __name__ == "__main__":
    typer.run(cli_entry)()
