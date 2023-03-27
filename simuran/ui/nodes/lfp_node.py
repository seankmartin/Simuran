import contextlib
import os

from simuran.ui.node import BaseNode, NodeFactory
from simuran.plot.figure import SimuranFigure
from simuran.core.base_signal import Eeg, BaseSignal
from simuran.ui.node_elements import create_input
from simuran.plot.signal import plot_signals


class LFPViewNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "View signals")
        self.node_class = LFPViewNode
        self.category = "Visualise"

        self.attributes = [
            create_input(label="Input neural data", hint="Data input"),
        ]


class LFPViewNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)

    def process(self, nodes):
        super().process(nodes)

        self.input_recording_node = self.find_matching_input_node(
            reciever_label="Input neural data", nodes=nodes
        )
        input_recording = self.input_recording_node.recording
        base_dir = None
        output_dir = os.getcwd()

        name_for_save = input_recording.get_name_for_save(base_dir)
        signals = input_recording.attrs["signals"]
        if not all([isinstance(signals, BaseSignal) for signals in signals]):
            eeg_array = [
                Eeg.from_numpy(s, 250) for s in input_recording.attrs["signals"]
            ]
        else:
            eeg_array = signals
        fig = plot_signals(eeg_array, title=name_for_save, show=False)
        all_figs = [(fig, "all")]

        bitmap_fnames = []
        for f in all_figs:
            figure, name = f
            fname = os.path.join(output_dir, "lfp_signals", name_for_save + name)
            fig = SimuranFigure(
                figure=figure, filename=fname, done=True, verbose=self.debug
            )
            fig.save()
            bitmap_fnames.append(fig.output_filenames["raster"])

        self.plot_paths = bitmap_fnames

        return True
