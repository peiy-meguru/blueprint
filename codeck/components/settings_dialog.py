"""Settings Dialog - Configure application preferences."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QPushButton, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..store.settings import SettingsStore, tr


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('settings'))
        self.setMinimumSize(400, 250)
        
        self._setup_ui()
        self._load_current_settings()
        self._apply_style()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Language settings
        lang_group = QGroupBox(tr('language'))
        lang_layout = QFormLayout(lang_group)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(tr('chinese'), 'zh_CN')
        self.lang_combo.addItem(tr('english'), 'en_US')
        lang_layout.addRow(tr('language') + ':', self.lang_combo)
        
        layout.addWidget(lang_group)
        
        # Theme settings
        theme_group = QGroupBox(tr('theme'))
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr('dark_theme'), 'dark')
        self.theme_combo.addItem(tr('light_theme'), 'light')
        theme_layout.addRow(tr('theme') + ':', self.theme_combo)
        
        layout.addWidget(theme_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(tr('reset'))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton(tr('save'))
        apply_btn.clicked.connect(self._on_apply)
        apply_btn.setDefault(True)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
    
    def _load_current_settings(self):
        """Load current settings into the UI."""
        settings = SettingsStore.get_instance()
        
        # Set language
        lang_index = self.lang_combo.findData(settings.language)
        if lang_index >= 0:
            self.lang_combo.setCurrentIndex(lang_index)
        
        # Set theme
        theme_index = self.theme_combo.findData(settings.theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
    
    def _apply_style(self):
        """Apply dialog styling."""
        settings = SettingsStore.get_instance()
        
        if settings.theme == 'dark':
            self.setStyleSheet('''
                QDialog {
                    background-color: #252526;
                }
                QLabel {
                    color: #cccccc;
                }
                QGroupBox {
                    color: #cccccc;
                    border: 1px solid #444;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 12px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    border: 1px solid #555;
                    padding: 5px;
                    border-radius: 3px;
                    color: #cccccc;
                    min-width: 150px;
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
                QComboBox QAbstractItemView {
                    background-color: #3c3c3c;
                    border: 1px solid #555;
                    selection-background-color: #0e639c;
                }
                QPushButton {
                    background-color: #0e639c;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 3px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
            ''')
        else:
            self.setStyleSheet('''
                QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
                QGroupBox {
                    color: #333333;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 12px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
                QComboBox {
                    background-color: white;
                    border: 1px solid #ccc;
                    padding: 5px;
                    border-radius: 3px;
                    color: #333333;
                    min-width: 150px;
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
                QComboBox QAbstractItemView {
                    background-color: white;
                    border: 1px solid #ccc;
                    selection-background-color: #0078d4;
                }
                QPushButton {
                    background-color: #0078d4;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 3px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #1c88db;
                }
            ''')
    
    def _on_apply(self):
        """Apply settings and close dialog."""
        settings = SettingsStore.get_instance()
        
        # Save language
        settings.language = self.lang_combo.currentData()
        
        # Save theme
        settings.theme = self.theme_combo.currentData()
        
        self.accept()
