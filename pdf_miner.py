"""
PDF processing and rendering functionality using PyMuPDF and pikepdf.
"""

import os
import tempfile
import fitz
import pikepdf
from tkinter import PhotoImage

DEFAULT_ZOOM = 2.5

class PDFMiner:
    """Handles PDF file opening, rendering, and basic operations."""
    
    def __init__(self, path, pwd=None):
        self.path = path
        try:
            self.doc = fitz.open(path)
            # Better password handling for encrypted PDFs
            if self.doc.needs_pass:
                if pwd:
                    auth_result = self.doc.authenticate(pwd)
                    if not auth_result:
                        self.doc.close()
                        raise RuntimeError("password required")
                else:
                    self.doc.close()
                    raise RuntimeError("password required")
        except Exception as exc:
            # If fitz fails, try with pikepdf first to handle encryption properly
            if pwd:
                try:
                    # Try opening with pikepdf to handle complex encryption
                    temp_pdf = pikepdf.open(path, password=pwd)
                    temp_path = os.path.join(tempfile.gettempdir(), "temp_decrypted.pdf")
                    temp_pdf.save(temp_path)
                    temp_pdf.close()
                    
                    # Now open with fitz
                    self.doc = fitz.open(temp_path)
                    
                    # Clean up temp file after opening
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                        
                except Exception:
                    raise RuntimeError(str(exc)) from exc
            else:
                raise RuntimeError(str(exc)) from exc
        
        # Set base zoom based on page width
        if self.doc.page_count > 0:
            w = int(self.doc[0].rect.width // 100 * 100)
            self.base_zoom = {800:0.8, 700:0.6, 600:1.0, 500:1.0}.get(w, DEFAULT_ZOOM)
        else:
            self.base_zoom = DEFAULT_ZOOM

    @property
    def pages(self):
        """Return the total number of pages in the PDF."""
        return self.doc.page_count

    def image(self, pno, factor=1.0):
        """Generate a PhotoImage for the specified page number with zoom factor."""
        mat = fitz.Matrix(self.base_zoom * factor, self.base_zoom * factor)
        pix = self.doc[pno].get_pixmap(matrix=mat)
        if pix.alpha:
            pix = fitz.Pixmap(pix, 0)
        return PhotoImage(data=pix.tobytes("ppm"))

    def close(self):
        """Close the PDF document."""
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
