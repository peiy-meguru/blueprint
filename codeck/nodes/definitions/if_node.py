"""If node definition."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import build_node_height
from ...utils.standard import exec_pin_input, exec_pin_output, port_pin_input, exec_pin_custom_output
from ...utils.string_helper import format_function_indent


width = 180
height = build_node_height(2)


def if_code_fn(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for If node."""
    condition = get_connection_input('condition')
    if condition is None:
        condition = str(node.data.get('condition', False)).lower()
    
    true_branch = format_function_indent(get_connection_exec_output('true'), 2)
    false_branch = format_function_indent(get_connection_exec_output('false'), 2)
    
    return f'''if ({condition}) {{
  {true_branch}
}} else {{
  {false_branch}
}}
'''


IfNodeDefinition = CodeckNodeDefinition(
    name='if',
    label='If',
    node_type='logic',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    inputs=[
        exec_pin_input(width),
        port_pin_input('condition', width, 1, input_type='boolean')
    ],
    outputs=[
        exec_pin_output(width),
        exec_pin_custom_output('true', width, 1),
        exec_pin_custom_output('false', width, 2)
    ],
    code_fn=if_code_fn
)
