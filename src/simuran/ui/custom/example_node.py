import contextlib
import os
import dearpygui.dearpygui as dpg

from simuran.ui.node import BaseNode, NodeFactory
from simuran.recording import Recording
from simuran.plot.figure import SimuranFigure
from simuran.eeg import EEGArray, EEG
from simuran.loaders.loader_list import loader_from_string

## TODO add run button, and then test

## TODO make a converter from py files
class RecordingNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Neural data source file")
        self.node_class = RecordingNode
        self.category = "Source"

        contents = [
            dict(
                type="TEXT",
                width=200,
                label="File: Recording mapping",
            )
        ]

        contents2 = [
            dict(
                type="TEXT",
                width=200,
                label="File: Recording source",
            )
        ]

        self.attributes = [
            dict(
                label="File: Recording mapping",
                attribute_type=dpg.mvNode_Attr_Output,
                shape=dpg.mvNode_PinShape_Triangle,
                category="File select",
                contents=contents,
                tooltip="Choose the source file by right clicking the node.",
            ),
            dict(
                label="File: Recording source",
                attribute_type=dpg.mvNode_Attr_Static,
                shape=dpg.mvNode_PinShape_Triangle,
                category="File select",
                contents=contents2,
                tooltip="Choose the source file by right clicking the node.",
            ),
        ]


class RecordingNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.recording = Recording()
        self.last_loaded_param_file = None
        self.last_loaded_source_file = None
        self.param_file = None
        self.source_file = None

    def process(self, nodes):
        super().process(nodes)

        # Use set parameters
        self.param_file = self.get_value_of_label(label="File: Recording mapping")
        self.source_file = self.get_value_of_label(label="File: Recording source")

        if self.param_file == "":
            print("ERROR: No file selected")
            return False

        if not os.path.isfile(self.param_file):
            print(f"ERROR: Non existant file {self.param_file} selected")
            return False

        if self.source_file == "":
            print("ERROR: No file selected")
            return False

        if not os.path.isfile(self.source_file):
            print(f"ERROR: Non existant file {self.source_file} selected")
            return False

        if (
            self.last_loaded_param_file != self.param_file
            or self.last_loaded_source_file != self.source_file
        ):
            self.load_setup()
        else:
            print(f"Already Loaded {self.source_file} with params {self.param_file}")

        return True

    def load_setup(self):
        if self.debug:
            print(f"Loading {self.source_file} with params {self.param_file}")
        self.recording.attrs["source_file"] = self.source_file
        self.recording.attrs["mapping_file"] = self.param_file
        # TODO add as UI parameter
        self.recording.loader = loader_from_string("neurochat")
        self.recording.parse_metadata()

        self.recording.load()
        self.last_loaded_param_file = self.param_file
        self.last_loaded_source_file = self.source_file
        if self.debug:
            print(f"Loaded {self.source_file} with params {self.param_file}")


class LFPViewFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "LFP signal cleaning")
        self.node_class = LFPViewNode
        self.category = "Processing"

        contents1 = [
            dict(
                type="TEXT",
                width=100,
                label="Input recording",
                hint="SIMURAN.recording",
                readonly=True,
            )
        ]

        contents = [
            dict(
                type="TEXT",
                width=100,
                label="Clean method",
                hint="avg",
            )
        ]

        self.attributes = [
            dict(
                label="Input recording",
                attribute_type=dpg.mvNode_Attr_Input,
                shape=dpg.mvNode_PinShape_Triangle,
                category="File input",
                tooltip="Connect a source file node.",
                contents=contents1,
            ),
            dict(
                label="Clean method",
                attribute_type=dpg.mvNode_Attr_Static,
                category="Parameters",
                contents=contents,
                tooltip="Options: avg, zscore, ica",
            ),
        ]


class LFPViewNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)

    def process(self, nodes):
        super().process(nodes)

        # Use set parameters
        # method = self.get_value_of_label(label="Clean method")
        # self.lfp_clean.method = method
        # if method == "" or method.startswith(" "):
        #     method = "avg"

        # Use the input data
        for key, _ in self.input_attributes.items():
            sender, receiver = key.split("--")
            with contextlib.suppress(ValueError):
                sender = int(sender)
            with contextlib.suppress(ValueError):
                receiver = int(receiver)
            attr = self.get_attribute(receiver)
            if attr["label"] == "Input recording":
                source_file_tag = sender
                break

        for node in nodes.values():
            if node.has_attribute(source_file_tag):
                input_recording = node.recording
                break

        # TODO include config for things like a base dir / output dir
        BASE_DIR = None
        OUTPUT_DIR = os.getcwd()

        name_for_save = input_recording.get_name_for_save(BASE_DIR)
        # TODO clean up
        eeg_array = EEGArray(input_recording.data["signals"])
        fig = eeg_array.plot(title=name_for_save, show=False)
        all_figs = [(fig, "all")]

        bitmap_fnames = []
        for f in all_figs:
            figure, name = f
            fname = os.path.join(OUTPUT_DIR, "lfp_signals", name_for_save + name)
            fig = SimuranFigure(
                figure=figure, filename=fname, done=True, verbose=self.debug
            )
            fig.save()
            bitmap_fnames.append(fig.output_filenames["raster"])

        self.plot_paths = bitmap_fnames

        return True


def create_example_nodes():
    node1 = LFPViewFactory()

    node2 = RecordingNodeFactory()

    return [node1, node2]
