"""Size helper utilities for node positioning."""

from .consts import NODE_TITLE_HEIGHT

PIN_HEIGHT = 20


def build_pin_pos_x(width: int, pin_type: str) -> int:
    """Build the X coordinate for a pin position.
    
    Args:
        width: Node width
        pin_type: Either 'input' or 'output'
    
    Returns:
        X coordinate position
    """
    if pin_type == 'output':
        return width - 14
    return 14


def build_pin_pos_y(position: int) -> int:
    """Build the Y coordinate for a pin position.
    
    Args:
        position: Position index (0-based)
    
    Returns:
        Y coordinate position
        
    Examples:
        position 0 -> 16
        position 1 -> 50
        position 2 -> 70
        position 3 -> 90
    """
    return position * PIN_HEIGHT + 16 + (NODE_TITLE_HEIGHT - 18 if position > 0 else 0)


# Default node width
DEFAULT_NODE_WIDTH = 150


def build_node_height(slot_num: int) -> int:
    """Calculate node height based on number of slots.
    
    Args:
        slot_num: Number of pin slots needed
    
    Returns:
        Node height
        
    Examples:
        1 slot -> 70
        2 slots -> 90
        4 slots -> 130
    """
    slot_num = max(slot_num, 0)
    return NODE_TITLE_HEIGHT + 16 + slot_num * PIN_HEIGHT + 2
