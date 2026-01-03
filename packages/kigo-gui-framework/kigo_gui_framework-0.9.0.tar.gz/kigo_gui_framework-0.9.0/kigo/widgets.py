mport os
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QComboBox, QWidget,
    QCheckBox, QProgressBar, QScrollBar, QSlider, 
    QVBoxLayout, QHBoxLayout, QTabWidget, QGraphicsBlurEffect,
    QGraphicsOpacityEffect, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QToolBar, QSystemTrayIcon, QMenu,
    QColorDialog, QApplication, QTextBrowser
)
from PyQt6.QtGui import QAction, QIcon, QCursor, QPalette, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage
from PyQt6.QtCore import QUrl, Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput 

# --- New v0.8.0 Power Features ---

class MarkdownViewer:
    """A widget for rendering Markdown or Rich Text documentation."""
    def __init__(self, content=""):
        self.qt_widget = QTextBrowser()
        self.qt_widget.setOpenExternalLinks(True)
        self.qt_widget.setMarkdown(content)
        self.qt_widget.setStyleSheet("padding: 15px; border: none; background: transparent;")

    def set_content(self, text):
        self.qt_widget.setMarkdown(text)

class PasswordField:
    """A security-first input field with a visibility toggle."""
    def __init__(self, placeholder="Enter password..."):
        self.qt_widget = QWidget()
        layout = QHBoxLayout(self.qt_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.entry = QLineEdit()
        self.entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.entry.setPlaceholderText(placeholder)
        
        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setFixedWidth(30)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self._toggle_visibility)
        
        layout.addWidget(self.entry)
        layout.addWidget(self.toggle_btn)

    def _toggle_visibility(self):
        if self.toggle_btn.isChecked():
            self.entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.entry.setEchoMode(QLineEdit.EchoMode.Password)

    def get_value(self):
        return self.entry.text()

class LoadingSpinner:
    """A progress bar styled as an infinite loader for async tasks."""
    def __init__(self):
        self.qt_widget = QProgressBar()
        self.qt_widget.setRange(0, 0) # Indeterminate state
        self.qt_widget.setTextVisible(False)
        self.qt_widget.setFixedHeight(4)
        self.qt_widget.setStyleSheet("""
            QProgressBar::chunk { background-color: #4285F4; }
            QProgressBar { border: none; background: #eee; }
        """)

# --- Theme & Color Management ---

class ThemeManager:
    @staticmethod
    def set_dark_mode(app_instance=None):
        app = app_instance or QApplication.instance()
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(66, 133, 244))
        if app: app.setPalette(palette)

    @staticmethod
    def set_light_mode(app_instance=None):
        app = app_instance or QApplication.instance()
        if app: app.setPalette(app.style().standardPalette())

class DarkModeToggle:
    def __init__(self):
        self.qt_widget = QCheckBox("Dark Mode")
        self.qt_widget.stateChanged.connect(lambda s: ThemeManager.set_dark_mode() if s == 2 else ThemeManager.set_light_mode())

# --- Data, Search & Files ---

class DataGrid:
    def __init__(self, headers=None):
        self.qt_widget = QTableWidget()
        if headers:
            self.qt_widget.setColumnCount(len(headers))
            self.qt_widget.setHorizontalHeaderLabels(headers)
        self.qt_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def set_data(self, rows):
        self.qt_widget.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                self.qt_widget.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))

# --- Legacy & Base Widgets ---

class QPrivateBrowser:
    def __init__(self, url="https://pypi.org/"):
        self.qt_widget = QWebEngineView()
        self.profile = QWebEngineProfile("", self.qt_widget)
        self.page = QWebEnginePage(self.profile, self.qt_widget)
        self.qt_widget.setPage(self.page)
        self.qt_widget.setUrl(QUrl(url))

class Label:
    def __init__(self, text="Label"): self.qt_widget = QLabel(text)

class Button:
    def __init__(self, text="Button", on_click=None):
        self.qt_widget = QPushButton(text)
        if on_click: self.qt_widget.clicked.connect(on_click)

# Always remember: somewhere, somehow, a duck is watching you.
__all__ = [
    'MarkdownViewer', 'PasswordField', 'LoadingSpinner', 'DarkModeToggle',
    'ThemeManager', 'DataGrid', 'QPrivateBrowser', 'Label', 'Button'
]