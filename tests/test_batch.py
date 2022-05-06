import os

import simuran.batch_setup
import simuran.param_handler

here = os.path.dirname(os.path.abspath(__file__))


def test_batch_setup():
    in_dir = os.path.join(here, "resources", "batch_start")
    batch_setup = simuran.batch_setup.BatchSetup(in_dir, "simuran_b_params.py")
    dirs = batch_setup.write_batch_params()
    names = [os.path.basename(f) for f in dirs]

    # Check if writing occurs to the correct directories.
    assert sorted(["test_this1", "test_this_ok_thanks"]) == sorted(names)

    ph = simuran.param_handler.ParamHandler(
        source_file=os.path.join(in_dir, "simuran_b_params.py"), name="params"
    )
    out_name = ph["out_basename"]
    write_files = [os.path.join(d, out_name) for d in dirs]

    read_files = simuran.batch_setup.BatchSetup.get_param_locations(
        in_dir, to_find=out_name, recursive=True
    )

    # Check if all files read are those written
    assert sorted(read_files) == sorted(write_files)

    read_files = simuran.batch_setup.BatchSetup.get_params_matching_pattern(
        in_dir, recursive=True
    )
    name_read = [os.path.basename(f) for f in read_files]
    retrieved_files = [
        "simuran_b_params.py",
        "simuran_params_t.py",
        "simuran_params_t.py",
    ]
    assert sorted(name_read) == sorted(retrieved_files)

    read_files = simuran.batch_setup.BatchSetup.copy_params(
        in_dir, "here", recursive=True, test_only=True
    )


if __name__ == "__main__":
    test_batch_setup()
