import seaborn as sns
from typing import TYPE_CHECKING, List, Dict, Optional, Union
import matplotlib.pyplot as plt
from pathlib import Path

if TYPE_CHECKING:
    from pandas import DataFrame

from simuran.plot.base_plot import set_plot_style, despine
from simuran.plot.figure import SimuranFigure


def plot_unit_properties(
    units_table: "DataFrame",
    properties: List[str],
    log_scale: List[bool],
    output_directory: Union[Path, str],
    region_dict: Optional[Dict[str, str]] = None,
    structure_name: str = "structure_acronym",
    split_regions: bool = False,
):
    set_plot_style()

    def match_region(region):
        for k, v in region_dict.items():
            if region in v:
                return k
        return "Other"

    if split_regions:
        units_table["Structure"] = units_table[structure_name].apply(match_region)
    for prop, log in zip(properties, log_scale):
        fig, ax = plt.subplots()
        hue = "Structure" if split_regions else None
        sns.kdeplot(
            data=units_table, x=prop, log_scale=log, hue=hue, ax=ax, common_norm=False
        )
        despine()

        fig = SimuranFigure(fig)
        fig.save(Path(output_directory) / f"{prop}_distribution")


def get_brain_regions_units(units, n=20):
    return units["structure_acronym"].value_counts()[:n].index.tolist()


color_dict = {
    "cortex": "#08858C",
    "thalamus": "#FC6B6F",
    "hippocampus": "#7ED04B",
    "midbrain": "#FC9DFE",
}


def ccf_unit_plot(session_units_channels):
    from matplotlib import pyplot as plt

    fig = plt.figure()
    fig.set_size_inches([14, 8])
    ax = fig.add_subplot(111, projection="3d")

    def plot_probe_coords(probe_group):
        ax.scatter(
            probe_group["left_right_ccf_coordinate"],
            probe_group["anterior_posterior_ccf_coordinate"],
            -probe_group[
                "dorsal_ventral_ccf_coordinate"
            ],  # reverse the z coord so that down is into the brain
        )
        return probe_group["probe_id"].values[0]

    probe_ids = session_units_channels.groupby("probe_id").apply(plot_probe_coords)

    ax.set_zlabel("D/V")
    ax.set_xlabel("Left/Right")
    ax.set_ylabel("A/P")
    ax.legend(probe_ids)
    ax.view_init(elev=55, azim=70)
