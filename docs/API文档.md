# Codeck API Documentation

This document provides comprehensive API documentation for the Codeck visual blueprint programming engine. It is designed for developers who want to extend, integrate, or understand the internal architecture of Codeck.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Store System](#store-system)
3. [Node System](#node-system)
4. [Connection System](#connection-system)
5. [Variable System](#variable-system)
6. [Code Generation](#code-generation)
7. [UI Components](#ui-components)
8. [Settings and Localization](#settings-and-localization)
9. [Extension Guide](#extension-guide)

---

## Architecture Overview

Codeck follows a store-based architecture with Qt signals for reactivity.

```
┌─────────────────────────────────────────────────────────────┐
│                      MainWindow                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ManagerPanel  │  │ FlowEditorView │  │ CodeEditor     │   │
│  └──────────────┘  └────────────────┘  └────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                       Stores (Singletons)                    │
│  ┌────────────┐ ┌────────────────┐ ┌────────────────────┐   │
│  │ NodeStore  │ │ConnectionStore │ │ VariableStore      │   │
│  └────────────┘ └────────────────┘ └────────────────────┘   │
│  ┌────────────┐ ┌────────────────┐ ┌────────────────────┐   │
│  │ UIStore    │ │ StageStore     │ │ SettingsStore      │   │
│  └────────────┘ └────────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Key Concepts

- **Stores**: Singleton classes that manage application state and emit Qt signals for reactivity
- **Components**: PySide6 widgets that display and interact with the stores
- **Node Definitions**: Configuration objects that define node types, pins, and code generation

---

## Store System

### NodeStore

Manages nodes and their definitions.

**Location**: `codeck/store/node.py`

#### Classes

##### CodeckNode
```python
@dataclass
class CodeckNode:
    id: str               # Unique node identifier
    name: str             # Reference to CodeckNodeDefinition name
    position: QPointF     # Position on canvas
    data: dict[str, Any]  # Node-specific data
```

##### CodeckNodePinDefinition
```python
@dataclass
class CodeckNodePinDefinition:
    name: str                        # Pin name
    type: CodeckNodePortType         # 'port' or 'exec'
    position: QPointF                # Position relative to node
    default_value: Any               # Default value
    render_type: Optional[str]       # Display type label
    input_type: Optional[str]        # Input widget type
```

##### CodeckNodeDefinition
```python
class CodeckNodeDefinition:
    name: str                                    # Unique identifier
    label: str                                   # Display name
    type: CodeckNodeType                         # 'begin', 'return', 'function', 'logic', 'call'
    width: int                                   # Node width
    height: int                                  # Node height
    category: str                                # Category for menu
    inputs: list[CodeckNodePinDefinition]        # Input pins
    outputs: list[CodeckNodePinDefinition]       # Output pins
    hidden: bool                                 # Hide from menu
    prepare: list[CodePrepare]                   # Code preparation
    code_fn: Optional[Callable]                  # Code generation function
    output_code_fns: dict[str, Callable]         # Output pin code functions
```

#### NodeStore API

```python
class NodeStore(QObject):
    # Signals
    nodes_changed = Signal()
    node_position_changed = Signal(str)  # node_id
    node_data_changed = Signal(str)      # node_id
    
    @classmethod
    def get_instance(cls) -> 'NodeStore':
        """Get the singleton instance."""
    
    def reg_node(self, definition: CodeckNodeDefinition) -> None:
        """Register a node definition."""
    
    def create_node(
        self,
        node_name: str,
        position: QPointF,
        data: Optional[dict[str, Any]] = None
    ) -> Optional[str]:
        """Create a new node. Returns node ID or None."""
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node (cannot remove begin node)."""
    
    def update_node_pos(self, node_id: str, position: QPointF) -> None:
        """Update a node's position."""
    
    def set_node_data(self, node_id: str, key: str, value: Any) -> None:
        """Set data on a node."""
    
    def get_node_definition(self, node_id: str) -> Optional[CodeckNodeDefinition]:
        """Get the definition for a node."""
    
    def get_pin_definition_by_name(
        self,
        node_id: str,
        pin_name: str
    ) -> Optional[CodeckNodePinDefinition]:
        """Get a pin definition by name."""
    
    def get_all_nodes(self) -> list[CodeckNode]:
        """Get all nodes."""
    
    def get_all_visible_definitions(self) -> list[CodeckNodeDefinition]:
        """Get all non-hidden node definitions."""
    
    def reset_nodes(self) -> None:
        """Reset all nodes to default state."""
```

---

### ConnectionStore

Manages connections between nodes.

**Location**: `codeck/store/connection.py`

#### Classes

##### ConnectInfo
```python
@dataclass
class ConnectInfo:
    id: str                  # Unique connection identifier
    from_node_id: str        # Source node ID
    from_node_pin_name: str  # Source pin name
    to_node_id: str          # Target node ID
    to_node_pin_name: str    # Target pin name
```

##### WorkingConnection
```python
@dataclass
class WorkingConnection:
    from_node_id: str
    from_node_pin_name: str
    from_node_pin_type: str   # 'exec' or 'port'
    from_node_direction: str  # 'out-in' or 'in-out'
```

#### ConnectionStore API

```python
class ConnectionStore(QObject):
    # Signals
    connections_changed = Signal()
    working_connection_changed = Signal()
    
    @classmethod
    def get_instance(cls) -> 'ConnectionStore':
        """Get the singleton instance."""
    
    def start_connect(
        self,
        node_id: str,
        pin_name: str,
        pin_type: str,
        direction: str
    ) -> None:
        """Start a new connection from a pin."""
    
    def end_connect(
        self,
        node_id: str,
        pin_name: str,
        pin_type: str,
        direction: str
    ) -> bool:
        """End a connection at a pin. Returns True if successful."""
    
    def cancel_connect(self) -> None:
        """Cancel the current connection attempt."""
    
    def remove_connection(self, connection_id: str) -> None:
        """Remove a connection by ID."""
    
    def check_is_connected(self, node_id: str, pin_name: str) -> bool:
        """Check if a pin is connected."""
    
    def get_connections_for_node(self, node_id: str) -> list[ConnectInfo]:
        """Get all connections involving a node."""
    
    def clear_connections(self) -> None:
        """Clear all connections."""
```

---

### VariableStore

Manages blueprint variables.

**Location**: `codeck/store/variable.py`

#### Classes

##### VariableItem
```python
@dataclass
class VariableItem:
    name: str
    type: VariableType       # 'string', 'number', 'boolean', 'object', 'array'
    default_value: Any
    current_value: Any
```

#### VariableStore API

```python
class VariableStore(QObject):
    # Signals
    variable_changed = Signal()
    
    @classmethod
    def get_instance(cls) -> 'VariableStore':
        """Get the singleton instance."""
    
    def create_variable(
        self,
        name: str,
        var_type: VariableType,
        default_value: Any = None
    ) -> bool:
        """Create a new variable. Returns True if successful."""
    
    def delete_variable(self, name: str) -> bool:
        """Delete a variable. Returns True if successful."""
    
    def get_variable(self, name: str) -> Optional[VariableItem]:
        """Get a variable by name."""
    
    def get_all_variables(self) -> list[VariableItem]:
        """Get all variables."""
    
    def clear_variables(self) -> None:
        """Clear all variables."""
```

---

### SettingsStore

Manages application settings.

**Location**: `codeck/store/settings.py`

#### SettingsStore API

```python
class SettingsStore(QObject):
    # Signals
    settings_changed = Signal()
    language_changed = Signal(str)
    theme_changed = Signal(str)
    recent_projects_changed = Signal()
    
    @classmethod
    def get_instance(cls) -> 'SettingsStore':
        """Get the singleton instance."""
    
    @property
    def language(self) -> Language:
        """Get current language ('zh_CN' or 'en_US')."""
    
    @language.setter
    def language(self, value: Language) -> None:
        """Set language."""
    
    @property
    def theme(self) -> Theme:
        """Get current theme ('dark' or 'light')."""
    
    @theme.setter
    def theme(self, value: Theme) -> None:
        """Set theme."""
    
    @property
    def recent_projects(self) -> list[RecentProject]:
        """Get recent projects."""
    
    def add_recent_project(self, project: RecentProject) -> None:
        """Add a project to recent projects list."""
    
    def remove_recent_project(self, path: str) -> None:
        """Remove a project from recent projects list."""
```

#### Translation Function

```python
def tr(key: str) -> str:
    """Get translated text for the given key."""
```

---

## Node System

### Creating Custom Nodes

To create a custom node:

1. **Define the node in a new file** under `codeck/nodes/definitions/`

```python
# my_node.py
from PySide6.QtCore import QPointF
from ...store.node import CodeckNodeDefinition
from ...utils.consts import DEFAULT_CORE_CATEGORY
from ...utils.size_helper import DEFAULT_NODE_WIDTH, build_node_height
from ...utils.standard import exec_pin_input, exec_pin_output, port_pin_input

width = DEFAULT_NODE_WIDTH
height = build_node_height(2)  # 2 pins

def my_node_code_fn(node, build_pin_var_name, get_connection_input, get_connection_exec_output):
    """Generate code for the node."""
    input_value = get_connection_input('input') or node.data.get('default', '')
    return f'# My custom code\nlog = "{input_value}"\n'

MyNodeDefinition = CodeckNodeDefinition(
    name='my_node',
    label='My Node',
    node_type='function',
    width=width,
    height=height,
    category=DEFAULT_CORE_CATEGORY,
    inputs=[
        exec_pin_input(width),
        port_pin_input('input', width, 1, input_type='text')
    ],
    outputs=[exec_pin_output(width)],
    code_fn=my_node_code_fn
)
```

2. **Register the node** in `codeck/nodes/definitions/all_nodes.py`:

```python
from .my_node import MyNodeDefinition

builtinNodeDefinitions = [
    # ... existing nodes
    MyNodeDefinition,
]
```

### Code Generation Function

The code generation function receives:

```python
def code_fn(
    node: CodeckNode,
    build_pin_var_name: Callable[[str, Optional[str]], str],
    get_connection_input: Callable[[str, Optional[str]], Optional[str]],
    get_connection_exec_output: Callable[[str, Optional[str]], Optional[str]]
) -> str:
```

- `node`: The current node instance
- `build_pin_var_name(pin_name, node_id?)`: Build a variable name for a pin
- `get_connection_input(pin_name, node_id?)`: Get the input value for a pin
- `get_connection_exec_output(pin_name, node_id?)`: Get the code for an execution branch

---

## Code Generation

### CodeCompiler

Generates HOI4 MOD scripts from blueprints.

**Location**: `codeck/code/compiler.py`

```python
class CodeCompiler:
    script_type: str        # 'event', 'decision', 'national_focus', 'idea'
    mod_namespace: str      # Namespace for the script
    print_comment: bool     # Include comments in output
    
    def generate(self) -> str:
        """Generate code from the blueprint."""
```

### Usage Example

```python
from codeck.code.compiler import CodeCompiler

compiler = CodeCompiler()
compiler.script_type = 'event'
compiler.mod_namespace = 'my_mod'

try:
    code = compiler.generate()
    print(code)
except ValueError as e:
    print(f"Error: {e}")
```

---

## UI Components

### FlowEditorView

The main canvas for node editing.

**Location**: `codeck/components/flow_editor.py`

Key features:
- Zoom with mouse wheel
- Pan with middle mouse button or Space+Left click
- Right-click context menu for adding nodes
- Node selection and deletion

### ManagerPanel

Sidebar for managing variables and files.

**Location**: `codeck/components/manager_panel.py`

Key features:
- File operations (Open, Save, Save As)
- Reset and Run buttons
- Build configuration
- Variable creation and management

### CodeEditor

Code preview panel.

**Location**: `codeck/components/code_editor.py`

Key features:
- Syntax highlighting for HOI4 scripts
- Auto-updates when nodes change
- Theme-aware styling

---

## Settings and Localization

### Adding Translations

To add a new translation key:

1. Open `codeck/store/settings.py`
2. Add the key to both `zh_CN` and `en_US` in the `TRANSLATIONS` dictionary:

```python
TRANSLATIONS = {
    'zh_CN': {
        # ... existing translations
        'my_new_key': '我的新文本',
    },
    'en_US': {
        # ... existing translations
        'my_new_key': 'My New Text',
    }
}
```

3. Use the translation in your code:

```python
from codeck.store.settings import tr

label = QLabel(tr('my_new_key'))
```

### Theme Support

Components should respond to theme changes:

```python
from codeck.store.settings import SettingsStore

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Connect to theme changes
        SettingsStore.get_instance().theme_changed.connect(self._apply_theme)
        self._apply_theme()
    
    def _apply_theme(self):
        settings = SettingsStore.get_instance()
        if settings.theme == 'dark':
            self.setStyleSheet('background-color: #252526; color: #ccc;')
        else:
            self.setStyleSheet('background-color: #fff; color: #333;')
```

---

## Extension Guide

### Adding a New Store

1. Create a new file in `codeck/store/`:

```python
# my_store.py
from typing import Optional
from PySide6.QtCore import QObject, Signal

class MyStore(QObject):
    # Signals
    data_changed = Signal()
    
    _instance: Optional['MyStore'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self.data = {}
    
    @classmethod
    def get_instance(cls) -> 'MyStore':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### Adding a New Component

1. Create a new file in `codeck/components/`:

```python
# my_component.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ..store.settings import tr, SettingsStore

class MyComponent(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        
        # Connect to settings
        SettingsStore.get_instance().language_changed.connect(self._update_labels)
        SettingsStore.get_instance().theme_changed.connect(self._apply_theme)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.label = QLabel(tr('my_label'))
        layout.addWidget(self.label)
    
    def _update_labels(self):
        self.label.setText(tr('my_label'))
    
    def _apply_theme(self):
        settings = SettingsStore.get_instance()
        # Apply theme-specific styles
```

---

## Testing

### Running Tests

```bash
pip install pytest
pytest tests/
```

### Writing Tests

```python
# tests/test_my_feature.py
import pytest
from PySide6.QtCore import QPointF

@pytest.fixture(autouse=True)
def reset_stores():
    """Reset all stores before each test."""
    from codeck.store.node import NodeStore
    from codeck.store.connection import ConnectionStore
    from codeck.store.variable import VariableStore
    
    NodeStore._instance = None
    ConnectionStore._instance = None
    VariableStore._instance = None
    
    yield

def test_my_feature():
    from codeck.store.node import NodeStore
    from codeck.nodes.definitions.all_nodes import register_builtin_nodes
    
    node_store = NodeStore.get_instance()
    register_builtin_nodes()
    node_store.reset_nodes()
    
    # Your test code here
    assert True
```

---

## Constants

**Location**: `codeck/utils/consts.py`

```python
STANDARD_PIN_EXEC_IN = '$pin_exec_in'
STANDARD_PIN_EXEC_OUT = '$pin_exec_out'

NODE_TITLE_HEIGHT = 32

DEFAULT_CORE_CATEGORY = 'Core'
DEFAULT_LOGIC_CATEGORY = 'Logic'

variableTypes = ['string', 'number', 'boolean', 'object', 'array']

BEGIN_NODE_ID = '$begin'
```

---

## Utility Functions

### Size Helper

**Location**: `codeck/utils/size_helper.py`

```python
DEFAULT_NODE_WIDTH = 180

def build_node_height(pin_count: int) -> int:
    """Calculate node height based on pin count."""
```

### Standard Pins

**Location**: `codeck/utils/standard.py`

```python
def exec_pin_input(width: int) -> CodeckNodePinDefinition:
    """Create standard execution input pin."""

def exec_pin_output(width: int) -> CodeckNodePinDefinition:
    """Create standard execution output pin."""

def port_pin_input(
    name: str,
    width: int,
    index: int,
    input_type: Optional[str] = None
) -> CodeckNodePinDefinition:
    """Create data input pin."""

def port_pin_output(
    name: str,
    width: int,
    index: int,
    render_type: Optional[str] = None
) -> CodeckNodePinDefinition:
    """Create data output pin."""
```

---

## License

Apache-2.0 License

---

For more information, see the [User Manual](./用户手册.md) (Chinese) or the [README](../README.md).
