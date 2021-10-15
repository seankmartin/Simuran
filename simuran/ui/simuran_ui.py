print("Starting application...")

import click_spinner

with click_spinner.spinner():
    import os
    import traceback

    import matplotlib

    matplotlib.use("TkAgg")
    from rich import print
    import typer
    import dearpygui.dearpygui as dpg
    import PIL
    import numpy as np

    from simuran.ui.example_node import create_example_nodes


class SimuranUI(object):
    def __init__(self, **kwargs):
        self.width = kwargs.get("width", 1200)
        self.height = kwargs.get("height", 800)
        self.viewport = None
        self.main_window_id = kwargs.get("main_window_id", "M1")
        self.nodes = {}
        self.node_factories = []
        self.button_to_node_mapping = {}
        self.debug = kwargs.get("debug", False)
        self.last_clicked_node = None
        self.last_clicked_content = None
        self.loaded_images = {}
        self.links = {}

    # Control functions
    def main(self):
        dpg.create_context()
        self.init_nodes()
        self.setup_viewport()
        self.create_main_window()
        self.create_node_editor()
        self.create_menu_bar()
        self.create_file_selection_window()

        if self.debug:
            dpg.show_debug()
            dpg.show_item_registry()

        self.start_render()

    def init_nodes(self):
        # TODO currently a set list, should be expanded
        # TODO change the context menu based on category.
        for node in create_example_nodes():
            node.clicked_callback = self.show_plot_menu
            self.node_factories.append(node)

    def start_render(self):
        dpg.start_dearpygui()
        dpg.destroy_context()

    def setup_viewport(self):
        vp = dpg.create_viewport(
            title="SIMURAN demo", width=self.width, height=self.height
        )  # create viewport takes in config options too!

        # must be called before showing viewport
        here = os.path.dirname(os.path.realpath(__file__))
        dpg.set_viewport_small_icon(os.path.join(here, "favicon.ico"))
        dpg.set_viewport_large_icon(os.path.join(here, "favicon.ico"))

        dpg.setup_dearpygui()
        dpg.show_viewport()

        self.viewport = vp

    # Callbacks and handlers
    def show_popup_menu(self, sender, app_data, user_data):
        mouse_pos = dpg.get_mouse_pos(local=False)
        dpg.configure_item("NodeAddWindow", show=True, pos=mouse_pos)

    def show_plot_menu(self, sender, app_data, user_data):
        if self.debug:
            print(f"Clicked {user_data}")
        # TODO pass through the node selected here
        if user_data[0] == "node":
            self.last_clicked_node = user_data[1]
            self.last_clicked_content = None
        elif user_data[0] == "content":
            self.last_clicked_content = user_data[1]
            self.last_clicked_node = user_data[2]
        else:
            print("Unrecognised clicked type {}".format(user_data[0]))

        mouse_pos = dpg.get_mouse_pos(local=False)
        dpg.configure_item("NodeContextWindow", show=True, pos=mouse_pos)

    def create_node(self, sender, app_data, user_data):
        node_factory = self.button_to_node_mapping[sender]
        total_pos = dpg.get_mouse_pos(local=False)
        position = [max(total_pos[0] - 250, 0), max(total_pos[1] - 60, 0)]
        node = node_factory.create("E1", position=position)
        self.nodes[node.tag] = node
        dpg.configure_item("NodeAddWindow", show=False)
        node.debug = self.debug

    def global_handlers(self):
        with dpg.handler_registry(label="global handlers"):
            # Use this for right click
            # dpg.add_mouse_click_handler(button=1, callback=self.show_popup_menu)
            dpg.add_key_press_handler(key=78, callback=self.show_popup_menu)

    def link_callback(self, sender, app_data, user_data):
        # app_data -> (link_id1, link_id2)
        from_tag, to_tag = app_data[0], app_data[1]
        link_tag = dpg.add_node_link(from_tag, to_tag, parent=sender)

        for node_id, node in self.nodes.items():
            if node.has_attribute(from_tag):
                node.on_connect(from_tag, to_tag)
            if node.has_attribute(to_tag):
                node.on_connect(from_tag, to_tag)

        self.links[link_tag] = (from_tag, to_tag)

    def delink_callback(self, sender, app_data, user_data):
        # app_data -> link_id
        dpg.delete_item(app_data)
        from_tag, to_tag = self.links.pop(app_data)

        for node_id, node in self.nodes.items():
            if node.has_attribute(from_tag):
                node.on_disconnect(from_tag, to_tag)
            if node.has_attribute(to_tag):
                node.on_disconnect(from_tag, to_tag)

    def file_select_callback(self, sender, app_data, user_data):
        selections = app_data["selections"]

        if user_data is None:
            for basename, fpath in selections.items():
                last_node = self.nodes[self.last_clicked_node]
                last_node.set_source_file(fpath, label=self.last_clicked_content)
        else:
            if len(selections) == 1:
                dpg.set_value(user_data, selections[0])
            else:
                print("Selected multiple files, please choose one.")

    def show_plots_callback(self, sender, app_data, user_data):
        node_clicked = self.last_clicked_node
        paths = self.nodes[node_clicked].plot_paths
        for i, path in enumerate(paths):
            if path not in self.loaded_images.keys():
                t_id = dpg.generate_uuid()
                image = PIL.Image.open(path)
                image = image.resize(
                    (self.width - 50, self.height - 40), PIL.Image.ANTIALIAS
                )
                has_alpha = image.mode == "RGBA"
                if not has_alpha:
                    image.putalpha(255)
                dpg_image = np.frombuffer(image.tobytes(), dtype=np.uint8) / 255.0

                dpg.add_static_texture(
                    tag=t_id,
                    default_value=dpg_image,
                    width=self.width - 50,
                    height=self.height - 40,
                    parent="plot_registry",
                )
                self.loaded_images[path] = t_id
            else:
                t_id = self.loaded_images[path]

            with dpg.window(
                label="Plot information from {}".format(self.nodes[node_clicked].label),
                width=self.width - 50,
                height=self.height - 40,
            ):
                dpg.add_image(label="drawing", texture_id=t_id)

    def run_graph_callback(self, sender, app_data, user_data):
        dpg.configure_item("MainRunButton", enabled=False, label="Running...")
        # TODO revise this for performance (e.g. multiprocessing or live running)
        def kill_process():
            print("There was an error in processing. Aborting.")
            dpg.configure_item("MainRunButton", enabled=True, label="Run")
            return False

        try:
            connected_nodes = set()
            # Process source nodes
            for tag, node in self.nodes.items():
                if node.category == "Source":
                    keep_going = node.process(self.nodes)
                    if not keep_going:
                        kill_process()
                    downstream_node_tags = node.get_downstream_nodes(self.nodes)
                    for i in downstream_node_tags:
                        connected_nodes.add(i)

            # Process connected nodes
            condition = True
            while condition:
                if self.debug:
                    print(f"Downstream nodes {connected_nodes}")

                intermediate_connected_nodes = set()
                for element in connected_nodes:
                    node = self.nodes[element]
                    keep_going = node.process(self.nodes)
                    if not keep_going:
                        kill_process()
                    downstream_node_tags = node.get_downstream_nodes(self.nodes)
                    for i in downstream_node_tags:
                        intermediate_connected_nodes.add(i)
                condition = len(intermediate_connected_nodes) != 0
                connected_nodes = intermediate_connected_nodes

            dpg.configure_item("MainRunButton", enabled=True, label="Run")
        except:
            traceback.print_exc()
            dpg.configure_item("MainRunButton", enabled=True, label="Run")

        return True

    # Windows
    def create_add_node_window(self):
        with dpg.window(label="Add Node", show=False, id="NodeAddWindow", modal=True):

            for node in self.node_factories:
                tag = dpg.add_button(
                    label=node.label,
                    width=200,
                    callback=self.create_node,
                )
                self.button_to_node_mapping[tag] = node
            dpg.add_button(
                label="Close",
                width=75,
                indent=75,
                callback=lambda: dpg.configure_item("NodeAddWindow", show=False),
            )

    def create_node_info_window(self):

        with dpg.window(
            label="Node context", show=False, id="NodeContextWindow", modal=True
        ):
            dpg.add_button(
                label="Show plots",
                width=200,
                callback=self.show_plots_callback,
            )
            dpg.add_button(
                label="Select file path",
                width=200,
                callback=lambda: dpg.show_item("file_dialog_id"),
            )
            dpg.add_button(
                label="Close",
                width=75,
                indent=75,
                callback=lambda: dpg.configure_item("NodeContextWindow", show=False),
            )

    def create_main_window(self):
        with dpg.window(label="SIMURAN Demo", tag=self.main_window_id):
            dpg.add_text("Main menu")
            self.create_add_node_window()
            self.create_node_info_window()
            self.global_handlers()

            dpg.add_button(
                label="Run",
                width=150,
                indent=25,
                callback=self.run_graph_callback,
                tag="MainRunButton",
            )

        dpg.set_primary_window(self.main_window_id, True)

    def create_node_editor(self):
        dpg.add_window(
            label="Node editor",
            tag="NodeWindow",
            width=self.width - 250,
            height=self.height - 50,
            pos=[200, 0],
            horizontal_scrollbar=False,
        )
        dpg.add_node_editor(
            label="NEditor",
            callback=self.link_callback,
            delink_callback=self.delink_callback,
            tag="E1",
            parent="NodeWindow",
        )
        dpg.add_item_handler_registry(tag="node context handler")
        dpg.add_texture_registry(tag="plot_registry")

    def create_menu_bar(self):
        def print_me(sender):
            print(f"Menu Item: {sender}")

        with dpg.menu_bar(parent=self.main_window_id):
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Save", callback=print_me)
                dpg.add_menu_item(label="Save As", callback=print_me)

                with dpg.menu(label="Settings"):
                    dpg.add_menu_item(label="Setting 1", callback=print_me, check=True)
                    dpg.add_menu_item(label="Setting 2", callback=print_me)

            dpg.add_menu_item(label="Help", callback=print_me)

            with dpg.menu(label="Widget Items"):
                dpg.add_checkbox(label="Pick Me", callback=print_me)
                dpg.add_button(label="Press Me", callback=print_me)
                dpg.add_color_picker(label="Color Me", callback=print_me)

    def create_file_selection_window(self):

        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=self.file_select_callback,
            id="file_dialog_id",
        ):
            dpg.add_file_extension(".*")
            dpg.add_file_extension("", color=(150, 255, 150, 255))
            dpg.add_file_extension(
                ".py", color=(0, 255, 0, 255), custom_text="[Python]"
            )


def main_ui(debug: bool = False):
    su = SimuranUI(debug=debug)
    su.main()


def cli_entry():
    typer.run(main_ui)


if __name__ == "__main__":
    cli_entry()
