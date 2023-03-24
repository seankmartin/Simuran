from simuran.ui.nodes.recording_node import RecordingNodeFactory, InspectRecordingFactory

def get_node_factories():
    return [
        RecordingNodeFactory,
        InspectRecordingFactory,
    ]
