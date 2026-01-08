"""Not (logical) node definition."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_LOGIC_CATEGORY
from ...utils.size_helper import DEFAULT_NODE_WIDTH, build_node_height
from ...utils.standard import port_pin_input, port_pin_output


width = DEFAULT_NODE_WIDTH
height = build_node_height(2)


def output_code(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for output."""
    input1 = get_connection_input('input')
    if input1 is None:
        input1 = str(node.data.get('input', False)).lower()
    
    return f'(!{input1})'


NotNodeDefinition = CodeckNodeDefinition(
    name='not',
    label='Not (!)',
    node_type='logic',
    width=width,
    height=height,
    category=DEFAULT_LOGIC_CATEGORY,
    inputs=[
        port_pin_input('input', width, 1, input_type='boolean')
    ],
    outputs=[
        port_pin_output('output', width, 1)
    ],
    output_code_fns={
        'output': output_code
    }
)
