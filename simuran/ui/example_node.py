import dearpygui.dearpygui as dpg

from simuran.ui.node import BaseNode, NodeFactory
from simuran.analysis.custom.lfp_clean import LFPClean
from simuran.recording import Recording

## TODO add run button, and then test

## TODO make a converter from py files
class RecordingNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Recording file")
        self.node_class = RecordingNode

        contents = [
            dict(
                type="TEXT",
                width=200,
                label="File selector",
            )
        ]

        self.attributes = [
            dict(
                label="Attr 1",
                attribute_type=dpg.mvNode_Attr_Output,
                shape=dpg.mvNode_PinShape_Triangle,
                category="File select",
                contents=contents,
                tooltip="Choose the source file by right clicking the node.",
            )
        ]


class RecordingNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.recording = Recording()

    def process(self, nodes):
        # Use set parameters
        self.param_file = self.get_value_of_label(label="File selector")

        self.recording.setup_from_file(self.param_file, load=True)


class LFPCleanNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Node with function")
        self.node_class = BaseNode

        # TODO make this match input
        contents1 = [
            dict(
                type="TEXT",
                width=100,
                label="Input recording",
                hint="SIMURAN.recording",
                readonly=True,
            )
        ]

        contents = [
            dict(
                type="TEXT",
                width=100,
                label="Clean method",
                hint="avg",
            )
        ]

        self.attributes = [
            dict(
                label="Input recording",
                attribute_type=dpg.mvNode_Attr_Input,
                shape=dpg.mvNode_PinShape_Triangle,
                category="File input",
                tooltip="Connect a source file node.",
                contents=contents1,
            ),
            dict(
                label="Clean method",
                attribute_type=dpg.mvNode_Attr_Static,
                category="Parameters",
                contents=contents,
                tooltip="Options: avg, zscore, ica"
            )
        ]
        self.label = "Neural data source file"
        self.node_class = LFPCleanNode


class LFPCleanNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.lfp_clean = LFPClean()

    def process(self, nodes):
        # Use set parameters
        method = self.get_value_of_label(label="Clean method")
        self.lfp_clean.method = method

        # Use the input data
        for key, value in self.input_attributes.items():
            if value.label == "Input recording":
                source_file_tag = key.split("--")[0]
                try:
                    source_file_tag = int(source_file_tag)
                except ValueError:
                    pass
                break

        for node in nodes:
            if node.has_attribute(source_file_tag):
                input_recording = node.recording
                break

        # TODO need to figure out method kwargs
        self.lfp_clean.clean(input_recording)


def create_example_nodes():
    node1 = LFPCleanNodeFactory()

    node2 = RecordingNodeFactory()

    return [node1, node2]
