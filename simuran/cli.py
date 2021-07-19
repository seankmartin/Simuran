"""A command line interface into SIMURAN."""
import argparse
import os
import logging
import time
import sys

from sumatra.projects import load_project
from sumatra.programs import Executable

import simuran.main
import simuran.batch_setup
import simuran.param_handler
from skm_pyutils.py_log import setup_text_logging, get_default_log_loc

VERSION = "0.0.1"


def establish_logger(loglevel, params):
    """
    Establish a logging file
    
    Parameters
    ----------
    loglevel: string or int
        The logging level to set.
    params : object
        The parameters being used for this logger.

    Returns
    -------
    None

    """
    fname = get_default_log_loc("simuran_cli.log")
    setup_text_logging(None, loglevel, fname, append=True)

    logging.info("New run with params {}".format(params))


def main():
    """
    Start the SIMURAN command line interface.

    Raises
    ------
    ValueError
        If any command line arguments are not recognised.
    FileNotFoundError
        The path to the file describing the program behaviour is not found.
    ValueError
        If the -r flag is not present, and the -fn variable is not a valid path.

    Returns
    -------
    dict or list of dicts
        The output of running analysis from the specified configuration.

    """
    description = f"simuran version {VERSION}"
    parser = argparse.ArgumentParser(description)
    parser.add_argument(
        "batch_config_path",
        type=str,
        help="path to configuration file for program behaviour",
    )
    parser.add_argument(
        "--function_config_path",
        "-fn",
        type=str,
        default="",
        help="path to configuration file for functions to run, "
        + "must be present if -r is not flagged",
    )
    parser.add_argument(
        "--editor",
        "-e",
        type=str,
        default="nano",
        help="the text editor to use for any file changes, default is nano",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="whether to launch the batch version of SIMURAN",
    )
    parser.add_argument(
        "--check_params",
        "-c",
        action="store_true",
        help="whether to check input parameter files before running",
    )
    parser.add_argument(
        "--skip_batch_setup",
        "-s",
        action="store_true",
        help="whether to run parameter setup for the input folder",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="whether to print extra information during runtime",
    )
    parser.add_argument(
        "--grab_params",
        "-g",
        action="store_true",
        help="whether to grab all parameters from the input location",
    )
    parser.add_argument(
        "--do_cell_picker",
        "-p",
        action="store_true",
        help="whether to launch an interactive cell picker",
    )
    parser.add_argument(
        "--dummy",
        "-d",
        action="store_true",
        help="Whether to do a full run or a dummy run",
    )
    parser.add_argument(
        "--merge",
        "-m",
        action="store_true",
        help="Whether to merge files in recursive mode after running",
    )
    parser.add_argument(
        "--num_workers",
        "-n",
        type=int,
        default=1,
        help="Number of worker threads to launch, default is 1",
    )
    parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        help="Whether to overwrite existing output",
    )
    parser.add_argument(
        "--dirname",
        type=str,
        default="",
        help="Directory to replace __dirname__ by in parameter files.",
    )
    parser.add_argument(
        "--log",
        type=str,
        default="warning",
        help="Log level (e.g. debug, or warning) or the numeric value (20 is info)",
    )
    parser.add_argument(
        "--reason",
        type=str,
        default="Not specified",
        help="Reason for running this experiment",
    )

    parsed, unparsed = parser.parse_known_args()

    if os.path.isfile(parsed.batch_config_path):
        ph = simuran.param_handler.ParamHandler(
            in_loc=parsed.batch_config_path, name="params"
        )
        params = ph.params
    else:
        params = {}

    ex = Executable(path="simuran", version=VERSION, name="simuran")
    project = load_project()
    record = project.new_record(
        parameters=params,
        script_args=" ".join(sys.argv[1:]),
        reason=parsed.reason,
        executable=ex,
    )
    start_time = time.time()

    establish_logger(parsed.log, parsed)

    if parsed.dummy is True:
        parsed.skip_batch_setup = False

    if len(unparsed) > 0:
        raise ValueError("Unrecognized arguments passed {}".format(unparsed))

    if parsed.recursive:
        if not os.path.isfile(parsed.batch_config_path):
            raise FileNotFoundError("Please provide batch_config_path as a valid path")
        if not os.path.isfile(parsed.function_config_path):
            parsed.function_config_path = None

        result = simuran.batch_run(
            parsed.batch_config_path,
            function_to_use=parsed.function_config_path,
            text_editor=parsed.editor,
            check_params=parsed.check_params,
            do_batch_setup=not parsed.skip_batch_setup,
            do_cell_picker=parsed.do_cell_picker,
            verbose=parsed.verbose,
            only_check=parsed.dummy,
            merge=parsed.merge,
            num_cpus=parsed.num_workers,
            overwrite=parsed.overwrite,
            dirname=parsed.dirname,
        )
    elif parsed.grab_params:
        output_location = os.path.join(
            os.path.dirname(parsed.location),
            "simuran_params--" + os.path.basename(parsed.location),
        )
        print(
            "Copying parameters from {} to {}".format(parsed.location, output_location)
        )
        result = simuran.batch_setup.BatchSetup.copy_params(
            parsed.location, output_location
        )
    else:
        if parsed.function_config_path == "":
            raise ValueError(
                "In non recursive mode, the function configuration path must be a file"
            )
        result = simuran.run(
            parsed.batch_config_path,
            parsed.function_config_path,
            text_editor=parsed.editor,
            check_params=parsed.check_params,
            do_batch_setup=not parsed.skip_batch_setup,
            do_cell_picker=parsed.do_cell_picker,
            verbose=parsed.verbose,
            only_check=parsed.dummy,
            num_cpus=parsed.num_workers,
            dirname=parsed.dirname,
        )

    record.duration = time.time() - start_time
    record.output_data = record.datastore.find_new_data(record.timestamp)
    project.add_record(record)
    project.save()

    return result


def cli_entry():
    """The command line entry point."""
    main()
    return None


def merge_entry():
    """The merge operation entry point."""
    from simuran.main.merge import cli as merge_cli

    merge_cli()
    return None


if __name__ == "__main__":
    cli_entry()
