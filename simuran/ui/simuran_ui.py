print("Starting application:")
import click_spinner

with click_spinner.spinner():
    import os
    import traceback
    from pathlib import Path
    import json

    import matplotlib

    matplotlib.use("TkAgg")
    from rich import print
    import typer
    import dearpygui.dearpygui as dpg
    import PIL
    import numpy as np
    import dearpygui._dearpygui as internal_dpg

    from simuran.ui.node_factories import get_node_factories
    from simuran.loaders.loader_list import supported_loaders, installed_loaders


class SimuranUI(object):
    def __init__(self, **kwargs):
        self.width = kwargs.get("width", kwargs.get("width", 1400))
        self.height = kwargs.get("height", kwargs.get("height", 950))
        self.viewport = None
        self.main_window_id = kwargs.get("main_window_id", "M1")
        self.nodes = {}
        self.node_factories = {}
        self.button_to_node_mapping = {}
        self.debug = kwargs.get("debug", False)
        self.last_clicked_node = None
        self.last_clicked_content = None
        self.loaded_images = {}
        self.links = {}
        self.editor_tag = "E1"
        self.default_location = Path.home()
        if os.path.exists(self.default_location / ".skm_python" / "ui_settings.json"):
            try:
                self.default_location = Path(
                    json.load(
                        open(self.default_location / ".skm_python" / "ui_settings.json")
                    )["last_file_location"]
                )
            except Exception:
                print("Failed to load last file location")
        self.graph_location = self.default_location / "graph.json"

    # Control functions
    def main(self):
        dpg.create_context()
        self.init_nodes()
        self.setup_viewport()
        self.create_main_window()
        self.create_node_editor()
        self.create_menu_bar()
        self.create_file_selection_window()
        self.create_file_save_window()
        self.create_file_load_window()

        if self.debug:
            dpg.show_debug()
            dpg.show_item_registry()

        self.start_render()

    def init_nodes(self):
        node_factories = [c() for c in get_node_factories()]
        for node_factory in node_factories:
            node_factory.clicked_callback = self.show_plot_menu
            self.node_factories[node_factory.label] = node_factory

    def start_render(self):
        dpg.start_dearpygui()
        dpg.destroy_context()

    def setup_viewport(self):
        vp = dpg.create_viewport(title="SIMURAN", width=self.width, height=self.height)

        here = os.path.dirname(os.path.realpath(__file__))
        favicon_path = os.path.join(here, "favicon.ico")
        if os.path.exists(favicon_path):
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
        if user_data[0] == "node":
            self.last_clicked_node = user_data[1]
            self.last_clicked_content = None
        elif user_data[0] == "content":
            self.last_clicked_content = user_data[1]
            self.last_clicked_node = user_data[2]
        else:
            print(f"Unrecognised clicked type {user_data[0]}")

        mouse_pos = dpg.get_mouse_pos(local=False)
        dpg.configure_item("NodeContextWindow", show=True, pos=mouse_pos)

    def create_node(self, sender, app_data, user_data):
        node_factory = self.button_to_node_mapping[sender]
        total_pos = dpg.get_mouse_pos(local=False)
        position = [max(total_pos[0] - 250, 0), max(total_pos[1] - 60, 0)]
        node = node_factory.create(self.editor_tag, position=position)
        self.nodes[node.tag] = node
        dpg.configure_item("NodeAddWindow", show=False)
        node.debug = self.debug

    def create_saved_node(self, label, position, attributes, id_):
        node_factory = self.node_factories[label]
        node = node_factory.create(self.editor_tag, position=position)
        self.nodes[node.tag] = node
        node.debug = self.debug
        node.internal_id = id_
        for k, v in attributes.items():
            content_tag, content = node.get_content_with_label(k)
            if content_tag is None:
                raise ValueError("No content tag found for " + k)
            dpg.set_value(content_tag, v)

    def global_handlers(self):
        with dpg.handler_registry(label="global handlers"):
            # Use this for right click
            # dpg.add_mouse_click_handler(button=1, callback=self.show_popup_menu)
            # dpg.add_key_press_handler(
            #     key=internal_dpg.mvKey_Control, callback=self.show_popup_menu
            # )
            dpg.add_key_press_handler(
                key=internal_dpg.mvKey_Delete, callback=self.delete_item
            )
            dpg.add_key_press_handler(
                key=internal_dpg.mvKey_F1, callback=self.show_popup_menu
            )

    def link_callback(self, sender, app_data, user_data):
        # app_data -> (link_id1, link_id2)
        from_tag, to_tag = app_data[0], app_data[1]
        link_tag = dpg.add_node_link(from_tag, to_tag, parent=sender)
        if self.debug:
            print(f"Linking {from_tag} to {to_tag}")

        for node_id, node in self.nodes.items():
            if self.debug:
                print(f"Node {node_id} has attributes {list(node.attributes.keys())}")
            if node.has_attribute(from_tag):
                node.on_connect(from_tag, to_tag)
            if node.has_attribute(to_tag):
                node.on_connect(from_tag, to_tag)

        self.links[link_tag] = (from_tag, to_tag)

    def delink_callback(self, sender, app_data, user_data):
        # app_data -> link_id
        dpg.delete_item(app_data)
        from_tag, to_tag = self.links.pop(app_data)
        if self.debug:
            print(f"Unlinking {from_tag} to {to_tag}")

        for node_id, node in self.nodes.items():
            if self.debug:
                print(f"Node {node_id} has attributes {list(node.attributes.keys())}")
            if node.has_attribute(from_tag):
                node.on_disconnect(from_tag, to_tag)
            if node.has_attribute(to_tag):
                node.on_disconnect(from_tag, to_tag)

    def file_select_callback(self, sender, app_data, user_data):
        selections = app_data["selections"]
        location_to_save = None

        if user_data is None:
            for basename, fpath in selections.items():
                last_node = self.nodes[self.last_clicked_node]
                last_node.set_source_file(fpath, label=self.last_clicked_content)
                location_to_save = Path(fpath).parent
        elif user_data == "save":
            if len(selections) == 0:
                self.graph_location = Path(app_data["file_path_name"])
            else:
                for basename, fpath in selections.items():
                    self.graph_location = Path(fpath)
            location_to_save = self.graph_location.parent
            self.save_graph()
        elif user_data == "load":
            for basename, fpath in selections.items():
                self.graph_location = Path(fpath)
            self.load_graph()
            location_to_save = self.graph_location.parent
        elif len(selections) > 1:
            print("Selected multiple files, please choose one.")
            return

        default_location = Path.home()
        if location_to_save is not None:
            with open(default_location / ".skm_python" / "ui_settings.json", "w") as f:
                json.dump({"last_file_location": str(location_to_save)}, f)
        self.default_location = location_to_save

    def show_plots_callback(self, sender, app_data, user_data):
        node_clicked = self.last_clicked_node
        paths = self.nodes[node_clicked].plot_paths
        if paths is None:
            print("No plots generated yet.")
            return
        for path in paths:
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
                label=f"Plot information from {self.nodes[node_clicked].label}",
                width=self.width - 50,
                height=self.height - 40,
            ):
                dpg.add_image(label="drawing", texture_tag=t_id)

    def run_graph_callback(self, sender, app_data, user_data):
        dpg.configure_item("MainRunButton", enabled=False, label="Running...")

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

        print("Finished processing.")
        return True

    def print_loaders_callback(self, sender, app_data, user_data):
        print(installed_loaders())

    def print_all_loaders_callback(self, sender, app_data, user_data):
        print(supported_loaders())

    def create_add_node_window(self):
        with dpg.window(label="Add Node", show=False, id="NodeAddWindow", modal=True):

            for node in self.node_factories.values():
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
            label="Node options", show=False, id="NodeContextWindow", modal=True
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
        with dpg.window(label="SIMURAN", tag=self.main_window_id):
            self.create_add_node_window()
            self.create_node_info_window()
            self.global_handlers()

            dpg.add_button(
                label="Add node",
                width=175,
                indent=7,
                callback=lambda: dpg.configure_item("NodeAddWindow", show=True),
                tag="MainAddButton",
            )

            dpg.add_button(
                label="Installed data loaders",
                width=175,
                indent=7,
                callback=self.print_loaders_callback,
                tag="MainLoadersButton",
            )

            dpg.add_button(
                label="All data loaders",
                width=175,
                indent=7,
                callback=self.print_all_loaders_callback,
                tag="MainAllLoadersButton",
            )

            dpg.add_button(
                label="Run",
                width=175,
                indent=7,
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
        dpg.add_text("Ctrl+Click to remove a link.", bullet=True, parent="NodeWindow")
        dpg.add_node_editor(
            label="NEditor",
            callback=self.link_callback,
            delink_callback=self.delink_callback,
            tag=self.editor_tag,
            parent="NodeWindow",
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_BottomRight,
            # height=self.height - 100,
        )
        dpg.add_item_handler_registry(tag="node context handler")
        dpg.add_texture_registry(tag="plot_registry")

    def create_menu_bar(self):
        with dpg.menu_bar(parent=self.main_window_id):
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Save", callback=self.save_graph)
                dpg.add_menu_item(label="Save As", callback=self.save_graph_callback)
                dpg.add_menu_item(label="Load", callback=self.load_graph_callback)

    def create_file_selection_window(self):

        with dpg.file_dialog(
            label="Load data from...",
            directory_selector=False,
            show=False,
            callback=self.file_select_callback,
            id="file_dialog_id",
            width=600,
            height=400,
            default_path=str(self.default_location),
        ):
            dpg.add_file_extension(".*")
            dpg.add_file_extension("", color=(150, 255, 150, 255))
            dpg.add_file_extension(
                ".nwb",
                color=(0, 255, 0, 255),
                custom_text="[Neurodata Without Borders]",
            )
            dpg.add_file_extension(".h5", color=(0, 255, 0, 255))
            dpg.add_file_extension(
                ".set", color=(0, 255, 0, 255), custom_text="Axona .set"
            )

    def create_file_save_window(self):

        with dpg.file_dialog(
            label="Save graph to...",
            directory_selector=False,
            show=False,
            callback=self.file_select_callback,
            id="file_save_id",
            width=600,
            height=400,
            default_path=str(self.default_location),
            default_filename="graph.json",
            user_data="save",
        ):
            dpg.add_file_extension(
                ".json",
                color=(0, 255, 0, 255),
                custom_text="[Saved graphs]",
            )
            dpg.add_file_extension(".*")
            dpg.add_file_extension("", color=(150, 255, 150, 255))

    def create_file_load_window(self):

        with dpg.file_dialog(
            label="Load graph from...",
            directory_selector=False,
            show=False,
            callback=self.file_select_callback,
            id="file_load_id",
            width=600,
            height=400,
            default_path=str(self.default_location),
            default_filename="graph.json",
            user_data="load",
        ):
            dpg.add_file_extension(
                ".json",
                color=(0, 255, 0, 255),
                custom_text="[Saved graphs]",
            )
            dpg.add_file_extension(".*")
            dpg.add_file_extension("", color=(150, 255, 150, 255))

    def save_graph_callback(self):
        dpg.show_item("file_save_id")

    def load_graph_callback(self):
        dpg.show_item("file_load_id")

    def save_graph(self):
        dict_nodes = {}
        link_graph = {}
        nodes = list(self.nodes.values())
        for n in nodes:
            dict_nodes[n.label] = {}
            dict_nodes[n.label]["id"] = n.tag
            dict_nodes[n.label]["factory_label"] = n.factory_label
            dict_nodes[n.label]["postition"] = dpg.get_item_pos(n.tag)
            attribute_dict = {}
            for k, v in n.attributes.items():
                attribute_dict[v["label"]] = n.get_value_of_label(v["label"])
            dict_nodes[n.label]["attributes"] = attribute_dict
            link_graph[n.tag] = {}
            if len(n.input_attributes) > 0:
                for tags, v in n.input_attributes.items():
                    input_tag, output_tag = tags.split("->")
                    input_tag, output_tag = int(input_tag), int(output_tag)
                    for n2 in nodes:
                        if n2.has_attribute(input_tag):
                            input_label = n2.get_attribute(input_tag)["label"]
                            input_node_tag = str(n2.tag)
                        if n2.has_attribute(output_tag):
                            output_label = n2.get_attribute(output_tag)["label"]
                            output_node_tag = str(n2.tag)
                    link_graph[n.tag][tags] = [
                        input_node_tag + "->" + output_node_tag,
                        input_label + "->" + output_label,
                    ]

        result = {}
        result["link_graph"] = link_graph
        result["nodes"] = dict_nodes

        with open(self.graph_location, "w") as f:
            json.dump(result, f)

    def load_graph(self):
        self.reset()
        with open(self.graph_location, "r") as f:
            result = json.load(f)

        dict_nodes = result["nodes"]
        for k, v in dict_nodes.items():
            self.create_saved_node(
                v["factory_label"], v["postition"], v["attributes"], v["id"]
            )

        link_graph = result["link_graph"]
        for k, v in link_graph.items():
            for k2, label_list in v.items():
                node_labels, attribute_labels = label_list
                input_node_tag, output_node_tag = node_labels.split("->")
                input_node_tag, output_node_tag = int(input_node_tag), int(
                    output_node_tag
                )
                input_label, output_label = attribute_labels.split("->")
                input_node = [
                    n
                    for n in list(self.nodes.values())
                    if n.internal_id == input_node_tag
                ][0]
                output_node = [
                    n
                    for n in list(self.nodes.values())
                    if n.internal_id == output_node_tag
                ][0]
                input_tag, input_ = input_node.get_attribute_with_label(input_label)
                output_tag, output_ = output_node.get_attribute_with_label(output_label)
                dpg.add_node_link(input_tag, output_tag, parent=self.editor_tag)

    def reset(self):
        tags = [n.tag for n in list(self.nodes.values())]
        for tag in tags:
            self.delete_node_with_tag(tag)

    def delete_item(self, sender, app_data, user_data):
        selected_nodes = dpg.get_selected_nodes(self.editor_tag)
        for tag in selected_nodes:
            self.delete_node_with_tag(tag)

    def delete_node_with_tag(self, tag):
        dpg.delete_item(tag)
        node = self.nodes.pop(tag)
        node_factory_label = node.factory_label
        self.node_factories[node_factory_label].created_nodes.remove(tag)


def main_ui(debug: bool = False, height: int = 950, width: int = 1400):
    su = SimuranUI(debug=debug, height=height, width=width)
    su.main()


def cli_entry():
    typer.run(main_ui)


if __name__ == "__main__":
    cli_entry()
