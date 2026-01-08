"""Settings store for application preferences."""

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Literal, Optional
from PySide6.QtCore import QObject, Signal


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
            
            self._settings.language = data.get('language', 'zh_CN')
            self._settings.theme = data.get('theme', 'dark')
            self._settings.last_project_path = data.get('last_project_path', '')
            
            # Load recent projects
            recent = data.get('recent_projects', [])
            self._settings.recent_projects = [
                RecentProject(
                    name=p.get('name', ''),
                    path=p.get('path', ''),
                    image_path=p.get('image_path'),
                    description=p.get('description', ''),
                    last_opened=p.get('last_opened', '')
                )
                for p in recent
            ]
        except (json.JSONDecodeError, IOError) as e:
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
        'app_title': 'Codeck - HOI4 MOD 可视化编程',
        'new_project': '新建项目',
        'open_project': '打开项目',
        'recent_projects': '最近项目',
        'settings': '设置',
        'language': '语言',
        'theme': '界面风格',
        'dark_theme': '深色主题',
        'light_theme': '浅色主题',
        'file': '文件',
        'edit': '编辑',
        'help': '帮助',
        'save': '保存',
        'save_as': '另存为',
        'open': '打开',
        'reset': '重置',
        'run': '运行',
        'pack': '打包',
        'variables': '变量',
        'create_variable': '创建变量',
        'delete': '删除',
        'name': '名称',
        'type': '类型',
        'default': '默认值',
        'mod_name': 'MOD 名称',
        'mod_description': 'MOD 描述',
        'mod_image': 'MOD 图片',
        'generated_code': '生成的脚本',
        'no_recent_projects': '暂无最近项目',
        'project_info': '项目信息',
        'build': '构建',
        'platform': '平台',
        'module_type': '模块类型',
        'current_file': '当前文件',
        'local_storage': '本地存储',
        'confirm_reset': '确认重置',
        'reset_warning': '确定要重置吗？所有未保存的更改将会丢失。',
        'error': '错误',
        'success': '成功',
        'code_saved': '代码已保存到',
        'blueprint_saved': '蓝图保存成功',
        'chinese': '中文',
        'english': 'English',
        'mod_name_required': 'MOD名称是必填项',
        'project_path_required': '项目路径是必填项',
        'project_not_found': '项目文件未找到',
    },
    'en_US': {
        'app_title': 'Codeck - HOI4 MOD Visual Programming',
        'new_project': 'New Project',
        'open_project': 'Open Project',
        'recent_projects': 'Recent Projects',
        'settings': 'Settings',
        'language': 'Language',
        'theme': 'Interface Style',
        'dark_theme': 'Dark Theme',
        'light_theme': 'Light Theme',
        'file': 'File',
        'edit': 'Edit',
        'help': 'Help',
        'save': 'Save',
        'save_as': 'Save As',
        'open': 'Open',
        'reset': 'Reset',
        'run': 'Run',
        'pack': 'Pack',
        'variables': 'Variables',
        'create_variable': 'Create Variable',
        'delete': 'Delete',
        'name': 'Name',
        'type': 'Type',
        'default': 'Default',
        'mod_name': 'MOD Name',
        'mod_description': 'MOD Description',
        'mod_image': 'MOD Image',
        'generated_code': 'Generated Script',
        'no_recent_projects': 'No Recent Projects',
        'project_info': 'Project Info',
        'build': 'Build',
        'platform': 'Platform',
        'module_type': 'Module Type',
        'current_file': 'Current File',
        'local_storage': 'Local Storage',
        'confirm_reset': 'Confirm Reset',
        'reset_warning': 'Are you sure you want to reset? All unsaved changes will be lost.',
        'error': 'Error',
        'success': 'Success',
        'code_saved': 'Code saved to',
        'blueprint_saved': 'Blueprint saved successfully',
        'chinese': '中文',
        'english': 'English',
        'mod_name_required': 'MOD name is required',
        'project_path_required': 'Project path is required',
        'project_not_found': 'Project file not found',
    }
}


def tr(key: str) -> str:
    """Get translated text for the given key."""
    settings = SettingsStore.get_instance()
    lang = settings.language
    return TRANSLATIONS.get(lang, TRANSLATIONS['en_US']).get(key, key)
