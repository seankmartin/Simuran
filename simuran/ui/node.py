"""
Handles creating nodes in the UI.

Uses the factory method design pattern.
"""

import dearpygui.dearpygui as dpg
from rich import print

# Should probably convert to abstract

# TODO this needs to be a factory method
# And then nodes - so node factories make nodes

# TODO abstract
class BaseNode(object):
    def __init__(self, tag, **kwargs):
        self.tag = tag
        self.links = {}

    
    def add_link(self, link_id, sender, receiver):
        self.links[link_id] = (sender, receiver)

    def on_connect(self, sender, receiver):
        # Needs work for context
        sender_attr = self.get_attribute_id(sender)
        receiver_attr = self.get_attribute_id(receiver)

        if sender_attr[0]:
            print("Connected to {} as sender".format(receiver))

        if receiver_attr[0]:
            print("Connected to {} as receiver".format(sender))

    def on_disconnect(self, sender, receiver):
        # Needs work for context
        sender_attr = self.get_attribute_id(sender)
        receiver_attr = self.get_attribute_id(receiver)

        if sender_attr[0]:
            print("Disconnected from {} as sender".format(receiver))

        if receiver_attr[0]:
            print("Disconnected from {} as receiver".format(sender))

    def delete(self, link_id):
        # Needs work for context
        if link_id in self.links.keys():
            sender, receiver = self.links.pop(link_id)
            print("Deleted link {} to {}".format(sender, receiver))
            self.on_disconnect(sender, receiver)
        else:
            raise ValueError("{} is not a valid link id".format(link_id))
    
    def create(self, editor_id, attributes, contents):
        

    def get_path_to_plots(self, )

class NodeFactory(object):
    def __init__(self, **kwargs):
        self.label = kwargs.get("label", "Custom name")
        self.debug = kwargs.get("debug", False)
        self.attributes = kwargs.get("attributes", [])

        # Keep track of the ID of created items
        self.created_nodes = []

    def get_attribute_id(self, id_):
        for i, attribute in enumerate(self.stored_attrs):
            if id_ == attribute.get("tag", None):
                return True, attribute, i
        return False, None, None

    def create(self, editor_id, **kwargs):
        position = kwargs.get("position", [])

        node_tag = kwargs.get("tag", dpg.generate_uuid())
        self.created_nodes.append(node_tag)

        if self.debug:
            print(self)
        dpg.add_node(
            label=self.label,
            parent=editor_id,
            show=True,
            pos=position,
            tag=node_tag,
            use_internal_label=self.debug,
        )
        for attribute in self.attributes:
            attribute_tag = dpg.generate_uuid()
            self.created_attributes.append(attribute_tag)
            contents = attribute.pop("contents", [])
            dpg.add_node_attribute(
                parent=node_tag,
                tag=attribute_tag,
                use_internal_label=self.debug,
                **attribute,
            )
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
                else:
                    raise ValueError(
                        "Unsupported content type {}, options are {}".format(type_),
                        ("INT", "FLOAT", "TEXT"),
                    )
                content["type"] = type_
                self.created_contents.append(content_tag)

        return node_tag

    def __str__(self):
        return (
            f"SIMURAN Node Factory with label {self.label},"
            + f" and attributes {self.attributes}"
        )
