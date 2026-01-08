"""Begin node definition."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import DEFAULT_NODE_WIDTH, build_node_height
from ...utils.standard import exec_pin_output


width = DEFAULT_NODE_WIDTH
height = build_node_height(1)


BeginNodeDefinition = CodeckNodeDefinition(
    name='begin',
    label='Begin',
    node_type='begin',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    hidden=True,
    inputs=[],
    outputs=[exec_pin_output(width)]
)
