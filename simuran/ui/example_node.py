from simuran.ui.node import BaseNode

import dearpygui.dearpygui as dpg


class NodeWithFunction(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Node with function")


def create_example_node():
    contents = [
        dict(
            type="INT",
            width=150,
            label="Sum",
            min_value=1,
            max_value=100,
        )
    ]

    attributes = [
        dict(
            label="Attr 1",
            attribute_type=dpg.mvNode_Attr_Input,
            shape=dpg.mvNode_PinShape_Triangle,
            category="Example",
            contents=contents,
        )
    ]

    node = NodeWithFunction(attributes=attributes)

    return node
