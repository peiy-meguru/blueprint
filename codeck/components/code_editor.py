"""Code Editor - Display generated code."""

from PySide6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont, QColor, QPalette, QSyntaxHighlighter, QTextCharFormat, QTextDocument
from PySide6.QtCore import Qt, QRegularExpression

from ..store.node import NodeStore
from ..store.connection import ConnectionStore
from ..store.variable import VariableStore
from ..code.compiler import CodeCompiler


class JavaScriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JavaScript code."""
    
    def __init__(self, document: QTextDocument):
        super().__init__(document)
        
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor('#569cd6'))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'const', 'let', 'var', 'function', 'return', 'if', 'else',
            'for', 'while', 'do', 'switch', 'case', 'break', 'continue',
            'try', 'catch', 'finally', 'throw', 'new', 'delete', 'typeof',
            'instanceof', 'in', 'of', 'class', 'extends', 'import', 'export',
            'from', 'as', 'default', 'async', 'await', 'yield', 'true', 'false',
            'null', 'undefined', 'this'
        ]
        for word in keywords:
            pattern = QRegularExpression(f'\\b{word}\\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor('#b5cea8'))
        self.highlighting_rules.append(
            (QRegularExpression(r'\b\d+\.?\d*\b'), number_format)
        )
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor('#ce9178'))
        self.highlighting_rules.append(
            (QRegularExpression(r'"[^"]*"'), string_format)
        )
        self.highlighting_rules.append(
            (QRegularExpression(r"'[^']*'"), string_format)
        )
        self.highlighting_rules.append(
            (QRegularExpression(r'`[^`]*`'), string_format)
        )
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor('#6a9955'))
        self.highlighting_rules.append(
            (QRegularExpression(r'//[^\n]*'), comment_format)
        )
        
        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor('#dcdcaa'))
        self.highlighting_rules.append(
            (QRegularExpression(r'\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()'), function_format)
        )
    
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text."""
        for pattern, format_style in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format_style)


class CodeEditor(QWidget):
    """Code editor widget for displaying generated JavaScript code."""
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title bar
        title = QLabel('Generated Code')
        title.setStyleSheet('background-color: #333; color: white; padding: 5px;')
        layout.addWidget(title)
        
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
        self.highlighter = JavaScriptHighlighter(self.editor.document())
        
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
        
        node_store.nodes_changed.connect(self._update_code)
        node_store.node_data_changed.connect(self._update_code)
        connection_store.connections_changed.connect(self._update_code)
        variable_store.variable_changed.connect(self._update_code)
    
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
