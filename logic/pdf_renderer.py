import pymupdf
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QSize, Qt

class PDFRenderer:
    """Handles PDF rendering using PyMuPDF for preview generation"""

    def __init__(self):
        self.current_doc = None
        self.current_path = None

    def load_pdf(self, file_path):
        """Open a PDF file and cache the document"""
        # Close existing document if any
        if self.current_doc:
            self.current_doc.close()

        # Open new document
        try:
            self.current_doc = pymupdf.open(file_path)
            self.current_path = file_path
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            self.current_doc = None
            self.current_path = None
            return False

    def get_page_count(self):
        """Return total pages in current document"""
        return len(self.current_doc) if self.current_doc else 0

    def render_page(self, page_num, zoom=1.0):
        """
        Render a single page to QPixmap
        Args:
            page_num (int): 0-indexed page number
            zoom (float): Scaling factor (1.0 = 100%)
        Returns:
            QPixmap: Rendered page image
        """
        if not self.current_doc or page_num < 0 or page_num >= len(self.current_doc):
            return None

        try:
            # Get page
            page = self.current_doc[page_num]

            # Create matrix for scaling
            mat = pymupdf.Matrix(zoom, zoom)

            # Render to pixmap
            pix = page.get_pixmap(matrix=mat)

            # Convert to QImage - must copy samples data as memoryview doesn't persist
            img_data = bytes(pix.samples)
            qimage = QImage(img_data, pix.width, pix.height,
                           pix.stride, QImage.Format.Format_RGB888)

            # Convert to QPixmap (this copies the data, so img_data can be freed)
            qpixmap = QPixmap.fromImage(qimage)

            return qpixmap
        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return None

    def render_thumbnail(self, page_num, max_width=200):
        """
        Render page as thumbnail with fixed max width
        Args:
            page_num (int): 0-indexed page number
            max_width (int): Maximum width in pixels
        Returns:
            QPixmap: Rendered thumbnail image
        """
        if not self.current_doc or page_num < 0 or page_num >= len(self.current_doc):
            return None

        try:
            # Get page
            page = self.current_doc[page_num]

            # Calculate zoom to fit max_width
            zoom = max_width / page.rect.width

            # Render with calculated zoom
            return self.render_page(page_num, zoom)
        except Exception as e:
            print(f"Error rendering thumbnail {page_num}: {e}")
            return None

    def close(self):
        """Close current document and free resources"""
        if self.current_doc:
            self.current_doc.close()
            self.current_doc = None
            self.current_path = None
