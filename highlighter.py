from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlight_rules = []

        # Форматирование для разных элементов кода
        def add_rule(pattern, color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold: fmt.setFontWeight(QFont.Weight.Bold)
            self.highlight_rules.append((QRegularExpression(pattern), fmt))

        # Ключевые слова Python (Синий)
        add_rule(r'\b(False|None|True|and|as|assert|async|await|break|class|'
                 r'continue|def|del|elif|else|except|finally|for|from|global|'
                 r'if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|'
                 r'try|while|with|yield)\b', "#569CD6", bold=True)
        
        add_rule(r'\b[A-Za-z0-9_]+(?=\()', "#DCDCAA") # Функции (Желтый)
        add_rule(r'".*"|\'.*\'', "#CE9178")           # Строки (Оранжевый)
        add_rule(r'#.*', "#6A9955")                    # Комментарии (Зеленый)
        add_rule(r'\b\d+\b', "#B5CEA8")                # Числа (Салатовый)

    def highlightBlock(self, text):
        for pattern, fmt in self.highlight_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)
