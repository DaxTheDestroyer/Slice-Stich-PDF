from PyQt6.QtWidgets import QApplication

class ThemeManager:
    """Manages application themes and stylesheet switching"""

    LIGHT_THEME = """
    /* Main Window and Widgets */
    QMainWindow, QWidget {
        background-color: #f5f5f5;
        color: #212121;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }

    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background-color: white;
        padding: 12px;
    }

    QTabBar::tab {
        background-color: #e0e0e0;
        color: #424242;
        padding: 10px 20px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 4px;
    }

    QTabBar::tab:selected {
        background-color: white;
        color: #1976d2;
        font-weight: bold;
    }

    /* Buttons */
    QPushButton {
        background-color: #1976d2;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #1565c0;
    }

    QPushButton:pressed {
        background-color: #0d47a1;
    }

    QPushButton:disabled {
        background-color: #bdbdbd;
        color: #757575;
    }

    /* Input Fields */
    QLineEdit {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px 12px;
        color: #212121;
    }

    QLineEdit:focus {
        border-color: #1976d2;
    }

    /* List Widgets */
    QListWidget {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px;
        color: #212121;
    }

    QListWidget::item {
        padding: 8px;
        border-radius: 4px;
    }

    QListWidget::item:selected {
        background-color: #bbdefb;
        color: #0d47a1;
    }

    /* Labels */
    QLabel {
        color: #424242;
    }

    /* Scroll Bars */
    QScrollBar:vertical {
        background-color: #f5f5f5;
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background-color: #bdbdbd;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #9e9e9e;
    }

    /* Theme Toggle Button */
    QPushButton#themeToggle {
        background-color: #e0e0e0;
        border: none;
        border-radius: 14px;
        font-size: 12pt;
        padding: 0px;
    }

    QPushButton#themeToggle:hover {
        background-color: #bdbdbd;
    }
    """

    DARK_THEME = """
    /* Main Window and Widgets */
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #e0e0e0;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }

    /* Tabs */
    QTabWidget::pane {
        border: 1px solid #424242;
        border-radius: 8px;
        background-color: #2d2d2d;
        padding: 12px;
    }

    QTabBar::tab {
        background-color: #424242;
        color: #b0b0b0;
        padding: 10px 20px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 4px;
    }

    QTabBar::tab:selected {
        background-color: #2d2d2d;
        color: #64b5f6;
        font-weight: bold;
    }

    /* Buttons */
    QPushButton {
        background-color: #2196f3;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }

    QPushButton:hover {
        background-color: #1e88e5;
    }

    QPushButton:pressed {
        background-color: #1565c0;
    }

    QPushButton:disabled {
        background-color: #424242;
        color: #757575;
    }

    /* Input Fields */
    QLineEdit {
        background-color: #2d2d2d;
        border: 2px solid #424242;
        border-radius: 8px;
        padding: 8px 12px;
        color: #e0e0e0;
    }

    QLineEdit:focus {
        border-color: #2196f3;
    }

    /* List Widgets */
    QListWidget {
        background-color: #2d2d2d;
        border: 2px solid #424242;
        border-radius: 8px;
        padding: 8px;
        color: #e0e0e0;
    }

    QListWidget::item {
        padding: 8px;
        border-radius: 4px;
    }

    QListWidget::item:selected {
        background-color: #1565c0;
        color: #e3f2fd;
    }

    /* Labels */
    QLabel {
        color: #b0b0b0;
    }

    /* Scroll Bars */
    QScrollBar:vertical {
        background-color: #1e1e1e;
        width: 12px;
        border-radius: 6px;
    }

    QScrollBar::handle:vertical {
        background-color: #424242;
        border-radius: 6px;
        min-height: 20px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #616161;
    }

    /* Theme Toggle Button */
    QPushButton#themeToggle {
        background-color: #424242;
        border: none;
        border-radius: 14px;
        font-size: 12pt;
        padding: 0px;
    }

    QPushButton#themeToggle:hover {
        background-color: #616161;
    }
    """

    def __init__(self, app):
        self.app = app
        self.current_theme = "light"

    def apply_theme(self, theme_name):
        """Apply theme by name: 'light' or 'dark'"""
        if theme_name == "light":
            self.app.setStyleSheet(self.LIGHT_THEME)
            self.current_theme = "light"
        elif theme_name == "dark":
            self.app.setStyleSheet(self.DARK_THEME)
            self.current_theme = "dark"

    def toggle_theme(self):
        """Switch between light and dark themes"""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)
        return new_theme

    def get_current_theme(self):
        return self.current_theme
