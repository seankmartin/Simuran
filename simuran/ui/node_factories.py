from simuran.ui.nodes.recording_node import (
    RecordingNodeFactory,
    InspectRecordingNodeFactory,
)
from simuran.ui.nodes.lfp_node import LFPViewNodeFactory
from simuran.ui.nodes.python_node import PythonCodeNodeFactory


def get_node_factories():
    return [
        RecordingNodeFactory,
        InspectRecordingNodeFactory,
        LFPViewNodeFactory,
        PythonCodeNodeFactory,
    ]
