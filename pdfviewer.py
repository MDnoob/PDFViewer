import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import PhotoImage
from pdf2docx import Converter
import threading
import os
import sys
import math
import fitz
from docx2pdf import convert

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# =======================
# PDFMiner Class (Part 2)
# =======================
class PDFMiner:
    def __init__(self, filepath):
        self.filepath = filepath
        self.pdf = fitz.open(self.filepath)
        self.first_page = self.pdf.load_page(0)
        self.width, self.height = self.first_page.rect.width, self.first_page.rect.height
        zoomdict = {800: 0.8, 700: 0.6, 600: 1.0, 500: 1.0}
        width_key = int(math.floor(self.width / 100.0) * 100)
        self.zoom = zoomdict.get(width_key, 1.0)
        
    def get_metadata(self):
        metadata = self.pdf.metadata
        numPages = self.pdf.page_count
        return metadata, numPages
    
    def get_page(self, page_num, zoom_factor=1.0):
        page = self.pdf.load_page(page_num)
        if self.zoom:
            mat = fitz.Matrix(self.zoom * zoom_factor, self.zoom * zoom_factor)
            pix = page.get_pixmap(matrix=mat)
        else:
            pix = page.get_pixmap()
        px1 = fitz.Pixmap(pix, 0) if pix.alpha else pix
        imgdata = px1.tobytes("ppm")
        return PhotoImage(data=imgdata)
    
    def get_text(self, page_num):
        page = self.pdf.load_page(page_num)
        text = page.get_text('text')
        return text

# =======================
# PDFViewer Class (Part 1)
# =======================
class PDFViewer:
    def __init__(self, master):
        # PDF file related variables
        self.path = None
        self.fileisopen = False
        self.author = None
        self.name = None
        self.current_page = 0
        self.numPages = None
        self.zoom_factor = 1.0

        self.master = master
        self.master.title('PDF Viewer')
        self.master.geometry('1400x800')
        self.master.resizable(width=True, height=True)
        self.master.iconbitmap(resource_path("resources/pdf_file_icon.ico"))

        # Create menu bar
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open File", command=self.open_file, accelerator="[Ctrl+O]")
        self.filemenu.add_command(label="Convert to Word", command=self.convert_to_word_threaded)
        self.filemenu.add_command(label="Convert to PDF", command=self.convert_to_pdf_threaded)
        self.filemenu.add_command(label="Exit", command=self.master.destroy)

        # Keyboard bindings
        self.master.bind("<Control-o>", lambda event: self.open_file())
        self.master.bind("=", lambda event: self.zoom_in())
        self.master.bind("+", lambda event: self.zoom_in())
        self.master.bind("-", lambda event: self.zoom_out())
        self.master.bind("<Prior>", lambda event: self.previous_page())
        self.master.bind("<Next>", lambda event: self.next_page())
        self.master.bind("<Up>", lambda event: self.previous_page())
        self.master.bind("<Down>", lambda event: self.next_page())

        # Configure grid for 3 columns:
        # Column 0: Left (collapsible) toolbar
        # Column 1: Canvas for PDF display
        # Column 2: Right toolbar (navigation/zoom)
        self.master.columnconfigure(0, weight=0)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=0)
        self.master.rowconfigure(0, weight=1)

        # ---------------------------------------------------------
        # Left Toolbar Frame (Collapsible "Tools" bar)
        # ---------------------------------------------------------
        self.left_toolbar_frame = ttk.Frame(self.master, width=30)
        self.left_toolbar_frame.grid(row=0, column=0, sticky="ns")
        self.left_toolbar_frame.grid_propagate(False)
        self.left_toolbar_expanded = False

        # Toggle button always visible
        self.toolbar_toggle_button = ttk.Button(self.left_toolbar_frame, text="Tools", command=self.toggle_left_toolbar)
        self.toolbar_toggle_button.grid(row=0, column=0, padx=5, pady=5)

        # ---------------------------------------------------------
        # Canvas Frame (PDF display area)
        # ---------------------------------------------------------
        self.canvas_frame = ttk.Frame(self.master)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew")
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)

        self.scrolly = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.scrollx = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        self.output = tk.Canvas(self.canvas_frame, bg='#ECE8F3',
                                xscrollcommand=self.scrollx.set,
                                yscrollcommand=self.scrolly.set)
        self.output.grid(row=0, column=0, sticky="nsew")
        self.scrolly.grid(row=0, column=1, sticky="ns")
        self.scrollx.grid(row=1, column=0, sticky="ew")
        self.scrolly.config(command=self.output.yview)
        self.scrollx.config(command=self.output.xview)
        self.output.bind("<MouseWheel>", self.on_mousewheel)

        # ---------------------------------------------------------
        # Right Toolbar Frame (Vertical toolbar for navigation, zoom, etc.)
        # ---------------------------------------------------------
        self.right_toolbar_frame = ttk.Frame(self.master, width=200)
        self.right_toolbar_frame.grid(row=0, column=2, sticky="ns")
        self.right_toolbar_frame.grid_propagate(False)

        self.uparrow_icon = PhotoImage(file=resource_path("resources/uparrow.png"))
        self.downarrow_icon = PhotoImage(file=resource_path("resources/downarrow.png"))
        self.zoomin_icon = PhotoImage(file=resource_path("resources/zoomin.png"))
        self.zoomout_icon = PhotoImage(file=resource_path("resources/zoomout.png"))
        self.uparrow = self.uparrow_icon.subsample(3, 3)
        self.downarrow = self.downarrow_icon.subsample(3, 3)
        self.zoomin_img = self.zoomin_icon.subsample(20, 20)
        self.zoomout_img = self.zoomout_icon.subsample(20, 20)

        self.upbutton = ttk.Button(self.right_toolbar_frame, image=self.uparrow, command=self.previous_page)
        self.upbutton.grid(row=0, column=0, pady=4, padx=5)

        self.downbutton = ttk.Button(self.right_toolbar_frame, image=self.downarrow, command=self.next_page)
        self.downbutton.grid(row=1, column=0, pady=4, padx=5)

        self.page_label = ttk.Label(self.right_toolbar_frame, text='Page No.')
        self.page_label.grid(row=2, column=0, pady=(20, 4), padx=5)

        self.jump_button = ttk.Button(self.right_toolbar_frame, text='Jump', command=self.jump_to_page)
        self.jump_button.grid(row=3, column=0, pady=4, padx=5)

        self.jump_var = tk.StringVar()
        self.jump_entry = ttk.Entry(self.right_toolbar_frame, textvariable=self.jump_var)
        self.jump_entry.grid(row=4, column=0, pady=4, padx=5)

        self.zoomin_button = ttk.Button(self.right_toolbar_frame, image=self.zoomin_img, command=self.zoom_in)
        self.zoomin_button.grid(row=5, column=0, pady=(20, 4), padx=5)

        self.zoomout_button = ttk.Button(self.right_toolbar_frame, image=self.zoomout_img, command=self.zoom_out)
        self.zoomout_button.grid(row=6, column=0, pady=4, padx=5)

        self.miner = None

    # ------------------------------
    # Toggle Left Toolbar Expansion
    # ------------------------------
    def toggle_left_toolbar(self):
        if not self.left_toolbar_expanded:
            self.left_toolbar_expanded = True
            self.left_toolbar_frame.config(width=200)
            # Add tool label and buttons below the toggle button
            self.tools_label = ttk.Label(self.left_toolbar_frame, text="Tools Bar", anchor="center")
            self.tools_label.grid(row=1, column=0, pady=10, padx=5)
            self.convert_to_word_button = ttk.Button(self.left_toolbar_frame, text="Convert to Word", command=self.convert_to_word_threaded)
            self.convert_to_word_button.grid(row=2, column=0, pady=5, padx=5)
            self.convert_to_pdf_button = ttk.Button(self.left_toolbar_frame, text="Convert to PDF", command=self.convert_to_pdf_threaded)
            self.convert_to_pdf_button.grid(row=3, column=0, pady=5, padx=5)
        else:
            self.left_toolbar_expanded = False
            self.left_toolbar_frame.config(width=30)
            # Remove all widgets except the toggle button
            for widget in self.left_toolbar_frame.winfo_children():
                if widget != self.toolbar_toggle_button:
                    widget.destroy()

    # ------------------------------
    # File Operations & PDF Display
    # ------------------------------
    def open_file(self):
        filepath = fd.askopenfilename(title='Select a PDF file', initialdir=os.getcwd(), filetypes=(('PDF', '*.pdf'),))
        if filepath:
            self.path = filepath
            filename = os.path.basename(self.path)
            self.miner = PDFMiner(self.path)
            data, numPages = self.miner.get_metadata()
            self.current_page = 0
            if numPages:
                self.name = data.get('title', filename[:-4])
                self.author = data.get('author', None)
                self.numPages = numPages
                self.fileisopen = True
                self.display_page()
                self.master.title(self.name)

    def display_page(self):
        if self.fileisopen and 0 <= self.current_page < self.numPages:
            self.output.delete("all")
            self.img_file = self.miner.get_page(self.current_page, zoom_factor=self.zoom_factor)
            self.master.update_idletasks()
            canvas_width = self.output.winfo_width()
            canvas_height = self.output.winfo_height()
            img_width = self.img_file.width()
            img_height = self.img_file.height()
            x_pos = (canvas_width - img_width) // 2
            y_pos = (canvas_height - img_height) // 2
            self.output.create_image(x_pos, y_pos, anchor='nw', image=self.img_file)
            self.page_label['text'] = f"{self.current_page + 1} of {self.numPages}"
            region = self.output.bbox("all")
            self.output.configure(scrollregion=region)

    def on_mousewheel(self, event):
        speed = -2 if event.delta > 0 else 2
        self.output.yview_scroll(speed, "units")

    def next_page(self, event=None):
        if self.fileisopen and self.current_page < self.numPages - 1:
            self.current_page += 1
            self.display_page()

    def previous_page(self, event=None):
        if self.fileisopen and self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def jump_to_page(self):
        try:
            page_number = int(self.jump_var.get()) - 1
            if 0 <= page_number < self.numPages:
                self.current_page = page_number
                self.display_page()
        except ValueError:
            pass

    def zoom_in(self):
        self.zoom_factor *= 1.1
        self.display_page()

    def zoom_out(self):
        self.zoom_factor /= 1.1
        self.display_page()

    # ------------------------------
    # Conversion Operations (Threaded)
    # ------------------------------
    def convert_to_word_threaded(self):
        def convert_and_show_message():
            try:
                pdf_path = fd.askopenfilename(title='Select a PDF file', initialdir=os.getcwd(), filetypes=(('PDF', '*.pdf'),))
                if pdf_path:
                    word_output_path = fd.asksaveasfilename(defaultextension=".docx", filetypes=[("Word files", "*.docx")])
                    if word_output_path:
                        cv = Converter(pdf_path)
                        cv.convert(word_output_path, start=0, end=None)
                        cv.close()
                        messagebox.showinfo("Success", "Conversion to Word completed successfully.")
                        self.clear_entry_fields()
                    else:
                        messagebox.showinfo("Info", "Word conversion cancelled.")
                else:
                    messagebox.showerror("Error", "Please select a PDF file for conversion.")
            except Exception as e:
                messagebox.showerror("Error", f"Error during Word conversion: {e}")
        threading.Thread(target=convert_and_show_message).start()

    def clear_entry_fields(self):
        # Additional clearing logic if needed
        pass

    def convert_to_pdf_threaded(self):
        def convert_to_pdf_and_show_message():
            try:
                docx_path = fd.askopenfilename(title='Select a DOCX file', initialdir=os.getcwd(), filetypes=(('Word files', '*.docx'),))
                if docx_path:
                    pdf_output_path = fd.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
                    if pdf_output_path:
                        convert(docx_path, pdf_output_path)
                        messagebox.showinfo("Success", "Conversion to PDF completed successfully.")
                    else:
                        messagebox.showinfo("Info", "PDF conversion cancelled.")
                else:
                    messagebox.showerror("Error", "Please select a DOCX file for conversion.")
            except Exception as e:
                messagebox.showerror("Error", f"Error during PDF conversion: {e}")
        threading.Thread(target=convert_to_pdf_and_show_message).start()

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    root = tk.Tk()
    app = PDFViewer(root)
    root.mainloop()
