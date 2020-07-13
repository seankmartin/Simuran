"""A command line interface into SIMURAN."""
import argparse
import simuran.main
import simuran.batch_setup
import os


def main():
    description = "Command line arguments"
    parser = argparse.ArgumentParser(description)
    # TODO refactor to support optional
    parser.add_argument(
        "function_config_path",
        type=str,
        help="path to configuration file for functions to run",
    )
    parser.add_argument("location", type=str, help="where to run the program")
    parser.add_argument(
        "--editor", "-e", type=str, default="nano", help="the text editor to use"
    )
    parser.add_argument(
        "--recursive", "-r", action="store_true", help="whether to run in a batch"
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
        help="whether to run batch setup for the input folder",
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
        help="whether to grab all parameters from location",
    )
    parser.add_argument(
        "--do_cell_picker",
        "-d",
        action="store_true",
        help="whether to launch an interactive cell picker",
    )

    parsed, unparsed = parser.parse_known_args()
    if len(unparsed) > 0:
        raise ValueError("Unrecognized arguments passed {}".format(unparsed))

    if parsed.recursive:
        # TODO set this up properly
        simuran.main.batch_main.main([], [])

    elif parsed.grab_params:
        output_location = os.path.join(
            os.path.dirname(parsed.location),
            "simuran_params--" + os.path.basename(parsed.location),
        )
        print(
            "Copying parameters from {} to {}".format(parsed.location, output_location)
        )
        simuran.batch_setup.BatchSetup.copy_params(parsed.location, output_location)
    else:
        # TODO probably just make one verbose option instead of many
        simuran.main.main.run(
            parsed.location,
            text_editor=parsed.editor,
            check_params=parsed.check_params,
            fn_param_loc=parsed.function_config_path,
            do_batch_setup=not parsed.skip_batch_setup,
            do_cell_picker=parsed.do_cell_picker,
            verbose_batch_params=parsed.verbose,
        )


if __name__ == "__main__":
    main()
