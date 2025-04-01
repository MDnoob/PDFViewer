# PDF Viewer - An Open Source Alternative

**Version 1.1**

## Overview

Hello, I'm **Molin Dave**. Tired of Adobe's high pricing for its reader, I developed this open-source PDF Viewer as a free alternative. This application is built in Python using Tkinter for the graphical interface, PyMuPDF for rendering PDFs, and several other open-source libraries for conversion and PDF manipulation. 

This app not only allows you to view PDF files but also provides advanced features like multi-tab viewing, conversion to and from Word documents, basic printing capabilities, and file security management (locking/unlocking, setting permissions, and removing passwords).

## Features

### PDF Viewing
- **Multi-tab Interface:**  
  Open multiple PDF files simultaneously in separate tabs.
- **Scrolling and Navigation:**  
  Use mouse wheel scrolling, page navigation buttons, and keyboard shortcuts to navigate through your PDF.
- **Zoom In/Out:**  
  Easily adjust the zoom level using on-screen buttons or the keyboard shortcuts (Ctrl + '+' and Ctrl + '-').

### File Conversion
- **PDF to Word Conversion:**  
  Convert your PDF files into editable Word documents.
- **Word to PDF Conversion:**  
  Convert DOCX files back into PDFs.

### File Security & Permissions
- **Lock PDF:**  
  Secure your PDF by setting a password to restrict access.
- **Remove Password:**  
  Remove password protection from your PDF for easier viewing.
- **Manage Permissions:**  
  Customize file permissions with options to allow or restrict:
  - **Viewing:** If disabled, a password is required to open the PDF.
  - **Printing:** Allow or restrict printing.
  - **Copying:** Allow or restrict copying of text.
  - **Modifying:** Allow or restrict modifications.
  
  *Note: Permissions are enforced via PDF encryption. If “Allow Viewing” is checked, no password is required to open the file; if unchecked, the same password set for other restrictions is required to view the file.*

### Printing
- **Basic Print Functionality:**  
  Send your PDF file to the printer with a simple print dialog that lets you choose the number of copies. (Note: Printing is implemented for Windows systems using the OS print command.)

### Theme and Customization
- **Dark Theme Option:**  
  Under the **Options** menu, you can switch to a Dark Theme. This adjusts the UI colors to a black and grey combination (including buttons and backgrounds) for a more comfortable viewing experience in low light environments.

### Keyboard Shortcuts
- **Ctrl+O:** Open PDF file.
- **Ctrl+P:** Print the active PDF.
- **Ctrl++ / Ctrl+-:** Zoom in and out.
- **Arrow Keys / Page Up/Down:** Navigate between pages.

## Installation
- Just download the latest release from the repository.

### Developed by Molin Dave.
- Contributions, issues, and feature requests are welcome!
- If you have any questions or suggestions, feel free to reach out.
