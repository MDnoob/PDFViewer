"""
Custom dialog boxes and user input forms.
"""

import tkinter as tk
from tkinter import ttk, messagebox

class PasswordDialog:
    """Custom password dialog with confirmation field."""
    
    @staticmethod
    def get_password_with_confirmation(parent, title="Set Password"):
        """Show password dialog with confirmation field."""
        
        # Create the dialog window
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("350x200")
        dialog.grab_set()  # Make it modal
        dialog.transient(parent)
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Result variable
        result = {"password": None}
        
        # UI Elements
        ttk.Label(dialog, text="Set PDF Password", font=('Arial', 12, 'bold')).pack(pady=15)
        
        # Password entry frame
        pwd_frame = ttk.Frame(dialog)
        pwd_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(pwd_frame, text="Enter password:").pack(anchor='w')
        pwd_entry = ttk.Entry(pwd_frame, show="*", width=30)
        pwd_entry.pack(pady=5, fill='x')
        
        ttk.Label(pwd_frame, text="Confirm password:").pack(anchor='w', pady=(10,0))
        confirm_entry = ttk.Entry(pwd_frame, show="*", width=30)
        confirm_entry.pack(pady=5, fill='x')
        
        # Button frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        def on_ok():
            pwd = pwd_entry.get()
            confirm = confirm_entry.get()
            
            if not pwd:
                messagebox.showerror("Error", "Please enter a password.", parent=dialog)
                pwd_entry.focus()
                return
                
            if pwd != confirm:
                messagebox.showerror("Error", "Passwords do not match.", parent=dialog)
                confirm_entry.delete(0, tk.END)
                confirm_entry.focus()
                return
            
            result["password"] = pwd
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side='left', padx=5)
        
        # Enter key binding
        def handle_enter(event):
            on_ok()
        
        pwd_entry.bind('<Return>', handle_enter)
        confirm_entry.bind('<Return>', handle_enter)
        pwd_entry.focus()
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result["password"]
