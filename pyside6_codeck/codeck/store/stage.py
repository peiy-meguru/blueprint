"""Stage store for managing the canvas/stage state."""

from typing import Optional
from PySide6.QtCore import QObject, Signal, QPointF


class StageStore(QObject):
    """Store for managing stage (canvas) state."""
    
    # Signals
    stage_changed = Signal()
    scale_changed = Signal()
    position_changed = Signal()
    
    _instance: Optional['StageStore'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self.width = 800
        self.height = 600
        self.scale = 1.0
        self.position = QPointF(0, 0)
    
    @classmethod
    def get_instance(cls) -> 'StageStore':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_size(self, width: int, height: int) -> None:
        """Set the stage size."""
        self.width = width
        self.height = height
        self.stage_changed.emit()
    
    def set_scale(self, new_scale: float) -> None:
        """Set the stage scale (zoom level)."""
        self.scale = max(0.1, min(5.0, new_scale))  # Clamp between 0.1 and 5.0
        self.scale_changed.emit()
    
    def set_position(self, position: QPointF) -> None:
        """Set the stage position (pan offset)."""
        self.position = position
        self.position_changed.emit()
    
    def unscale(self, position: QPointF) -> QPointF:
        """Convert a position from scaled to unscaled coordinates."""
        return QPointF(
            position.x() / self.scale,
            position.y() / self.scale
        )
    
    def calc_absolute_to_relative(self, absolute_pos: QPointF) -> QPointF:
        """Convert absolute screen position to relative stage position."""
        return self.unscale(QPointF(
            absolute_pos.x() - self.position.x(),
            absolute_pos.y() - self.position.y()
        ))
    
    def focus(self) -> None:
        """Focus the view on the nodes."""
        from .node import NodeStore
        
        nodes = NodeStore.get_instance().get_all_nodes()
        if not nodes:
            return
        
        # Find minimum position
        min_x = min(node.position.x() for node in nodes)
        min_y = min(node.position.y() for node in nodes)
        
        self.set_position(QPointF(-min_x + 40, -min_y + 40))
        self.set_scale(1.0)
