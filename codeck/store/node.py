"""Node store for managing nodes and their definitions."""

from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Optional, TYPE_CHECKING
from PySide6.QtCore import QObject, Signal, QPointF

from ..utils.string_helper import generate_node_id
from ..utils.consts import BEGIN_NODE_ID
from .connection import ConnectionStore

if TYPE_CHECKING:
    from PySide6.QtWidgets import QGraphicsItem


CodeckNodeType = Literal['begin', 'return', 'function', 'logic', 'call']
CodeckNodePortType = Literal['port', 'exec']


@dataclass
class CodeckNode:
    """A node instance in the blueprint."""
    id: str
    name: str  # Reference to CodeckNodeDefinition name
    position: QPointF
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeckNodePinDefinition:
    """Definition of a node pin (input/output port)."""
    name: str
    type: CodeckNodePortType
    position: QPointF
    default_value: Any = None
    render_type: Optional[str] = None
    input_type: Optional[str] = None  # 'text', 'number', 'boolean', 'select', 'textarea'


@dataclass
class CodeImportPrepare:
    """Import preparation for code generation."""
    type: str = 'import'
    module: str = ''
    member: Optional[str | tuple[str, str]] = None
    version: Optional[str] = None


@dataclass
class CodeFunctionPrepare:
    """Function preparation for code generation."""
    type: str = 'function'
    name: str = ''
    parameters: list[str] = field(default_factory=list)
    body: str = ''


CodePrepare = CodeImportPrepare | CodeFunctionPrepare


class CodeckNodeDefinition:
    """Definition of a node type."""
    
    def __init__(
        self,
        name: str,
        label: str,
        node_type: CodeckNodeType,
        width: int,
        height: int,
        category: str,
        inputs: list[CodeckNodePinDefinition],
        outputs: list[CodeckNodePinDefinition],
        hidden: bool = False,
        prepare: Optional[list[CodePrepare]] = None,
        code_fn: Optional[Callable] = None,
        output_code_fns: Optional[dict[str, Callable]] = None
    ):
        self.name = name
        self.label = label
        self.type = node_type
        self.width = width
        self.height = height
        self.category = category
        self.inputs = inputs
        self.outputs = outputs
        self.hidden = hidden
        self.prepare = prepare or []
        self.code_fn = code_fn
        self.output_code_fns = output_code_fns or {}


class NodeStore(QObject):
    """Store for managing nodes and their definitions."""
    
    # Signals
    nodes_changed = Signal()
    node_position_changed = Signal(str)  # node_id
    node_data_changed = Signal(str)  # node_id
    
    _instance: Optional['NodeStore'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self.node_map: dict[str, CodeckNode] = {}
        self.node_definition: dict[str, CodeckNodeDefinition] = {}
        self._init_default_nodes()
    
    def _init_default_nodes(self):
        """Initialize with default Begin node."""
        # Will be called after node definitions are registered
        pass
    
    @classmethod
    def get_instance(cls) -> 'NodeStore':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def reg_node(self, definition: CodeckNodeDefinition) -> None:
        """Register a node definition."""
        if definition.name in self.node_definition:
            print(f'Warning: Node "{definition.name}" is already registered')
            return
        
        self.node_definition[definition.name] = definition
    
    def update_node_pos(self, node_id: str, position: QPointF) -> None:
        """Update a node's position."""
        node = self.node_map.get(node_id)
        if not node:
            print(f'Warning: Node "{node_id}" not found')
            return
        
        node.position = position
        self.node_position_changed.emit(node_id)
    
    def move_node(self, node_id: str, delta_x: float, delta_y: float) -> None:
        """Move a node by delta."""
        node = self.node_map.get(node_id)
        if not node:
            print(f'Warning: Node "{node_id}" not found')
            return
        
        node.position = QPointF(
            node.position.x() + delta_x,
            node.position.y() + delta_y
        )
        self.node_position_changed.emit(node_id)
    
    def get_node_definition(self, node_id: str) -> Optional[CodeckNodeDefinition]:
        """Get the definition for a node."""
        node = self.node_map.get(node_id)
        if not node:
            return None
        
        return self.node_definition.get(node.name)
    
    def get_pin_definition_by_name(
        self,
        node_id: str,
        pin_name: str
    ) -> Optional[CodeckNodePinDefinition]:
        """Get a pin definition by name."""
        definition = self.get_node_definition(node_id)
        if not definition:
            return None
        
        all_pins = definition.inputs + definition.outputs
        for pin in all_pins:
            if pin.name == pin_name:
                return pin
        
        return None
    
    def create_node(
        self,
        node_name: str,
        position: QPointF,
        data: Optional[dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new node.
        
        Returns:
            The node ID if created successfully, None otherwise
        """
        if node_name not in self.node_definition:
            print(f'Warning: Node definition "{node_name}" not found')
            return None
        
        node_id = generate_node_id()
        self.node_map[node_id] = CodeckNode(
            id=node_id,
            name=node_name,
            position=position,
            data=data or {}
        )
        self.nodes_changed.emit()
        return node_id
    
    def set_node_data(self, node_id: str, key: str, value: Any) -> None:
        """Set data on a node."""
        node = self.node_map.get(node_id)
        if not node:
            print(f'Warning: Node "{node_id}" not found')
            return
        
        node.data[key] = value
        self.node_data_changed.emit(node_id)
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node."""
        if node_id == BEGIN_NODE_ID:
            # Cannot delete begin node
            return
        
        if node_id not in self.node_map:
            return
        
        # Remove connections for this node
        connection_store = ConnectionStore.get_instance()
        connections_to_remove = connection_store.get_connections_for_node(node_id)
        for conn in connections_to_remove:
            connection_store.remove_connection(conn.id)
        
        del self.node_map[node_id]
        self.nodes_changed.emit()
    
    def reset_nodes(self) -> None:
        """Reset all nodes to default state."""
        self.node_map.clear()
        
        # Clear connections
        connection_store = ConnectionStore.get_instance()
        connection_store.clear_connections()
        
        # Add default Begin node
        if 'begin' in self.node_definition:
            self.node_map[BEGIN_NODE_ID] = CodeckNode(
                id=BEGIN_NODE_ID,
                name='begin',
                position=QPointF(10, 10)
            )
            
            # Add default Log node
            if 'log' in self.node_definition:
                self.node_map['log'] = CodeckNode(
                    id='log',
                    name='log',
                    position=QPointF(240, 10),
                    data={'message': 'Hello World'}
                )
        
        self.nodes_changed.emit()
    
    def get_all_nodes(self) -> list[CodeckNode]:
        """Get all nodes."""
        return list(self.node_map.values())
    
    def get_all_visible_definitions(self) -> list[CodeckNodeDefinition]:
        """Get all non-hidden node definitions."""
        return [d for d in self.node_definition.values() if not d.hidden]


def regNode(definition: CodeckNodeDefinition) -> None:
    """Register a node definition (convenience function)."""
    NodeStore.get_instance().reg_node(definition)
