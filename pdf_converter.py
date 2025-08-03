"""
PDF conversion functionality for Word documents and other formats.
"""

import threading
from tkinter import filedialog as fd, messagebox
from pdf2docx import Converter
from docx2pdf import convert

class PDFConverter:
    """Handles PDF conversion operations."""
    
    def __init__(self, parent):
        self.parent = parent
    
    def pdf_to_word(self, source_path=None):
        """Convert PDF to Word document."""
        def run():
            src = source_path or fd.askopenfilename(filetypes=[("PDF", "*.pdf")])
            if not src:
                return
            
            dst = fd.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word", "*.docx")]
            )
            if not dst:
                return
            
            try:
                Converter(src).convert(dst)
                messagebox.showinfo("Done", "Converted to Word.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=run, daemon=True).start()
    
    def word_to_pdf(self):
        """Convert Word document to PDF."""
        def run():
            src = fd.askopenfilename(filetypes=[("Word", "*.docx")])
            if not src:
                return
            
            dst = fd.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")]
            )
            if not dst:
                return
            
            try:
                convert(src, dst)
                messagebox.showinfo("Done", "DOCX converted to PDF.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=run, daemon=True).start()
    
    def convert_current_to_word(self, pdf_path):
        """Convert currently opened PDF to Word."""
        def run():
            dst = fd.asksaveasfilename(
                defaultextension=".docx",
                filetypes=[("Word", "*.docx")]
            )
            if not dst:
                return
            
            try:
                Converter(pdf_path).convert(dst)
                messagebox.showinfo("Done", "Converted to Word.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        threading.Thread(target=run, daemon=True).start()
