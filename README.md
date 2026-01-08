# Codeck

一个基于 Python 和 PySide6 的可视化蓝图编程引擎。

`codeck` 是一款蓝图可视化编程系统，其理念是，使用基于节点的界面创建任何编程语言能够编程出的脚本。其设计灵感来源于虚幻 4 引擎的蓝图可视化脚本。

## 使用场景

与一般的编程语言不同的是，`codeck` 的设计方向在于一些需要快速实现的地方，对于一些简单的编程场景，单独开一个项目的成本会相对较高。而 `codeck` 则实现了**随用随编程**的理念，将快速验证的成本降低到一个很低的地步。

使用 `codeck`, 你甚至不需要了解其背后的细节。我们会将很多内容封装成一个单独的节点，并通过一些 `端点(pin)` 将这些上下文暴露出来。

## Features

- **Visual Node Editor**: Drag and drop nodes to create programs visually
- **Code Generation**: Automatically generates code from your blueprint
- **Variable Management**: Create and manage variables that can be used in your blueprint
- **Built-in Nodes**:
  - **Core**: Begin, Log, Alert, If, ForEach, Loop, Variable Get/Set
  - **Logic**: Add, Subtract, Multiply, Divide, Equal, Greater Than, Less Than, And, Or, Not
- **Save/Load**: Save and load blueprints as JSON files
- **Dark Theme**: Modern dark UI theme

## Requirements

- Python 3.10+
- PySide6

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python run.py
```

Or:

```bash
python -m codeck.main
```

## Usage

### Basic Operations

1. **Adding Nodes**: Right-click on the canvas to open the context menu and select a node to add
2. **Connecting Nodes**: Click and drag from a pin on one node to a pin on another
3. **Moving Nodes**: Click and drag nodes to move them
4. **Deleting**: Select nodes/connections and press Delete or Backspace
5. **Panning**: Hold middle mouse button or Space + Left mouse button to pan
6. **Zooming**: Use mouse wheel to zoom in/out
7. **Focus**: Press F to focus view on nodes

### Managing Variables

1. Click "Create Variable ▼" in the left panel
2. Enter a name, select a type, and optionally set a default value
3. Click "Create Variable"
4. Use the variable by right-clicking and selecting it from the Variables menu

### File Operations

- **Open**: Load a blueprint from a JSON file
- **Save**: Save the current blueprint (to last opened file or prompts for new file)
- **Save As**: Save the blueprint to a new file
- **Reset**: Clear all nodes and start fresh

### Building/Running

- **Run**: Generate JavaScript code and display it
- **Pack**: Generate code and save to a JavaScript file

## Project Structure

```
codeck/
├── codeck/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── code/
│   │   └── compiler.py      # Code compiler
│   ├── components/
│   │   ├── flow_editor.py   # Main canvas/node editor
│   │   ├── manager_panel.py # Left sidebar
│   │   └── code_editor.py   # Code display panel
│   ├── nodes/
│   │   └── definitions/     # Node type definitions
│   ├── store/
│   │   ├── node.py          # Node state management
│   │   ├── connection.py    # Connection state management
│   │   ├── variable.py      # Variable state management
│   │   ├── stage.py         # Canvas state management
│   │   └── ui.py            # UI state management
│   └── utils/
│       ├── color.py         # Color scheme
│       ├── consts.py        # Constants
│       ├── size_helper.py   # Size calculations
│       ├── standard.py      # Standard node helpers
│       └── string_helper.py # String utilities
├── tests/                   # Unit tests
├── requirements.txt
├── run.py
└── README.md
```

## Running Tests

```bash
pip install pytest
pytest tests/
```

## Architecture

- **Stores**: Singleton classes that manage application state with Qt signals for reactivity
- **Components**: PySide6 widgets that display and interact with the stores
- **Node Definitions**: Configuration objects that define node types, pins, and code generation

## Technical Stack

| Component | Technology |
|-----------|------------|
| UI Framework | PySide6 (Qt6) |
| Canvas | QGraphicsView |
| State Management | Custom stores with Qt signals |
| Styling | Qt stylesheets |
| Code Editor | QPlainTextEdit with syntax highlighting |

## License

Apache-2.0 License
