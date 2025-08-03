"""
Main PDF Viewer application class that coordinates all components.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox, simpledialog

from pdf_miner import PDFMiner
from pdf_security import PDFSecurity
from pdf_converter import PDFConverter
from ui_components import UIManager, res
from dialogs import PasswordDialog

class Viewer:
    """Main PDF viewer application."""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Initialize components
        self.ui_manager = UIManager(root)
        self.pdf_security = PDFSecurity(self)
        self.pdf_converter = PDFConverter(self)
        
        # Initialize UI
        self.setup_menu()
        self.setup_layout()
        self.setup_key_bindings()
        
        # Application state
        self.tabs = {}
        
        # Apply initial theme
        self.ui_manager.apply_theme()
    
    def setup_window(self):
        """Configure the main window."""
        self.root.title("PDF Viewer")
        self.root.geometry("1400x800")
        try:
            self.root.iconbitmap(res("resources/pdf_file_icon.ico"))
        except:
            pass  # Icon file not found
    
    def setup_menu(self):
        """Create the menu bar."""
        bar = tk.Menu(self.root)
        self.root.config(menu=bar)
        
        # File menu
        mf = tk.Menu(bar, tearoff=0)
        bar.add_cascade(label="File", menu=mf)
        mf.add_command(label="Open", accelerator="Ctrl+O", command=self.open_file)
        mf.add_command(label="Convert to Word", command=self.pdf_converter.pdf_to_word)
        mf.add_command(label="Convert DOCX to PDF", command=self.pdf_converter.word_to_pdf)
        mf.add_separator()
        mf.add_command(label="Exit", command=self.root.destroy)
        
        # View menu
        mv = tk.Menu(bar, tearoff=0)
        bar.add_cascade(label="View", menu=mv)
        mv.add_checkbutton(label="Dark Mode", 
                          variable=self.ui_manager.dark, 
                          command=self.ui_manager.apply_theme)
    
    def setup_layout(self):
        """Setup the main window layout."""
        self.ui_manager.setup_grid()
        
        # Button commands for left panel
        button_commands = {
            'convert_to_word': self.pdf_converter.pdf_to_word,
            'convert_to_pdf': self.pdf_converter.word_to_pdf,
            'lock_pdf': self.lock_pdf,
            'unlock_pdf': self.unlock_pdf
        }
        
        # Control commands for right panel
        control_commands = {
            'print': self.print_pdf,
            'zoom_in': self.zoom_in,
            'zoom_out': self.zoom_out,
            'jump': self.jump,
            'prev': self.prev,
            'next': self.next
        }
        
        # Notebook commands for center panel
        notebook_commands = {
            'manage_permissions': self.manage_permissions
        }
        
        # Create panels
        self.left_panel = self.ui_manager.create_left_panel(self.root, button_commands)
        self.center_panel, self.nb = self.ui_manager.create_center_panel(self.root, notebook_commands)
        self.right_panel, self.page_var, self.page_lbl = self.ui_manager.create_right_panel(self.root, control_commands)
        
        # Bind notebook events
        self.nb.bind("<Button-3>", self._tab_menu)
    
    def setup_key_bindings(self):
        """Setup keyboard shortcuts."""
        self.root.bind("<Control-o>", lambda *_: self.open_file())
        
        key_bindings = [
            ("<Prior>", self.prev), ("<Next>", self.next),
            ("<Up>", self.prev), ("<Down>", self.next),
            ("+", self.zoom_in), ("=", self.zoom_in),
            ("-", self.zoom_out)
        ]
        
        for key, func in key_bindings:
            self.root.bind(key, lambda e, fn=func: fn())
    
    def get_password_with_confirmation(self, title="Set Password"):
        """Get password with confirmation dialog."""
        return PasswordDialog.get_password_with_confirmation(self.root, title)
    
    # File operations
    def _try_open(self, path, pwd=None):
        """Try to open a PDF file."""
        try:
            return PDFMiner(path, pwd)
        except RuntimeError as e:
            if "password required" in str(e):
                return None
            else:
                try:
                    if pwd:
                        # Test if pikepdf can open it
                        import pikepdf
                        test_pdf = pikepdf.open(path, password=pwd)
                        test_pdf.close()
                        return PDFMiner(path, pwd)
                    return None
                except:
                    return None
    
    def open_file(self):
        """Open a PDF file."""
        path = fd.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path:
            return
        
        miner = self._try_open(path)
        if not miner:
            pwd = simpledialog.askstring("Password", "Enter PDF password:", show="*")
            if not pwd:
                return
            miner = self._try_open(path, pwd)
            if not miner:
                messagebox.showerror("Error", "Incorrect password or unreadable file.")
                return
        
        self._add_tab(miner)
    
    def _add_tab(self, miner):
        """Add a new tab for a PDF."""
        frm = ttk.Frame(self.nb)
        frm.columnconfigure(0, weight=1)
        frm.rowconfigure(0, weight=1)
        
        # Canvas for PDF display
        cv = tk.Canvas(frm, bg=self.ui_manager.get_canvas_bg())
        cv.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        vs = tk.Scrollbar(frm, orient="vertical", command=cv.yview)
        vs.grid(row=0, column=1, sticky="ns")
        hs = tk.Scrollbar(frm, orient="horizontal", command=cv.xview)
        hs.grid(row=1, column=0, sticky="ew")
        
        cv.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        cv.bind("<MouseWheel>", lambda e, c=cv: c.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        
        # Add tab
        self.nb.add(frm, text=os.path.basename(miner.path))
        self.nb.select(frm)
        
        # Store tab data
        self.tabs[frm] = dict(miner=miner, canvas=cv, page=0, zoom=1.0)
        self._render(frm)
    
    def _get_active_tab(self):
        """Get the currently active tab."""
        tid = self.nb.select()
        return next(((f, d) for f, d in self.tabs.items() if str(f) == tid), (None, None))
    
    def _render(self, frm):
        """Render the current page of a PDF in the given frame."""
        d = self.tabs[frm]
        cv = d["canvas"]
        cv.delete("all")
        
        img = d["miner"].image(d["page"], d["zoom"])
        d["img"] = img
        
        cw, ch = cv.winfo_width(), cv.winfo_height()
        cv.create_image(max((cw - img.width()) // 2, 0),
                       max((ch - img.height()) // 2, 0),
                       anchor="nw", image=img)
        cv.configure(scrollregion=cv.bbox("all"))
        self.page_lbl.config(text=f"{d['page'] + 1}/{d['miner'].pages}")
    
    # Navigation
    def _shift(self, delta):
        """Move to next/previous page."""
        frm, d = self._get_active_tab()
        if d and 0 <= d["page"] + delta < d["miner"].pages:
            d["page"] += delta
            self._render(frm)
    
    def next(self):
        """Go to next page."""
        self._shift(1)
    
    def prev(self):
        """Go to previous page."""
        self._shift(-1)
    
    def jump(self):
        """Jump to a specific page."""
        frm, d = self._get_active_tab()
        if not d:
            return
        try:
            tgt = int(self.page_var.get()) - 1
        except:
            return
        if 0 <= tgt < d["miner"].pages:
            d["page"] = tgt
            self._render(frm)
    
    # Zoom
    def _zoom(self, factor):
        """Apply zoom factor to current tab."""
        frm, d = self._get_active_tab()
        if d:
            d["zoom"] *= factor
            self._render(frm)
    
    def zoom_in(self):
        """Zoom in."""
        self._zoom(1.1)
    
    def zoom_out(self):
        """Zoom out."""
        self._zoom(1 / 1.1)
    
    # Security operations
    def lock_pdf(self):
        """Lock a PDF file."""
        frm, d = self._get_active_tab()
        source_path = d["miner"].path if d else None
        
        result = self.pdf_security.lock_pdf(source_path)
        if result and len(result) == 2:
            dst_path, pwd = result
            if pwd:  # User wants to open the locked file
                miner = self._try_open(dst_path, pwd)
                if miner:
                    self._add_tab(miner)
    
    def unlock_pdf(self):
        """Unlock a PDF file."""
        frm, d = self._get_active_tab()
        source_path = d["miner"].path if d else None
        
        result = self.pdf_security.unlock_pdf(source_path)
        if result and len(result) == 2:
            dst_path, _ = result
            miner = self._try_open(dst_path)
            if miner:
                self._add_tab(miner)
    
    def manage_permissions(self):
        """Manage PDF permissions."""
        frm, d = self._get_active_tab()
        source_path = d["miner"].path if d else None
        self.pdf_security.manage_permissions(source_path)
    
    # Other operations
    def print_pdf(self):
        """Print the current PDF."""
        frm, d = self._get_active_tab()
        if not d:
            path = fd.askopenfilename(title="Select PDF to print", 
                                    filetypes=[("PDF", "*.pdf")])
        else:
            path = d["miner"].path
        
        if not path:
            return
        
        if os.name != "nt":
            messagebox.showinfo("Info", "Print demo only on Windows.")
            return
        
        try:
            os.startfile(path, "print")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _tab_menu(self, ev):
        """Show context menu for tabs."""
        idx = self.nb.index(f"@{ev.x},{ev.y}")
        if idx == -1:
            return
        
        frm = self.nb.nametowidget(self.nb.tabs()[idx])
        self.nb.select(frm)
        d = self.tabs[frm]
        
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="Close", command=lambda: self._close_tab(frm))
        m.add_command(label="Convert to Word", 
                     command=lambda: self.pdf_converter.convert_current_to_word(d["miner"].path))
        m.add_separator()
        m.add_command(label="Lock PDF", command=self.lock_pdf)
        m.add_command(label="Unlock PDF", command=self.unlock_pdf)
        m.add_separator()
        m.add_command(label="Manage Permissions", command=self.manage_permissions)
        m.tk_popup(ev.x_root, ev.y_root)
    
    def _close_tab(self, frm):
        """Close a tab."""
        if frm in self.tabs:
            self.tabs[frm]["miner"].close()  # Clean up PDF resources
            self.nb.forget(frm)
            self.tabs.pop(frm, None)
