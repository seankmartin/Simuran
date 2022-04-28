"""Package for multi-region analysis."""
from . import analysis
from . import loaders
from . import params
from . import plot

# For main import differently
from .main.batch_main import batch_run, batch_main
from .main.copy_params import copy_param_files
from .main.single_main import run, analyse_files, save_figures
from .main.table import (
    index_ephys_files,
    analyse_cell_list,
    populate_table_directories,
    recording_container_from_file,
    recording_container_from_df,
    main_analyse_cell_list,
    dir_to_table,
)

from .batch_setup import BatchSetup
from .param_handler import ParamHandler
from .recording import Recording
from .recording_container import RecordingContainer
from .eeg import Eeg, EegArray
from .single_unit import SingleUnit
from .spatial import Spatial
from .analysis.analysis_handler import AnalysisHandler
from .plot.figure import SimuranFigure
from .plot.base_plot import save_simuran_plot, setup_ax, despine, set_plot_style
from .base_container import GenericContainer
from .config_handler import parse_config, set_config_path
from .log_handler import log, print, log_exception

from .loaders.loader_list import loaders_dict, loader_from_str

loader = loader_from_str
