"""Loop node definition - Iteration for HOI4 MOD scripts."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import build_node_height
from ...utils.standard import exec_pin_input, exec_pin_output, port_pin_input, port_pin_output, exec_pin_custom_output
from ...utils.string_helper import format_function_indent


width = 180
height = build_node_height(3)


def loop_code_fn(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for Loop node in HOI4 script format.
    
    In HOI4, loops are typically done with every_* or random_* scopes.
    This generates a random_list with equal weights as a loop simulation.
    """
    count = get_connection_input('count')
    if count is None:
        count = node.data.get('count', 0)
    
    # Convert to int for comparison, handle edge case of count <= 0
    try:
        count_int = int(count)
    except (ValueError, TypeError):
        count_int = 0
    
    if count_int <= 0:
        return '# Loop skipped (count = 0)\n'
    
    body = format_function_indent(get_connection_exec_output('body'), 1)
    
    # HOI4 doesn't have traditional loops, use random_list as an example
    return f'''# Loop {count_int} times (using random_list)
random_list = {{
    {count_int} = {{
        {body}
    }}
}}
'''


def index_output_code(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for index output."""
    return build_pin_var_name('index')


LoopNodeDefinition = CodeckNodeDefinition(
    name='loop',
    label='Loop',
    node_type='function',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    inputs=[
        exec_pin_input(width),
        port_pin_input('count', width, 1, input_type='number')
    ],
    outputs=[
        exec_pin_output(width),
        exec_pin_custom_output('body', width, 1),
        port_pin_output('index', width, 2)
    ],
    code_fn=loop_code_fn,
    output_code_fns={
        'index': index_output_code
    }
)
