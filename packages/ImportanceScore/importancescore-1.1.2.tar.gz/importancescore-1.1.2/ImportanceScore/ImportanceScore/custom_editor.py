# custom_editor.py
from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.token import Token
from pygments.styles import get_style_by_name

class PygmentsHighlighter(QSyntaxHighlighter):
    """A QSyntaxHighlighter that uses the Pygments library for styling."""

    def __init__(self, parent):
        super().__init__(parent)

        # The lexer is responsible for breaking text into tokens
        self.lexer = YamlLexer()

        # 1. Get a Pygments style.
        # 2. Create a dictionary mapping token types to QTextCharFormat objects.
        self.styles = {}
        style = get_style_by_name('dracula')
        for token, s in style:
            q_format = QTextCharFormat()
            if s['color']:
                q_format.setForeground(QColor(f"#{s['color']}"))

            self.styles[token] = q_format

    def highlightBlock(self, text: str):
        """
        This method is called by Qt for each block of text to be highlighted.
        """
        # Get the tokens from Pygments
        tokens = self.lexer.get_tokens_unprocessed(text)

        start_index = 0
        for index, token_type, value in tokens:
            # Find the correct style for this token
            # We traverse up the token hierarchy (e.g., from Number.Integer to Number to Token)
            # until we find a style defined.
            current_format = None
            temp_token_type = token_type
            while current_format is None:
                current_format = self.styles.get(temp_token_type)
                if temp_token_type is Token:
                    break
                temp_token_type = temp_token_type.parent

            # Apply the format if one was found
            if current_format:
                self.setFormat(index, len(value), current_format)