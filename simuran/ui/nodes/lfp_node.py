import contextlib
import os
import dearpygui.dearpygui as dpg

from simuran.ui.node import BaseNode, NodeFactory
from simuran.plot.figure import SimuranFigure
from simuran.core.base_signal import Eeg


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
        eeg_array = [Eeg.from_numpy(s, 250) for s in input_recording.data["signals"]]
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
