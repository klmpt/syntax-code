from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit
from PyQt6.QtGui import QColor, QFont, QPainter, QTextCursor, QTextCharFormat
from PyQt6.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QSize(self.codeEditor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class SyntaxEditor(QPlainTextEdit):
    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = file_path
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        # Стиль редактора
        self.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; border: none;")
        
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)
        
        self.brackets_map = {'(': ')', '[': ']', '{': '}', '"': '"', "'": "'"}

    def line_number_area_width(self):
        digits, max_b = 1, max(1, self.blockCount())
        while max_b >= 10:
            max_b /= 10
            digits += 1
        return 20 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy: self.lineNumberArea.scroll(0, dy)
        else: self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()): self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#1E1E1E"))
        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor("#C6C6C6" if block == self.textCursor().block() else "#858585"))
                painter.drawText(0, top, self.lineNumberArea.width() - 5, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, str(block_num + 1))
            block, block_num = block.next(), block_num + 1
            top, bottom = bottom, top + round(self.blockBoundingRect(block).height())

    def highlight_current_line(self):
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("#2A2A2A"))
        selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        txt = event.text()

        if txt in self.brackets_map:
            self.insertPlainText(txt + self.brackets_map[txt])
            cursor.movePosition(QTextCursor.MoveOperation.Left)
            self.setTextCursor(cursor)
            return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            line = cursor.block().text()
            indent = line[:len(line) - len(line.lstrip())]
            super().keyPressEvent(event)
            self.insertPlainText(indent + ("    " if line.strip().endswith(':') else ""))
            return

        super().keyPressEvent(event)
