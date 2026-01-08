"""ForEach loop node definition."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import build_node_height
from ...utils.standard import exec_pin_input, exec_pin_output, port_pin_input, port_pin_output, exec_pin_custom_output
from ...utils.string_helper import format_function_indent


width = 180
height = build_node_height(3)


def foreach_code_fn(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for ForEach node."""
    array = get_connection_input('array')
    if array is None:
        array = '[]'
    
    item_var = build_pin_var_name('item')
    index_var = build_pin_var_name('index')
    body = format_function_indent(get_connection_exec_output('body'), 2)
    
    return f'''for (let {index_var} = 0; {index_var} < {array}.length; {index_var}++) {{
  const {item_var} = {array}[{index_var}];
  {body}
}}
'''


def item_output_code(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for item output."""
    return build_pin_var_name('item')


def index_output_code(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for index output."""
    return build_pin_var_name('index')


ForEachNodeDefinition = CodeckNodeDefinition(
    name='foreach',
    label='ForEach',
    node_type='function',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    inputs=[
        exec_pin_input(width),
        port_pin_input('array', width, 1)
    ],
    outputs=[
        exec_pin_output(width),
        exec_pin_custom_output('body', width, 1),
        port_pin_output('item', width, 2),
        port_pin_output('index', width, 3)
    ],
    code_fn=foreach_code_fn,
    output_code_fns={
        'item': item_output_code,
        'index': index_output_code
    }
)
