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
from ..store.settings import SettingsStore, tr
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
        
        delete_btn = QPushButton(tr('delete'))
        delete_btn.clicked.connect(self._on_delete)
        info_layout.addWidget(delete_btn)
        
        layout.addLayout(info_layout)
        
        # Default value
        if variable.default_value is not None:
            layout.addWidget(QLabel(f'{tr("default")}: {variable.default_value}'))
    
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
        name_layout.addWidget(QLabel(f'{tr("name")}:'))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(tr('variable_name_placeholder'))
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel(f'{tr("type")}:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(variableTypes)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Default value
        default_layout = QHBoxLayout()
        default_layout.addWidget(QLabel(f'{tr("default")}:'))
        self.default_input = QLineEdit()
        self.default_input.setPlaceholderText(tr('default_optional'))
        default_layout.addWidget(self.default_input)
        layout.addLayout(default_layout)
        
        # Create button
        create_btn = QPushButton(tr('create_variable'))
        create_btn.clicked.connect(self._on_create)
        layout.addWidget(create_btn)
    
    def _on_create(self):
        """Handle create button click."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, tr('error'), tr('variable_name_required'))
            return
        
        # Validate name starts with letter or underscore
        if len(name) > 0 and not name[0].isalpha() and name[0] != '_':
            QMessageBox.warning(self, tr('error'), tr('variable_name_invalid'))
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
            QMessageBox.warning(self, tr('error'), f'{tr("variable_exists")}: {name}')


class BuildConfigWidget(QWidget):
    """Widget for build configuration for HOI4 MOD scripts."""
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Script type selection
        script_group = QGroupBox(tr('script_type'))
        script_layout = QHBoxLayout(script_group)
        self.script_group = QButtonGroup(self)
        
        self.event_radio = QRadioButton(tr('event'))
        self.event_radio.setChecked(True)
        self.decision_radio = QRadioButton(tr('decision'))
        self.focus_radio = QRadioButton(tr('focus'))
        
        self.script_group.addButton(self.event_radio)
        self.script_group.addButton(self.decision_radio)
        self.script_group.addButton(self.focus_radio)
        script_layout.addWidget(self.event_radio)
        script_layout.addWidget(self.decision_radio)
        script_layout.addWidget(self.focus_radio)
        layout.addWidget(script_group)
        
        # Namespace input
        namespace_layout = QHBoxLayout()
        namespace_layout.addWidget(QLabel(f'{tr("namespace")}:'))
        self.namespace_input = QLineEdit('my_mod')
        namespace_layout.addWidget(self.namespace_input)
        layout.addLayout(namespace_layout)
        
        # Pack button
        pack_btn = QPushButton(tr('export_mod_script'))
        pack_btn.clicked.connect(self._on_pack)
        layout.addWidget(pack_btn)
    
    def _on_pack(self):
        """Handle pack button click."""
        compiler = CodeCompiler()
        
        # Set script type
        if self.event_radio.isChecked():
            compiler.script_type = 'event'
        elif self.decision_radio.isChecked():
            compiler.script_type = 'decision'
        else:
            compiler.script_type = 'national_focus'
        
        compiler.mod_namespace = self.namespace_input.text().strip() or 'my_mod'
        
        try:
            code = compiler.generate()
            
            # Save to file
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                tr('export_mod_script'),
                f'{compiler.mod_namespace}_{compiler.script_type}.txt',
                'HOI4 Script Files (*.txt);;All Files (*)'
            )
            
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(code)
                QMessageBox.information(self, tr('success'), f'{tr("file_saved_to")} {file_name}')
        except Exception as e:
            QMessageBox.warning(self, tr('error'), f'{tr("generate_error")}: {e}')


class ManagerPanel(QWidget):
    """Manager panel for variables, files, and build configuration."""
    
    code_updated = Signal(str)  # Generated code
    
    def __init__(self):
        super().__init__()
        self._current_file: Optional[str] = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # File operations
        self.file_group = QGroupBox(tr('file'))
        file_layout = QVBoxLayout(self.file_group)
        
        file_buttons = QHBoxLayout()
        
        self.open_btn = QPushButton(tr('open'))
        self.open_btn.clicked.connect(self._on_open)
        file_buttons.addWidget(self.open_btn)
        
        self.save_btn = QPushButton(tr('save'))
        self.save_btn.clicked.connect(self._on_save)
        file_buttons.addWidget(self.save_btn)
        
        self.save_as_btn = QPushButton(tr('save_as'))
        self.save_as_btn.clicked.connect(self._on_save_as)
        file_buttons.addWidget(self.save_as_btn)
        
        file_layout.addLayout(file_buttons)
        
        self.file_label = QLabel(f'{tr("current_file")}: {tr("local_storage")}')
        file_layout.addWidget(self.file_label)
        
        layout.addWidget(self.file_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton(tr('reset'))
        self.reset_btn.clicked.connect(self._on_reset)
        actions_layout.addWidget(self.reset_btn)
        
        self.run_btn = QPushButton(tr('run'))
        self.run_btn.clicked.connect(self._on_run)
        actions_layout.addWidget(self.run_btn)
        
        layout.addLayout(actions_layout)
        
        # Build configuration (collapsible)
        self.build_widget = BuildConfigWidget()
        self.build_widget.setVisible(False)
        
        self.build_toggle = QPushButton(f'{tr("build")} ▼')
        self.build_toggle.clicked.connect(lambda: self._toggle_section(self.build_widget, self.build_toggle, tr('build')))
        layout.addWidget(self.build_toggle)
        layout.addWidget(self.build_widget)
        
        # Variable creation (collapsible)
        self.create_var_widget = CreateVariableDialog()
        self.create_var_widget.setVisible(False)
        self.create_var_widget.created.connect(self._refresh_variables)
        
        self.create_var_toggle = QPushButton(f'{tr("create_variable")} ▼')
        self.create_var_toggle.clicked.connect(lambda: self._toggle_section(self.create_var_widget, self.create_var_toggle, tr('create_variable')))
        layout.addWidget(self.create_var_toggle)
        layout.addWidget(self.create_var_widget)
        
        # Variables list
        self.var_group = QGroupBox(tr('variables'))
        var_layout = QVBoxLayout(self.var_group)
        
        self.variables_list = QVBoxLayout()
        var_layout.addLayout(self.variables_list)
        
        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.var_group)
        layout.addWidget(scroll, 1)
        
        # Connect to variable store and settings
        VariableStore.get_instance().variable_changed.connect(self._refresh_variables)
        SettingsStore.get_instance().language_changed.connect(self._update_labels)
        
        # Initial refresh
        self._refresh_variables()
    
    def _update_labels(self):
        """Update labels when language changes."""
        self.file_group.setTitle(tr('file'))
        self.open_btn.setText(tr('open'))
        self.save_btn.setText(tr('save'))
        self.save_as_btn.setText(tr('save_as'))
        self.reset_btn.setText(tr('reset'))
        self.run_btn.setText(tr('run'))
        self.build_toggle.setText(f'{tr("build")} {"▲" if self.build_widget.isVisible() else "▼"}')
        self.create_var_toggle.setText(f'{tr("create_variable")} {"▲" if self.create_var_widget.isVisible() else "▼"}')
        self.var_group.setTitle(tr('variables'))
        if self._current_file:
            self.file_label.setText(f'{tr("current_file")}: {self._current_file.split("/")[-1]}')
        else:
            self.file_label.setText(f'{tr("current_file")}: {tr("local_storage")}')
    
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
            tr('open'),
            '',
            'JSON Files (*.json)'
        )
        
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._load_data(data)
                self._current_file = file_name
                self.file_label.setText(f'{tr("current_file")}: {file_name.split("/")[-1]}')
            except Exception as e:
                QMessageBox.warning(self, tr('error'), f'{tr("open_file_error")}: {e}')
    
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
            tr('save_as'),
            'blueprint.json',
            'JSON Files (*.json)'
        )
        
        if file_name:
            self._save_to_file(file_name)
            self._current_file = file_name
            self.file_label.setText(f'{tr("current_file")}: {file_name.split("/")[-1]}')
    
    def _save_to_file(self, file_name: str):
        """Save current state to file."""
        try:
            data = self._get_save_data()
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, tr('success'), tr('blueprint_saved'))
        except Exception as e:
            QMessageBox.warning(self, tr('error'), f'{tr("save_file_error")}: {e}')
    
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
            tr('confirm_reset'),
            tr('reset_warning'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            NodeStore.get_instance().reset_nodes()
            VariableStore.get_instance().clear_variables()
            self._current_file = None
            self.file_label.setText(f'{tr("current_file")}: {tr("local_storage")}')
    
    def _on_run(self):
        """Handle run - generate and display HOI4 MOD script code."""
        compiler = CodeCompiler()
        compiler.script_type = 'event'
        compiler.mod_namespace = 'my_mod'
        
        try:
            code = compiler.generate()
            self.code_updated.emit(code)
            preview = code[:500] + '...' if len(code) > 500 else code
            QMessageBox.information(self, tr('generated_mod_script'), f'{tr("generate_success")}\n\n{preview}')
        except Exception as e:
            QMessageBox.warning(self, tr('error'), f'{tr("generate_error")}: {e}')
