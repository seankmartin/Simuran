"""Package for multi-region analysis."""
from . import analysis
from . import loaders
from . import main
from . import params
from . import plot

from .batch_setup import BatchSetup
from .param_handler import ParamHandler
from .recording import Recording
from .recording_container import RecordingContainer
from .eeg import Eeg, EegArray
from .single_unit import SingleUnit
from .spatial import Spatial
