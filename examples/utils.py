from pathlib import Path
from urllib.parse import urljoin

import requests
from tqdm import tqdm

# TODO move to config
OUTPUT_DIR = Path(r"D:\AllenBrainObservatory\ophys_data\results")
HERE = Path(__file__).parent.absolute()
MANIFEST_VERSION = "1.0.1"
DATA_STORAGE_DIRECTORY = Path(r"D:\AllenBrainObservatory\ophys_data")


def get_behavior_ophys_experiment_url(ophys_experiment_id: int) -> str:
    hostname = "https://visual-behavior-ophys-data.s3-us-west-2.amazonaws.com/"
    object_key = f"visual-behavior-ophys/behavior_ophys_experiments/behavior_ophys_experiment_{ophys_experiment_id}.nwb"
    return urljoin(hostname, object_key)


def get_path_to_allen_ophys_nwb(experiment_id):
    fname = (
        DATA_STORAGE_DIRECTORY
        / f"visual-behavior-ophys-{MANIFEST_VERSION}"
        / "behavior_ophys_experiments"
        / f"behavior_ophys_experiment_{experiment_id}.nwb"
    )
    return fname


def manual_download(experiment_id):
    url = get_behavior_ophys_experiment_url(experiment_id)
    response = requests.get(url, stream=True)
    fname = get_path_to_allen_ophys_nwb(experiment_id)

    with open(fname, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)
