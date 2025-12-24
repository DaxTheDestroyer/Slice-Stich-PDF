"""
Splash screen module for application startup.
Displays app name, version, and loading status while heavy imports occur.
"""

from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QPen

class SplashScreen(QSplashScreen):
    """
    Custom dark-themed splash screen with app branding.
    Shows application name, version, and loading progress.
    """

    def __init__(self, app_name: str, version: str):
        # Create the splash pixmap
        pixmap = self._create_splash_pixmap(app_name, version)
        super().__init__(pixmap)

        self.setWindowFlags(
            Qt.WindowType.SplashScreen |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self._status_message = "Loading..."
        self._app_name = app_name
        self._version = version

    def _create_splash_pixmap(self, app_name: str, version: str) -> QPixmap:
        """Generate the splash screen graphics"""
        width, height = 500, 300
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background with gradient
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor("#1e1e1e"))
        gradient.setColorAt(1, QColor("#2d2d2d"))

        # Rounded rectangle background
        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#424242"), 2))
        painter.drawRoundedRect(1, 1, width - 2, height - 2, 16, 16)

        # Accent line at top
        accent_gradient = QLinearGradient(0, 0, width, 0)
        accent_gradient.setColorAt(0, QColor("#2196F3"))
        accent_gradient.setColorAt(0.5, QColor("#64B5F6"))
        accent_gradient.setColorAt(1, QColor("#2196F3"))
        painter.setBrush(accent_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, width, 6, 3, 3)

        # Draw decorative elements (representing slice & stitch)
        self._draw_decorative_elements(painter, width, height)

        # Application name
        painter.setPen(QColor("#FFFFFF"))
        title_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(0, 70, width, 50, Qt.AlignmentFlag.AlignCenter, app_name)

        # Version
        painter.setPen(QColor("#64B5F6"))
        version_font = QFont("Segoe UI", 14, QFont.Weight.Normal)
        painter.setFont(version_font)
        painter.drawText(0, 115, width, 30, Qt.AlignmentFlag.AlignCenter, f"Version {version}")

        # Tagline
        painter.setPen(QColor("#9E9E9E"))
        tagline_font = QFont("Segoe UI", 10, QFont.Weight.Normal)
        painter.setFont(tagline_font)
        painter.drawText(0, 145, width, 25, Qt.AlignmentFlag.AlignCenter, "Split and merge PDF files with ease")

        # Loading area placeholder (status will be drawn dynamically)
        painter.setPen(QColor("#757575"))
        loading_font = QFont("Segoe UI", 10)
        painter.setFont(loading_font)
        painter.drawText(0, height - 45, width, 25, Qt.AlignmentFlag.AlignCenter, "Loading...")

        # Copyright/author
        painter.setPen(QColor("#616161"))
        copyright_font = QFont("Segoe UI", 8)
        painter.setFont(copyright_font)
        painter.drawText(0, height - 25, width, 20, Qt.AlignmentFlag.AlignCenter, "AntiGravity Projects")

        painter.end()
        return pixmap

    def _draw_decorative_elements(self, painter: QPainter, width: int, height: int):
        """Draw subtle decorative elements representing slice & stitch"""
        # Left side - scissor/slice hint (abstract lines)
        painter.setPen(QPen(QColor("#424242"), 2))

        # Diagonal slice lines on left
        for i in range(3):
            y_offset = 180 + i * 15
            painter.drawLine(30, y_offset, 70, y_offset + 20)

        # Right side - stitch pattern hint
        # Dashed stitch line
        pen = QPen(QColor("#424242"), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        for i in range(3):
            y_offset = 180 + i * 15
            painter.drawLine(width - 70, y_offset, width - 30, y_offset + 20)

        # Center connecting element
        painter.setPen(QPen(QColor("#2196F3"), 2))
        painter.drawLine(width // 2 - 30, 200, width // 2 + 30, 200)
        painter.drawLine(width // 2, 185, width // 2, 215)

    def showStatusMessage(self, message: str):
        """Update the status message displayed on splash"""
        self._status_message = message
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            QColor("#9E9E9E")
        )
        QApplication.processEvents()

    def finish_with_delay(self, window, delay_ms: int = 500):
        """
        Finish splash screen with a small delay for smooth transition.

        Args:
            window: The main window to show after splash
            delay_ms: Delay in milliseconds before closing splash
        """
        def do_finish():
            self.finish(window)

        QTimer.singleShot(delay_ms, do_finish)


def create_splash(app_name: str, version: str) -> SplashScreen:
    """
    Factory function to create and show a splash screen.

    Args:
        app_name: Application name to display
        version: Version string to display

    Returns:
        SplashScreen instance (already shown)
    """
    splash = SplashScreen(app_name, version)
    splash.show()
    QApplication.processEvents()
    return splash
