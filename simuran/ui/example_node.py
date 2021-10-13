import dearpygui.dearpygui as dpg

from simuran.ui.node import BaseNode, NodeFactory
from simuran.analysis.custom.lfp_clean import LFPClean

class NodeWithFunction(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Node with function")
        self.node_class = BaseNode


## TODO make a converter from py files
class FileSelectNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        contents = [
            dict(
                type="TEXT",
                width=300,
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
        self.label = "Neural data source file"
        self.node_class = BaseNode

class LFPCleanNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.lfp_clean = LFPClean()

    def process(self, nodes):
        # Use set parameters
        method = self.get_value_of_label(label="Method")
        self.lfp_clean.method = method

        # Use the input data
        for key, value in self.input_attributes.items():
            if value.label == "Recording":
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



# TODO make these from custom python files.
class FunctionNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, editor_id, **kwargs):
        super().create(editor_id, **kwargs)
        lfp_clean = LFPClean()

    


def create_example_nodes():
    contents1 = [
        dict(
            type="INT",
            width=150,
            label="Sum",
            min_value=1,
            max_value=100,
        )
    ]

    attributes1 = [
        dict(
            label="Attr 1",
            attribute_type=dpg.mvNode_Attr_Input,
            shape=dpg.mvNode_PinShape_Triangle,
            category="Example",
            contents=contents1,
            tooltip="Great extra information",
        )
    ]

    node1 = NodeWithFunction(attributes=attributes1)
    node1.label = "First node with function"

    node2 = FileSelectNodeFactory()

    return [node1, node2]
