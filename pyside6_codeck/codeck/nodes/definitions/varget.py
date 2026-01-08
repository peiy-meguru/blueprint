"""Variable Get node definition."""

from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import DEFAULT_NODE_WIDTH, build_node_height, build_pin_pos_x, build_pin_pos_y
from ...store.node import CodeckNodePinDefinition


width = DEFAULT_NODE_WIDTH
height = build_node_height(1)


VarGetNodeDefinition = CodeckNodeDefinition(
    name='varget',
    label='Get Variable',
    node_type='logic',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    hidden=True,
    inputs=[],
    outputs=[
        CodeckNodePinDefinition(
            name='variable',
            type='port',
            position=QPointF(build_pin_pos_x(width, 'output'), build_pin_pos_y(0))
        )
    ]
)
