import os
from pypdf import PdfReader, PdfWriter

class PDFManager:
    """
    Handles the core PDF logic using pypdf.
    
    Architectural Note:
    We separate this logic from the GUI (window.py). This is known as
    "Separation of Concerns". It allows us to:
    1. Test this logic without launching a window.
    2. Swap out the GUI later (e.g., for a web app) without rewriting the logic.
    3. Keep the code clean and readable.
    """

    def get_pdf_info(self, file_path):
        """
        Returns basic info about the PDF to display to the user.
        """
        try:
            reader = PdfReader(file_path)
            # len(reader.pages) is the standard way to get page count in pypdf 3.x+
            return {"num_pages": len(reader.pages), "valid": True}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def parse_page_groups(self, range_str, max_pages):
        """
        Parses a string like "1-3, 5" into a list of page lists.
        Example: "1-3, 5" -> [[0, 1, 2], [4]] (0-indexed)
        """
        groups = []
        try:
            parts = [p.strip() for p in range_str.split(',') if p.strip()]
            for part in parts:
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    # Convert 1-based to 0-based, inclusive
                    # Ensure within bounds
                    start = max(1, start)
                    end = min(max_pages, end)
                    if start > end:
                        continue
                    groups.append(list(range(start - 1, end)))
                else:
                    page_num = int(part)
                    if 1 <= page_num <= max_pages:
                        groups.append([page_num - 1])
        except ValueError:
            pass # Ignore malformed parts for now
        return groups

    def split_pdf(self, input_path, output_folder, file_prefix="split", range_str=None):
        """
        Splits a PDF into individual pages or groups.
        
        Args:
            input_path (str): Full path to source PDF.
            output_folder (str): Folder to save split files.
            file_prefix (str): Prefix for filenames.
            range_str (str): Optional string like "1-3, 5".
        
        Returns:
            list: Paths of created files.
        """
        created_files = []
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        # Determine how to split
        if range_str:
            groups = self.parse_page_groups(range_str, total_pages)
            if not groups:
                # Fallback if parse failed or empty? Or raise error?
                # For now let's just return empty list or fallback to all?
                # Let's return empty to indicate "no valid pages selected"
                return []
        else:
            # Default: specific "explode" behavior (one page per group)
            groups = [[i] for i in range(total_pages)]
            
        for i, page_indices in enumerate(groups):
            if not page_indices:
                continue
                
            writer = PdfWriter()
            # Add all pages in this group to the new PDF
            for page_idx in page_indices:
                writer.add_page(reader.pages[page_idx])
            
            # Naming logic
            if len(page_indices) == 1:
                # Single page: split_page_1.pdf
                suffix = f"page_{page_indices[0] + 1}"
            else:
                # Range: split_pages_1-3.pdf
                first = page_indices[0] + 1
                last = page_indices[-1] + 1
                suffix = f"pages_{first}-{last}"
                
            output_filename = f"{file_prefix}_{suffix}.pdf"
            output_path = os.path.join(output_folder, output_filename)
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            created_files.append(output_path)
            
        return created_files

    def merge_pdfs(self, input_paths, output_path):
        """
        Merges multiple PDFs into one.
        
        Args:
            input_paths (list): List of file path strings.
            output_path (str): Destination path.
        """
        merger = PdfWriter()
        
        for path in input_paths:
            # pypdf's append method (via PdfWriter) is efficient
            # In older versions this was PdfFileMerger, now merged into PdfWriter
            merger.append(path)
            
        with open(output_path, "wb") as f:
            merger.write(f)
        
        return output_path
