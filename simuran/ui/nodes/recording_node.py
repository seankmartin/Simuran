import os

from simuran.ui.node import BaseNode, NodeFactory
from simuran.ui.node_elements import create_file_select, create_parameter, create_input
from simuran.ui.common import dict_from_string
from simuran.recording import Recording
from simuran.loaders.loader_list import loader_from_string


class RecordingNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Neural data source file")
        self.node_class = RecordingNode
        self.category = "Source"

        self.attributes = [
            create_file_select("Recording source file", output=True),
            create_parameter(
                "Recording format",
                "The format of the recording as a string. ",
            ),
            create_parameter(
                "Loader keyword arguments", "In the form of a dictionary, like {'a': 1}"
            ),
            create_parameter(
                "Recording metadata", "In the form of a dictionary, like {'a': 1}"
            ),
        ]


class RecordingNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.recording = Recording()
        self.last_loaded_param_file = None
        self.last_loaded_source_file = None
        self.param_file = None
        self.source_file = None

    def process(self, nodes):
        super().process(nodes)

        # Use set parameters
        self.source_file = self.get_value_of_label(label="Recording source file")
        self.loader = self.get_value_of_label(label="Recording format")
        if self.source_file == "":
            print("ERROR: No source file selected")
            return False

        if not os.path.isfile(self.source_file):
            print(f"Warning: Non existant source file {self.source_file} selected")
            print(f"This might be fine if the source file is an ID, or URL")
            print(f"However, if it is a path, it is likely to be a mistake")

        load_params = self.get_value_of_label(label="Loading parameters")
        self.loader_kwargs = dict_from_string(load_params)
        load_params = self.get_value_of_label(label="Recording metadata")
        self.metadata = dict_from_string(load_params)

        if (
            self.last_loaded_param_file != self.metadata
            or self.last_loaded_source_file != self.source_file
        ):
            self.load_setup()
        else:
            print(f"Already Loaded {self.source_file} with params {self.param_file}")

        return True

    def load_setup(self):
        if self.debug:
            print(f"Loading {self.source_file} with params {self.param_file}")
        self.recording.attrs.update(self.metadata)
        self.recording.attrs["source_file"] = self.source_file
        self.recording.loader = loader_from_string(self.loader, **self.loader_kwargs)
        self.recording.parse_metadata()

        self.recording.load()
        self.last_loaded_param_file = self.metadata
        self.last_loaded_source_file = self.source_file
        if self.debug:
            print(f"Loaded {self.source_file} with params {self.param_file}")


class InspectRecordingNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Inspect neural data")
        self.node_class = InspectRecordingNode
        self.category = "Processing"

        self.attributes = [
            create_input(label="Input neural data", hint="Data input"),
            create_file_select(label="Output file location", output=False),
        ]


class InspectRecordingNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)

    def process(self, nodes):
        super().process(nodes)

        # Use set parameters
        self.output_file = self.get_value_of_label(label="Output file location")
        self.input_recording_node = self.find_matching_input_node(
            reciever_label="Input neural data", nodes=nodes
        )
        recording = self.input_recording_node.recording
        recording.inspect()

        try:
            summary_info = recording.summarise()
        except NotImplementedError:
            print(
                "WARNING: the selected neural data source does not support summarising in text, please see the console instead."
            )
        with open(self.output_file, "w") as f:
            f.write(summary_info)

        return True
