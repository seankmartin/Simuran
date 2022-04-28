"""Package for multi-region analysis."""
from . import analysis, loaders, params, plot
from .analysis.analysis_handler import AnalysisHandler
from .base_container import GenericContainer
from .batch_setup import BatchSetup
from .config_handler import parse_config, set_config_path
from .eeg import Eeg, EegArray
from .loaders.loader_list import loader_from_str, loaders_dict
from .log_handler import log, log_exception, print

# For main import differently
from .main.batch_main import batch_main, batch_run
from .main.copy_params import copy_param_files
from .main.single_main import analyse_files, run, save_figures
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
from .single_unit import SingleUnit
from .spatial import Spatial

loader = loader_from_str
