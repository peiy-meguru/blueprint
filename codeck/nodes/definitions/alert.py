"""Alert node definition - Creates a news event popup in HOI4."""

import json
from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import DEFAULT_NODE_WIDTH, build_node_height
from ...utils.standard import exec_pin_input, exec_pin_output, port_pin_input


width = DEFAULT_NODE_WIDTH
height = build_node_height(2)


def alert_code_fn(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for Alert node in HOI4 script format - creates a news event."""
    message = get_connection_input('message')
    if message is None:
        message = node.data.get('message', '')
    return f'# Show news event with message\nnews_event = {{ id = news.1 }}\n'


AlertNodeDefinition = CodeckNodeDefinition(
    name='alert',
    label='News Event',
    node_type='function',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    inputs=[
        exec_pin_input(width),
        port_pin_input('message', width, 1, input_type='text')
    ],
    outputs=[exec_pin_output(width)],
    code_fn=alert_code_fn
)
