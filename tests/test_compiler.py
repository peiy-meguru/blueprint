"""Tests for the code compiler."""

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


def test_generate_basic_code():
    """Test generating basic code with Begin and Log nodes."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.code.compiler import CodeCompiler
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    
    # Create Begin node
    node_store.reset_nodes()  # This creates Begin and Log with default connection
    
    # Connect Begin to Log
    conn_store.start_connect('$begin', '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect('log', '$pin_exec_in', 'exec', 'in-out')
    
    compiler = CodeCompiler()
    code = compiler.generate()
    
    assert 'console.log' in code
    assert 'Hello World' in code


def test_generate_code_with_variable():
    """Test generating code with a variable."""
    from codeck.store.node import NodeStore
    from codeck.store.variable import VariableStore
    from codeck.code.compiler import CodeCompiler
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    var_store = VariableStore.get_instance()
    register_builtin_nodes()
    node_store.reset_nodes()
    
    # Create a variable
    var_store.create_variable('counter', 'number', 0)
    
    compiler = CodeCompiler()
    code = compiler.generate()
    
    assert 'let counter = 0' in code


def test_generate_if_code():
    """Test generating If node code."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.code.compiler import CodeCompiler
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    from codeck.utils.consts import BEGIN_NODE_ID
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    node_store.reset_nodes()
    
    # Remove default log node
    node_store.remove_node('log')
    
    # Create If node
    if_node_id = node_store.create_node('if', QPointF(200, 10), {'condition': True})
    
    # Connect Begin to If
    conn_store.start_connect(BEGIN_NODE_ID, '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect(if_node_id, '$pin_exec_in', 'exec', 'in-out')
    
    compiler = CodeCompiler()
    code = compiler.generate()
    
    assert 'if (' in code
    assert 'else' in code


def test_generate_loop_code():
    """Test generating Loop node code."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.code.compiler import CodeCompiler
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    from codeck.utils.consts import BEGIN_NODE_ID
    
    node_store = NodeStore.get_instance()
    conn_store = ConnectionStore.get_instance()
    register_builtin_nodes()
    node_store.reset_nodes()
    
    # Remove default log node
    node_store.remove_node('log')
    
    # Create Loop node
    loop_node_id = node_store.create_node('loop', QPointF(200, 10), {'count': 5})
    
    # Connect Begin to Loop
    conn_store.start_connect(BEGIN_NODE_ID, '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect(loop_node_id, '$pin_exec_in', 'exec', 'in-out')
    
    compiler = CodeCompiler()
    code = compiler.generate()
    
    assert 'for (' in code
    assert '5' in code
