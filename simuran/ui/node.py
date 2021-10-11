"""Handles creating nodes in the UI"""

import dearpygui.dearpygui as dpg

# Should probably convert to abstract

# TODO this needs to be a factory method
class BaseNode(object):
    def __init__(self, **kwargs):
        self.label = kwargs.get("label", "Custom name")

        # TODO will need work
        self.attributes = kwargs.get(
            "attributes",
        )

        self.stored_attrs = []
        self.links = {}

        self.debug = False

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

    def get_attribute_id(self, id_):
        for i, attribute in enumerate(self.stored_attrs):
            if id_ == attribute.get("tag", None):
                return True, attribute, i
        return False, None, None

    def create(self, editor_id, **kwargs):
        position = kwargs.get("position", [])

        tag = kwargs.get("tag", dpg.generate_uuid())

        dpg.add_node(
            label=self.label,
            parent=editor_id,
            show=True,
            pos=position,
            tag=tag,
            use_internal_label=self.debug,
        )
        for attribute in self.attributes:
            attribute["parent"] = tag
            attribute["use_internal_label"] = self.debug
            attribute["tag"] = dpg.generate_uuid()
            self.stored_attrs.append(attribute["tag"])
            contents = attribute.pop("contents", [])
            dpg.add_node_attribute(**attribute)
            attribute["contents"] = contents

            for content in contents:
                content["parent"] = attribute["tag"]
                content["tag"] = dpg.generate_uuid()
                type_ = content.pop("type", "TEXT")
                if type_ == "INT":
                    dpg.add_input_int(**content)
                elif type_ == "FLOAT":
                    dpg.add_input_int(**content)
                elif type_ == "TEXT":
                    dpg.add_input_int(**content)
                else:
                    raise ValueError(
                        "Unsupported content type {}, options are {}".format(type_),
                        ("INT", "FLOAT", "TEXT"),
                    )

        print(self.attributes)
        print(self.stored_attrs)

        return tag

    def add_link(self, link_id, sender, receiver):
        self.links[link_id] = (sender, receiver)
