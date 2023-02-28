"""
Handles creating nodes in the UI.

Uses the factory method design pattern.
"""

from copy import deepcopy
import contextlib

import dearpygui.dearpygui as dpg
from rich import print


class BaseNode(object):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        self.tag = dpg.generate_uuid() if tag is None else tag
        self.label = label
        self.parent = parent
        self.attributes = {}
        self.contents = {}
        self.debug = debug
        self.category = None
        self.position = None
        self.factory_label = None
        self.internal_id = None

        self.state = {}
        self.input_attributes = {}
        self.output_attributes = {}

        self.plot_paths = None

    def on_connect(self, sender, receiver):
        sender_attr = self.get_attribute(sender)
        receiver_attr = self.get_attribute(receiver)

        if sender_attr is not None:
            self.output_attributes[f"{sender}--{receiver}"] = receiver

            if self.debug:
                print(f"{self.tag}: Connected to {receiver} as sender")

        if receiver_attr is not None:
            self.input_attributes[f"{sender}--{receiver}"] = sender

            if self.debug:
                print(f"{self.tag}: Connected to {sender} as receiver")

    def on_disconnect(self, sender, receiver):
        sender_attr = self.get_attribute(sender)
        receiver_attr = self.get_attribute(receiver)

        if sender_attr is not None:
            receiver_attr = self.output_attributes.pop(f"{sender}--{receiver}")

            if self.debug:
                print(f"{self.tag}: Disconnected from {receiver} as sender")

        if receiver_attr is not None:
            sender_attr = self.input_attributes.pop(f"{sender}--{receiver}")

            if self.debug:
                print(f"{self.tag}: Disconnected from {sender} as receiver")

    def create(self, attributes, clicked_callback, position=None):
        self.position = position
        if position is None:
            position = []
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
                    handler_tag = dpg.generate_uuid()
                    with dpg.item_handler_registry(tag=handler_tag) as handler:
                        dpg.add_item_clicked_handler(
                            button=1,
                            callback=clicked_callback,
                            user_data=["content", content["label"], self.tag],
                        )
                    dpg.bind_item_handler_registry(content_tag, handler_tag)
                else:
                    raise ValueError(
                        f'Unsupported content type {type_}, options are {("INT", "FLOAT", "TEXT")}'
                    )

                content["type"] = type_
                content["parent"] = attribute_tag
                self.contents[content_tag] = content

        # real version node.tag
        dpg.add_item_clicked_handler(
            button=1,
            callback=clicked_callback,
            user_data=["node", self.tag],
            parent="node context handler",
        )
        dpg.bind_item_handler_registry(self.tag, "node context handler")

    def process(self, nodes):
        if self.debug:
            print(f"Processing {self.tag} -- {self.label}")

    def __str__(self):
        return f"SIMURAN node with label {self.label}, tag {self.tag} and contains {[self.attribute_tags, self.content_tags]}"

    def get_values(self):
        return dpg.get_values(list(self.contents.keys()))

    def get_value_of_label(self, label):
        content_tag, _ = self.get_content_with_label(label)
        return dpg.get_value(content_tag)

    def get_content_with_label(self, label):
        return next(
            (
                (content_tag, content)
                for content_tag, content in self.contents.items()
                if label == content.get("label", "")
            ),
            (None, None),
        )

    def has_attribute(self, tag):
        return tag in self.attributes.keys()

    def get_attribute(self, tag):
        return self.attributes[tag] if tag in self.attributes.keys() else None

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
        for _, node in nodes.items():
            downstream_nodes.extend(
                node.tag
                for attribute in output_attributes
                if node.has_attribute(attribute)
            )

        return downstream_nodes

    def find_matching_input_node(self, receiver_label, nodes):
        for key, _ in self.input_attributes.items():
            sender, receiver = key.split("--")
            with contextlib.suppress(ValueError):
                sender = int(sender)
            with contextlib.suppress(ValueError):
                receiver = int(receiver)
            attr = self.get_attribute(receiver)
            if attr["label"] == receiver_label:
                source_file_tag = sender
                break

        for node in nodes.values():
            if node.has_attribute(source_file_tag):
                input_recording = node.recording
                break

        return input_recording


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
            new_node_label = f"{new_node_label} {num_nodes}"
        new_node = self.node_class(
            parent=editor_id, label=new_node_label, debug=self.debug
        )
        new_node.name = self.label
        new_node.category = self.category
        new_node.create(
            deepcopy(self.attributes), self.clicked_callback, position=position
        )
        new_node.factory_label = self.label

        self.created_nodes.append(new_node.tag)

        if self.debug:
            print(self)

        return new_node

    def __str__(self):
        return (
            f"SIMURAN Node Factory with label {self.label},"
            + f" and attributes {self.attributes}"
        )
