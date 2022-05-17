"""Package for multi-region analysis."""
from rich import inspect

from . import analysis, loaders, params, plot
from .analysis.analysis_handler import AnalysisHandler
from .base_container import GenericContainer
from .config_handler import parse_config, set_config_path
from .eeg import Eeg, EegArray
from .loaders.loader_list import loader_from_string, loaders_dict
from .log_handler import log, log_exception, print

# For main import differently
from .main.table import (
    analyse_cell_list,
    dir_to_table,
    index_ephys_files,
    main_analyse_cell_list,
    populate_table_directories,
    recording_container_from_df,
    recording_container_from_file,
)
from .param_handler import ParamHandler
from .plot.base_plot import despine, save_simuran_plot, set_plot_style, setup_ax
from .plot.figure import SimuranFigure
from .recording import Recording
from .recording_container import RecordingContainer

loader = loader_from_string
