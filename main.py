import sys
import os

# Ensure the project root is in python path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication

# Import version info early (lightweight)
from version import __version__, __app_name__

def main():
    """
    Application Entry Point.

    1. Create the QApplication (required for any PyQt app).
    2. Show splash screen immediately.
    3. Load heavy modules while splash is visible.
    4. Create the MainWindow.
    5. Hide splash and show the window.
    6. Start the event loop (app.exec).
    """
    app = QApplication(sys.argv)

    # Set application-wide style
    app.setStyle("Fusion")

    # Show splash screen immediately (before heavy imports)
    from gui.splash import create_splash
    splash = create_splash(__app_name__, __version__)

    # Now do heavy imports while splash is visible
    splash.showStatusMessage("Loading theme system...")
    from gui.themes import ThemeManager
    theme_manager = ThemeManager(app)
    theme_manager.apply_theme("dark")

    splash.showStatusMessage("Loading PDF engine...")
    # Pre-import heavy modules to front-load the delay
    import pypdf
    import pymupdf

    splash.showStatusMessage("Initializing interface...")
    from gui.window import MainWindow
    window = MainWindow(theme_manager)

    splash.showStatusMessage("Ready!")

    # Show window and close splash with smooth transition
    window.show()
    splash.finish_with_delay(window, delay_ms=300)

    # sys.exit ensures a clean exit code is returned to the OS
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
