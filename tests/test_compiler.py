"""Tests for the code compiler - HOI4 MOD script generation."""

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
    """Test generating basic HOI4 MOD script code with Begin and Log nodes."""
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
    
    # HOI4 script uses log = "message" format
    assert 'Log:' in code or 'log =' in code
    assert 'Hello World' in code


def test_generate_code_with_variable():
    """Test generating HOI4 MOD script code with a variable."""
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
    
    # HOI4 uses set_variable for variable assignment
    assert 'counter' in code
    assert 'set_variable' in code or 'Variable Definitions' in code


def test_generate_if_code():
    """Test generating If node HOI4 MOD script code."""
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
    if_node_id = node_store.create_node('if', QPointF(200, 10), {'condition': 'always = yes'})
    
    # Connect Begin to If
    conn_store.start_connect(BEGIN_NODE_ID, '$pin_exec_out', 'exec', 'out-in')
    conn_store.end_connect(if_node_id, '$pin_exec_in', 'exec', 'in-out')
    
    compiler = CodeCompiler()
    code = compiler.generate()
    
    # HOI4 script uses if = { limit = { } }
    assert 'if =' in code
    assert 'limit' in code


def test_generate_loop_code():
    """Test generating Loop node HOI4 MOD script code."""
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
    
    # HOI4 uses random_list for loop-like behavior
    assert 'random_list' in code or 'Loop' in code
    assert '5' in code


def test_generate_hoi4_script_header():
    """Test that generated code includes HOI4 MOD script header."""
    from codeck.store.node import NodeStore
    from codeck.code.compiler import CodeCompiler
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    register_builtin_nodes()
    node_store.reset_nodes()
    
    compiler = CodeCompiler()
    compiler.mod_namespace = 'test_mod'
    compiler.script_type = 'event'
    
    code = compiler.generate()
    
    # Should include HOI4 script header
    assert 'HOI4 MOD Script' in code
    assert 'test_mod' in code
    assert 'add_namespace' in code
