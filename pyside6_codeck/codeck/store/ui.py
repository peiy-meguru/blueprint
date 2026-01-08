"""UI store for managing selection state."""

from typing import Optional
from PySide6.QtCore import QObject, Signal

from .connection import ConnectionStore
from .node import NodeStore


class UIStore(QObject):
    """Store for managing UI selection state."""
    
    # Signals
    selection_changed = Signal()
    
    _instance: Optional['UIStore'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self.selected_node_ids: list[str] = []
        self.selected_connection_ids: list[str] = []
    
    @classmethod
    def get_instance(cls) -> 'UIStore':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def add_selected_nodes(self, node_ids: list[str]) -> None:
        """Add nodes to selection."""
        for node_id in node_ids:
            if node_id not in self.selected_node_ids:
                self.selected_node_ids.append(node_id)
        self.selection_changed.emit()
    
    def switch_select_nodes(self, node_ids: list[str]) -> None:
        """Toggle node selection."""
        if len(node_ids) == 1 and node_ids[0] in self.selected_node_ids:
            self.selected_node_ids.remove(node_ids[0])
        else:
            for node_id in node_ids:
                if node_id not in self.selected_node_ids:
                    self.selected_node_ids.append(node_id)
        self.selection_changed.emit()
    
    def add_selected_connections(self, connection_ids: list[str]) -> None:
        """Add/toggle connections in selection."""
        if len(connection_ids) == 1 and connection_ids[0] in self.selected_connection_ids:
            self.selected_connection_ids.remove(connection_ids[0])
        else:
            for conn_id in connection_ids:
                if conn_id not in self.selected_connection_ids:
                    self.selected_connection_ids.append(conn_id)
        self.selection_changed.emit()
    
    def clear_selected_status(self) -> None:
        """Clear all selection."""
        self.selected_node_ids.clear()
        self.selected_connection_ids.clear()
        self.selection_changed.emit()
    
    def delete_all_selected(self) -> None:
        """Delete all selected nodes and connections."""
        connection_store = ConnectionStore.get_instance()
        node_store = NodeStore.get_instance()
        
        # Remove selected connections
        for conn_id in self.selected_connection_ids:
            connection_store.remove_connection(conn_id)
        
        # Remove selected nodes
        for node_id in self.selected_node_ids:
            node_store.remove_node(node_id)
        
        self.selected_node_ids.clear()
        self.selected_connection_ids.clear()
        self.selection_changed.emit()
    
    def move_selected(self, delta_x: float, delta_y: float) -> None:
        """Move all selected nodes."""
        node_store = NodeStore.get_instance()
        
        for node_id in self.selected_node_ids:
            node_store.move_node(node_id, delta_x, delta_y)
