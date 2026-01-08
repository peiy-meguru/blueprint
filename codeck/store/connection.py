"""Connection store for managing node connections."""

from dataclasses import dataclass, field
from typing import Callable, Literal, Optional
from PySide6.QtCore import QObject, Signal

from ..utils.string_helper import generate_node_id


@dataclass
class ConnectInfo:
    """Information about a connection between nodes."""
    id: str
    from_node_id: str
    from_node_pin_name: str
    to_node_id: str
    to_node_pin_name: str


PinDirection = Literal['out-in', 'in-out']
PinType = Literal['port', 'exec']


@dataclass
class WorkingConnection:
    """Information about connection currently being created."""
    from_node_id: str
    from_node_pin_name: str
    from_node_pin_type: PinType
    from_node_direction: PinDirection


class ConnectionStore(QObject):
    """Store for managing connections between nodes."""
    
    # Signals
    connections_changed = Signal()
    working_connection_changed = Signal()
    
    _instance: Optional['ConnectionStore'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self.connections: list[ConnectInfo] = []
        self.working_connection: Optional[WorkingConnection] = None
    
    @classmethod
    def get_instance(cls) -> 'ConnectionStore':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def start_connect(
        self,
        from_node_id: str,
        from_node_pin_name: str,
        from_node_pin_type: PinType,
        from_node_direction: PinDirection
    ) -> None:
        """Start a new connection."""
        if self.working_connection:
            return
        
        self.working_connection = WorkingConnection(
            from_node_id=from_node_id,
            from_node_pin_name=from_node_pin_name,
            from_node_pin_type=from_node_pin_type,
            from_node_direction=from_node_direction
        )
        self.working_connection_changed.emit()
    
    def end_connect(
        self,
        to_node_id: str,
        to_node_pin_name: str,
        to_node_pin_type: PinType,
        to_node_direction: PinDirection
    ) -> None:
        """End a connection."""
        if not self.working_connection:
            return
        
        working = self.working_connection
        
        # Cannot connect to the same node
        if to_node_id == working.from_node_id:
            self.cancel_connect()
            return
        
        # Cannot connect same direction
        if to_node_direction == working.from_node_direction:
            self.cancel_connect()
            return
        
        # Cannot connect different types
        if to_node_pin_type != working.from_node_pin_type:
            self.cancel_connect()
            return
        
        # Handle exec connections (one-to-one)
        if working.from_node_pin_type == 'exec':
            connections_to_remove = [
                conn for conn in self.connections
                if (conn.from_node_id == working.from_node_id and
                    conn.from_node_pin_name == working.from_node_pin_name) or
                   (conn.to_node_id == working.from_node_id and
                    conn.to_node_pin_name == working.from_node_pin_name) or
                   (conn.from_node_id == to_node_id and
                    conn.from_node_pin_name == to_node_pin_name) or
                   (conn.to_node_id == to_node_id and
                    conn.to_node_pin_name == to_node_pin_name)
            ]
            for conn in connections_to_remove:
                self.connections.remove(conn)
        
        # Handle port connections (one-to-many output, but one-to-one input)
        elif working.from_node_pin_type == 'port':
            if working.from_node_direction == 'out-in':
                connections_to_remove = [
                    conn for conn in self.connections
                    if conn.to_node_id == to_node_id and
                       conn.to_node_pin_name == to_node_pin_name
                ]
            else:
                connections_to_remove = [
                    conn for conn in self.connections
                    if conn.to_node_id == working.from_node_id and
                       conn.to_node_pin_name == working.from_node_pin_name
                ]
            for conn in connections_to_remove:
                self.connections.remove(conn)
        
        # Create new connection
        if working.from_node_direction == 'out-in':
            new_connection = ConnectInfo(
                id=generate_node_id(),
                from_node_id=working.from_node_id,
                from_node_pin_name=working.from_node_pin_name,
                to_node_id=to_node_id,
                to_node_pin_name=to_node_pin_name
            )
        else:
            new_connection = ConnectInfo(
                id=generate_node_id(),
                from_node_id=to_node_id,
                from_node_pin_name=to_node_pin_name,
                to_node_id=working.from_node_id,
                to_node_pin_name=working.from_node_pin_name
            )
        
        # Check for duplicates
        existing = [
            conn for conn in self.connections
            if conn.from_node_id == new_connection.from_node_id and
               conn.from_node_pin_name == new_connection.from_node_pin_name and
               conn.to_node_id == new_connection.to_node_id and
               conn.to_node_pin_name == new_connection.to_node_pin_name
        ]
        if not existing:
            self.connections.append(new_connection)
        
        self.cancel_connect()
        self.connections_changed.emit()
    
    def cancel_connect(self) -> None:
        """Cancel the current connection operation."""
        self.working_connection = None
        self.working_connection_changed.emit()
    
    def check_is_connected(self, node_id: str, pin_name: str) -> bool:
        """Check if a pin is connected."""
        if (self.working_connection and
            self.working_connection.from_node_id == node_id and
            self.working_connection.from_node_pin_name == pin_name):
            return True
        
        return any(
            (c.from_node_id == node_id and c.from_node_pin_name == pin_name) or
            (c.to_node_id == node_id and c.to_node_pin_name == pin_name)
            for c in self.connections
        )
    
    def remove_connection(self, connection_id: str) -> None:
        """Remove a connection by ID."""
        self.connections = [c for c in self.connections if c.id != connection_id]
        self.connections_changed.emit()
    
    def clear_connections(self) -> None:
        """Clear all connections."""
        self.connections.clear()
        self.connections_changed.emit()
    
    def get_connections_for_node(self, node_id: str) -> list[ConnectInfo]:
        """Get all connections involving a node."""
        return [
            c for c in self.connections
            if c.from_node_id == node_id or c.to_node_id == node_id
        ]
