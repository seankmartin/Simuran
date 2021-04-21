"""Package for multi-region analysis."""
from . import analysis
from . import loaders
from . import params
from . import plot

# For main import differently
from .main.batch_main import batch_run, batch_main
from .main.copy_params import copy_param_files
from .main.doit import create_task
from .main.single_main import run, analyse_files
from .main.table import index_ephys_files, analyse_cell_list, populate_table_directories

from .batch_setup import BatchSetup
from .param_handler import ParamHandler
from .recording import Recording
from .recording_container import RecordingContainer
from .eeg import Eeg, EegArray
from .single_unit import SingleUnit
from .spatial import Spatial
from .analysis.analysis_handler import AnalysisHandler
