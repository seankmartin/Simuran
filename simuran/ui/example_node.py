from simuran.ui.node import BaseNode

import dearpygui.dearpygui as dpg
from rich import print


class NodeWithFunction(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Node with function")

        print(self)


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
        )
    ]

    node1 = NodeWithFunction(attributes=attributes1, debug=True)
    node1.label = "First node with function"

    contents2 = [
        dict(
            type="TEXT",
            width=150,
            label="Say hi",
        )
    ]

    attributes2 = [
        dict(
            label="Attr 1",
            attribute_type=dpg.mvNode_Attr_Static,
            category="Example",
            contents=contents2,
        )
    ]

    node2 = NodeWithFunction(attributes=attributes2, debug=True)

    return [node1, node2]
