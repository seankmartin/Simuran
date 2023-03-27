from simuran.recording import Recording
from simuran.ui.node import BaseNode, NodeFactory
from simuran.ui.node_elements import create_input, create_code_block


class PythonCodeNodeFactory(NodeFactory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = kwargs.get("label", "Python code")
        self.node_class = PythonCodeNode
        self.category = "Processing"

        self.attributes = [
            create_input(label="Input data", hint="Data input", width=350),
            create_code_block(
                label="Python code",
                tooltip="Inline Python code",
                width=350,
                height=120,
            ),
        ]


class PythonCodeNode(BaseNode):
    def __init__(self, parent, label="Node", tag=None, debug=False):
        super().__init__(parent, label=label, tag=tag, debug=debug)
        self.recording = Recording()
        self.code = ""

    def process(self, nodes):
        super().process(nodes)

        # Use set parameters
        self.code = self.get_value_of_label(label="Python code")
        self.input_recording_node = self.find_matching_input_node(
            reciever_label="Input data", nodes=nodes
        )
        recording = self.input_recording_node.recording
        exec(self.code)
        self.recording = recording
        return True
