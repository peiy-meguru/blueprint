"""Tests for the connection store."""

import pytest
from PySide6.QtCore import QPointF


@pytest.fixture(autouse=True)
def reset_stores():
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.store.variable import VariableStore
    from codeck.store.ui import UIStore
    
    NodeStore._instance = None
    ConnectionStore._instance = None
    VariableStore._instance = None
    UIStore._instance = None
    
    yield


def test_connection_store_singleton():
    """Test that ConnectionStore is a singleton."""
    from codeck.store.connection import ConnectionStore
    
    store1 = ConnectionStore.get_instance()
    store2 = ConnectionStore.get_instance()
    
    assert store1 is store2


def test_start_and_end_connect():
    """Test starting and ending a connection."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    
    # Create two nodes
    node1_id = node_store.create_node('log', QPointF(100, 100))
    node2_id = node_store.create_node('log', QPointF(300, 100))
    
    # Start connection
    conn_store.start_connect(node1_id, '$pin_exec_out', 'exec', 'out-in')
    assert conn_store.working_connection is not None
    
    # End connection
    conn_store.end_connect(node2_id, '$pin_exec_in', 'exec', 'in-out')
    
    assert conn_store.working_connection is None
    assert len(conn_store.connections) == 1
    assert conn_store.connections[0].from_node_id == node1_id
    assert conn_store.connections[0].to_node_id == node2_id


def test_cannot_connect_same_node():
    """Test that a node cannot connect to itself."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    
    node_id = node_store.create_node('log', QPointF(100, 100))
    
    conn_store.start_connect(node_id, '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect(node_id, '$pin_exec_in', 'exec', 'in-out')
    
    assert len(conn_store.connections) == 0


def test_cannot_connect_same_direction():
    """Test that pins of the same direction cannot connect."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    
    node1_id = node_store.create_node('log', QPointF(100, 100))
    node2_id = node_store.create_node('log', QPointF(300, 100))
    
    # Both output to output
    conn_store.start_connect(node1_id, '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect(node2_id, '$pin_exec_out', 'exec', 'out-in')
    
    assert len(conn_store.connections) == 0


def test_check_is_connected():
    """Test checking if a pin is connected."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    
    node1_id = node_store.create_node('log', QPointF(100, 100))
    node2_id = node_store.create_node('log', QPointF(300, 100))
    
    assert not conn_store.check_is_connected(node1_id, '$pin_exec_out')
    
    conn_store.start_connect(node1_id, '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect(node2_id, '$pin_exec_in', 'exec', 'in-out')
    
    assert conn_store.check_is_connected(node1_id, '$pin_exec_out')
    assert conn_store.check_is_connected(node2_id, '$pin_exec_in')


def test_remove_connection():
    """Test removing a connection."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    
    node1_id = node_store.create_node('log', QPointF(100, 100))
    node2_id = node_store.create_node('log', QPointF(300, 100))
    
    conn_store.start_connect(node1_id, '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect(node2_id, '$pin_exec_in', 'exec', 'in-out')
    
    assert len(conn_store.connections) == 1
    
    conn_id = conn_store.connections[0].id
    conn_store.remove_connection(conn_id)
    
    assert len(conn_store.connections) == 0
