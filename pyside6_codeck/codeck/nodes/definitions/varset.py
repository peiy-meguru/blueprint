"""Variable Set node definition."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import DEFAULT_NODE_WIDTH, build_node_height, build_pin_pos_x, build_pin_pos_y
from ...utils.standard import exec_pin_input, exec_pin_output, port_pin_input
from ...store.node import CodeckNodePinDefinition


width = DEFAULT_NODE_WIDTH
height = build_node_height(2)


def varset_code_fn(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for Variable Set node."""
    var_name = node.data.get('name', '')
    if not var_name:
        return '// Variable name not set\n'
    
    value = get_connection_input('value')
    if value is None:
        import json
        value = json.dumps(node.data.get('value', ''))
    
    return f'{var_name} = {value};\n'


VarSetNodeDefinition = CodeckNodeDefinition(
    name='varset',
    label='Set Variable',
    node_type='function',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    hidden=True,
    inputs=[
        exec_pin_input(width),
        port_pin_input('value', width, 1, input_type='text')
    ],
    outputs=[
        exec_pin_output(width)
    ],
    code_fn=varset_code_fn
)
