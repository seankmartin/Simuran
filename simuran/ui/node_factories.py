from simuran.ui.nodes.recording_node import (
    RecordingNodeFactory,
    InspectRecordingNodeFactory,
)
from simuran.ui.nodes.lfp_node import LFPViewNodeFactory
from simuran.ui.nodes.python_node import PythonCodeNodeFactory

factories = [
    RecordingNodeFactory,
    InspectRecordingNodeFactory,
    LFPViewNodeFactory,
    PythonCodeNodeFactory,
]

def register_node_factory(factory):
    if factory not in factories:
        factories.append(factory)

def get_node_factories():
    return factories
