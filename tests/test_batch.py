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
    assert (["test_this1", "test_this_ok_thanks"] == names)
    all_files = skm_pyutils.py_path.get_all_files_in_dir(
        in_dir, ext=".py", return_absolute=False, recursive=True)[2:]
    ph = simuran.param_handler.ParamHandler(
        in_loc=os.path.join(in_dir, "simuran_b_params.py"),
        name="params")
    assert (all_files ==
            [os.path.join(name, ph["out_basename"]) for name in names])


if __name__ == "__main__":
    test_batch_setup()
