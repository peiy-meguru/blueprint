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
        
        # Connect to settings changes for immediate feedback
        self.lang_combo.currentIndexChanged.connect(self._on_language_preview)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_preview)
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Language settings
        self.lang_group = QGroupBox(tr('language'))
        lang_layout = QFormLayout(self.lang_group)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem(tr('chinese'), 'zh_CN')
        self.lang_combo.addItem(tr('english'), 'en_US')
        self.lang_label = QLabel(f'{tr("language")}:')
        lang_layout.addRow(self.lang_label, self.lang_combo)
        
        layout.addWidget(self.lang_group)
        
        # Theme settings
        self.theme_group = QGroupBox(tr('theme'))
        theme_layout = QFormLayout(self.theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(tr('dark_theme'), 'dark')
        self.theme_combo.addItem(tr('light_theme'), 'light')
        self.theme_label = QLabel(f'{tr("theme")}:')
        theme_layout.addRow(self.theme_label, self.theme_combo)
        
        layout.addWidget(self.theme_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton(tr('cancel'))
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton(tr('apply'))
        self.apply_btn.clicked.connect(self._on_apply)
        self.apply_btn.setDefault(True)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
        
        # Store original settings for cancel
        settings = SettingsStore.get_instance()
        self._original_language = settings.language
        self._original_theme = settings.theme
    
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
    
    def _on_language_preview(self):
        """Preview language change immediately."""
        settings = SettingsStore.get_instance()
        new_lang = self.lang_combo.currentData()
        if new_lang != settings.language:
            settings.language = new_lang
            self._update_labels()
            self._apply_style()
    
    def _on_theme_preview(self):
        """Preview theme change immediately."""
        settings = SettingsStore.get_instance()
        new_theme = self.theme_combo.currentData()
        if new_theme != settings.theme:
            settings.theme = new_theme
            self._apply_style()
    
    def _update_labels(self):
        """Update labels when language changes."""
        self.setWindowTitle(tr('settings'))
        self.lang_group.setTitle(tr('language'))
        self.theme_group.setTitle(tr('theme'))
        self.lang_label.setText(f'{tr("language")}:')
        self.theme_label.setText(f'{tr("theme")}:')
        self.cancel_btn.setText(tr('cancel'))
        self.apply_btn.setText(tr('apply'))
        
        # Update combo box items
        current_lang = self.lang_combo.currentData()
        current_theme = self.theme_combo.currentData()
        
        self.lang_combo.clear()
        self.lang_combo.addItem(tr('chinese'), 'zh_CN')
        self.lang_combo.addItem(tr('english'), 'en_US')
        lang_index = self.lang_combo.findData(current_lang)
        if lang_index >= 0:
            self.lang_combo.setCurrentIndex(lang_index)
        
        self.theme_combo.clear()
        self.theme_combo.addItem(tr('dark_theme'), 'dark')
        self.theme_combo.addItem(tr('light_theme'), 'light')
        theme_index = self.theme_combo.findData(current_theme)
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
        # Settings are already applied via preview, just accept
        self.accept()
    
    def _on_cancel(self):
        """Cancel changes and restore original settings."""
        settings = SettingsStore.get_instance()
        
        # Restore original settings
        if settings.language != self._original_language:
            settings.language = self._original_language
        
        if settings.theme != self._original_theme:
            settings.theme = self._original_theme
        
        self.reject()
