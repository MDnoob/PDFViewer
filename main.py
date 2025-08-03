#!/usr/bin/env python3
"""
PDF Viewer Application
Main entry point for the PDF viewer application.
"""

import tkinter as tk
from pdf_viewer import Viewer

def main():
    """Initialize and run the PDF viewer application."""
    root = tk.Tk()
    app = Viewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
