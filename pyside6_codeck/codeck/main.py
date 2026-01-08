"""Main application window for Codeck."""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from .components.flow_editor import FlowEditorView
from .components.manager_panel import ManagerPanel
from .components.code_editor import CodeEditor
from .nodes.definitions.all_nodes import register_builtin_nodes
from .store.node import NodeStore


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Codeck - Visual Blueprint Programming')
        self.setMinimumSize(1200, 800)
        
        # Register builtin nodes
        register_builtin_nodes()
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
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
        
        # Initialize with default nodes (after UI is created)
        NodeStore.get_instance().reset_nodes()
        
        # Apply dark theme
        self._apply_dark_theme()
    
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
        ''')


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
