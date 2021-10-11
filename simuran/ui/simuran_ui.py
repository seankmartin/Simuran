import os

import dearpygui.dearpygui as dpg

from simuran.ui.example_node import create_example_node


class SimuranUI(object):
    def __init__(self, **kwargs):
        self.width = kwargs.get("width", 1200)
        self.height = kwargs.get("height", 1200)
        self.viewport = None
        self.main_window_id = None
        self.nodes = []

    def main(self):
        dpg.create_context()
        self.setup_viewport()
        self.setup_main_window()
        self.create_node_editor()
        self.start_render()

    def start_render(self):
        # dpg.start_dearpygui()
        frame = 0

        while dpg.is_dearpygui_running():
            # insert here any code you would like to run in the render loop
            frame += 1

            if frame % 1000 == 0:
                print(frame)

            if frame == 200:
                # dpg.add_node(label="Node 3", parent="NEditor", before="NEditor", show=True)
                dpg.add_button(label="Generated dynamically", parent="M1", show=True)

            # you can manually stop by using stop_dearpygui()
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

    def show_popup_menu(self):
        mouse_pos = dpg.get_mouse_pos(local=False)
        dpg.configure_item("NodeAddWindow", show=True, pos=mouse_pos)

    def create_node(self, node):
        total_pos = dpg.get_mouse_pos(local=False)
        position = [max(total_pos[0] - 250, 0), max(total_pos[1] - 60, 0)]
        tag = node.create("E1", position=position)
        self.nodes.append(tag)
        print(self.nodes)

    def setup_main_window(self):
        self.main_window_id = "M1"

        node_to_add = create_example_node()
        with dpg.window(label="SIMURAN Demo", tag=self.main_window_id):

            # Popup node add window
            with dpg.handler_registry():
                # Use this for right click
                # dpg.add_mouse_click_handler(button=1, callback=self.show_popup_menu)

                dpg.add_key_press_handler(key=78, callback=self.show_popup_menu)

            with dpg.window(
                label="Node add", show=False, id="NodeAddWindow", modal=True
            ):  
                dpg.add_button(
                    label="New node",
                    width=75,
                    callback=lambda: self.create_node(node_to_add)
                )
                dpg.add_button(
                    label="Close",
                    width=75,
                    callback=lambda: dpg.configure_item("NodeAddWindow", show=False),
                )

        dpg.set_primary_window(self.main_window_id, True)

    def create_node_editor(self):
        # callback runs when user attempts to connect attributes
        def link_callback(sender, app_data, user_data):
            # app_data -> (link_id1, link_id2)
            dpg.add_node_link(app_data[0], app_data[1], parent=sender)
            print("Added link from {} to {}".format(app_data[0], app_data[1]))
            print(user_data)

        # callback runs when user attempts to disconnect attributes
        def delink_callback(sender, app_data, user_data):
            # app_data -> link_id
            dpg.delete_item(app_data)
            print("Deleted link {}".format(app_data))
            print(user_data)

        def mouse_context(sender, app_data, user_data):
            print(sender, app_data, user_data)

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
            callback=link_callback,
            delink_callback=delink_callback,
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

        with dpg.item_handler_registry(tag="widget handler") as handler:
            dpg.add_item_clicked_handler(button=1, callback=mouse_context)
        dpg.bind_item_handler_registry("Node1", "widget handler")

if __name__ == "__main__":
    su = SimuranUI()
    su.main()
