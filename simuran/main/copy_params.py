"""TODO update batch setup and this to match."""

import os
import shutil
import argparse

from skm_pyutils.py_path import get_all_files_in_dir


def find_param_files(in_dir):
    files = get_all_files_in_dir(
        in_dir, ext=".py", recursive=True, return_absolute=False
    )
    return files


def main(in_dir, out_dir, test=True):
    files = find_param_files(in_dir)
    last_dir = os.path.basename(in_dir)

    for f in files:
        abs_loc = os.path.join(in_dir, f)
        out_loc = os.path.join(out_dir, last_dir, f)
        os.makedirs(os.path.dirname(out_loc), exist_ok=True)
        if test:
            print(f"Would copy {abs_loc} to {out_loc}")
        else:
            shutil.copyfile(abs_loc, out_loc)


def cli():
    description = "SIMURAN parameter copying"
    parser = argparse.ArgumentParser(description)
    parser.add_argument(
        "copy_from", type=str, help="path to directory to copy .py files from"
    )
    parser.add_argument(
        "copy_to", type=str, help="path to directory to copy .py files to"
    )
    parser.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="if the test flag is present, just prints what would be copied",
    )

    parsed, unparsed = parser.parse_known_args()

    main(parsed.copy_from, parsed.copy_to, parsed.test)


if __name__ == "__main__":
    cli()
