"""Manager Panel - Sidebar for managing variables and files."""

import json
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QGroupBox, QScrollArea, QListWidget,
    QListWidgetItem, QMessageBox, QFileDialog, QSplitter,
    QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal

from ..store.node import NodeStore
from ..store.connection import ConnectionStore
from ..store.variable import VariableStore, VariableItem
from ..utils.consts import variableTypes
from ..code.compiler import CodeCompiler


class VariableWidget(QWidget):
    """Widget for displaying and editing a variable."""
    
    deleted = Signal(str)  # Variable name
    
    def __init__(self, variable: VariableItem):
        super().__init__()
        self.variable = variable
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Name and type
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f'{variable.name}'))
        info_layout.addWidget(QLabel(f'({variable.type})'))
        info_layout.addStretch()
        
        delete_btn = QPushButton('Delete')
        delete_btn.clicked.connect(self._on_delete)
        info_layout.addWidget(delete_btn)
        
        layout.addLayout(info_layout)
        
        # Default value
        if variable.default_value is not None:
            layout.addWidget(QLabel(f'Default: {variable.default_value}'))
    
    def _on_delete(self):
        """Handle delete button click."""
        self.deleted.emit(self.variable.name)


class CreateVariableDialog(QWidget):
    """Widget for creating a new variable."""
    
    created = Signal()
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('Name:'))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Variable name')
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('Type:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(variableTypes)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Default value
        default_layout = QHBoxLayout()
        default_layout.addWidget(QLabel('Default:'))
        self.default_input = QLineEdit()
        self.default_input.setPlaceholderText('(optional)')
        default_layout.addWidget(self.default_input)
        layout.addLayout(default_layout)
        
        # Create button
        create_btn = QPushButton('Create Variable')
        create_btn.clicked.connect(self._on_create)
        layout.addWidget(create_btn)
    
    def _on_create(self):
        """Handle create button click."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, 'Error', 'Variable name is required')
            return
        
        # Validate name starts with letter or underscore
        if len(name) > 0 and not name[0].isalpha() and name[0] != '_':
            QMessageBox.warning(self, 'Error', 'Variable name must start with a letter or underscore')
            return
        
        var_type = self.type_combo.currentText()
        default_value = self.default_input.text().strip()
        
        # Parse default value based on type
        parsed_default = None
        if default_value:
            try:
                if var_type == 'number':
                    parsed_default = float(default_value)
                elif var_type == 'boolean':
                    parsed_default = default_value.lower() in ('true', '1', 'yes')
                elif var_type in ('object', 'array'):
                    parsed_default = json.loads(default_value)
                else:
                    parsed_default = default_value
            except (ValueError, json.JSONDecodeError):
                parsed_default = default_value
        
        variable_store = VariableStore.get_instance()
        if variable_store.create_variable(name, var_type, parsed_default):
            self.name_input.clear()
            self.default_input.clear()
            self.created.emit()
        else:
            QMessageBox.warning(self, 'Error', f'Variable "{name}" already exists')


class BuildConfigWidget(QWidget):
    """Widget for build configuration."""
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Platform selection
        platform_group = QGroupBox('Platform')
        platform_layout = QHBoxLayout(platform_group)
        self.platform_group = QButtonGroup(self)
        
        self.web_radio = QRadioButton('Web')
        self.web_radio.setChecked(True)
        self.nodejs_radio = QRadioButton('Node.js')
        
        self.platform_group.addButton(self.web_radio)
        self.platform_group.addButton(self.nodejs_radio)
        platform_layout.addWidget(self.web_radio)
        platform_layout.addWidget(self.nodejs_radio)
        layout.addWidget(platform_group)
        
        # Module type selection
        module_group = QGroupBox('Module Type')
        module_layout = QHBoxLayout(module_group)
        self.module_group = QButtonGroup(self)
        
        self.esm_radio = QRadioButton('ESModule')
        self.esm_radio.setChecked(True)
        self.cjs_radio = QRadioButton('CommonJS')
        
        self.module_group.addButton(self.esm_radio)
        self.module_group.addButton(self.cjs_radio)
        module_layout.addWidget(self.esm_radio)
        module_layout.addWidget(self.cjs_radio)
        layout.addWidget(module_group)
        
        # Pack button
        pack_btn = QPushButton('Pack')
        pack_btn.clicked.connect(self._on_pack)
        layout.addWidget(pack_btn)
    
    def _on_pack(self):
        """Handle pack button click."""
        compiler = CodeCompiler()
        compiler.module_type = 'esmodule' if self.esm_radio.isChecked() else 'commonjs'
        compiler.use_skypack = self.web_radio.isChecked()
        
        try:
            code = compiler.generate()
            
            # Save to file
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                'Save Generated Code',
                'generated.js',
                'JavaScript Files (*.js)'
            )
            
            if file_name:
                with open(file_name, 'w') as f:
                    f.write(code)
                QMessageBox.information(self, 'Success', f'Code saved to {file_name}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to generate code: {e}')


class ManagerPanel(QWidget):
    """Manager panel for variables, files, and build configuration."""
    
    code_updated = Signal(str)  # Generated code
    
    def __init__(self):
        super().__init__()
        self._current_file: Optional[str] = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # File operations
        file_group = QGroupBox('File')
        file_layout = QVBoxLayout(file_group)
        
        file_buttons = QHBoxLayout()
        
        open_btn = QPushButton('Open')
        open_btn.clicked.connect(self._on_open)
        file_buttons.addWidget(open_btn)
        
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self._on_save)
        file_buttons.addWidget(save_btn)
        
        save_as_btn = QPushButton('Save As')
        save_as_btn.clicked.connect(self._on_save_as)
        file_buttons.addWidget(save_as_btn)
        
        file_layout.addLayout(file_buttons)
        
        self.file_label = QLabel('Current: Local Storage')
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(file_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(self._on_reset)
        actions_layout.addWidget(reset_btn)
        
        run_btn = QPushButton('Run')
        run_btn.clicked.connect(self._on_run)
        actions_layout.addWidget(run_btn)
        
        layout.addLayout(actions_layout)
        
        # Build configuration (collapsible)
        self.build_widget = BuildConfigWidget()
        self.build_widget.setVisible(False)
        
        build_toggle = QPushButton('Build ▼')
        build_toggle.clicked.connect(lambda: self._toggle_section(self.build_widget, build_toggle, 'Build'))
        layout.addWidget(build_toggle)
        layout.addWidget(self.build_widget)
        
        # Variable creation (collapsible)
        self.create_var_widget = CreateVariableDialog()
        self.create_var_widget.setVisible(False)
        self.create_var_widget.created.connect(self._refresh_variables)
        
        create_var_toggle = QPushButton('Create Variable ▼')
        create_var_toggle.clicked.connect(lambda: self._toggle_section(self.create_var_widget, create_var_toggle, 'Create Variable'))
        layout.addWidget(create_var_toggle)
        layout.addWidget(self.create_var_widget)
        
        # Variables list
        var_group = QGroupBox('Variables')
        var_layout = QVBoxLayout(var_group)
        
        self.variables_list = QVBoxLayout()
        var_layout.addLayout(self.variables_list)
        
        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(var_group)
        layout.addWidget(scroll, 1)
        
        # Connect to variable store
        VariableStore.get_instance().variable_changed.connect(self._refresh_variables)
        
        # Initial refresh
        self._refresh_variables()
    
    def _toggle_section(self, widget: QWidget, button: QPushButton, name: str):
        """Toggle visibility of a collapsible section."""
        visible = not widget.isVisible()
        widget.setVisible(visible)
        button.setText(f'{name} {"▲" if visible else "▼"}')
    
    def _refresh_variables(self):
        """Refresh the variables list."""
        # Clear existing widgets
        while self.variables_list.count():
            item = self.variables_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add variable widgets
        variable_store = VariableStore.get_instance()
        for var in variable_store.get_all_variables():
            widget = VariableWidget(var)
            widget.deleted.connect(self._on_delete_variable)
            self.variables_list.addWidget(widget)
    
    def _on_delete_variable(self, name: str):
        """Handle variable deletion."""
        variable_store = VariableStore.get_instance()
        variable_store.delete_variable(name)
    
    def _on_open(self):
        """Handle open file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            'Open Blueprint',
            '',
            'JSON Files (*.json)'
        )
        
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    data = json.load(f)
                
                self._load_data(data)
                self._current_file = file_name
                self.file_label.setText(f'Current: {file_name.split("/")[-1]}')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Failed to open file: {e}')
    
    def _on_save(self):
        """Handle save file."""
        if self._current_file:
            self._save_to_file(self._current_file)
        else:
            self._on_save_as()
    
    def _on_save_as(self):
        """Handle save as."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            'Save Blueprint',
            'blueprint.json',
            'JSON Files (*.json)'
        )
        
        if file_name:
            self._save_to_file(file_name)
            self._current_file = file_name
            self.file_label.setText(f'Current: {file_name.split("/")[-1]}')
    
    def _save_to_file(self, file_name: str):
        """Save current state to file."""
        try:
            data = self._get_save_data()
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, 'Success', 'Blueprint saved successfully')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to save file: {e}')
    
    def _get_save_data(self) -> dict:
        """Get current state as saveable data."""
        node_store = NodeStore.get_instance()
        connection_store = ConnectionStore.get_instance()
        variable_store = VariableStore.get_instance()
        
        # Convert nodes
        nodes = {}
        for node_id, node in node_store.node_map.items():
            nodes[node_id] = {
                'id': node.id,
                'name': node.name,
                'position': {'x': node.position.x(), 'y': node.position.y()},
                'data': node.data
            }
        
        # Convert connections
        connections = []
        for conn in connection_store.connections:
            connections.append({
                'id': conn.id,
                'fromNodeId': conn.from_node_id,
                'fromNodePinName': conn.from_node_pin_name,
                'toNodeId': conn.to_node_id,
                'toNodePinName': conn.to_node_pin_name
            })
        
        # Convert variables
        variables = {}
        for name, var in variable_store.variable_map.items():
            variables[name] = {
                'name': var.name,
                'type': var.type,
                'defaultValue': var.default_value
            }
        
        return {
            'modules': {
                'entry': {
                    'nodeMap': nodes,
                    'connections': connections,
                    'variable': variables
                }
            }
        }
    
    def _load_data(self, data: dict):
        """Load state from saved data."""
        from PySide6.QtCore import QPointF
        from ..store.node import CodeckNode
        from ..store.connection import ConnectInfo
        
        if 'modules' not in data or 'entry' not in data['modules']:
            raise ValueError('Invalid blueprint format')
        
        entry = data['modules']['entry']
        
        node_store = NodeStore.get_instance()
        connection_store = ConnectionStore.get_instance()
        variable_store = VariableStore.get_instance()
        
        # Load nodes
        node_store.node_map.clear()
        for node_id, node_data in entry.get('nodeMap', {}).items():
            node_store.node_map[node_id] = CodeckNode(
                id=node_data['id'],
                name=node_data['name'],
                position=QPointF(node_data['position']['x'], node_data['position']['y']),
                data=node_data.get('data', {})
            )
        
        # Load connections
        connection_store.connections.clear()
        for conn_data in entry.get('connections', []):
            connection_store.connections.append(ConnectInfo(
                id=conn_data['id'],
                from_node_id=conn_data['fromNodeId'],
                from_node_pin_name=conn_data['fromNodePinName'],
                to_node_id=conn_data['toNodeId'],
                to_node_pin_name=conn_data['toNodePinName']
            ))
        
        # Load variables
        variable_store.variable_map.clear()
        for name, var_data in entry.get('variable', {}).items():
            variable_store.variable_map[name] = VariableItem(
                name=var_data['name'],
                type=var_data['type'],
                default_value=var_data.get('defaultValue')
            )
        
        # Emit signals
        node_store.nodes_changed.emit()
        connection_store.connections_changed.emit()
        variable_store.variable_changed.emit()
    
    def _on_reset(self):
        """Handle reset."""
        reply = QMessageBox.question(
            self,
            'Confirm Reset',
            'Are you sure you want to reset? All unsaved changes will be lost.',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            NodeStore.get_instance().reset_nodes()
            VariableStore.get_instance().clear_variables()
            self._current_file = None
            self.file_label.setText('Current: Local Storage')
    
    def _on_run(self):
        """Handle run - generate and display code."""
        compiler = CodeCompiler()
        compiler.use_skypack = True
        
        try:
            code = compiler.generate()
            self.code_updated.emit(code)
            QMessageBox.information(self, 'Generated Code', f'Code generated successfully!\n\nPreview (first 500 chars):\n{code[:500]}...')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to generate code: {e}')
