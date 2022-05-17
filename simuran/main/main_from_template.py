"""main using old as templates"""
import logging
import re
import site
import time
from pathlib import Path
from pprint import pformat
from typing import TYPE_CHECKING, Optional, Union

import typer
from rich import print
from simuran.analysis.run_analysis import (
    run_all_analysis,
    save_figures,
    save_unclosed_figures,
    set_output_locations,
)
from simuran.loaders.base_loader import BaseLoader
from simuran.loaders.loader_list import loader_from_string
from simuran.log_handler import establish_main_logger
from simuran.param_handler import ParamHandler
from simuran.recording_container import RecordingContainer
from skm_pyutils.py_table import df_from_file, filter_table

if TYPE_CHECKING:
    from pandas import DataFrame

logger = logging.getLogger("simuran")
establish_main_logger(logger)


def update_path(base_path: str):
    possible_analysis_directories = [
        Path(base_path).parent.parent / "Scripts",
        Path.cwd() / "scripts",
    ]
    for site_dir in possible_analysis_directories:
        if site_dir.is_dir():
            logger.debug(f"Added {site_dir} to path")
            site.addsitedir(site_dir)


def wrap_up(recording_container):
    if len(recording_container.get_invalid_locations()) > 0:
        msg = pformat(
            "Loaded {} recordings and skipped loading from {} locations:\n {}".format(
                len(recording_container),
                len(recording_container.get_invalid_locations()),
                recording_container.get_invalid_locations(),
            )
        )
        logger.warning(msg)
        print("WARNING: " + msg)


def main(
    datatable: "DataFrame",
    loader: "BaseLoader",
    output_directory: "Path",
    output_name: str,
    param_config: Union[dict, "ParamHandler"],
    function_config: Union[dict, "ParamHandler"],
    dummy: bool = False,
    handle_errors: bool = False,
    num_cpus: int = 1,
):
    start_time = time.perf_counter()
    recording_container = RecordingContainer.from_table(datatable, loader)
    recording_container.attrs["base_dir"] = param_config.get("cfg_base_dir", "")

    if dummy:
        print(
            "Would run on {} and write results of {} with config {} to {}".format(
                recording_container, function_config, param_config, output_directory
            )
        )
        return

    figures = function_config.get("figures", [])
    figure_names = function_config.get("figure_names", [])
    figures = run_all_analysis(
        recording_container=recording_container,
        functions=function_config["functions"],
        args_fn=function_config.get("args_function", None),
        figures=figures,
        figure_names=figure_names,
        load_all=function_config.get("load_all", True),
        to_load=function_config.get("to_load", None),
        out_dir=output_directory,
        cfg=param_config,
        num_cpus=num_cpus,
        handle_errors=handle_errors,
    )
    recording_container.save_summary_data(
        output_directory / output_name,
        function_config["data_to_save"],
        function_config.get("data_names", None),
        decimals=function_config.get(""),
    )
    save_figures(
        figures,
        output_directory,
        figure_names=figure_names,
        verbose=False,
        set_done=True,
    )
    save_unclosed_figures(output_directory)

    results = recording_container.get_results()

    logger.info(
        "Operation completed in {:.2f}mins".format(
            (time.perf_counter() - start_time) / 60
        )
    )

    return results, recording_container


def cli_entry(
    datatable_filepath: str,
    config_filepath: str,
    function_filepath: str,
    dry_run: bool = False,
    handle_errors: bool = False,
    num_cpus: int = 1,
    data_filter: Optional[str] = None,
    output_directory: Optional[str] = None,
):
    update_path(function_filepath)
    datatable = df_from_file(datatable_filepath)
    config_params = ParamHandler(source_file=config_filepath, name="params")
    function_params = ParamHandler(source_file=function_filepath, name="params")

    data_filter = "" if data_filter is None else data_filter
    if Path(data_filter).is_file():
        data_filter = ParamHandler(source_file=data_filter, name="params")
        if "data_filter_function" in data_filter:
            datatable = data_filter["data_filter_function"](datatable)
        else:
            datatable = filter_table(datatable, data_filter)
    else:
        datatable = filter_table(datatable, dict(data_filter))

    loader_kwargs = config_params.get("loader_kwargs", {})
    if "loader" not in config_params:
        raise ValueError("Please provide a loader value in the config")
    loader = loader_from_string(config_params["loader"])(**loader_kwargs)

    od, output_name = set_output_locations(
        datatable_filepath, function_filepath, config_filepath
    )
    output_directory = output_directory if output_directory is not None else od
    main(
        datatable,
        loader,
        output_directory,
        output_name,
        config_params,
        function_params,
        dry_run,
        handle_errors,
        num_cpus,
    )


def typer_entry():
    typer.run(cli_entry)


if __name__ == "__main__":
    typer_entry()
