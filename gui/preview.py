from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QGridLayout, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class SinglePageView(QWidget):
    """Displays one PDF page with navigation controls"""

    def __init__(self, renderer):
        super().__init__()
        self.renderer = renderer
        self.current_page = 0

        # Create layout
        layout = QVBoxLayout(self)

        # Scroll area for page image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label to display page image
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setText("No preview available")
        scroll_area.setWidget(self.page_label)

        layout.addWidget(scroll_area)

        # Navigation bar
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)

        self.page_info_label = QLabel("Page 0/0")
        self.page_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_info_label)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

    def set_page(self, page_num):
        """Load and display specific page"""
        if not self.renderer.current_doc:
            return

        page_count = self.renderer.get_page_count()
        if page_num < 0 or page_num >= page_count:
            return

        self.current_page = page_num

        # Render page at 1.5x zoom for better readability
        pixmap = self.renderer.render_page(page_num, zoom=1.5)

        if pixmap:
            # Scale to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                800, 1000,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.page_label.setPixmap(scaled_pixmap)
        else:
            self.page_label.setText("Error rendering page")

        # Update page counter
        self.page_info_label.setText(f"Page {page_num + 1}/{page_count}")

        # Update button states
        self.prev_btn.setEnabled(page_num > 0)
        self.next_btn.setEnabled(page_num < page_count - 1)

    def next_page(self):
        """Go to next page"""
        self.set_page(self.current_page + 1)

    def previous_page(self):
        """Go to previous page"""
        self.set_page(self.current_page - 1)

    def clear(self):
        """Clear the preview"""
        self.page_label.clear()
        self.page_label.setText("No preview available")
        self.page_info_label.setText("Page 0/0")
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.current_page = 0


class ThumbnailGridView(QScrollArea):
    """Displays all pages as thumbnail grid"""

    def __init__(self, renderer):
        super().__init__()
        self.renderer = renderer

        # Make scrollable
        self.setWidgetResizable(True)

        # Container widget
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(10)

        self.setWidget(self.container)

    def load_thumbnails(self):
        """Generate and display all page thumbnails"""
        # Clear existing thumbnails
        self.clear()

        if not self.renderer.current_doc:
            return

        page_count = self.renderer.get_page_count()

        # Generate thumbnails in a 4-column grid
        columns = 4

        for page_num in range(page_count):
            # Create container for thumbnail and label
            thumb_widget = QWidget()
            thumb_layout = QVBoxLayout(thumb_widget)
            thumb_layout.setContentsMargins(0, 0, 0, 0)

            # Render thumbnail
            pixmap = self.renderer.render_thumbnail(page_num, max_width=200)

            if pixmap:
                # Create label for thumbnail image
                img_label = QLabel()
                img_label.setPixmap(pixmap)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumb_layout.addWidget(img_label)

                # Create label for page number
                page_label = QLabel(f"Page {page_num + 1}")
                page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumb_layout.addWidget(page_label)

                # Add to grid
                row = page_num // columns
                col = page_num % columns
                self.grid_layout.addWidget(thumb_widget, row, col)

    def clear(self):
        """Remove all thumbnails from grid"""
        # Remove all widgets from layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class PreviewWidget(QWidget):
    """Main preview widget with view toggle"""

    def __init__(self, renderer):
        super().__init__()
        self.renderer = renderer
        self.thumbnails_loaded = False

        # Create layout
        layout = QVBoxLayout(self)

        # Header with toggle button
        header_layout = QHBoxLayout()

        header_label = QLabel("Preview")
        header_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        self.toggle_btn = QPushButton("Show Thumbnail Grid")
        self.toggle_btn.clicked.connect(self.switch_view)
        header_layout.addWidget(self.toggle_btn)

        layout.addLayout(header_layout)

        # Stacked widget to switch between views
        self.stacked_widget = QStackedWidget()

        # Create both views
        self.single_view = SinglePageView(renderer)
        self.thumbnail_view = ThumbnailGridView(renderer)

        self.stacked_widget.addWidget(self.single_view)
        self.stacked_widget.addWidget(self.thumbnail_view)

        layout.addWidget(self.stacked_widget)

        # Start with single page view
        self.stacked_widget.setCurrentIndex(0)

    def load_pdf(self, file_path):
        """Load new PDF for preview"""
        # Load PDF in renderer
        success = self.renderer.load_pdf(file_path)

        if success:
            # Load single page view (page 0)
            self.single_view.set_page(0)

            # Reset thumbnails loaded flag
            self.thumbnails_loaded = False

            # If currently in grid view, load thumbnails
            if self.stacked_widget.currentIndex() == 1:
                self.thumbnail_view.load_thumbnails()
                self.thumbnails_loaded = True
        else:
            self.clear()

    def switch_view(self):
        """Toggle between single and grid view"""
        current_index = self.stacked_widget.currentIndex()

        if current_index == 0:
            # Switch to thumbnail grid
            self.stacked_widget.setCurrentIndex(1)
            self.toggle_btn.setText("Show Single Page")

            # Load thumbnails if not already loaded
            if not self.thumbnails_loaded and self.renderer.current_doc:
                self.thumbnail_view.load_thumbnails()
                self.thumbnails_loaded = True
        else:
            # Switch to single page
            self.stacked_widget.setCurrentIndex(0)
            self.toggle_btn.setText("Show Thumbnail Grid")

    def clear(self):
        """Clear preview (when no file selected)"""
        self.single_view.clear()
        self.thumbnail_view.clear()
        self.thumbnails_loaded = False
        self.stacked_widget.setCurrentIndex(0)
        self.toggle_btn.setText("Show Thumbnail Grid")
