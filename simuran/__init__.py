"""
Package for multi-region analysis.

To get started, a good place can be to check the supported
data loaders, and the installed loaders:
simuran.supported_loaders(), simuran.installed_loaders()

A general flow might be something like:

recording = simuran.Recording()
recording.loader = simuran.loader("NWB")
recording.attrs["source_file"] = PATH_TO_NWB
recording.parse_metadata()
recording.load()
recording.inspect()
"""
from rich import inspect
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from .analysis.analysis_handler import AnalysisHandler
from .core.base_class import BaseSimuran, NoLoader
from .core.base_container import GenericContainer
from .core.base_signal import BaseSignal, Eeg
from .core.log_handler import log_exception, set_only_log_to_file
from .core.param_handler import ParamHandler
from .loaders.loader_list import (
    loader_from_string,
    supported_loaders,
    installed_loaders,
)
from .plot.base_plot import despine, save_simuran_plot, set_plot_style, setup_ax
from .plot.figure import SimuranFigure
from .recording import Recording
from .recording_container import RecordingContainer
from .ui.node_factories import register_node_factory
from skm_pyutils.table import df_from_file, df_to_file

loader = loader_from_string


def config_from_file(filename: Union[str, "Path"]) -> ParamHandler:
    """Return a configuration from a filename."""
    return ParamHandler(source_file=filename)


load_config = config_from_file
load_table = df_from_file
save_table = df_to_file
