"""Project Manager - Start page for managing MOD projects."""

import os
from datetime import datetime
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QFileDialog, QMessageBox, QDialog,
    QLineEdit, QTextEdit, QFormLayout, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QColor, QPalette

from ..store.settings import SettingsStore, RecentProject, tr, get_font_family


def _get_font(size: int, bold: bool = False) -> QFont:
    """Get a font with Chinese support at the specified size."""
    font_family = get_font_family()
    if font_family:
        font = QFont(font_family, size)
    else:
        font = QFont()
        font.setPointSize(size)
    if bold:
        font.setBold(True)
    return font

class ProjectCard(QFrame):
    """A card widget displaying a recent project."""
    
    clicked = Signal(str)  # Project path
    
    def __init__(self, project: RecentProject):
        super().__init__()
        self.project = project
        
        self.setMinimumSize(280, 100)
        self.setMaximumHeight(120)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Project image/icon
        image_label = QLabel()
        image_label.setFixedSize(60, 60)
        image_label.setAlignment(Qt.AlignCenter)
        
        if project.image_path and os.path.exists(project.image_path):
            pixmap = QPixmap(project.image_path)
            pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            # Default placeholder with icon-like appearance
            image_label.setText('📁')
            image_label.setStyleSheet('''
                QLabel {
                    background-color: #3c3c3c;
                    border: 1px solid #555;
                    border-radius: 8px;
                    color: #888;
                    font-size: 24px;
                }
            ''')
        
        layout.addWidget(image_label)
        
        # Project info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Name
        name_label = QLabel(project.name or os.path.basename(project.path))
        name_label.setFont(_get_font(12, bold=True))
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        
        # Description or path
        if project.description:
            desc_text = project.description[:40] + '...' if len(project.description) > 40 else project.description
            desc_label = QLabel(desc_text)
            desc_label.setStyleSheet('color: #888; font-size: 11px;')
            desc_label.setWordWrap(True)
            info_layout.addWidget(desc_label)
        
        # Path (truncated)
        path_label = QLabel(self._truncate_path(project.path, 30))
        path_label.setStyleSheet('color: #666; font-size: 10px;')
        info_layout.addWidget(path_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)
        
        self._apply_style()
    
    def _truncate_path(self, path: str, max_len: int = 35) -> str:
        """Truncate a path for display."""
        if len(path) <= max_len:
            return path
        return '...' + path[-(max_len - 3):]
    
    def _apply_style(self):
        """Apply card styling."""
        self.setStyleSheet('''
            ProjectCard {
                background-color: #2d2d30;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
            }
            ProjectCard:hover {
                background-color: #383838;
                border-color: #0e639c;
            }
        ''')
    
    def mousePressEvent(self, event):
        """Handle click to open project."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.project.path)
        super().mousePressEvent(event)


class NewProjectDialog(QDialog):
    """Dialog for creating a new MOD project."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('new_project'))
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # MOD name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(tr('mod_name'))
        form_layout.addRow(tr('mod_name') + ':', self.name_input)
        
        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText(tr('mod_description'))
        self.desc_input.setMaximumHeight(80)
        form_layout.addRow(tr('mod_description') + ':', self.desc_input)
        
        # Project path
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(tr('open_project'))
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton('...')
        browse_btn.setMaximumWidth(40)
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)
        
        form_layout.addRow(tr('project_info') + ':', path_layout)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton(tr('reset'))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton(tr('new_project'))
        create_btn.clicked.connect(self._on_create)
        create_btn.setDefault(True)
        button_layout.addWidget(create_btn)
        
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self._apply_style()
    
    def _apply_style(self):
        """Apply dialog styling."""
        self.setStyleSheet('''
            QDialog {
                background-color: #252526;
            }
            QLabel {
                color: #cccccc;
            }
            QLineEdit, QTextEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
                color: #cccccc;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #007acc;
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
    
    def _browse_path(self):
        """Browse for project directory."""
        path = QFileDialog.getSaveFileName(
            self,
            tr('new_project'),
            '',
            'MOD Project (*.modproj)'
        )[0]
        
        if path:
            if not path.endswith('.modproj'):
                path += '.modproj'
            self.path_input.setText(path)
    
    def _on_create(self):
        """Handle project creation."""
        name = self.name_input.text().strip()
        path = self.path_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, tr('error'), tr('mod_name_required'))
            return
        
        if not path:
            QMessageBox.warning(self, tr('error'), tr('project_path_required'))
            return
        
        self.accept()
    
    def get_project_info(self) -> dict:
        """Get the entered project information."""
        return {
            'name': self.name_input.text().strip(),
            'description': self.desc_input.toPlainText().strip(),
            'path': self.path_input.text().strip()
        }


class ProjectManager(QWidget):
    """Project manager start page."""
    
    project_opened = Signal(str)  # Project path
    project_created = Signal(dict)  # Project info dict
    
    def __init__(self):
        super().__init__()
        
        self._setup_ui()
        self._apply_style()
        self._refresh_recent_projects()
        
        # Connect to settings changes
        settings = SettingsStore.get_instance()
        settings.recent_projects_changed.connect(self._refresh_recent_projects)
        settings.language_changed.connect(self._update_labels)
    
    def _setup_ui(self):
        """Set up the user interface with modern horizontal layout."""
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== Left Sidebar =====
        left_panel = QFrame()
        left_panel.setObjectName('leftPanel')
        left_panel.setFixedWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 40, 30, 40)
        left_layout.setSpacing(20)
        
        # App logo/title in sidebar
        self.title_label = QLabel(tr('app_title'))
        self.title_label.setFont(_get_font(16, bold=True))
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignLeft)
        left_layout.addWidget(self.title_label)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName('separator')
        left_layout.addWidget(separator)
        
        # Action buttons - vertically arranged
        self.new_btn = QPushButton('  ' + tr('new_project'))
        self.new_btn.setFixedHeight(45)
        self.new_btn.setFont(_get_font(12))
        self.new_btn.setCursor(Qt.PointingHandCursor)
        self.new_btn.clicked.connect(self._on_new_project)
        left_layout.addWidget(self.new_btn)
        
        self.open_btn = QPushButton('  ' + tr('open_project'))
        self.open_btn.setFixedHeight(45)
        self.open_btn.setFont(_get_font(12))
        self.open_btn.setCursor(Qt.PointingHandCursor)
        self.open_btn.clicked.connect(self._on_open_project)
        left_layout.addWidget(self.open_btn)
        
        self.settings_btn = QPushButton('  ' + tr('settings'))
        self.settings_btn.setFixedHeight(45)
        self.settings_btn.setFont(_get_font(12))
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self._on_settings)
        left_layout.addWidget(self.settings_btn)
        
        left_layout.addStretch()
        
        # Version info at bottom
        version_label = QLabel('v1.0.0')
        version_label.setStyleSheet('color: #666; font-size: 11px;')
        version_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(version_label)
        
        main_layout.addWidget(left_panel)
        
        # ===== Right Panel - Recent Projects =====
        right_panel = QFrame()
        right_panel.setObjectName('rightPanel')
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(20)
        
        # Recent projects header
        self.recent_label = QLabel(tr('recent_projects'))
        self.recent_label.setFont(_get_font(18, bold=True))
        right_layout.addWidget(self.recent_label)
        
        # Scroll area for recent projects - grid layout
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setObjectName('projectsScrollArea')
        
        self.projects_widget = QWidget()
        self.projects_widget.setObjectName('projectsWidget')
        self.projects_layout = QGridLayout(self.projects_widget)
        self.projects_layout.setContentsMargins(0, 0, 10, 0)
        self.projects_layout.setSpacing(15)
        self.projects_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.scroll_area.setWidget(self.projects_widget)
        right_layout.addWidget(self.scroll_area, 1)
        
        # No recent projects label (centered in the scroll area)
        self.no_projects_label = QLabel(tr('no_recent_projects'))
        self.no_projects_label.setAlignment(Qt.AlignCenter)
        self.no_projects_label.setFont(_get_font(14))
        self.no_projects_label.setStyleSheet('color: #666;')
        self.no_projects_label.hide()
        right_layout.addWidget(self.no_projects_label, 1)
        
        main_layout.addWidget(right_panel, 1)
    
    def _apply_style(self):
        """Apply styling based on current theme."""
        settings = SettingsStore.get_instance()
        
        if settings.theme == 'dark':
            self.setStyleSheet('''
                QWidget {
                    background-color: #1e1e1e;
                    color: #cccccc;
                }
                QFrame#leftPanel {
                    background-color: #252526;
                    border-right: 1px solid #3c3c3c;
                }
                QFrame#rightPanel {
                    background-color: #1e1e1e;
                }
                QFrame#separator {
                    background-color: #3c3c3c;
                    max-height: 1px;
                }
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 12px 15px;
                    border-radius: 6px;
                    color: #cccccc;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3c3c3c;
                }
                QPushButton:pressed {
                    background-color: #0e639c;
                }
                QScrollArea#projectsScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QWidget#projectsWidget {
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #1e1e1e;
                    width: 10px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background-color: #555;
                    min-height: 30px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #666;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            ''')
        else:
            self.setStyleSheet('''
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QFrame#leftPanel {
                    background-color: #ffffff;
                    border-right: 1px solid #e0e0e0;
                }
                QFrame#rightPanel {
                    background-color: #f5f5f5;
                }
                QFrame#separator {
                    background-color: #e0e0e0;
                    max-height: 1px;
                }
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 12px 15px;
                    border-radius: 6px;
                    color: #333333;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #0078d4;
                    color: white;
                }
                QScrollArea#projectsScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QWidget#projectsWidget {
                    background-color: transparent;
                }
                QScrollBar:vertical {
                    background-color: #f5f5f5;
                    width: 10px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background-color: #ccc;
                    min-height: 30px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #bbb;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            ''')
    
    def _update_labels(self):
        """Update labels when language changes."""
        self.title_label.setText(tr('app_title'))
        self.new_btn.setText('  ' + tr('new_project'))
        self.open_btn.setText('  ' + tr('open_project'))
        self.settings_btn.setText('  ' + tr('settings'))
        self.recent_label.setText(tr('recent_projects'))
        self.no_projects_label.setText(tr('no_recent_projects'))
    
    def _refresh_recent_projects(self):
        """Refresh the recent projects display."""
        # Clear existing project cards
        while self.projects_layout.count():
            item = self.projects_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get recent projects
        settings = SettingsStore.get_instance()
        projects = settings.recent_projects
        
        if not projects:
            self.scroll_area.hide()
            self.no_projects_label.show()
        else:
            self.no_projects_label.hide()
            self.scroll_area.show()
            
            # Add cards in a grid layout (2 columns)
            cols = 2
            for idx, project in enumerate(projects):
                card = ProjectCard(project)
                card.clicked.connect(self._on_project_clicked)
                row = idx // cols
                col = idx % cols
                self.projects_layout.addWidget(card, row, col)
    
    def _on_new_project(self):
        """Handle new project button click."""
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            info = dialog.get_project_info()
            
            # Add to recent projects
            settings = SettingsStore.get_instance()
            settings.add_recent_project(RecentProject(
                name=info['name'],
                path=info['path'],
                description=info['description'],
                last_opened=datetime.now().isoformat()
            ))
            
            self.project_created.emit(info)
    
    def _on_open_project(self):
        """Handle open project button click."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            tr('open_project'),
            '',
            'MOD Project (*.modproj);;JSON Files (*.json);;All Files (*)'
        )
        
        if file_name:
            self._open_project(file_name)
    
    def _on_project_clicked(self, path: str):
        """Handle project card click."""
        self._open_project(path)
    
    def _open_project(self, path: str):
        """Open a project from the given path."""
        if not os.path.exists(path):
            settings = SettingsStore.get_instance()
            settings.remove_recent_project(path)
            QMessageBox.warning(
                self,
                tr('error'),
                f'{tr("project_not_found")}: {path}'
            )
            return
        
        # Add/update in recent projects
        settings = SettingsStore.get_instance()
        
        # Try to read project info
        name = os.path.basename(path).replace('.modproj', '').replace('.json', '')
        
        settings.add_recent_project(RecentProject(
            name=name,
            path=path,
            last_opened=datetime.now().isoformat()
        ))
        
        self.project_opened.emit(path)
    
    def _on_settings(self):
        """Handle settings button click."""
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
        
        # Re-apply styles after settings change
        self._apply_style()
        self._update_labels()
