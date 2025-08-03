"""
PDF security functionality including password protection and permissions management.
"""

import os
import tempfile
import pikepdf
from tkinter import messagebox, simpledialog, filedialog as fd

def build_permissions(allow_view, allow_print, allow_copy, allow_modify):
    """Build permissions object - simplified for compatibility."""
    from pikepdf import Permissions
    return Permissions()

def build_default_permissions():
    """Build default permissions object."""
    from pikepdf import Permissions
    return Permissions()

def lock_pdf_with_pikepdf(src, dst, owner_pwd, user_pwd, perms):
    """Lock a PDF file with password and permissions."""
    pdf = pikepdf.open(src)
    pdf.save(dst, encryption=pikepdf.Encryption(
        owner=owner_pwd,
        user=user_pwd,
        R=6,
        allow=perms
    ))
    pdf.close()

def unlock_pdf_with_pikepdf(src, pwd):
    """Unlock a PDF file and return temporary unlocked file path."""
    pdf = pikepdf.open(src, password=pwd)
    tmp = os.path.join(tempfile.gettempdir(), "unlocked_temp.pdf")
    pdf.save(tmp)
    pdf.close()
    return tmp

class PDFSecurity:
    """Handles PDF security operations like locking, unlocking, and permissions."""
    
    def __init__(self, parent):
        self.parent = parent
    
    def open_pdf_maybe_password(self, path):
        """Open PDF with pikepdf, prompting for password if needed."""
        try:
            return pikepdf.open(path)
        except pikepdf.PasswordError:
            pwd = simpledialog.askstring("Password", "Enter current PDF password:", show="*")
            if not pwd:
                return None
            try:
                return pikepdf.open(path, password=pwd)
            except pikepdf.PasswordError:
                messagebox.showerror("Error", "Incorrect password.")
                return None
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {str(e)}")
            return None
    
    def lock_pdf(self, source_path=None):
        """Lock a PDF with password protection."""
        if not source_path:
            source_path = fd.askopenfilename(
                title="Select PDF to lock",
                filetypes=[("PDF", "*.pdf")]
            )
        
        if not source_path:
            return False
        
        # Check if PDF is already password protected
        try:
            test_pdf = pikepdf.open(source_path)
            test_pdf.close()
        except pikepdf.PasswordError:
            messagebox.showwarning("Warning", "This PDF is already password protected.")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Could not read PDF: {str(e)}")
            return False
        
        # Get password using the dialog from parent
        if hasattr(self.parent, 'get_password_with_confirmation'):
            pwd = self.parent.get_password_with_confirmation("Lock PDF")
        else:
            pwd = simpledialog.askstring("Password", "Set password for PDF:", show="*")
        
        if not pwd:
            return False
        
        # Get destination file
        dst = fd.asksaveasfilename(
            title="Save locked PDF as...",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if not dst:
            return False
        
        try:
            # Create locked PDF
            lock_pdf_with_pikepdf(source_path, dst, pwd, pwd, build_default_permissions())
            messagebox.showinfo("Success", f"PDF locked successfully!\nSaved as: {os.path.basename(dst)}")
            
            # Ask if user wants to open the locked PDF
            if messagebox.askyesno("Open File", "Would you like to open the locked PDF?"):
                return dst, pwd
            return dst, None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to lock PDF: {str(e)}")
            return False
    
    def unlock_pdf(self, source_path=None):
        """Remove password protection from a PDF."""
        if not source_path:
            source_path = fd.askopenfilename(
                title="Select PDF to unlock",
                filetypes=[("PDF", "*.pdf")]
            )
        
        if not source_path:
            return False
        
        # Try to open the PDF (will prompt for password if needed)
        pdf = self.open_pdf_maybe_password(source_path)
        if pdf is None:
            return False
        
        # Get destination file
        dst = fd.asksaveasfilename(
            title="Save unlocked PDF as...",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if not dst:
            pdf.close()
            return False
        
        try:
            # Save without encryption
            pdf.save(dst)
            pdf.close()
            messagebox.showinfo("Success", f"PDF unlocked successfully!\nSaved as: {os.path.basename(dst)}")
            
            # Ask if user wants to open the unlocked PDF
            if messagebox.askyesno("Open File", "Would you like to open the unlocked PDF?"):
                return dst, None
            return dst, None
            
        except Exception as e:
            pdf.close()
            messagebox.showerror("Error", f"Failed to unlock PDF: {str(e)}")
            return False
    
    def manage_permissions(self, source_path=None):
        """Manage PDF permissions - simplified for now."""
        messagebox.showinfo(
            "Info", 
            "Permissions management is temporarily disabled due to library compatibility issues.\n"
            "This feature will be implemented in a future update."
        )
        return False
