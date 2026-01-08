"""Add node definition."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_LOGIC_CATEGORY
from ...utils.size_helper import DEFAULT_NODE_WIDTH, build_node_height
from ...utils.standard import port_pin_input, port_pin_output


width = DEFAULT_NODE_WIDTH
height = build_node_height(3)


def output_code(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for output."""
    input1 = get_connection_input('input1')
    if input1 is None:
        input1 = str(node.data.get('input1', 0))
    
    input2 = get_connection_input('input2')
    if input2 is None:
        input2 = str(node.data.get('input2', 0))
    
    return f'({input1} + {input2})'


AddNodeDefinition = CodeckNodeDefinition(
    name='add',
    label='Add',
    node_type='logic',
    width=width,
    height=height,
    category=DEFAULT_LOGIC_CATEGORY,
    inputs=[
        port_pin_input('input1', width, 1, input_type='number'),
        port_pin_input('input2', width, 2, input_type='number')
    ],
    outputs=[
        port_pin_output('output', width, 1)
    ],
    output_code_fns={
        'output': output_code
    }
)
