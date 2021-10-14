"""
Handles creating nodes in the UI.

Uses the factory method design pattern.
"""

from copy import copy

import dearpygui.dearpygui as dpg
from rich import print

# Should probably convert to abstract

# TODO this needs to be a factory method
# And then nodes - so node factories make nodes

# TODO abstract
class BaseNode(object):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        if tag is None:
            self.tag = dpg.generate_uuid()
        else:
            self.tag = tag
        self.label = label
        self.parent = parent
        self.attributes = {}
        self.contents = {}
        self.debug = debug
        self.category = None

        # TODO this should hold application state
        self.state = {}

        self.input_attributes = {}
        self.output_attributes = {}

        self.plot_paths = None

    def on_connect(self, sender, receiver):
        # Needs work for context
        sender_attr = self.get_attribute(sender)
        receiver_attr = self.get_attribute(receiver)

        if sender_attr is not None:
            self.input_attributes[f"{sender}--{receiver}"] = receiver_attr

            if self.debug:
                print("{}: Connected to {} as sender".format(self.tag, receiver))

        if receiver_attr is not None:
            self.input_attributes[f"{sender}--{receiver}"] = sender_attr

            if self.debug:
                print("{}: Connected to {} as receiver".format(self.tag, sender))

    def on_disconnect(self, sender, receiver):
        # Needs work for context
        sender_attr = self.get_attribute(sender)
        receiver_attr = self.get_attribute(receiver)

        if sender_attr is not None:
            receiver_attr = self.input_attributes.pop(f"{sender}--{receiver}")

            if self.debug:
                print("{}: Disconnected from {} as sender".format(self.tag, receiver))

        if receiver_attr is not None:
            sender_attr = self.input_attributes.pop(f"{sender}--{receiver}")

            if self.debug:
                print("{}: Disconnected from {} as receiver".format(self.tag, sender))

    def create(self, attributes, clicked_callback, tooltip=None, position=[]):
        dpg.add_node(
            label=self.label,
            parent=self.parent,
            show=True,
            pos=position,
            tag=self.tag,
            use_internal_label=self.debug,
        )

        for attribute in attributes:
            attribute_tag = dpg.generate_uuid()
            self.attributes[attribute_tag] = attribute
            contents = attribute.pop("contents", [])
            attribute_tooltip = attribute.pop("tooltip", None)
            dpg.add_node_attribute(
                parent=self.tag,
                tag=attribute_tag,
                use_internal_label=self.debug,
                **attribute,
            )
            if attribute_tooltip is not None:
                tooltip_tag = dpg.generate_uuid()
                with dpg.tooltip(parent=attribute_tag):
                    dpg.add_text(default_value=attribute_tooltip, tag=tooltip_tag)
                attribute["tooltip"] = attribute_tooltip
                attribute["tooltip_tag"] = tooltip_tag
            if len(contents) != 0:
                attribute["contents"] = contents

            for content in contents:
                type_ = content.pop("type", "TEXT")
                content_tag = dpg.generate_uuid()
                if type_ == "INT":
                    dpg.add_input_int(parent=attribute_tag, tag=content_tag, **content)
                elif type_ == "FLOAT":
                    dpg.add_input_float(
                        parent=attribute_tag, tag=content_tag, **content
                    )
                elif type_ == "TEXT":
                    dpg.add_input_text(parent=attribute_tag, tag=content_tag, **content)
                    # TODO perhaps a separate menu for selecting files
                    dpg.add_item_clicked_handler(
                        button=1,
                        callback=clicked_callback,
                        user_data=self.tag,
                        parent="node context handler",
                    )
                    dpg.bind_item_handler_registry(content_tag, "node context handler")
                else:
                    raise ValueError(
                        "Unsupported content type {}, options are {}".format(type_),
                        ("INT", "FLOAT", "TEXT"),
                    )
                content["type"] = type_
                content["parent"] = attribute_tag
                self.contents[content_tag] = content

        # real version node.tag
        dpg.add_item_clicked_handler(
            button=1,
            callback=clicked_callback,
            user_data=self.tag,
            parent="node context handler",
        )
        dpg.bind_item_handler_registry(self.tag, "node context handler")

    def process(self, nodes):
        if self.debug:
            print(f"Processing {self.tag} -- {self.label}")

    def __str__(self):
        return "SIMURAN node with label {}, tag {} and contains {}".format(
            self.label, self.tag, [self.attribute_tags, self.content_tags]
        )

    def get_path_to_plots(self):
        # TEMP should come from state
        plot_path = r"E:\Repos\privateCode\UI\CSR1-openfield--plots--CSR1_small sq--07092017--07092017_CSubRet1_smallsq_d3_1_power_SUB.png"

        return plot_path

    def get_values(self):
        return dpg.get_values(list(self.contents.keys()))

    def get_value_of_label(self, label):
        content_tag, _ = self.get_content_with_label(label)
        return dpg.get_value(content_tag)

    def get_content_with_label(self, label):
        for content_tag, content in self.contents.items():
            if label == content.get("label", ""):
                return content_tag, content
        return None, None

    def has_attribute(self, tag):
        return tag in self.attributes.keys()

    def get_attribute(self, tag):
        if tag in self.attributes.keys():
            return self.attributes[tag]
        else:
            return None

    def get_owning_attribute(self, content_tag):
        return self.attributes[self.contents[content_tag]["parent"]]

    def set_source_file(self, fpath, label=None):
        if label is None:
            for content_tag, content in self.contents.items():
                if content.get("label", "").startswith("File"):
                    break
        else:
            content_tag, content = self.get_content_with_label(label)
        dpg.set_value(content_tag, fpath)

        owning_attribute = self.get_owning_attribute(content_tag)
        tooltip_tag = owning_attribute["tooltip_tag"]
        dpg.set_value(tooltip_tag, fpath)

    def get_downstream_nodes(self, nodes):
        downstream_nodes = []
        output_attributes = self.output_attributes.values()
        for i, node in enumerate(nodes):
            for attribute in output_attributes:
                if node.has_attribute(attribute):
                    downstream_nodes.append(node.tag)
        return downstream_nodes




class NodeFactory(object):
    def __init__(self, **kwargs):
        self.node_class = kwargs.get("node_class", BaseNode)
        self.label = kwargs.get("label", "Custom name")
        self.category = kwargs.get("category", "default")
        self.debug = kwargs.get("debug", False)
        self.attributes = kwargs.get("attributes", [])
        self.clicked_callback = kwargs.get("clicked_callback", None)

        # Keep track of the ID of created items
        self.created_nodes = []

    def create(self, editor_id, **kwargs):
        position = kwargs.get("position", [])

        num_nodes = len(self.created_nodes)
        new_node_label = self.label
        if num_nodes > 0:
            new_node_label = new_node_label + " " + str(num_nodes)
        new_node = self.node_class(
            parent=editor_id, label=new_node_label, debug=self.debug
        )
        new_node.name = self.label
        new_node.category = self.category
        new_node.create(copy(self.attributes), self.clicked_callback, position=position)

        self.created_nodes.append(new_node.tag)

        if self.debug:
            print(self)

        return new_node

    def __str__(self):
        return (
            f"SIMURAN Node Factory with label {self.label},"
            + f" and attributes {self.attributes}"
        )
