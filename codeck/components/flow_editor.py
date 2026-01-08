"""Flow Editor - Main canvas for node-based visual programming."""

import math
from typing import Optional
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem,
    QGraphicsEllipseItem, QGraphicsPathItem, QMenu, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QLineF
from PySide6.QtGui import (
    QPen, QBrush, QColor, QPainterPath, QLinearGradient, QPainter,
    QFont, QWheelEvent, QMouseEvent, QKeyEvent, QContextMenuEvent
)

from ..store.node import NodeStore, CodeckNodeDefinition, CodeckNodePinDefinition
from ..store.connection import ConnectionStore
from ..store.variable import VariableStore
from ..store.ui import UIStore
from ..store.stage import StageStore
from ..store.settings import SettingsStore, tr
from ..utils.color import color
from ..utils.consts import NODE_TITLE_HEIGHT, BEGIN_NODE_ID


class ConnectionItem(QGraphicsPathItem):
    """A bezier curve connection between nodes."""
    
    def __init__(self, connection_id: str, from_pos: QPointF, to_pos: QPointF, direction: str = 'out-in'):
        super().__init__()
        self.connection_id = connection_id
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.direction = direction
        self._is_active = False
        
        self.setPen(QPen(Qt.white, 2))
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self._update_path()
    
    def set_active(self, active: bool):
        """Set whether the connection is highlighted."""
        self._is_active = active
        if active:
            self.setPen(QPen(Qt.white, 4))
        else:
            self.setPen(QPen(Qt.white, 2))
    
    def update_positions(self, from_pos: QPointF, to_pos: QPointF):
        """Update the connection endpoints."""
        self.from_pos = from_pos
        self.to_pos = to_pos
        self._update_path()
    
    def _update_path(self):
        """Update the bezier path."""
        path = QPainterPath()
        path.moveTo(self.from_pos)
        
        dir_mult = 1 if self.direction == 'out-in' else -1
        
        dx = self.to_pos.x() - self.from_pos.x()
        dy = abs(self.to_pos.y() - self.from_pos.y())
        
        hold_len = dx / 3
        hold_len = dir_mult * (abs(hold_len) + dy / 4)
        
        mid1 = QPointF(self.from_pos.x() + hold_len, self.from_pos.y())
        mid2 = QPointF(self.to_pos.x() - hold_len, self.to_pos.y())
        
        path.cubicTo(mid1, mid2, self.to_pos)
        self.setPath(path)
    
    def mousePressEvent(self, event):
        """Handle mouse press on connection."""
        if event.button() == Qt.LeftButton:
            ui_store = UIStore.get_instance()
            if not event.modifiers() & Qt.ShiftModifier:
                ui_store.clear_selected_status()
            ui_store.add_selected_connections([self.connection_id])
        super().mousePressEvent(event)


class PinItem(QGraphicsEllipseItem):
    """A pin (port) on a node."""
    
    def __init__(self, node_id: str, pin_def: CodeckNodePinDefinition, parent: QGraphicsItem = None):
        self.pin_size = 6
        super().__init__(-self.pin_size, -self.pin_size, self.pin_size * 2, self.pin_size * 2, parent)
        
        self.node_id = node_id
        self.pin_def = pin_def
        self.is_exec = pin_def.type == 'exec'
        
        self.setPos(pin_def.position)
        self.setPen(QPen(Qt.white, 2))
        self.setBrush(QBrush(Qt.transparent))
        self.setAcceptHoverEvents(True)
        
        # Create pin label
        if pin_def.render_type:
            is_output = pin_def.position.x() > 75  # Rough check for output side
            label = QGraphicsTextItem(pin_def.render_type, parent)
            label.setDefaultTextColor(Qt.white)
            label.setFont(QFont('Arial', 9))
            
            if is_output:
                # Right-align for output pins
                text_width = label.boundingRect().width()
                label.setPos(pin_def.position.x() - text_width - 15, pin_def.position.y() - 8)
            else:
                label.setPos(pin_def.position.x() + 10, pin_def.position.y() - 8)
    
    def set_connected(self, connected: bool):
        """Set whether the pin is connected."""
        if connected:
            self.setBrush(QBrush(Qt.white))
        else:
            self.setBrush(QBrush(Qt.transparent))
    
    def hoverEnterEvent(self, event):
        self.setPen(QPen(Qt.white, 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setPen(QPen(Qt.white, 2))
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Start a connection."""
        if event.button() == Qt.LeftButton:
            # Determine direction based on position
            is_output = self.pin_def.position.x() > 75
            direction = 'out-in' if is_output else 'in-out'
            
            connection_store = ConnectionStore.get_instance()
            connection_store.start_connect(
                self.node_id,
                self.pin_def.name,
                self.pin_def.type,
                direction
            )
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """End a connection."""
        if event.button() == Qt.LeftButton:
            connection_store = ConnectionStore.get_instance()
            if connection_store.working_connection:
                is_output = self.pin_def.position.x() > 75
                direction = 'out-in' if is_output else 'in-out'
                
                connection_store.end_connect(
                    self.node_id,
                    self.pin_def.name,
                    self.pin_def.type,
                    direction
                )
            event.accept()


class ExecPinItem(QGraphicsPathItem):
    """An execution pin (arrow shape) on a node."""
    
    def __init__(self, node_id: str, pin_def: CodeckNodePinDefinition, parent: QGraphicsItem = None):
        super().__init__(parent)
        
        self.pin_size = 6
        self.node_id = node_id
        self.pin_def = pin_def
        
        self.setPos(pin_def.position)
        self.setPen(QPen(Qt.white, 2))
        self.setBrush(QBrush(Qt.transparent))
        self.setAcceptHoverEvents(True)
        
        # Create arrow shape
        path = QPainterPath()
        path.moveTo(self.pin_size, 0)
        path.lineTo(0, -self.pin_size)
        path.lineTo(-self.pin_size, -self.pin_size)
        path.lineTo(-self.pin_size, self.pin_size)
        path.lineTo(0, self.pin_size)
        path.closeSubpath()
        self.setPath(path)
        
        # Create pin label
        if pin_def.render_type:
            is_output = pin_def.position.x() > 75
            label = QGraphicsTextItem(pin_def.render_type, parent)
            label.setDefaultTextColor(Qt.white)
            label.setFont(QFont('Arial', 9))
            
            if is_output:
                text_width = label.boundingRect().width()
                label.setPos(pin_def.position.x() - text_width - 15, pin_def.position.y() - 8)
            else:
                label.setPos(pin_def.position.x() + 10, pin_def.position.y() - 8)
    
    def set_connected(self, connected: bool):
        """Set whether the pin is connected."""
        if connected:
            self.setBrush(QBrush(Qt.white))
        else:
            self.setBrush(QBrush(Qt.transparent))
    
    def hoverEnterEvent(self, event):
        self.setPen(QPen(Qt.white, 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setPen(QPen(Qt.white, 2))
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Start a connection."""
        if event.button() == Qt.LeftButton:
            is_output = self.pin_def.position.x() > 75
            direction = 'out-in' if is_output else 'in-out'
            
            connection_store = ConnectionStore.get_instance()
            connection_store.start_connect(
                self.node_id,
                self.pin_def.name,
                self.pin_def.type,
                direction
            )
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """End a connection."""
        if event.button() == Qt.LeftButton:
            connection_store = ConnectionStore.get_instance()
            if connection_store.working_connection:
                is_output = self.pin_def.position.x() > 75
                direction = 'out-in' if is_output else 'in-out'
                
                connection_store.end_connect(
                    self.node_id,
                    self.pin_def.name,
                    self.pin_def.type,
                    direction
                )
            event.accept()


class NodeItem(QGraphicsRectItem):
    """A visual node in the flow editor."""
    
    def __init__(self, node_id: str, definition: CodeckNodeDefinition):
        super().__init__(0, 0, definition.width, definition.height)
        
        self.node_id = node_id
        self.definition = definition
        self.pins: dict[str, PinItem | ExecPinItem] = {}
        
        # Set up appearance
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, definition.width, definition.height)
        gradient.setColorAt(0, color['nodeBoxGradient']['start'])
        gradient.setColorAt(1, color['nodeBoxGradient']['end'])
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(Qt.transparent))
        self.setOpacity(0.9)
        
        # Title bar
        self.title_rect = QGraphicsRectItem(0, 0, definition.width, NODE_TITLE_HEIGHT, self)
        title_color = color['node'].get(definition.type, QColor('#0984e3'))
        self.title_rect.setBrush(QBrush(title_color))
        self.title_rect.setPen(QPen(Qt.transparent))
        
        # Title text
        self.title_text = QGraphicsTextItem(definition.label, self)
        self.title_text.setDefaultTextColor(Qt.white)
        self.title_text.setFont(QFont('Arial', 11, QFont.Bold))
        self.title_text.setPos(10, 5)
        
        # Create pins
        for pin_def in definition.inputs:
            self._create_pin(node_id, pin_def)
        
        for pin_def in definition.outputs:
            self._create_pin(node_id, pin_def)
    
    def _create_pin(self, node_id: str, pin_def: CodeckNodePinDefinition):
        """Create a pin item."""
        if pin_def.type == 'exec':
            pin = ExecPinItem(node_id, pin_def, self)
        else:
            pin = PinItem(node_id, pin_def, self)
        self.pins[pin_def.name] = pin
    
    def update_pin_connections(self):
        """Update pin connection states."""
        connection_store = ConnectionStore.get_instance()
        for name, pin in self.pins.items():
            connected = connection_store.check_is_connected(self.node_id, name)
            pin.set_connected(connected)
    
    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update node position in store
            node_store = NodeStore.get_instance()
            node_store.update_node_pos(self.node_id, self.pos())
        
        return super().itemChange(change, value)
    
    def paint(self, painter, option, widget=None):
        """Paint the node with selection highlight."""
        super().paint(painter, option, widget)
        
        # Draw selection border
        if self.isSelected():
            painter.setPen(QPen(Qt.white, 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.rect(), 5, 5)


class VariableNodeItem(QGraphicsRectItem):
    """A variable node (Get/Set) in the flow editor."""
    
    def __init__(self, node_id: str, definition: CodeckNodeDefinition, var_name: str, is_getter: bool = True):
        super().__init__(0, 0, definition.width, 34)
        
        self.node_id = node_id
        self.definition = definition
        self.var_name = var_name
        self.is_getter = is_getter
        self.pins: dict[str, PinItem | ExecPinItem] = {}
        
        # Set up appearance
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, definition.width, definition.height)
        gradient.setColorAt(0, color['variable']['data'])
        gradient.setColorAt(1, color['nodeBoxGradient']['end'])
        self.setBrush(QBrush(gradient))
        self.setPen(QPen(Qt.transparent))
        self.setOpacity(0.9)
        
        # Title text
        prefix = 'Get' if is_getter else 'Set'
        title = QGraphicsTextItem(f'{prefix} {var_name}', self)
        title.setDefaultTextColor(Qt.white)
        title.setFont(QFont('Arial', 11))
        title.setPos(14, 5)
        
        # Create pins
        for pin_def in definition.inputs:
            self._create_pin(node_id, pin_def)
        
        for pin_def in definition.outputs:
            self._create_pin(node_id, pin_def)
    
    def _create_pin(self, node_id: str, pin_def: CodeckNodePinDefinition):
        """Create a pin item."""
        if pin_def.type == 'exec':
            pin = ExecPinItem(node_id, pin_def, self)
        else:
            pin = PinItem(node_id, pin_def, self)
        self.pins[pin_def.name] = pin
    
    def update_pin_connections(self):
        """Update pin connection states."""
        connection_store = ConnectionStore.get_instance()
        for name, pin in self.pins.items():
            connected = connection_store.check_is_connected(self.node_id, name)
            pin.set_connected(connected)
    
    def itemChange(self, change, value):
        """Handle item changes."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            node_store = NodeStore.get_instance()
            node_store.update_node_pos(self.node_id, self.pos())
        
        return super().itemChange(change, value)
    
    def paint(self, painter, option, widget=None):
        """Paint the node with selection highlight."""
        super().paint(painter, option, widget)
        
        if self.isSelected():
            painter.setPen(QPen(Qt.white, 3))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.rect(), 5, 5)


class FlowEditorScene(QGraphicsScene):
    """The scene containing all nodes and connections."""
    
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QBrush(QColor('#1e1e1e')))
        
        self.node_items: dict[str, NodeItem | VariableNodeItem] = {}
        self.connection_items: dict[str, ConnectionItem] = {}
        self.working_connection_item: Optional[ConnectionItem] = None
        
        # Connect to stores
        self._connect_stores()
        
        # Draw grid
        self._draw_grid()
    
    def _connect_stores(self):
        """Connect to store signals."""
        node_store = NodeStore.get_instance()
        connection_store = ConnectionStore.get_instance()
        
        node_store.nodes_changed.connect(self._on_nodes_changed)
        node_store.node_position_changed.connect(self._on_node_position_changed)
        connection_store.connections_changed.connect(self._on_connections_changed)
        connection_store.working_connection_changed.connect(self._on_working_connection_changed)
    
    def _draw_grid(self):
        """Draw background grid."""
        step = 40
        grid_pen = QPen(QColor(255, 255, 255, 50), 1)
        
        # Draw vertical lines
        for x in range(-2000, 2001, step):
            line = self.addLine(x, -2000, x, 2000, grid_pen)
            line.setZValue(-100)
        
        # Draw horizontal lines
        for y in range(-2000, 2001, step):
            line = self.addLine(-2000, y, 2000, y, grid_pen)
            line.setZValue(-100)
    
    def _on_nodes_changed(self):
        """Handle nodes changed."""
        self.rebuild_nodes()
    
    def _on_node_position_changed(self, node_id: str):
        """Handle node position changed."""
        self.update_connections()
    
    def _on_connections_changed(self):
        """Handle connections changed."""
        self.rebuild_connections()
    
    def _on_working_connection_changed(self):
        """Handle working connection changed."""
        connection_store = ConnectionStore.get_instance()
        
        if connection_store.working_connection:
            # Create temporary connection line
            working = connection_store.working_connection
            node_store = NodeStore.get_instance()
            
            node = node_store.node_map.get(working.from_node_id)
            if not node:
                return
            
            pin_def = node_store.get_pin_definition_by_name(
                working.from_node_id,
                working.from_node_pin_name
            )
            if not pin_def:
                return
            
            from_pos = QPointF(
                node.position.x() + pin_def.position.x(),
                node.position.y() + pin_def.position.y()
            )
            
            if self.working_connection_item:
                self.removeItem(self.working_connection_item)
            
            self.working_connection_item = ConnectionItem(
                '_working',
                from_pos,
                from_pos,
                working.from_node_direction
            )
            self.working_connection_item.setPen(QPen(Qt.white, 2, Qt.DashLine))
            self.addItem(self.working_connection_item)
        else:
            # Remove temporary connection line
            if self.working_connection_item:
                self.removeItem(self.working_connection_item)
                self.working_connection_item = None
    
    def update_working_connection(self, mouse_pos: QPointF):
        """Update the working connection to follow mouse."""
        if self.working_connection_item:
            self.working_connection_item.update_positions(
                self.working_connection_item.from_pos,
                mouse_pos
            )
    
    def rebuild_nodes(self):
        """Rebuild all node items."""
        # Remove existing node items
        for item in list(self.node_items.values()):
            self.removeItem(item)
        self.node_items.clear()
        
        # Create new node items
        node_store = NodeStore.get_instance()
        for node in node_store.get_all_nodes():
            definition = node_store.get_node_definition(node.id)
            if not definition:
                continue
            
            # Check if this is a variable node
            if node.name in ('varget', 'varset'):
                var_name = node.data.get('name', 'unknown')
                is_getter = node.name == 'varget'
                item = VariableNodeItem(node.id, definition, var_name, is_getter)
            else:
                item = NodeItem(node.id, definition)
            
            item.setPos(node.position)
            self.addItem(item)
            self.node_items[node.id] = item
        
        # Update connections
        self.rebuild_connections()
    
    def rebuild_connections(self):
        """Rebuild all connection items."""
        # Remove existing connection items
        for item in list(self.connection_items.values()):
            self.removeItem(item)
        self.connection_items.clear()
        
        # Create new connection items
        connection_store = ConnectionStore.get_instance()
        node_store = NodeStore.get_instance()
        
        for conn in connection_store.connections:
            from_node = node_store.node_map.get(conn.from_node_id)
            to_node = node_store.node_map.get(conn.to_node_id)
            
            if not from_node or not to_node:
                continue
            
            from_pin = node_store.get_pin_definition_by_name(
                conn.from_node_id,
                conn.from_node_pin_name
            )
            to_pin = node_store.get_pin_definition_by_name(
                conn.to_node_id,
                conn.to_node_pin_name
            )
            
            if not from_pin or not to_pin:
                continue
            
            from_pos = QPointF(
                from_node.position.x() + from_pin.position.x(),
                from_node.position.y() + from_pin.position.y()
            )
            to_pos = QPointF(
                to_node.position.x() + to_pin.position.x(),
                to_node.position.y() + to_pin.position.y()
            )
            
            item = ConnectionItem(conn.id, from_pos, to_pos)
            item.setZValue(-1)
            self.addItem(item)
            self.connection_items[conn.id] = item
        
        # Update pin connection states
        for node_item in self.node_items.values():
            node_item.update_pin_connections()
    
    def update_connections(self):
        """Update connection positions without rebuilding."""
        connection_store = ConnectionStore.get_instance()
        node_store = NodeStore.get_instance()
        
        for conn in connection_store.connections:
            if conn.id not in self.connection_items:
                continue
            
            from_node = node_store.node_map.get(conn.from_node_id)
            to_node = node_store.node_map.get(conn.to_node_id)
            
            if not from_node or not to_node:
                continue
            
            from_pin = node_store.get_pin_definition_by_name(
                conn.from_node_id,
                conn.from_node_pin_name
            )
            to_pin = node_store.get_pin_definition_by_name(
                conn.to_node_id,
                conn.to_node_pin_name
            )
            
            if not from_pin or not to_pin:
                continue
            
            from_pos = QPointF(
                from_node.position.x() + from_pin.position.x(),
                from_node.position.y() + from_pin.position.y()
            )
            to_pos = QPointF(
                to_node.position.x() + to_pin.position.x(),
                to_node.position.y() + to_pin.position.y()
            )
            
            self.connection_items[conn.id].update_positions(from_pos, to_pos)


class FlowEditorView(QGraphicsView):
    """The view for the flow editor with zoom and pan."""
    
    def __init__(self):
        super().__init__()
        
        self.flow_scene = FlowEditorScene()
        self.setScene(self.flow_scene)
        
        # View settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)
        
        # Panning state
        self._is_panning = False
        self._pan_start = QPointF()
        self._space_pressed = False
        
        self.setMinimumSize(400, 300)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle zoom with mouse wheel."""
        zoom_factor = 1.15
        
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for panning."""
        if event.button() == Qt.MiddleButton or self._space_pressed:
            self._is_panning = True
            self._pan_start = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            # Cancel working connection on right click
            if event.button() == Qt.RightButton:
                connection_store = ConnectionStore.get_instance()
                if connection_store.working_connection:
                    connection_store.cancel_connect()
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release."""
        if event.button() == Qt.MiddleButton or (self._is_panning and event.button() == Qt.LeftButton):
            self._is_panning = False
            if self._space_pressed:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            # Cancel working connection if releasing on empty space
            connection_store = ConnectionStore.get_instance()
            if connection_store.working_connection:
                connection_store.cancel_connect()
            super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for panning and working connection."""
        if self._is_panning:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            
            # Pan the view
            self.horizontalScrollBar().setValue(
                int(self.horizontalScrollBar().value() - delta.x())
            )
            self.verticalScrollBar().setValue(
                int(self.verticalScrollBar().value() - delta.y())
            )
            event.accept()
        else:
            # Update working connection position
            connection_store = ConnectionStore.get_instance()
            if connection_store.working_connection:
                scene_pos = self.mapToScene(event.position().toPoint())
                self.flow_scene.update_working_connection(scene_pos)
            
            super().mouseMoveEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press."""
        if event.key() == Qt.Key_Space:
            self._space_pressed = True
            self.setCursor(Qt.OpenHandCursor)
        elif event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            UIStore.get_instance().delete_all_selected()
        elif event.key() == Qt.Key_F:
            StageStore.get_instance().focus()
            self.centerOn(0, 0)
        elif event.key() == Qt.Key_Escape:
            ConnectionStore.get_instance().cancel_connect()
        
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        """Handle key release."""
        if event.key() == Qt.Key_Space:
            self._space_pressed = False
            if not self._is_panning:
                self.setCursor(Qt.ArrowCursor)
        
        super().keyReleaseEvent(event)
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """Show context menu for adding nodes."""
        # Don't show menu if there's a working connection
        connection_store = ConnectionStore.get_instance()
        if connection_store.working_connection:
            connection_store.cancel_connect()
            return
        
        menu = QMenu(self)
        
        # Get all node definitions grouped by category
        node_store = NodeStore.get_instance()
        definitions = node_store.get_all_visible_definitions()
        
        # Group by category
        categories: dict[str, list[CodeckNodeDefinition]] = {}
        for defn in definitions:
            if defn.category not in categories:
                categories[defn.category] = []
            categories[defn.category].append(defn)
        
        # Add variable submenu
        variable_store = VariableStore.get_instance()
        variables = variable_store.get_all_variables()
        if variables:
            var_menu = menu.addMenu(tr('variables'))
            for var in variables:
                var_submenu = var_menu.addMenu(var.name)
                
                get_action = var_submenu.addAction(tr('get_variable'))
                get_action.triggered.connect(
                    lambda checked, v=var: self._create_var_node(event.pos(), v.name, True)
                )
                
                set_action = var_submenu.addAction(tr('set_variable'))
                set_action.triggered.connect(
                    lambda checked, v=var: self._create_var_node(event.pos(), v.name, False)
                )
            
            menu.addSeparator()
        
        # Add node categories
        for category, defs in sorted(categories.items()):
            cat_menu = menu.addMenu(category)
            for defn in sorted(defs, key=lambda d: d.label):
                action = cat_menu.addAction(defn.label)
                action.triggered.connect(
                    lambda checked, d=defn: self._create_node(event.pos(), d.name)
                )
        
        menu.exec(event.globalPos())
    
    def _create_node(self, view_pos, node_name: str):
        """Create a new node at the given position."""
        scene_pos = self.mapToScene(view_pos)
        node_store = NodeStore.get_instance()
        node_store.create_node(node_name, scene_pos)
    
    def _create_var_node(self, view_pos, var_name: str, is_getter: bool):
        """Create a variable get/set node."""
        scene_pos = self.mapToScene(view_pos)
        node_store = NodeStore.get_instance()
        
        if is_getter:
            node_store.create_node('varget', scene_pos, {'name': var_name})
        else:
            node_store.create_node('varset', scene_pos, {'name': var_name})
