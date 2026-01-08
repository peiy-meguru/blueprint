# Codeck - PySide6 Version

A visual blueprint programming engine built with PySide6 (Python).

This is a Python port of the original JavaScript/React Codeck project, providing the same visual node-based programming functionality using Qt6/PySide6.

## Features

- **Visual Node Editor**: Drag and drop nodes to create programs visually
- **Code Generation**: Automatically generates JavaScript code from your blueprint
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
cd pyside6_codeck
pip install -r requirements.txt
```

## Running the Application

```bash
cd pyside6_codeck
python run.py
```

Or:

```bash
cd pyside6_codeck
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
pyside6_codeck/
├── codeck/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── code/
│   │   └── compiler.py      # JavaScript code compiler
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
cd pyside6_codeck
pip install pytest
pytest tests/
```

## Architecture

The application follows a similar architecture to the original TypeScript version:

- **Stores**: Singleton classes that manage application state with Qt signals for reactivity
- **Components**: PySide6 widgets that display and interact with the stores
- **Node Definitions**: Configuration objects that define node types, pins, and code generation

## Comparison with Original

| Feature | Original (TypeScript/React) | PySide6 Port |
|---------|----------------------------|--------------|
| UI Framework | React | PySide6 |
| Canvas | Konva | QGraphicsView |
| State Management | Zustand | Custom stores with Qt signals |
| Styling | Tailwind CSS | Qt stylesheets |
| Code Editor | Monaco | QPlainTextEdit with syntax highlighting |

## License

Apache-2.0 License
