"""Main application window for Codeck - HOI4 MOD Visual Programming."""

import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout,
    QStackedWidget, QMenuBar, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QPointF

from .components.flow_editor import FlowEditorView
from .components.manager_panel import ManagerPanel
from .components.code_editor import CodeEditor
from .components.project_manager import ProjectManager
from .components.settings_dialog import SettingsDialog
from .nodes.definitions.all_nodes import register_builtin_nodes
from .store.node import NodeStore, CodeckNode
from .store.connection import ConnectionStore, ConnectInfo
from .store.variable import VariableStore, VariableItem
from .store.settings import SettingsStore, tr


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(tr('app_title'))
        self.setMinimumSize(1200, 800)
        
        # Register builtin nodes
        register_builtin_nodes()
        
        # Create stacked widget for switching between project manager and editor
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create project manager page
        self.project_manager = ProjectManager()
        self.project_manager.project_opened.connect(self._on_project_opened)
        self.project_manager.project_created.connect(self._on_project_created)
        self.stacked_widget.addWidget(self.project_manager)
        
        # Create editor page
        self.editor_widget = QWidget()
        self._setup_editor()
        self.stacked_widget.addWidget(self.editor_widget)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Start with project manager
        self.stacked_widget.setCurrentWidget(self.project_manager)
        
        # Apply theme
        self._apply_theme()
        
        # Connect to settings changes
        settings = SettingsStore.get_instance()
        settings.theme_changed.connect(self._apply_theme)
        settings.language_changed.connect(self._update_labels)
    
    def _setup_editor(self):
        """Set up the main editor layout."""
        main_layout = QVBoxLayout(self.editor_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Manager
        self.manager_panel = ManagerPanel()
        self.manager_panel.setMinimumWidth(250)
        self.manager_panel.setMaximumWidth(400)
        main_splitter.addWidget(self.manager_panel)
        
        # Right side - Flow editor and code editor in vertical splitter
        right_splitter = QSplitter(Qt.Vertical)
        
        # Flow editor
        self.flow_editor = FlowEditorView()
        right_splitter.addWidget(self.flow_editor)
        
        # Code editor
        self.code_editor = CodeEditor()
        self.code_editor.setMinimumHeight(150)
        right_splitter.addWidget(self.code_editor)
        
        # Set initial sizes for vertical splitter (70% flow, 30% code)
        right_splitter.setSizes([500, 200])
        
        main_splitter.addWidget(right_splitter)
        
        # Set initial sizes for horizontal splitter
        main_splitter.setSizes([250, 950])
        
        main_layout.addWidget(main_splitter)
        
        # Connect signals
        self.manager_panel.code_updated.connect(self.code_editor.set_code)
    
    def _create_menu_bar(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu(tr('file'))
        
        new_action = file_menu.addAction(tr('new_project'))
        new_action.triggered.connect(self._on_new_project)
        
        open_action = file_menu.addAction(tr('open_project'))
        open_action.triggered.connect(self._on_open_project)
        
        file_menu.addSeparator()
        
        save_action = file_menu.addAction(tr('save'))
        save_action.triggered.connect(self._on_save)
        
        save_as_action = file_menu.addAction(tr('save_as'))
        save_as_action.triggered.connect(self._on_save_as)
        
        file_menu.addSeparator()
        
        home_action = file_menu.addAction(tr('recent_projects'))
        home_action.triggered.connect(self._go_to_project_manager)
        
        # Edit menu
        edit_menu = menu_bar.addMenu(tr('edit'))
        
        reset_action = edit_menu.addAction(tr('reset'))
        reset_action.triggered.connect(self._on_reset)
        
        # Settings menu
        settings_menu = menu_bar.addMenu(tr('settings'))
        
        settings_action = settings_menu.addAction(tr('settings'))
        settings_action.triggered.connect(self._on_settings)
    
    def _update_labels(self):
        """Update labels when language changes."""
        self.setWindowTitle(tr('app_title'))
        self._create_menu_bar()
    
    def _apply_theme(self):
        """Apply theme to the application."""
        settings = SettingsStore.get_instance()
        
        if settings.theme == 'dark':
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_dark_theme(self):
        """Apply dark theme to the application."""
        self.setStyleSheet('''
            QMainWindow {
                background-color: #1e1e1e;
            }
            QSplitter::handle {
                background-color: #333;
            }
            QWidget {
                background-color: #252526;
                color: #cccccc;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #0e639c;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5085;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #ccc;
            }
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            QLabel {
                background-color: transparent;
            }
            QMenu {
                background-color: #252526;
                border: 1px solid #444;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QMenuBar {
                background-color: #333;
                color: #ccc;
            }
            QMenuBar::item:selected {
                background-color: #094771;
            }
        ''')
    
    def _apply_light_theme(self):
        """Apply light theme to the application."""
        self.setStyleSheet('''
            QMainWindow {
                background-color: #f5f5f5;
            }
            QSplitter::handle {
                background-color: #ddd;
            }
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1c88db;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 4px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 4px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
            }
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background-color: #f5f5f5;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #ccc;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #bbb;
            }
            QLabel {
                background-color: transparent;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #ccc;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QMenuBar {
                background-color: #f0f0f0;
                color: #333;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
                color: white;
            }
        ''')
    
    def _on_project_opened(self, path: str):
        """Handle project opened from project manager."""
        self._load_project(path)
        self.stacked_widget.setCurrentWidget(self.editor_widget)
    
    def _on_project_created(self, info: dict):
        """Handle new project created."""
        # Reset stores
        NodeStore.get_instance().reset_nodes()
        VariableStore.get_instance().clear_variables()
        
        # Save empty project
        self._save_project(info['path'])
        
        # Switch to editor
        self.stacked_widget.setCurrentWidget(self.editor_widget)
    
    def _on_new_project(self):
        """Handle new project menu action."""
        self._go_to_project_manager()
        self.project_manager._on_new_project()
    
    def _on_open_project(self):
        """Handle open project menu action."""
        self._go_to_project_manager()
        self.project_manager._on_open_project()
    
    def _on_save(self):
        """Handle save menu action."""
        if self.stacked_widget.currentWidget() == self.editor_widget:
            self.manager_panel._on_save()
    
    def _on_save_as(self):
        """Handle save as menu action."""
        if self.stacked_widget.currentWidget() == self.editor_widget:
            self.manager_panel._on_save_as()
    
    def _on_reset(self):
        """Handle reset menu action."""
        if self.stacked_widget.currentWidget() == self.editor_widget:
            self.manager_panel._on_reset()
    
    def _on_settings(self):
        """Handle settings menu action."""
        dialog = SettingsDialog(self)
        dialog.exec()
        self._apply_theme()
    
    def _go_to_project_manager(self):
        """Switch to project manager view."""
        self.stacked_widget.setCurrentWidget(self.project_manager)
    
    def _load_project(self, path: str):
        """Load a project from file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._load_data(data)
            self.manager_panel._current_file = path
            self.manager_panel.file_label.setText(f'{tr("current_file")}: {path.split("/")[-1]}')
        except Exception as e:
            QMessageBox.warning(self, tr('error'), f'{tr("load_project_error")}: {e}')
    
    def _save_project(self, path: str):
        """Save project to file."""
        try:
            data = self.manager_panel._get_save_data()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.manager_panel._current_file = path
            self.manager_panel.file_label.setText(f'{tr("current_file")}: {path.split("/")[-1]}')
        except Exception as e:
            QMessageBox.warning(self, tr('error'), f'{tr("save_project_error")}: {e}')
    
    def _load_data(self, data: dict):
        """Load state from saved data."""
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


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set up font with Chinese/Unicode support
    from PySide6.QtGui import QFont, QFontDatabase
    
    # Try to use fonts that support Chinese characters
    # Priority: Noto Sans CJK > Microsoft YaHei > SimHei > WenQuanYi > System default
    chinese_fonts = [
        'Noto Sans CJK SC',
        'Noto Sans SC', 
        'Microsoft YaHei',
        'SimHei',
        'WenQuanYi Micro Hei',
        'WenQuanYi Zen Hei',
        'Source Han Sans CN',
        'PingFang SC',
        'Hiragino Sans GB',
    ]
    
    # Find available font with Chinese support
    available_families = QFontDatabase.families()
    selected_font = None
    for font_name in chinese_fonts:
        if font_name in available_families:
            selected_font = font_name
            break
    
    if selected_font:
        font = QFont(selected_font, 10)
        app.setFont(font)
    else:
        # Fall back to default font but ensure it can handle Unicode
        font = app.font()
        font.setPointSize(10)
        app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
