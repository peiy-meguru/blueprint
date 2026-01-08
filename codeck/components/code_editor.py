"""Code Editor - Display generated HOI4 MOD script code."""

from PySide6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont, QColor, QPalette, QSyntaxHighlighter, QTextCharFormat, QTextDocument
from PySide6.QtCore import Qt, QRegularExpression

from ..store.node import NodeStore
from ..store.connection import ConnectionStore
from ..store.variable import VariableStore
from ..store.settings import SettingsStore, tr
from ..code.compiler import CodeCompiler


class HOI4ScriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for HOI4 MOD script code."""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        
        self.highlighting_rules = []
        
        # Keywords (HOI4 script commands)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor('#569cd6'))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'add_namespace', 'country_event', 'news_event', 'state_event',
            'id', 'title', 'desc', 'picture', 'fire_only_once', 'is_triggered_only',
            'trigger', 'mean_time_to_happen', 'immediate', 'option', 'hidden_effect',
            'effect', 'ai_chance', 'factor', 'modifier', 'days', 'months', 'years',
            'random', 'random_list', 'if', 'else', 'else_if', 'limit', 'NOT', 'OR', 'AND',
            'set_variable', 'add_to_variable', 'subtract_from_variable', 'multiply_variable',
            'divide_variable', 'check_variable', 'clamp_variable', 'round_variable',
            'set_country_flag', 'has_country_flag', 'clr_country_flag',
            'set_global_flag', 'has_global_flag', 'clr_global_flag',
            'add_political_power', 'add_stability', 'add_war_support',
            'add_manpower', 'add_equipment_to_stockpile', 'add_resource',
            'create_unit', 'delete_unit', 'transfer_state', 'annex_country',
            'declare_war_on', 'white_peace', 'add_opinion_modifier',
            'country_lock_all_division_template', 'load_oob',
            'set_politics', 'set_popularities', 'add_ideas', 'remove_ideas',
            'add_tech_bonus', 'set_technology', 'add_research_slot',
            'create_faction', 'add_to_faction', 'leave_faction',
            'give_guarantee', 'give_military_access', 'recall_attache',
            'focus_tree', 'national_focus', 'completion_reward', 'prerequisite',
            'mutually_exclusive', 'available', 'bypass', 'cancel', 'historical_ai',
            'ai_will_do', 'select_effect', 'complete_tooltip',
            'decision', 'decision_category', 'allowed', 'visible', 'cost',
            'days_remove', 'remove_effect', 'complete_effect', 'timeout_effect',
            'idea', 'law', 'equipment_bonus', 'research_bonus',
            'name', 'always', 'yes', 'no', 'tag', 'var', 'value', 'ROOT', 'FROM', 'PREV',
            'every_country', 'random_country', 'every_state', 'random_state',
            'every_owned_state', 'capital_scope', 'owner'
        ]
        for word in keywords:
            pattern = QRegularExpression(f'\\b{word}\\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor('#b5cea8'))
        self.highlighting_rules.append(
            (QRegularExpression(r'\b-?\d+\.?\d*\b'), number_format)
        )
        
        # Strings (quoted text)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor('#ce9178'))
        self.highlighting_rules.append(
            (QRegularExpression(r'"[^"]*"'), string_format)
        )
        
        # Comments (# style)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor('#6a9955'))
        self.highlighting_rules.append(
            (QRegularExpression(r'#[^\n]*'), comment_format)
        )
        
        # Localization keys (e.g., country_event.1.t)
        loc_format = QTextCharFormat()
        loc_format.setForeground(QColor('#dcdcaa'))
        self.highlighting_rules.append(
            (QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z0-9_.]+\b'), loc_format)
        )
        
        # Tags and scopes (e.g., GER, ENG, SOV)
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor('#4ec9b0'))
        self.highlighting_rules.append(
            (QRegularExpression(r'\b[A-Z]{3}\b'), tag_format)
        )
    
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text."""
        for pattern, format_style in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_style)


class CodeEditor(QWidget):
    """Code editor widget for displaying generated HOI4 MOD script code."""
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title bar
        self.title_label = QLabel(tr('generated_mod_script'))
        self.title_label.setStyleSheet('background-color: #333; color: white; padding: 5px;')
        layout.addWidget(self.title_label)
        
        # Code display
        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setFont(QFont('Consolas', 11))
        
        # Dark theme
        palette = self.editor.palette()
        palette.setColor(QPalette.Base, QColor('#1e1e1e'))
        palette.setColor(QPalette.Text, QColor('#d4d4d4'))
        self.editor.setPalette(palette)
        
        # Syntax highlighter
        self.highlighter = HOI4ScriptHighlighter(self.editor.document())
        
        layout.addWidget(self.editor)
        
        # Connect to store signals
        self._connect_stores()
        
        # Initial code generation
        self._update_code()
    
    def _connect_stores(self):
        """Connect to store signals for auto-update."""
        node_store = NodeStore.get_instance()
        connection_store = ConnectionStore.get_instance()
        variable_store = VariableStore.get_instance()
        settings_store = SettingsStore.get_instance()
        
        node_store.nodes_changed.connect(self._update_code)
        node_store.node_data_changed.connect(self._update_code)
        connection_store.connections_changed.connect(self._update_code)
        variable_store.variable_changed.connect(self._update_code)
        settings_store.language_changed.connect(self._update_labels)
        settings_store.theme_changed.connect(self._apply_theme)
    
    def _update_labels(self):
        """Update labels when language changes."""
        self.title_label.setText(tr('generated_mod_script'))
    
    def _apply_theme(self):
        """Apply theme to the code editor."""
        settings = SettingsStore.get_instance()
        
        if settings.theme == 'dark':
            self.title_label.setStyleSheet('background-color: #333; color: white; padding: 5px;')
            palette = self.editor.palette()
            palette.setColor(QPalette.Base, QColor('#1e1e1e'))
            palette.setColor(QPalette.Text, QColor('#d4d4d4'))
            self.editor.setPalette(palette)
        else:
            self.title_label.setStyleSheet('background-color: #e0e0e0; color: #333; padding: 5px;')
            palette = self.editor.palette()
            palette.setColor(QPalette.Base, QColor('#ffffff'))
            palette.setColor(QPalette.Text, QColor('#333333'))
            self.editor.setPalette(palette)
    
    def _update_code(self):
        """Update the displayed code."""
        try:
            compiler = CodeCompiler()
            code = compiler.generate()
            self.editor.setPlainText(code)
        except Exception as e:
            self.editor.setPlainText(f'// Error generating code:\n// {e}')
    
    def set_code(self, code: str):
        """Set the displayed code manually."""
        self.editor.setPlainText(code)
