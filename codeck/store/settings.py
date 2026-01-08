"""Settings store for application preferences."""

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Literal, Optional
from PySide6.QtCore import QObject, Signal


# Supported languages and themes
SUPPORTED_LANGUAGES = ('zh_CN', 'en_US')
SUPPORTED_THEMES = ('dark', 'light')

Language = Literal['zh_CN', 'en_US']
Theme = Literal['dark', 'light']


@dataclass
class RecentProject:
    """Information about a recently opened project."""
    name: str
    path: str
    image_path: Optional[str] = None
    description: str = ''
    last_opened: str = ''


@dataclass
class AppSettings:
    """Application settings data."""
    language: Language = 'zh_CN'
    theme: Theme = 'dark'
    recent_projects: list[RecentProject] = field(default_factory=list)
    last_project_path: str = ''


class SettingsStore(QObject):
    """Store for application settings."""
    
    # Signals
    settings_changed = Signal()
    language_changed = Signal(str)
    theme_changed = Signal(str)
    recent_projects_changed = Signal()
    
    _instance: Optional['SettingsStore'] = None
    
    # Settings file path - use platform-appropriate config directory
    MAX_RECENT_PROJECTS = 10
    
    @staticmethod
    def _get_config_dir() -> str:
        """Get platform-appropriate configuration directory."""
        if sys.platform == 'win32':
            config_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
        elif sys.platform == 'darwin':
            config_dir = os.path.expanduser('~/Library/Application Support')
        else:
            config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        
        codeck_dir = os.path.join(config_dir, 'codeck')
        os.makedirs(codeck_dir, exist_ok=True)
        return codeck_dir
    
    @property
    def settings_file(self) -> str:
        """Get settings file path."""
        return os.path.join(self._get_config_dir(), 'settings.json')
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()
        self._initialized = True
        self._settings = AppSettings()
        self._load_settings()
    
    @classmethod
    def get_instance(cls) -> 'SettingsStore':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def _load_settings(self) -> None:
        """Load settings from file."""
        if not os.path.exists(self.settings_file):
            return
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate and load language
            language = data.get('language', 'zh_CN')
            if language not in SUPPORTED_LANGUAGES:
                language = 'zh_CN'
            self._settings.language = language
            
            # Validate and load theme
            theme = data.get('theme', 'dark')
            if theme not in SUPPORTED_THEMES:
                theme = 'dark'
            self._settings.theme = theme
            
            self._settings.last_project_path = data.get('last_project_path', '')
            
            # Load recent projects with validation
            recent = data.get('recent_projects', [])
            self._settings.recent_projects = []
            for p in recent:
                if isinstance(p, dict) and p.get('path'):
                    self._settings.recent_projects.append(
                        RecentProject(
                            name=p.get('name', ''),
                            path=p.get('path', ''),
                            image_path=p.get('image_path'),
                            description=p.get('description', ''),
                            last_opened=p.get('last_opened', '')
                        )
                    )
        except (json.JSONDecodeError, IOError, TypeError) as e:
            print(f'Warning: Failed to load settings: {e}')
    
    def _save_settings(self) -> None:
        """Save settings to file."""
        try:
            data = {
                'language': self._settings.language,
                'theme': self._settings.theme,
                'last_project_path': self._settings.last_project_path,
                'recent_projects': [
                    {
                        'name': p.name,
                        'path': p.path,
                        'image_path': p.image_path,
                        'description': p.description,
                        'last_opened': p.last_opened
                    }
                    for p in self._settings.recent_projects
                ]
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f'Warning: Failed to save settings: {e}')
    
    @property
    def language(self) -> Language:
        """Get current language."""
        return self._settings.language
    
    @language.setter
    def language(self, value: Language) -> None:
        """Set language."""
        if self._settings.language != value:
            self._settings.language = value
            self._save_settings()
            self.language_changed.emit(value)
            self.settings_changed.emit()
    
    @property
    def theme(self) -> Theme:
        """Get current theme."""
        return self._settings.theme
    
    @theme.setter
    def theme(self, value: Theme) -> None:
        """Set theme."""
        if self._settings.theme != value:
            self._settings.theme = value
            self._save_settings()
            self.theme_changed.emit(value)
            self.settings_changed.emit()
    
    @property
    def recent_projects(self) -> list[RecentProject]:
        """Get recent projects."""
        return self._settings.recent_projects.copy()
    
    def add_recent_project(self, project: RecentProject) -> None:
        """Add a project to recent projects list."""
        # Remove existing entry if present
        self._settings.recent_projects = [
            p for p in self._settings.recent_projects
            if p.path != project.path
        ]
        
        # Add to front
        self._settings.recent_projects.insert(0, project)
        
        # Limit to max recent projects
        if len(self._settings.recent_projects) > self.MAX_RECENT_PROJECTS:
            self._settings.recent_projects = self._settings.recent_projects[:self.MAX_RECENT_PROJECTS]
        
        self._save_settings()
        self.recent_projects_changed.emit()
        self.settings_changed.emit()
    
    def remove_recent_project(self, path: str) -> None:
        """Remove a project from recent projects list."""
        self._settings.recent_projects = [
            p for p in self._settings.recent_projects
            if p.path != path
        ]
        self._save_settings()
        self.recent_projects_changed.emit()
        self.settings_changed.emit()
    
    def clear_recent_projects(self) -> None:
        """Clear all recent projects."""
        self._settings.recent_projects = []
        self._save_settings()
        self.recent_projects_changed.emit()
        self.settings_changed.emit()
    
    @property
    def last_project_path(self) -> str:
        """Get last project path."""
        return self._settings.last_project_path
    
    @last_project_path.setter
    def last_project_path(self, value: str) -> None:
        """Set last project path."""
        self._settings.last_project_path = value
        self._save_settings()


# Translations dictionary
TRANSLATIONS = {
    'zh_CN': {
        # Application
        'app_title': 'Codeck - HOI4 MOD 可视化编程',
        'version': '版本',
        
        # Menu - File
        'file': '文件',
        'new_project': '新建项目',
        'open_project': '打开项目',
        'open': '打开',
        'save': '保存',
        'save_as': '另存为',
        'recent_projects': '最近项目',
        'exit': '退出',
        
        # Menu - Edit
        'edit': '编辑',
        'reset': '重置',
        'undo': '撤销',
        'redo': '重做',
        'cut': '剪切',
        'copy': '复制',
        'paste': '粘贴',
        'select_all': '全选',
        
        # Menu - View
        'view': '视图',
        'zoom_in': '放大',
        'zoom_out': '缩小',
        'fit_to_window': '适应窗口',
        'focus_nodes': '聚焦节点',
        
        # Menu - Help
        'help': '帮助',
        'about': '关于',
        'documentation': '文档',
        'keyboard_shortcuts': '键盘快捷键',
        
        # Settings
        'settings': '设置',
        'language': '语言',
        'theme': '界面风格',
        'dark_theme': '深色主题',
        'light_theme': '浅色主题',
        'chinese': '中文',
        'english': 'English',
        'apply': '应用',
        'cancel': '取消',
        'ok': '确定',
        
        # Project
        'project_info': '项目信息',
        'project_path': '项目路径',
        'browse': '浏览',
        'no_recent_projects': '暂无最近项目',
        'project_not_found': '项目文件未找到',
        'mod_name_required': 'MOD名称是必填项',
        'project_path_required': '项目路径是必填项',
        
        # MOD
        'mod_name': 'MOD 名称',
        'mod_description': 'MOD 描述',
        'mod_image': 'MOD 图片',
        'namespace': '命名空间',
        
        # Build
        'build': '构建',
        'run': '运行',
        'pack': '打包',
        'export': '导出',
        'export_mod_script': '导出 MOD 脚本',
        'script_type': '脚本类型',
        'event': '事件',
        'decision': '决议',
        'focus': '国策',
        'idea': '国家精神',
        
        # Variables
        'variables': '变量',
        'create_variable': '创建变量',
        'delete_variable': '删除变量',
        'variable_name': '变量名',
        'variable_name_placeholder': '请输入变量名',
        'variable_name_required': '变量名是必填项',
        'variable_name_invalid': '变量名必须以字母或下划线开头',
        'variable_exists': '变量已存在',
        
        # Common labels
        'name': '名称',
        'type': '类型',
        'default': '默认值',
        'default_optional': '默认值（可选）',
        'value': '值',
        'delete': '删除',
        'confirm': '确认',
        
        # File operations
        'current_file': '当前文件',
        'local_storage': '本地存储',
        'blueprint_saved': '蓝图保存成功',
        'file_saved_to': '文件已保存到',
        'open_file_error': '打开文件失败',
        'save_file_error': '保存文件失败',
        'load_project_error': '加载项目失败',
        'save_project_error': '保存项目失败',
        
        # Code generation
        'generated_code': '生成的脚本',
        'generated_mod_script': '生成的 MOD 脚本',
        'code_saved': '代码已保存到',
        'generate_success': 'MOD 脚本生成成功！',
        'generate_error': '生成 MOD 脚本失败',
        
        # Dialogs
        'confirm_reset': '确认重置',
        'reset_warning': '确定要重置吗？所有未保存的更改将会丢失。',
        'error': '错误',
        'success': '成功',
        'warning': '警告',
        'info': '提示',
        
        # Platform
        'platform': '平台',
        'module_type': '模块类型',
        
        # Nodes
        'nodes': '节点',
        'core_nodes': '核心节点',
        'logic_nodes': '逻辑节点',
        'variable_nodes': '变量节点',
        'get_variable': '获取变量',
        'set_variable': '设置变量',
        
        # Flow editor context menu
        'add_node': '添加节点',
        
        # Error messages
        'invalid_blueprint_format': '无效的蓝图格式',
        'no_begin_node': '未找到开始节点',
        'multiple_begin_nodes': '存在多个开始节点',
    },
    'en_US': {
        # Application
        'app_title': 'Codeck - HOI4 MOD Visual Programming',
        'version': 'Version',
        
        # Menu - File
        'file': 'File',
        'new_project': 'New Project',
        'open_project': 'Open Project',
        'open': 'Open',
        'save': 'Save',
        'save_as': 'Save As',
        'recent_projects': 'Recent Projects',
        'exit': 'Exit',
        
        # Menu - Edit
        'edit': 'Edit',
        'reset': 'Reset',
        'undo': 'Undo',
        'redo': 'Redo',
        'cut': 'Cut',
        'copy': 'Copy',
        'paste': 'Paste',
        'select_all': 'Select All',
        
        # Menu - View
        'view': 'View',
        'zoom_in': 'Zoom In',
        'zoom_out': 'Zoom Out',
        'fit_to_window': 'Fit to Window',
        'focus_nodes': 'Focus Nodes',
        
        # Menu - Help
        'help': 'Help',
        'about': 'About',
        'documentation': 'Documentation',
        'keyboard_shortcuts': 'Keyboard Shortcuts',
        
        # Settings
        'settings': 'Settings',
        'language': 'Language',
        'theme': 'Interface Style',
        'dark_theme': 'Dark Theme',
        'light_theme': 'Light Theme',
        'chinese': '中文',
        'english': 'English',
        'apply': 'Apply',
        'cancel': 'Cancel',
        'ok': 'OK',
        
        # Project
        'project_info': 'Project Info',
        'project_path': 'Project Path',
        'browse': 'Browse',
        'no_recent_projects': 'No Recent Projects',
        'project_not_found': 'Project file not found',
        'mod_name_required': 'MOD name is required',
        'project_path_required': 'Project path is required',
        
        # MOD
        'mod_name': 'MOD Name',
        'mod_description': 'MOD Description',
        'mod_image': 'MOD Image',
        'namespace': 'Namespace',
        
        # Build
        'build': 'Build',
        'run': 'Run',
        'pack': 'Pack',
        'export': 'Export',
        'export_mod_script': 'Export MOD Script',
        'script_type': 'Script Type',
        'event': 'Event',
        'decision': 'Decision',
        'focus': 'Focus',
        'idea': 'Idea',
        
        # Variables
        'variables': 'Variables',
        'create_variable': 'Create Variable',
        'delete_variable': 'Delete Variable',
        'variable_name': 'Variable Name',
        'variable_name_placeholder': 'Enter variable name',
        'variable_name_required': 'Variable name is required',
        'variable_name_invalid': 'Variable name must start with a letter or underscore',
        'variable_exists': 'Variable already exists',
        
        # Common labels
        'name': 'Name',
        'type': 'Type',
        'default': 'Default',
        'default_optional': 'Default (optional)',
        'value': 'Value',
        'delete': 'Delete',
        'confirm': 'Confirm',
        
        # File operations
        'current_file': 'Current File',
        'local_storage': 'Local Storage',
        'blueprint_saved': 'Blueprint saved successfully',
        'file_saved_to': 'File saved to',
        'open_file_error': 'Failed to open file',
        'save_file_error': 'Failed to save file',
        'load_project_error': 'Failed to load project',
        'save_project_error': 'Failed to save project',
        
        # Code generation
        'generated_code': 'Generated Script',
        'generated_mod_script': 'Generated MOD Script',
        'code_saved': 'Code saved to',
        'generate_success': 'MOD script generated successfully!',
        'generate_error': 'Failed to generate MOD script',
        
        # Dialogs
        'confirm_reset': 'Confirm Reset',
        'reset_warning': 'Are you sure you want to reset? All unsaved changes will be lost.',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Information',
        
        # Platform
        'platform': 'Platform',
        'module_type': 'Module Type',
        
        # Nodes
        'nodes': 'Nodes',
        'core_nodes': 'Core Nodes',
        'logic_nodes': 'Logic Nodes',
        'variable_nodes': 'Variable Nodes',
        'get_variable': 'Get Variable',
        'set_variable': 'Set Variable',
        
        # Flow editor context menu
        'add_node': 'Add Node',
        
        # Error messages
        'invalid_blueprint_format': 'Invalid blueprint format',
        'no_begin_node': 'No Begin node found',
        'multiple_begin_nodes': 'Multiple Begin nodes found',
    }
}


def tr(key: str) -> str:
    """Get translated text for the given key."""
    settings = SettingsStore.get_instance()
    lang = settings.language
    return TRANSLATIONS.get(lang, TRANSLATIONS['en_US']).get(key, key)


def get_font_family() -> str:
    """Get a font family that supports Chinese characters.
    
    Returns:
        Font family name that supports Chinese, or empty string for system default.
    """
    from PySide6.QtGui import QFontDatabase
    
    # Priority list of fonts with Chinese support
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
        'Arial Unicode MS',
    ]
    
    available_families = QFontDatabase.families()
    for font_name in chinese_fonts:
        if font_name in available_families:
            return font_name
    
    return ''  # Use system default
