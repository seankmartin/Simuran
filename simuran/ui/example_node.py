from simuran.ui.node import BaseNode, NodeFactory

import dearpygui.dearpygui as dpg
from rich import print


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

    node1 = NodeWithFunction(attributes=attributes1, debug=False)
    node1.label = "First node with function"

    node2 = FileSelectNodeFactory()

    return [node1, node2]
