"""Tests for the node store."""

import pytest
from PySide6.QtCore import QPointF

# Reset singletons before each test
@pytest.fixture(autouse=True)
def reset_stores():
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.store.variable import VariableStore
    from codeck.store.ui import UIStore
    
    # Reset singleton instances
    NodeStore._instance = None
    ConnectionStore._instance = None
    VariableStore._instance = None
    UIStore._instance = None
    
    yield


def test_node_store_singleton():
    """Test that NodeStore is a singleton."""
    from codeck.store.node import NodeStore
    
    store1 = NodeStore.get_instance()
    store2 = NodeStore.get_instance()
    
    assert store1 is store2


def test_register_node_definition():
    """Test registering a node definition."""
    from codeck.store.node import NodeStore, CodeckNodeDefinition, CodeckNodePinDefinition
    
    store = NodeStore.get_instance()
    
    definition = CodeckNodeDefinition(
        name='test_node',
        label='Test Node',
        node_type='function',
        width=150,
        height=70,
        category='Test',
        inputs=[],
        outputs=[]
    )
    
    store.reg_node(definition)
    
    assert 'test_node' in store.node_definition
    assert store.node_definition['test_node'].label == 'Test Node'


def test_create_node():
    """Test creating a node."""
    from codeck.store.node import NodeStore, CodeckNodeDefinition
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    store = NodeStore.get_instance()
    register_builtin_nodes()
    
    node_id = store.create_node('log', QPointF(100, 100), {'message': 'Hello'})
    
    assert node_id is not None
    assert node_id in store.node_map
    assert store.node_map[node_id].name == 'log'
    assert store.node_map[node_id].data.get('message') == 'Hello'


def test_move_node():
    """Test moving a node."""
    from codeck.store.node import NodeStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    store = NodeStore.get_instance()
    register_builtin_nodes()
    
    node_id = store.create_node('log', QPointF(100, 100))
    store.move_node(node_id, 50, 30)
    
    assert store.node_map[node_id].position.x() == 150
    assert store.node_map[node_id].position.y() == 130


def test_remove_node():
    """Test removing a node."""
    from codeck.store.node import NodeStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    store = NodeStore.get_instance()
    register_builtin_nodes()
    
    node_id = store.create_node('log', QPointF(100, 100))
    assert node_id in store.node_map
    
    store.remove_node(node_id)
    assert node_id not in store.node_map


def test_cannot_remove_begin_node():
    """Test that begin node cannot be removed."""
    from codeck.store.node import NodeStore
    from codeck.utils.consts import BEGIN_NODE_ID
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    store = NodeStore.get_instance()
    register_builtin_nodes()
    store.reset_nodes()
    
    assert BEGIN_NODE_ID in store.node_map
    
    store.remove_node(BEGIN_NODE_ID)
    
    # Begin node should still exist
    assert BEGIN_NODE_ID in store.node_map
