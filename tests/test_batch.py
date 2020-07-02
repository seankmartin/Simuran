import os

import simuran.batch_setup
import simuran.param_handler
import skm_pyutils.py_path

here = os.path.dirname(os.path.abspath(__file__))


def test_batch_setup():
    in_dir = os.path.join(here, "resources", "batch_start")
    batch_setup = simuran.batch_setup.BatchSetup(
        in_dir, "simuran_b_params.py")
    dirs = batch_setup.write_batch_params()
    names = ([os.path.basename(f) for f in dirs])

    # Check if writing occurs to the correct directories.
    assert (["test_this1", "test_this_ok_thanks"] == names)

    ph = simuran.param_handler.ParamHandler(
        in_loc = os.path.join(in_dir, "simuran_b_params.py"),
        name="params")
    out_name = ph["out_basename"]
    write_files = [os.path.join(d, out_name) for d in dirs]

    read_files = simuran.batch_setup.BatchSetup.get_param_locations(
        in_dir, to_find=out_name, recursive=True)
    
    # Check if all files read are those written
    assert (read_files == write_files)


if __name__ == "__main__":
    test_batch_setup()
