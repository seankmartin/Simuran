"""This module can copy config files between directories."""

import argparse

from simuran.batch_setup import BatchSetup


def copy_param_files(in_dir, out_dir, ext, test=True):
    """
    Copy all parameters files in the given directory to the output directory.

    Parameters
    ----------
    in_dir : str
        The directory to start in.
    out_dir : str
        The directory to copy to.
    ext : str
        The file extension to search for (no . included, e.g. png)
    test : bool, optional
        Whether to actually copy or just print what would be copied.
        By default, True, so only prints.
    
    Returns
    -------
    None

    """
    BatchSetup.copy_params(
        in_dir, out_dir, re_filter=f"*.{ext}", recursive=True, test_only=test
    )


def cli():
    """Command line interface to the copying operation."""
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
