from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                             QLabel, QPushButton, QFileDialog, QHBoxLayout,
                             QListWidget, QMessageBox, QLineEdit, QListWidgetItem,
                             QAbstractItemView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
from logic.pdf_ops import PDFManager
from version import __version__, __app_name__
import os
import tempfile
import sys

class MainWindow(QMainWindow):
    """
    The main application window.
    Inherits from QMainWindow which gives us a native-looking window frame.
    """
    def __init__(self, theme_manager):
        super().__init__()

        self.theme_manager = theme_manager
        self.setWindowTitle(f"{__app_name__} v{__version__}")

        # Set window icon
        self._set_window_icon()
        self.resize(800, 600)

        # Initialize our Logic Controller
        self.manager = PDFManager()
        self.current_split_file = None

        # Initialize PDF Renderer for preview
        from logic.pdf_renderer import PDFRenderer
        self.split_renderer = PDFRenderer()
        self.merge_renderer = PDFRenderer()

        self._merge_preview_temp_path = None
        self._merge_preview_update_timer = QTimer(self)
        self._merge_preview_update_timer.setSingleShot(True)
        self._merge_preview_update_timer.setInterval(250)
        self._merge_preview_update_timer.timeout.connect(self._update_merge_preview_now)

        # Central widget is the container for everything inside the window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts manage positioning. QVBoxLayout stacks items vertically.
        layout = QVBoxLayout(central_widget)

        # QTabWidget lets us have "Split" and "Merge" modes clean and separate
        self.tabs = QTabWidget()

        # Theme toggle button (shown in the tab bar corner)
        self.theme_toggle_btn = QPushButton("☀")
        self.theme_toggle_btn.setFixedSize(28, 28)
        self.theme_toggle_btn.setToolTip("Switch to Light Theme")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        self.theme_toggle_btn.setObjectName("themeToggle")
        # Wrap in a container to add right-side spacing so it doesn't sit flush
        # against the window edge / tab bar border.
        self._theme_toggle_container = QWidget()
        theme_toggle_layout = QHBoxLayout(self._theme_toggle_container)
        theme_toggle_layout.setContentsMargins(0, 0, 8, 0)
        theme_toggle_layout.setSpacing(0)
        theme_toggle_layout.addWidget(self.theme_toggle_btn)

        self.tabs.setCornerWidget(self._theme_toggle_container, Qt.Corner.TopRightCorner)
        layout.addWidget(self.tabs)
        
        # Create the two tabs
        self.create_split_tab()
        self.create_merge_tab()

        self.setAcceptDrops(True)

    def _set_window_icon(self):
        """Set the application window icon"""
        # Try multiple paths to find the icon (works for both dev and packaged)
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.ico'),
            os.path.join(sys._MEIPASS, 'assets', 'icon.ico') if hasattr(sys, '_MEIPASS') else None,
            os.path.join(os.path.dirname(sys.executable), 'assets', 'icon.ico'),
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break

    def create_split_tab(self):
        """Setup the UI for the Split tab"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)

        # Left panel: controls (max 400px width)
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_widget.setMaximumWidth(400)

        # Instructions
        label = QLabel("Select a PDF to split:")
        controls_layout.addWidget(label)

        # File selection
        file_layout = QHBoxLayout()
        self.split_file_label = QLabel("No file selected")
        select_btn = QPushButton("Select PDF")
        select_btn.clicked.connect(self.select_split_file)
        file_layout.addWidget(select_btn)
        file_layout.addWidget(self.split_file_label)
        controls_layout.addLayout(file_layout)

        # Range Input
        range_label = QLabel("Optional: Enter Page Ranges (e.g. '1-3, 5'). Leave empty to split all pages.")
        controls_layout.addWidget(range_label)
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g. 1-5, 8, 10-12")
        controls_layout.addWidget(self.range_input)

        # Custom filename input
        filename_label = QLabel("Custom filename prefix (optional, default: 'split'):")
        controls_layout.addWidget(filename_label)
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("e.g. invoice, report, document")
        controls_layout.addWidget(self.filename_input)

        # Split button
        self.split_btn = QPushButton("Split PDF")
        self.split_btn.clicked.connect(self.process_split)
        self.split_btn.setEnabled(False)
        controls_layout.addWidget(self.split_btn)

        # Spacer
        controls_layout.addStretch()

        # Drag and drop hint
        drag_hint = QLabel("Tip: You can also drag and drop a PDF file here")
        drag_hint.setStyleSheet("color: #757575; font-style: italic; font-size: 9pt;")
        controls_layout.addWidget(drag_hint)

        # Right panel: preview
        from gui.preview import PreviewWidget
        self.split_preview = PreviewWidget(self.split_renderer)
        self.split_preview.setMinimumWidth(500)

        # Add to main layout
        main_layout.addWidget(controls_widget)
        main_layout.addWidget(self.split_preview)

        self.tabs.addTab(tab, "Slice PDF")

    def select_split_file(self):
        """Opens a file dialog to select the PDF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select PDF", 
            "", 
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self._set_split_file(file_path)

    def _set_split_file(self, file_path):
        self.current_split_file = file_path
        self.split_file_label.setText(os.path.basename(file_path))
        self.split_btn.setEnabled(True)
        self.split_preview.load_pdf(file_path)

    def process_split(self):
        """Executes the split operation"""
        if not self.current_split_file:
            return
            
        # Ask user where to save
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not output_folder:
            return

        range_str = self.range_input.text().strip()

        # Get custom filename prefix
        custom_prefix = self.filename_input.text().strip()
        if not custom_prefix:
            custom_prefix = "split"  # Default

        try:
            # Call our logic class
            created_files = self.manager.split_pdf(
                self.current_split_file,
                output_folder,
                file_prefix=custom_prefix,
                range_str=range_str if range_str else None
            )
            
            if not created_files and range_str:
                QMessageBox.warning(self, "Warning", "No files created. Check your page range.")
                return
            
            QMessageBox.information(
                self, 
                "Success", 
                f"Successfully created {len(created_files)} files in:\n{output_folder}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")

    def create_merge_tab(self):
        """Setup the UI for the Merge tab"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)

        # Left panel: controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_widget.setMaximumWidth(400)

        # Instructions
        label = QLabel("Select PDFs to merge (drag to reorder):")
        controls_layout.addWidget(label)

        # List widget
        self.merge_list = QListWidget()
        self.merge_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.merge_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._connect_merge_list_signals()
        controls_layout.addWidget(self.merge_list)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Files")
        add_btn.clicked.connect(self.add_merge_files)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_merge_items)
        merge_btn = QPushButton("Merge PDFs")
        merge_btn.clicked.connect(self.process_merge)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(merge_btn)
        controls_layout.addLayout(btn_layout)

        # Drag and drop hint
        drag_hint = QLabel("Tip: You can also drag and drop PDF files here")
        drag_hint.setStyleSheet("color: #757575; font-style: italic; font-size: 9pt;")
        controls_layout.addWidget(drag_hint)

        # Right panel: preview
        from gui.preview import PreviewWidget
        self.merge_preview = PreviewWidget(self.merge_renderer)
        self.merge_preview.setMinimumWidth(500)

        # Add to main layout
        main_layout.addWidget(controls_widget)
        main_layout.addWidget(self.merge_preview)

        self.tabs.addTab(tab, "Stich PDF")
        self.schedule_merge_preview_refresh()

    def _connect_merge_list_signals(self):
        model = self.merge_list.model()
        model.rowsInserted.connect(self.schedule_merge_preview_refresh)
        model.rowsRemoved.connect(self.schedule_merge_preview_refresh)
        model.rowsMoved.connect(self.schedule_merge_preview_refresh)
        model.dataChanged.connect(self.schedule_merge_preview_refresh)

    def schedule_merge_preview_refresh(self):
        self._merge_preview_update_timer.start()

    def add_merge_files(self):
        """Adds files to the merge list"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select PDFs", 
            "", 
            "PDF Files (*.pdf)"
        )
        
        self._add_merge_files(files)

        self.schedule_merge_preview_refresh()

    def _add_merge_files(self, files):
        for file_path in files:
            if not file_path:
                continue
            item = QListWidgetItem(os.path.basename(file_path))
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.merge_list.addItem(item)

    def remove_merge_items(self):
        """Removes selected items from the list"""
        # We must delete items carefully, usually loop backwards or use taken items
        for item in self.merge_list.selectedItems():
            self.merge_list.takeItem(self.merge_list.row(item))

        self.schedule_merge_preview_refresh()

    def process_merge(self):
        """Collects files from list and calls merge logic"""
        count = self.merge_list.count()
        if count < 2:
            QMessageBox.warning(self, "Warning", "Please add at least 2 PDF files to merge.")
            return
            
        # Collect paths in the order they appear in the list
        input_paths = []
        for i in range(count):
            item = self.merge_list.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            input_paths.append(path)
            
        # Ask for output filename (save dialog)
        output_file, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Merged PDF", 
            "merged.pdf", 
            "PDF Files (*.pdf)"
        )
        
        if not output_file:
            return
            
        try:
            self.manager.merge_pdfs(input_paths, output_file)
            QMessageBox.information(self, "Success", f"Merged PDF saved to:\n{output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to merge:\n{str(e)}")

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = self.theme_manager.toggle_theme()

        # Update button icon and tooltip
        if new_theme == "dark":
            self.theme_toggle_btn.setText("☀")
            self.theme_toggle_btn.setToolTip("Switch to Light Theme")
        else:
            self.theme_toggle_btn.setText("🌙")
            self.theme_toggle_btn.setToolTip("Switch to Dark Theme")

    def _merge_list_paths_in_order(self):
        paths = []
        for i in range(self.merge_list.count()):
            item = self.merge_list.item(i)
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                paths.append(path)
        return paths

    def _update_merge_preview_now(self):
        paths = self._merge_list_paths_in_order()
        if not paths:
            self.merge_preview.clear()
            self._cleanup_merge_preview_temp_file()
            return

        if len(paths) == 1:
            self.merge_preview.load_pdf(paths[0])
            self._cleanup_merge_preview_temp_file()
            return

        fd, temp_path = tempfile.mkstemp(prefix="merge_preview_", suffix=".pdf")
        os.close(fd)

        try:
            self.manager.merge_pdfs(paths, temp_path)
            old_path = self._merge_preview_temp_path
            self._merge_preview_temp_path = temp_path
            self.merge_preview.load_pdf(temp_path)
            if old_path:
                self._try_remove_file(old_path)
        except Exception:
            self._try_remove_file(temp_path)
            self.merge_preview.clear()

    def _cleanup_merge_preview_temp_file(self):
        if self._merge_preview_temp_path:
            self._try_remove_file(self._merge_preview_temp_path)
            self._merge_preview_temp_path = None

    def _try_remove_file(self, path):
        try:
            os.remove(path)
        except OSError:
            pass

    def closeEvent(self, event):
        self._cleanup_merge_preview_temp_file()
        super().closeEvent(event)

    def dragEnterEvent(self, event):
        if self._extract_pdf_paths_from_event(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        pdf_paths = self._extract_pdf_paths_from_event(event)
        if not pdf_paths:
            event.ignore()
            return

        active_tab = self.tabs.currentIndex()

        if active_tab == 0:
            self._set_split_file(pdf_paths[0])
        else:
            self._add_merge_files(pdf_paths)
            self.schedule_merge_preview_refresh()

        event.acceptProposedAction()

    def _extract_pdf_paths_from_event(self, event):
        mime = event.mimeData()
        if not mime.hasUrls():
            return []

        paths = []
        for url in mime.urls():
            local = url.toLocalFile()
            if local and local.lower().endswith(".pdf"):
                paths.append(local)

        return paths
