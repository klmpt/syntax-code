import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                             QPushButton, QTextEdit, QTabWidget, QFileDialog, 
                             QHBoxLayout, QFrame, QLabel, QStatusBar)
from PyQt6.QtCore import QProcess, Qt, QSize
from PyQt6.QtGui import QShortcut, QKeySequence, QFont

from highlighter import SyntaxHighlighter
from editor import SyntaxEditor

# Цвета VS Code
ACCENT_BLUE = "#007acc"
BG_SIDEBAR = "#333333"

class SyntaxCode(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Syntax Code")
        self.resize(1200, 850)
        
        # Стилизация интерфейса
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: #1e1e1e; }}
            #ActivityBar {{ background-color: {BG_SIDEBAR}; border-right: 1px solid #252526; min-width: 50px; }}
            #ActivityBtn {{ background-color: transparent; color: #858585; border: none; font-size: 20px; padding: 15px 0; }}
            #ActivityBtn:hover {{ color: #ffffff; }}
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{ background-color: #2d2d2d; color: #969696; padding: 10px 20px; border-right: 1px solid #1e1e1e; }}
            QTabBar::tab:selected {{ background-color: #1e1e1e; color: #ffffff; border-top: 1px solid {ACCENT_BLUE}; }}
            QTextEdit#Terminal {{ background-color: #1e1e1e; color: #cccccc; font-family: Monospace; border: none; border-top: 1px solid #333; padding: 10px; }}
        """)

        # --- Боковая панель ---
        self.activity_bar = QFrame()
        self.activity_bar.setObjectName("ActivityBar")
        act_layout = QVBoxLayout(self.activity_bar)
        act_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_open = QPushButton("📄")
        self.btn_open.setObjectName("ActivityBtn")
        self.btn_open.clicked.connect(self.open_file)
        
        self.btn_run = QPushButton("▶")
        self.btn_run.setObjectName("ActivityBtn")
        self.btn_run.clicked.connect(self.run_code)
        
        act_layout.addWidget(self.btn_open)
        act_layout.addWidget(self.btn_run)
        act_layout.addStretch()

        # --- Основная область ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.terminal = QTextEdit()
        self.terminal.setObjectName("Terminal")
        self.terminal.setReadOnly(True)
        self.terminal.setFixedHeight(180)

        content_layout.addWidget(self.tabs, stretch=10)
        content_layout.addWidget(self.terminal, stretch=2)

        # Сборка окна
        main_hbox = QHBoxLayout()
        main_hbox.setContentsMargins(0, 0, 0, 0)
        main_hbox.setSpacing(0)
        main_hbox.addWidget(self.activity_bar)
        main_hbox.addWidget(content_widget)

        container = QWidget()
        container.setLayout(main_hbox)
        self.setCentralWidget(container)

        # --- Статус-бар ---
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"background-color: {ACCENT_BLUE}; color: white; font-size: 11px;")
        self.setStatusBar(self.status_bar)
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.status_bar.addPermanentWidget(self.cursor_label)

        # Процесс
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

        self.add_new_tab()

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        QShortcut(QKeySequence("F5"), self, self.run_code)

    def add_new_tab(self, content="", file_path=None):
        editor = SyntaxEditor(file_path)
        editor.highlighter = SyntaxHighlighter(editor.document())
        editor.cursorPositionChanged.connect(self.update_cursor_info)
        
        title = os.path.basename(file_path) if file_path else "Untitled-1"
        index = self.tabs.addTab(editor, title)
        if content: editor.setPlainText(content)
        self.tabs.setCurrentIndex(index)

    def update_cursor_info(self):
        editor = self.tabs.currentWidget()
        if editor:
            cursor = editor.textCursor()
            self.cursor_label.setText(f"Ln {cursor.blockNumber()+1}, Col {cursor.columnNumber()+1}   ")

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.add_new_tab(f.read(), path)

    def close_tab(self, index):
        if self.tabs.count() > 1: self.tabs.removeTab(index)

    def run_code(self):
        editor = self.tabs.currentWidget()
        if not editor: return
        
        # Автосохранение перед запуском
        path = editor.file_path or "temp_run.py"
        with open(path, "w", encoding="utf-8") as f:
            f.write(editor.toPlainText())
        
        self.terminal.clear()
        self.terminal.append(f"<span style='color: #6a9955;'>[Running] {path}</span>")
        self.process.start("python3", [path])

    def handle_stdout(self):
        self.terminal.append(self.process.readAllStandardOutput().data().decode())

    def handle_stderr(self):
        self.terminal.append(f"<span style='color: #f44747;'>{self.process.readAllStandardError().data().decode()}</span>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SyntaxCode()
    window.show()
    sys.exit(app.exec())
