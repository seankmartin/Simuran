"""This module can copy config files between directories."""

import argparse

from simuran.batch_setup import BatchSetup


def copy_param_files(in_dir, out_dir, ext, test=True):
    BatchSetup.copy_params(
        in_dir, out_dir, re_filter=f"*.{ext}", recursive=True, test_only=test
    )


def cli():
    description = "SIMURAN parameter copying"
    parser = argparse.ArgumentParser(description)
    parser.add_argument(
        "copy_from", type=str, help="path to directory to copy files from"
    )
    parser.add_argument("copy_to", type=str, help="path to directory to copy files to")
    parser.add_argument(
        "ext", type=str, help="the extension to copy without the . - e.g. py for python"
    )
    parser.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="if the test flag is present, just prints what would be copied",
    )

    parsed, unparsed = parser.parse_known_args()

    copy_param_files(parsed.copy_from, parsed.copy_to, parsed.ext, parsed.test)


if __name__ == "__main__":
    cli()
