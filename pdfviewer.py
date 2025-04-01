import tkinter as tk
from tkinter import ttk, filedialog as fd, messagebox, PhotoImage, simpledialog
from pdf2docx import Converter
import threading
import os
import sys
import math
import fitz
from docx2pdf import convert
import tempfile
import pikepdf

# ------------------------------------------------------
# Resource Path Helper (for PyInstaller and dev)
# ------------------------------------------------------
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# ------------------------------------------------------
# Build Permissions Helper
# ------------------------------------------------------
def build_permissions(allow_view, allow_print, allow_copy, allow_modify):
    """Build a pikepdf.Permissions object based on checkbox values."""
    from pikepdf import Permissions, Permission
    perms = Permissions()
    if allow_print:
        perms.enable(Permission.printing)
    if allow_copy:
        perms.enable(Permission.copying)
    if allow_modify:
        perms.enable(Permission.modify_contents)
    return perms

def build_default_permissions():
    """Return a default pikepdf.Permissions object (all allowed)."""
    from pikepdf import Permissions
    return Permissions()

# ------------------------------------------------------
# PikePDF Helpers
# ------------------------------------------------------
def unlock_pdf_with_pikepdf(input_path, password):
    """
    Use pikepdf to open a password-protected PDF and save an unlocked copy
    to a temporary file. Returns the path to the unlocked PDF.
    """
    try:
        pdf = pikepdf.open(input_path, password=password)
        temp_dir = tempfile.gettempdir()
        unlocked_path = os.path.join(temp_dir, "unlocked_temp.pdf")
        pdf.save(unlocked_path)
        pdf.close()
        return unlocked_path
    except pikepdf._methods.PasswordError:
        raise ValueError("Incorrect password")

def lock_pdf_with_pikepdf(input_path, output_path, owner_pwd, user_pwd, permissions):
    """
    Use pikepdf to lock a PDF with the given owner password, user password,
    and a pikepdf.Permissions object.
    """
    pdf = pikepdf.open(input_path)
    pdf.save(
        output_path,
        encryption=pikepdf.Encryption(
            owner=owner_pwd,
            user=user_pwd,
            R=6,
            permissions=permissions
        )
    )
    pdf.close()

# ------------------------------------------------------
# PDFMiner Class (using PyMuPDF)
# ------------------------------------------------------
class PDFMiner:
    def __init__(self, filepath, password=""):
        self.filepath = filepath
        if password:
            self.pdf = fitz.open(self.filepath, password=password)
        else:
            self.pdf = fitz.open(self.filepath)
        self.first_page = self.pdf.load_page(0)
        self.width, self.height = self.first_page.rect.width, self.first_page.rect.height
        zoomdict = {800: 0.8, 700: 0.6, 600: 1.0, 500: 1.0}
        width_key = int(math.floor(self.width / 100.0) * 100)
        self.zoom = zoomdict.get(width_key, 1.0)
        
    def get_metadata(self):
        metadata = self.pdf.metadata
        num_pages = self.pdf.page_count
        return metadata, num_pages
    
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
        return page.get_text('text')

# ------------------------------------------------------
# PDFViewer Class
# ------------------------------------------------------
class PDFViewer:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Viewer")
        self.master.geometry("1400x800")
        self.master.resizable(width=True, height=True)
        self.master.iconbitmap(resource_path("resources/pdf_file_icon.ico"))

        # Menu
        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open File", command=self.open_file, accelerator="[Ctrl+O]")
        self.filemenu.add_command(label="Convert to Word", command=self.convert_to_word_threaded)
        self.filemenu.add_command(label="Convert to PDF", command=self.convert_to_pdf_threaded)
        self.filemenu.add_command(label="Exit", command=self.master.destroy)
        self.master.bind("<Control-o>", lambda event: self.open_file())
        self.master.bind("=", lambda event: self.zoom_in())
        self.master.bind("+", lambda event: self.zoom_in())
        self.master.bind("-", lambda event: self.zoom_out())
        self.master.bind("<Prior>", lambda event: self.previous_page())
        self.master.bind("<Next>", lambda event: self.next_page())
        self.master.bind("<Up>", lambda event: self.previous_page())
        self.master.bind("<Down>", lambda event: self.next_page())

        # Layout: 3 columns: left (tools), center (tabs), right (navigation)
        self.master.columnconfigure(0, weight=0, minsize=150)
        self.master.columnconfigure(1, weight=1)
        self.master.columnconfigure(2, weight=0, minsize=200)
        self.master.rowconfigure(0, weight=1)

        # -----------------------------
        # Left Toolbar (Fixed)
        # -----------------------------
        self.left_toolbar_frame = ttk.Frame(self.master, width=150)
        self.left_toolbar_frame.grid(row=0, column=0, sticky="ns")
        self.left_toolbar_frame.grid_propagate(False)

        self.tools_label = ttk.Label(self.left_toolbar_frame, text="Tools Bar", anchor="center")
        self.tools_label.grid(row=0, column=0, pady=5, padx=5)

        self.convert_to_word_button = ttk.Button(self.left_toolbar_frame, text="Convert to Word", command=self.convert_to_word_threaded)
        self.convert_to_word_button.grid(row=1, column=0, pady=5, padx=5)

        self.convert_to_pdf_button = ttk.Button(self.left_toolbar_frame, text="Convert to PDF", command=self.convert_to_pdf_threaded)
        self.convert_to_pdf_button.grid(row=2, column=0, pady=5, padx=5)

        self.lock_button = ttk.Button(self.left_toolbar_frame, text="Lock PDF", command=self.lock_pdf)
        self.lock_button.grid(row=3, column=0, pady=5, padx=5)

        self.remove_password_button = ttk.Button(self.left_toolbar_frame, text="Remove Password", command=self.remove_password)
        self.remove_password_button.grid(row=4, column=0, pady=5, padx=5)

        # -----------------------------
        # Center Frame: Top Bar + Notebook
        # -----------------------------
        self.center_frame = ttk.Frame(self.master)
        self.center_frame.grid(row=0, column=1, sticky="nsew")
        self.center_frame.columnconfigure(0, weight=1)
        self.center_frame.rowconfigure(1, weight=1)

        top_bar = ttk.Frame(self.center_frame)
        top_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.files_label = ttk.Label(top_bar, text="Open PDF(s):")
        self.files_label.pack(side="left")
        self.manage_perm_button = ttk.Button(top_bar, text="Manage Permissions", command=self.manage_permissions)
        self.manage_perm_button.pack(side="right", padx=5)

        self.notebook = ttk.Notebook(self.center_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        self.tabs = {}

        # -----------------------------
        # Right Toolbar (Navigation, Zoom, Print)
        # -----------------------------
        self.right_toolbar_frame = ttk.Frame(self.master, width=200)
        self.right_toolbar_frame.grid(row=0, column=2, sticky="ns")
        self.right_toolbar_frame.grid_propagate(False)

        # Right toolbar layout:
        # Row 0: Print button (small)
        # Row 1: Horizontal frame for Zoom In/Out buttons
        # Row 2: Jump label ("Page:")
        # Row 3: Jump entry
        # Row 4: "Go" button
        # Row 5: Spacer (weight=1)
        # Row 6: Up arrow
        # Row 7: Down arrow
        # Row 8: Page label
        self.right_toolbar_frame.rowconfigure(5, weight=1)

        self.printer_icon = PhotoImage(file=resource_path("resources/printer.png"))
        self.printer_img = self.printer_icon.subsample(8, 8)
        self.print_button = ttk.Button(self.right_toolbar_frame, image=self.printer_img, command=self.print_pdf)
        self.print_button.grid(row=0, column=0, padx=5, pady=5)

        zoom_frame = ttk.Frame(self.right_toolbar_frame)
        zoom_frame.grid(row=1, column=0, padx=5, pady=2)
        self.zoomin_icon = PhotoImage(file=resource_path("resources/zoomin.png"))
        self.zoomout_icon = PhotoImage(file=resource_path("resources/zoomout.png"))
        self.zoomin_img = self.zoomin_icon.subsample(20, 20)
        self.zoomout_img = self.zoomout_icon.subsample(20, 20)
        self.zoomin_button = ttk.Button(zoom_frame, image=self.zoomin_img, command=self.zoom_in)
        self.zoomin_button.pack(side="left", padx=2)
        self.zoomout_button = ttk.Button(zoom_frame, image=self.zoomout_img, command=self.zoom_out)
        self.zoomout_button.pack(side="left", padx=2)

        self.jump_label = ttk.Label(self.right_toolbar_frame, text="Page:")
        self.jump_label.grid(row=2, column=0, pady=(5,2))
        self.jump_var = tk.StringVar()
        self.jump_entry = ttk.Entry(self.right_toolbar_frame, textvariable=self.jump_var, width=5)
        self.jump_entry.grid(row=3, column=0, pady=2)
        self.jump_button = ttk.Button(self.right_toolbar_frame, text="Go", command=self.jump_to_page)
        self.jump_button.grid(row=4, column=0, pady=2)

        self.right_toolbar_frame.rowconfigure(5, weight=1)

        self.uparrow_icon = PhotoImage(file=resource_path("resources/uparrow.png"))
        self.uparrow = self.uparrow_icon.subsample(3, 3)
        self.up_button = ttk.Button(self.right_toolbar_frame, image=self.uparrow, command=self.previous_page)
        self.up_button.grid(row=6, column=0, padx=5, pady=2)

        self.downarrow_icon = PhotoImage(file=resource_path("resources/downarrow.png"))
        self.downarrow = self.downarrow_icon.subsample(3, 3)
        self.down_button = ttk.Button(self.right_toolbar_frame, image=self.downarrow, command=self.next_page)
        self.down_button.grid(row=7, column=0, padx=5, pady=2)

        self.page_label = ttk.Label(self.right_toolbar_frame, text="Page No.")
        self.page_label.grid(row=8, column=0, pady=2)

    # -----------------------------
    # Retrieve Active Tab Data
    # -----------------------------
    def get_active_tab(self):
        current_tab_id = self.notebook.select()
        for frame, data in self.tabs.items():
            if str(frame) == current_tab_id:
                return data
        return None

    # -----------------------------
    # Display the Current Page in the Active Tab
    # -----------------------------
    def display_page(self, tab_data):
        canvas = tab_data["canvas"]
        miner = tab_data["miner"]
        current_page = tab_data["current_page"]
        zoom_factor = tab_data["zoom_factor"]

        canvas.delete("all")
        img = miner.get_page(current_page, zoom_factor=zoom_factor)
        tab_data["img"] = img  # Keep reference
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        x_pos = max((canvas_width - img.width()) // 2, 0)
        y_pos = max((canvas_height - img.height()) // 2, 0)
        canvas.create_image(x_pos, y_pos, anchor="nw", image=img)
        canvas.configure(scrollregion=canvas.bbox("all"))
        self.page_label.config(text=f"{current_page+1} of {tab_data['numPages']}")

    # -----------------------------
    # Mouse Wheel Scrolling for Canvas
    # -----------------------------
    def on_mousewheel_canvas(self, event, canvas):
        direction = -1 if event.delta > 0 else 1
        canvas.yview_scroll(direction, "units")

    # -----------------------------
    # Open PDF File and Create New Tab
    # -----------------------------
    def open_file(self):
        filepath = fd.askopenfilename(
            title="Select a PDF file",
            initialdir=os.getcwd(),
            filetypes=[("PDF", "*.pdf")]
        )
        if not filepath:
            return
        filename = os.path.basename(filepath)
        try:
            miner = PDFMiner(filepath)
        except Exception as e:
            if "encrypted" in str(e).lower():
                pwd = simpledialog.askstring("Password Required", "Enter PDF password:", show="*")
                if pwd:
                    try:
                        unlocked_path = unlock_pdf_with_pikepdf(filepath, pwd)
                        filepath = unlocked_path
                        miner = PDFMiner(filepath)
                    except Exception:
                        messagebox.showerror("Error", "Unable to open PDF. Incorrect password?")
                        return
                else:
                    messagebox.showerror("Error", "Password is required to open this PDF.")
                    return
            else:
                messagebox.showerror("Error", f"Failed to open PDF: {e}")
                return

        data, num_pages = miner.get_metadata()

        tab_frame = ttk.Frame(self.notebook)
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(0, weight=1)

        canvas = tk.Canvas(tab_frame, bg="#ECE8F3")
        canvas.grid(row=0, column=0, sticky="nsew")

        scrolly = tk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrolly.grid(row=0, column=1, sticky="ns")

        scrollx = tk.Scrollbar(tab_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollx.grid(row=1, column=0, sticky="ew")

        canvas.config(xscrollcommand=scrollx.set, yscrollcommand=scrolly.set)
        canvas.bind("<MouseWheel>", lambda e, c=canvas: self.on_mousewheel_canvas(e, c))

        self.notebook.add(tab_frame, text=filename)
        self.notebook.select(tab_frame)

        tab_data = {
            "miner": miner,
            "path": filepath,
            "canvas": canvas,
            "scrolly": scrolly,
            "scrollx": scrollx,
            "current_page": 0,
            "numPages": num_pages,
            "zoom_factor": 1.0
        }
        self.tabs[tab_frame] = tab_data
        self.display_page(tab_data)

    # -----------------------------
    # Navigation / Zoom Functions
    # -----------------------------
    def next_page(self, event=None):
        tab_data = self.get_active_tab()
        if tab_data and tab_data["current_page"] < tab_data["numPages"] - 1:
            tab_data["current_page"] += 1
            self.display_page(tab_data)

    def previous_page(self, event=None):
        tab_data = self.get_active_tab()
        if tab_data and tab_data["current_page"] > 0:
            tab_data["current_page"] -= 1
            self.display_page(tab_data)

    def jump_to_page(self):
        tab_data = self.get_active_tab()
        if not tab_data:
            return
        try:
            page_number = int(self.jump_var.get()) - 1
            if 0 <= page_number < tab_data["numPages"]:
                tab_data["current_page"] = page_number
                self.display_page(tab_data)
        except ValueError:
            pass

    def zoom_in(self):
        tab_data = self.get_active_tab()
        if tab_data:
            tab_data["zoom_factor"] *= 1.1
            self.display_page(tab_data)

    def zoom_out(self):
        tab_data = self.get_active_tab()
        if tab_data:
            tab_data["zoom_factor"] /= 1.1
            self.display_page(tab_data)

    # -----------------------------
    # Manage Permissions
    # -----------------------------
    def manage_permissions(self):
        tab_data = self.get_active_tab()
        if not tab_data:
            messagebox.showerror("Error", "No active PDF file.")
            return

        perm_dialog = tk.Toplevel(self.master)
        perm_dialog.title("Manage Permissions")
        perm_dialog.grab_set()

        allow_viewing = tk.BooleanVar(value=True)
        allow_printing = tk.BooleanVar(value=True)
        allow_copying = tk.BooleanVar(value=True)
        allow_modifying = tk.BooleanVar(value=False)

        tk.Label(perm_dialog, text="Set Permissions:").grid(row=0, column=0, columnspan=2, pady=5)
        tk.Checkbutton(perm_dialog, text="Allow Viewing (no password to open)", variable=allow_viewing)\
            .grid(row=1, column=0, sticky="w", padx=10)
        tk.Checkbutton(perm_dialog, text="Allow Printing", variable=allow_printing)\
            .grid(row=2, column=0, sticky="w", padx=10)
        tk.Checkbutton(perm_dialog, text="Allow Copying", variable=allow_copying)\
            .grid(row=3, column=0, sticky="w", padx=10)
        tk.Checkbutton(perm_dialog, text="Allow Modifying", variable=allow_modifying)\
            .grid(row=4, column=0, sticky="w", padx=10)

        def save_permissions():
            perms = build_permissions(allow_viewing.get(), allow_printing.get(), allow_copying.get(), allow_modifying.get())
            new_pwd = simpledialog.askstring("Set Password", "Enter an owner password:", show="*")
            if not new_pwd:
                messagebox.showerror("Error", "Password is required.")
                return
            user_pwd = "" if allow_viewing.get() else new_pwd
            output_path = fd.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if not output_path:
                return
            try:
                lock_pdf_with_pikepdf(
                    input_path=tab_data["path"],
                    output_path=output_path,
                    owner_pwd=new_pwd,
                    user_pwd=user_pwd,
                    permissions=perms
                )
                messagebox.showinfo("Success", "Permissions updated successfully!")
                perm_dialog.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to update permissions: {ex}")

        ttk.Button(perm_dialog, text="Save", command=save_permissions)\
            .grid(row=5, column=0, columnspan=2, pady=10)

    # -----------------------------
    # Print Functionality
    # -----------------------------
    def print_pdf(self):
        tab_data = self.get_active_tab()
        if not tab_data:
            messagebox.showerror("Error", "No active PDF file.")
            return

        print_dialog = tk.Toplevel(self.master)
        print_dialog.title("Print Options")
        print_dialog.grab_set()

        tk.Label(print_dialog, text="Pages (e.g., 1-3 or 'all'):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        pages_entry = ttk.Entry(print_dialog)
        pages_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(print_dialog, text="Copies:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        copies_entry = ttk.Entry(print_dialog, width=5)
        copies_entry.insert(0, "1")
        copies_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        def perform_print():
            pages = pages_entry.get().strip().lower()
            copies = copies_entry.get().strip()
            try:
                copies = int(copies)
            except ValueError:
                messagebox.showerror("Error", "Invalid number of copies.")
                return

            if os.name == "nt":
                try:
                    for _ in range(copies):
                        os.startfile(tab_data["path"], "print")
                    messagebox.showinfo("Print", "Print command issued. Check your printer queue.")
                except Exception as e:
                    messagebox.showerror("Error", f"Print failed: {e}")
            else:
                messagebox.showinfo("Print", "Printing is only implemented on Windows in this example.")
            print_dialog.destroy()

        ttk.Button(print_dialog, text="Print", command=perform_print)\
            .grid(row=2, column=0, columnspan=2, pady=10)

    # -----------------------------
    # Remove Password Functionality
    # -----------------------------
    def remove_password(self):
        tab_data = self.get_active_tab()
        if not tab_data:
            messagebox.showerror("Error", "No active PDF file.")
            return
        output_path = fd.asksaveasfilename(
            title="Save PDF without password",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not output_path:
            return
        try:
            pdf = pikepdf.open(tab_data["path"])
            pdf.save(output_path)
            pdf.close()
            messagebox.showinfo("Success", "Password removed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove password: {e}")

    # -----------------------------
    # Lock PDF Functionality (added)
    # -----------------------------
    def lock_pdf(self):
        tab_data = self.get_active_tab()
        if not tab_data:
            messagebox.showerror("Error", "No active PDF file.")
            return
        # Prompt for a password to lock the PDF
        pwd = simpledialog.askstring("Set Password", "Enter a password to lock the PDF:", show="*")
        if not pwd:
            messagebox.showerror("Error", "Password is required to lock the PDF.")
            return
        output_path = fd.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not output_path:
            return
        try:
            perms = build_default_permissions()  # Allow everything by default
            lock_pdf_with_pikepdf(tab_data["path"], output_path, owner_pwd=pwd, user_pwd=pwd, permissions=perms)
            messagebox.showinfo("Success", "PDF locked successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to lock PDF: {e}")

    # -----------------------------
    # Convert to Word (Threaded)
    # -----------------------------
    def convert_to_word_threaded(self):
        def convert_and_show_message():
            try:
                pdf_path = fd.askopenfilename(
                    title="Select a PDF file",
                    initialdir=os.getcwd(),
                    filetypes=[("PDF", "*.pdf")]
                )
                if pdf_path:
                    word_output_path = fd.asksaveasfilename(
                        defaultextension=".docx",
                        filetypes=[("Word files", "*.docx")]
                    )
                    if word_output_path:
                        cv = Converter(pdf_path)
                        cv.convert(word_output_path, start=0, end=None)
                        cv.close()
                        messagebox.showinfo("Success", "Conversion to Word completed successfully.")
                    else:
                        messagebox.showinfo("Info", "Word conversion cancelled.")
                else:
                    messagebox.showerror("Error", "Please select a PDF file for conversion.")
            except Exception as e:
                messagebox.showerror("Error", f"Error during Word conversion: {e}")
        threading.Thread(target=convert_and_show_message).start()

    # -----------------------------
    # Convert to PDF (Threaded)
    # -----------------------------
    def convert_to_pdf_threaded(self):
        def convert_to_pdf_and_show_message():
            try:
                docx_path = fd.askopenfilename(
                    title="Select a DOCX file",
                    initialdir=os.getcwd(),
                    filetypes=[("Word files", "*.docx")]
                )
                if docx_path:
                    pdf_output_path = fd.asksaveasfilename(
                        defaultextension=".pdf",
                        filetypes=[("PDF files", "*.pdf")]
                    )
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

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewer(root)
    root.mainloop()
