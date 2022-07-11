"""Package for multi-region analysis."""
from rich import inspect
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from .analysis.analysis_handler import AnalysisHandler
from .core.base_container import GenericContainer
from .core.eeg import EEG, EEGArray
from .core.log_handler import log, log_exception, set_only_log_to_file
from .core.param_handler import ParamHandler
from .loaders.loader_list import loader_from_string
from .main import main_with_data, main_with_files
from .plot.base_plot import despine, save_simuran_plot, set_plot_style, setup_ax
from .plot.figure import SimuranFigure
from .recording import Recording
from .recording_container import RecordingContainer

# For main import differently
from .table import (
    dir_to_table,
    index_ephys_files,
    populate_table_directories,
    recording_container_from_df,
    recording_container_from_file,
)

loader = loader_from_string

def config_from_file(filename : Union[str, "Path"]) -> ParamHandler:
    """Return a configuration from a filename."""
    return ParamHandler(source_file=filename)
