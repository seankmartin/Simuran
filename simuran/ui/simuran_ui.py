import os

import dearpygui.dearpygui as dpg
from rich import print

from simuran.ui.example_node import create_example_nodes


class SimuranUI(object):
    def __init__(self, **kwargs):
        self.width = kwargs.get("width", 1200)
        self.height = kwargs.get("height", 1200)
        self.viewport = None
        self.main_window_id = kwargs.get("main_window_id", "M1")
        self.nodes = []
        self.node_factories = []

    # Control functions
    def main(self):
        dpg.create_context()
        self.init_nodes()
        self.setup_viewport()
        self.setup_main_window()
        self.create_node_editor()
        self.start_render()

    def init_nodes(self):
        # Currently a set list, should be expanded
        self.node_factories = create_example_nodes()

    def start_render(self):
        # dpg.start_dearpygui()
        frame = 0

        while dpg.is_dearpygui_running():
            # insert here any code you would like to run in the render loop
            # frame += 1
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def setup_viewport(self):
        vp = dpg.create_viewport(
            title="SIMURAN demo", width=1200, height=900
        )  # create viewport takes in config options too!

        # must be called before showing viewport
        here = os.path.dirname(os.path.realpath(__file__))
        dpg.set_viewport_small_icon(os.path.join(here, "favicon.ico"))
        dpg.set_viewport_large_icon(os.path.join(here, "favicon.ico"))

        dpg.setup_dearpygui()
        dpg.show_viewport()

        self.viewport = vp

    # Callbacks and handlers
    def show_popup_menu(self):
        mouse_pos = dpg.get_mouse_pos(local=False)
        dpg.configure_item("NodeAddWindow", show=True, pos=mouse_pos)

    def create_node(self, sender, app_data, user_data):
        i, node = user_data
        total_pos = dpg.get_mouse_pos(local=False)
        position = [max(total_pos[0] - 250, 0), max(total_pos[1] - 60, 0)]
        tag = node.create("E1", position=position)
        self.nodes.append(tag)

    def global_handlers(self):
        with dpg.handler_registry(label="global handlers"):
            # Use this for right click
            # dpg.add_mouse_click_handler(button=1, callback=self.show_popup_menu)
            dpg.add_key_press_handler(key=78, callback=self.show_popup_menu)

    def link_callback(self, sender, app_data, user_data):
        # app_data -> (link_id1, link_id2)
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)
        print("Added link from {} to {}".format(app_data[0], app_data[1]))
        print(user_data)

    # callback runs when user attempts to disconnect attributes
    def delink_callback(self, sender, app_data, user_data):
        # app_data -> link_id
        dpg.delete_item(app_data)
        print("Deleted link {}".format(app_data))
        print(user_data)

    def mouse_context(self, sender, app_data, user_data):
        print(sender, app_data, user_data)

    # Windows
    def create_add_node_window(self):
        with dpg.window(label="Add Node", show=False, id="NodeAddWindow", modal=True):

            for i, node in enumerate(self.node_factories):
                dpg.add_button(
                    label=node.label,
                    width=200,
                    callback=self.create_node,
                    user_data=[i, node]
                )
            dpg.add_button(
                label="Close",
                width=75,
                indent=75,
                callback=lambda: dpg.configure_item("NodeAddWindow", show=False),
            )

    def show_node_info_window(self):
        with dpg.window(label="Add Node", show=False, id="NodeAddWindow", modal=True):
            dpg.add_button(
                label=node.label,
                width=75,
                callback=lambda: self.create_node(node),
            )

    def setup_main_window(self):
        with dpg.window(label="SIMURAN Demo", tag=self.main_window_id):
            self.create_add_node_window()
            self.global_handlers()

        dpg.set_primary_window(self.main_window_id, True)

    def create_node_editor(self):
        dpg.add_window(
            label="Node editor",
            tag="NodeWindow",
            width=1000,
            height=800,
            pos=[200, 0],
            horizontal_scrollbar=True,
        )
        with dpg.node_editor(
            label="NEditor",
            callback=self.link_callback,
            delink_callback=self.delink_callback,
            tag="E1",
            parent="NodeWindow",
        ):
            with dpg.node(label="Node 1", tag="Node1"):
                with dpg.node_attribute(label="Node A1"):
                    dpg.add_input_float(label="F1", width=150)

                with dpg.node_attribute(
                    label="Node A2", attribute_type=dpg.mvNode_Attr_Output
                ):
                    dpg.add_input_float(label="F2", width=150)

            with dpg.node(label="Node 2"):
                with dpg.node_attribute(label="Node A3"):
                    dpg.add_input_float(label="F3", width=200)

                with dpg.node_attribute(
                    label="Node A4", attribute_type=dpg.mvNode_Attr_Output
                ):
                    dpg.add_input_float(label="F4", width=200)

        # TODO make a node context handler.
        with dpg.item_handler_registry(tag="node context handler") as handler:
            dpg.add_item_clicked_handler(button=1, callback=self.mouse_context)
        dpg.bind_item_handler_registry("Node1", "node context handler")


if __name__ == "__main__":
    su = SimuranUI()
    su.main()
