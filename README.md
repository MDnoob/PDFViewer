# 📄 PDF Viewer - An Open Source Alternative

**Version 1.2**

An open-source, lightweight, and feature-rich PDF Viewer built in **Python**.
Developed as a free alternative to Adobe Acrobat Reader, it supports PDF viewing, conversions, printing, and enhanced security — all wrapped in a clean, customizable interface.

---

## 🚀 Overview

Hi, I'm **Molin Dave** 👋

Tired of Adobe's high pricing for its reader, I developed this open-source PDF Viewer as a **free and user-friendly alternative**.
Built with:

* **Tkinter** → GUI
* **PyMuPDF** → PDF rendering
* **pikepdf & pdf2docx/docx2pdf** → File security & conversion

This app does more than just viewing PDFs:
✔ Multi-tab support
✔ PDF ↔ Word conversion
✔ Basic printing
✔ Secure file locking/unlocking
✔ Dark mode & keyboard shortcuts

---

## ✨ Features

### 📑 PDF Viewing

* **Multi-tab Interface** → Open multiple PDFs with right-click context menu
* **Smooth Navigation** → Mouse wheel, arrow keys, Page Up/Down
* **Zoom Controls** → Buttons or keyboard (`+` / `-`)
* **Jump to Page** → Input field with "Go" button

### 🔄 File Conversion

* **PDF ➝ Word** → Convert with threading for smooth performance
* **Word ➝ PDF** → Convert DOCX files back into PDFs

### 🔐 File Security & Permissions

* **Lock PDF** → Add password (single dialog with confirmation)
* **Unlock PDF** → Remove password protection
* **Enhanced Password Handling** → Hybrid PyMuPDF + pikepdf support
* **Automatic Prompts** → Enter passwords when opening encrypted files
* **Future Support** → Advanced permissions (coming soon)

### 🖨 Printing

* **Basic Print Functionality** → Integrated with Windows OS print command

### 🎨 Theme & Customization

* **Dark Mode** → Toggle via View menu for comfortable reading
* **Dynamic UI** → Proper canvas updates when switching themes

### ⌨ Keyboard Shortcuts

| Shortcut                 | Action               |
| ------------------------ | -------------------- |
| `Ctrl + O`               | Open PDF             |
| `+` / `=`                | Zoom in              |
| `-`                      | Zoom out             |
| Arrow Keys / PgUp / PgDn | Navigate pages       |
| Mouse Wheel              | Scroll through pages |

---

## 🛠 Installation

### Option 1: Run from Source

```bash
git clone https://github.com/your-username/pdf-viewer.git
cd pdf-viewer
pip install -r requirements.txt
python main.py
```

### Option 2: Download Executable

* Get the latest release from the [Releases Page](#)
* No Python installation required

### Building from Source

```bash
pyinstaller --onefile --windowed \
  --icon="resources/pdf_file_icon.ico" \
  --add-data "resources;resources" \
  --name="PDF_Viewer" main.py
```

---

## 📦 Requirements

* Python **3.8+**
* [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
* [pikepdf](https://pikepdf.readthedocs.io/)
* [pdf2docx](https://github.com/dothinking/pdf2docx)
* [docx2pdf](https://github.com/AlJohri/docx2pdf)
* Tkinter (included in standard Python distributions)

---

## 🗂 Project Structure

```
pdf-viewer/
│── main.py              # Application entry point
│── pdf_viewer.py        # Main viewer class
│── pdf_miner.py         # PDF processing & rendering
│── pdf_security.py      # Security & encryption
│── pdf_converter.py     # Document conversion
│── ui_components.py     # UI layout & theme handling
│── dialogs.py           # Custom dialogs
│── resources/           # Icons & assets
```

---

## 🆕 What’s New in v1.2

* 🔐 **Enhanced Security** → Improved locking/unlocking with better error handling
* 🧩 **Modular Architecture** → Cleaner, maintainable code
* 🔑 **Improved Password Dialog** → Single window with confirmation
* ⚡ **Better Compatibility** → Support for more PDF encryption methods
* 🖌 **Cleaner UI** → Renamed buttons & improved feedback
* 🛠 **Build Support** → PyInstaller config included

---

## 🤝 Contributing

Contributions, issues, and feature requests are always welcome!

* Fork the repo
* Create your feature branch (`git checkout -b feature/AmazingFeature`)
* Commit your changes (`git commit -m 'Add AmazingFeature'`)
* Push to the branch (`git push origin feature/AmazingFeature`)
* Open a Pull Request

---

## 📬 Contact

**Developed by:** Molin Dave
If you have suggestions, feedback, or questions → Feel free to open an issue or reach out!

---
