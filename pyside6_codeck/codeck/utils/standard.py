"""Standard node definitions and helpers."""

import json
from PySide6.QtCore import QPointF
from ..store.node import CodeckNodePinDefinition, CodeckNodeDefinition
from ..utils.consts import STANDARD_PIN_EXEC_IN, STANDARD_PIN_EXEC_OUT
from ..utils.size_helper import build_pin_pos_x, build_pin_pos_y, DEFAULT_NODE_WIDTH, build_node_height


def exec_pin_input(width: int) -> CodeckNodePinDefinition:
    """Create a standard execution input pin."""
    return CodeckNodePinDefinition(
        name=STANDARD_PIN_EXEC_IN,
        type='exec',
        position=QPointF(build_pin_pos_x(width, 'input'), build_pin_pos_y(0))
    )


def exec_pin_output(width: int) -> CodeckNodePinDefinition:
    """Create a standard execution output pin."""
    return CodeckNodePinDefinition(
        name=STANDARD_PIN_EXEC_OUT,
        type='exec',
        position=QPointF(build_pin_pos_x(width, 'output'), build_pin_pos_y(0))
    )


def port_pin_input(name: str, width: int, position: int, label: str = None, input_type: str = None, default_value=None) -> CodeckNodePinDefinition:
    """Create a standard port input pin."""
    return CodeckNodePinDefinition(
        name=name,
        type='port',
        position=QPointF(build_pin_pos_x(width, 'input'), build_pin_pos_y(position)),
        input_type=input_type,
        default_value=default_value,
        render_type=label or name
    )


def port_pin_output(name: str, width: int, position: int, label: str = None) -> CodeckNodePinDefinition:
    """Create a standard port output pin."""
    return CodeckNodePinDefinition(
        name=name,
        type='port',
        position=QPointF(build_pin_pos_x(width, 'output'), build_pin_pos_y(position)),
        render_type=label or name
    )


def exec_pin_custom_output(name: str, width: int, position: int, label: str = None) -> CodeckNodePinDefinition:
    """Create a custom execution output pin."""
    return CodeckNodePinDefinition(
        name=name,
        type='exec',
        position=QPointF(build_pin_pos_x(width, 'output'), build_pin_pos_y(position)),
        render_type=label or name
    )
