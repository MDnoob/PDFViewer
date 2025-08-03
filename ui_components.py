"""
UI components, layout management, and theme functionality.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, PhotoImage

def res(rel):
    """Get resource path for bundled applications."""
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base, rel)

class UIManager:
    """Manages UI layout, themes, and visual components."""
    
    def __init__(self, root):
        self.root = root
        self.setup_colors()
        self.setup_style()
        self.load_icons()
    
    def setup_colors(self):
        """Initialize color scheme."""
        self.col = dict(
            light_bg="#ECE8F3", 
            light_fg="#000",
            dark_bg="#1f1f1f",  
            dark_fg="#fff"
        )
        self.dark = tk.BooleanVar(value=False)
    
    def setup_style(self):
        """Initialize TTK style."""
        self.style = ttk.Style()
        self.style.theme_use("clam")
    
    def load_icons(self):
        """Load all icon resources."""
        try:
            self.icons = {
                'printer': PhotoImage(file=res("resources/printer.png")).subsample(8, 8),
                'zoom_in': PhotoImage(file=res("resources/zoomin.png")).subsample(20, 20),
                'zoom_out': PhotoImage(file=res("resources/zoomout.png")).subsample(20, 20),
                'up_arrow': PhotoImage(file=res("resources/uparrow.png")).subsample(3, 3),
                'down_arrow': PhotoImage(file=res("resources/downarrow.png")).subsample(3, 3)
            }
        except Exception as e:
            print(f"Warning: Could not load icons: {e}")
            self.icons = {}
    
    def apply_theme(self):
        """Apply the current theme (light/dark mode)."""
        bg = self.col["dark_bg"] if self.dark.get() else self.col["light_bg"]
        fg = self.col["dark_fg"] if self.dark.get() else self.col["light_fg"]
        
        for style_name in ("TFrame", "TLabel", "TButton", "TNotebook"):
            self.style.configure(style_name, background=bg, foreground=fg)
        
        self.style.configure("TNotebook.Tab", background=bg, foreground=fg)
        self.style.map("TNotebook.Tab",
                      background=[("selected", bg)], 
                      foreground=[("selected", fg)])
        
        self.root.configure(bg=bg)
    
    def get_canvas_bg(self):
        """Get the appropriate canvas background color."""
        return self.col["dark_bg"] if self.dark.get() else self.col["light_bg"]
    
    def setup_grid(self):
        """Setup the main window grid layout."""
        self.root.columnconfigure(0, weight=0, minsize=150)  # Left panel
        self.root.columnconfigure(1, weight=1)               # Center panel
        self.root.columnconfigure(2, weight=0, minsize=190)  # Right panel
        self.root.rowconfigure(0, weight=1)
    
    def create_left_panel(self, parent, button_commands):
        """Create the left tool panel."""
        lf = ttk.Frame(parent, width=150)
        lf.grid(row=0, column=0, sticky="ns")
        lf.grid_propagate(False)
        
        ttk.Label(lf, text="Tools").grid(pady=(6, 4))
        
        buttons = [
            ("Convert to Word", button_commands['convert_to_word']),
            ("Convert DOCX➜PDF", button_commands['convert_to_pdf']),
            ("Lock PDF", button_commands['lock_pdf']),
            ("Unlock PDF", button_commands['unlock_pdf'])
        ]
        
        for r, (txt, cmd) in enumerate(buttons, 1):
            ttk.Button(lf, text=txt, command=cmd).grid(row=r, column=0, pady=4, padx=4)
        
        return lf
    
    def create_center_panel(self, parent, notebook_commands):
        """Create the center panel with notebook."""
        cen = ttk.Frame(parent)
        cen.grid(row=0, column=1, sticky="nsew")
        cen.columnconfigure(0, weight=1)
        cen.rowconfigure(1, weight=1)
        
        # Top bar
        top = ttk.Frame(cen)
        top.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(top, text="Open PDF(s):").pack(side="left")
        ttk.Button(top, text="Manage Permissions", 
                  command=notebook_commands['manage_permissions']).pack(side="right", padx=6)
        
        # Notebook
        nb = ttk.Notebook(cen)
        nb.grid(row=1, column=0, sticky="nsew")
        
        return cen, nb
    
    def create_right_panel(self, parent, control_commands):
        """Create the right control panel."""
        rt = ttk.Frame(parent, width=190)
        rt.grid(row=0, column=2, sticky="ns")
        rt.grid_propagate(False)
        rt.rowconfigure(5, weight=1)
        
        # Print button
        if 'printer' in self.icons:
            ttk.Button(rt, image=self.icons['printer'], 
                      command=control_commands['print']).grid(row=0, column=0, pady=6)
        
        # Zoom controls
        zf = ttk.Frame(rt)
        zf.grid(row=1, column=0)
        
        if 'zoom_in' in self.icons and 'zoom_out' in self.icons:
            ttk.Button(zf, image=self.icons['zoom_in'], 
                      command=control_commands['zoom_in']).pack(side="left", padx=2)
            ttk.Button(zf, image=self.icons['zoom_out'], 
                      command=control_commands['zoom_out']).pack(side="left", padx=2)
        
        # Page controls
        ttk.Label(rt, text="Page:").grid(row=2, column=0, pady=(6, 2))
        
        page_var = tk.StringVar()
        ttk.Entry(rt, textvariable=page_var, width=6).grid(row=3, column=0)
        ttk.Button(rt, text="Go", command=control_commands['jump']).grid(row=4, column=0, pady=2)
        
        # Navigation arrows
        if 'up_arrow' in self.icons and 'down_arrow' in self.icons:
            ttk.Button(rt, image=self.icons['up_arrow'], 
                      command=control_commands['prev']).grid(row=6, column=0, pady=2)
            ttk.Button(rt, image=self.icons['down_arrow'], 
                      command=control_commands['next']).grid(row=7, column=0, pady=2)
        
        # Page label
        page_lbl = ttk.Label(rt, text="Page")
        page_lbl.grid(row=8, column=0, pady=4)
        
        return rt, page_var, page_lbl
