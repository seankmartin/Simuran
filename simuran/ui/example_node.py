import os
import dearpygui.dearpygui as dpg

from simuran.ui.node import BaseNode, NodeFactory
from simuran.analysis.custom.lfp_clean import LFPClean
from simuran.recording import Recording
from simuran.plot.figure import SimuranFigure

## TODO add run button, and then test

## TODO make a converter from py files
class RecordingNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Recording file")
        self.node_class = RecordingNode
        self.category="Source"

        contents = [
            dict(
                type="TEXT",
                width=200,
                label="File selector",
            )
        ]

        self.attributes = [
            dict(
                label="Attr 1",
                attribute_type=dpg.mvNode_Attr_Output,
                shape=dpg.mvNode_PinShape_Triangle,
                category="File select",
                contents=contents,
                tooltip="Choose the source file by right clicking the node.",
            )
        ]


class RecordingNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.recording = Recording()
        self.last_loaded_param_file = None

    def process(self, nodes):
        super().process(nodes)

        # Use set parameters
        self.param_file = self.get_value_of_label(label="File selector")
        
        if self.param_file == "":
            print("ERROR: No file selected")
            return False

        if not os.path.isfile(self.param_file):
            print(f"ERROR: Non existant file {self.param_file} selected")
            return False

        if self.last_loaded_param_file != self.param_file:
            self.recording.setup_from_file(self.param_file, load=True)
            self.last_loaded_param_file = self.param_file

        return True


class LFPCleanNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Node with function")
        self.node_class = BaseNode
        self.category = "Processing"

        # TODO make this match input
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
        self.label = "Neural data source file"
        self.node_class = LFPCleanNode


class LFPCleanNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.lfp_clean = LFPClean()

    def process(self, nodes):
        super().process(nodes)

        # Use set parameters
        method = self.get_value_of_label(label="Clean method")
        self.lfp_clean.method = method

        # Use the input data
        for key, value in self.input_attributes.items():
            if value.label == "Input recording":
                source_file_tag = key.split("--")[0]
                try:
                    source_file_tag = int(source_file_tag)
                except ValueError:
                    pass
                break

        for node in nodes.values():
            if node.has_attribute(source_file_tag):
                input_recording = node.recording
                break

        # TODO need to figure out method kwargs
        results = self.lfp_clean.clean(input_recording)

        # TODO work on naming
        clean_fig = results["fig"]

        # TODO include config for things like a base dir / output dir
        BASE_DIR = r"D:\SubRet_recordings_imaging"
        OUTPUT_DIR = r"E:\Repos\SIMURAN\examples\Results"

        name_for_save = input_recording.get_name_for_save(BASE_DIR)
        all_figs = [
            (clean_fig, f"_cleaned_signals_{method}"),
        ]

        bitmap_fnames = []

        if "ica_figs" in results.keys():
            ica_figs = [
                (results["ica_figs"][0], f"ica_excluded_{method}"),
                (results["ica_figs"][1], f"ica_reconstructed_{method}"),
            ]
            all_figs = all_figs + ica_figs

        for f in all_figs:
            figure, name = f
            fname = os.path.join(OUTPUT_DIR, "lfp_clean", name_for_save + name)
            fig = SimuranFigure(figure=figure, filename=fname, done=True)
            fig.save()
            bitmap_fnames.append(fig.get_filenames()["raster"])

        self.plot_paths = bitmap_fnames

        return True


def create_example_nodes():
    node1 = LFPCleanNodeFactory()

    node2 = RecordingNodeFactory()

    return [node1, node2]
