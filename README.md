**PDF Viewer - An Open Source Alternative**
**Version 1.2**

**Overview**
Hello, I'm Molin Dave. Tired of Adobe's high pricing for its reader, I developed this open-source PDF Viewer as a free alternative. This application is built in Python using Tkinter for the graphical interface, PyMuPDF for rendering PDFs, and several other open-source libraries for conversion and PDF manipulation.

This app not only allows you to view PDF files but also provides advanced features like multi-tab viewing, conversion to and from Word documents, basic printing capabilities, and enhanced file security management with improved password protection workflows.

**Features**
PDF Viewing
Multi-tab Interface:
Open multiple PDF files simultaneously in separate tabs with right-click context menu support.

Scrolling and Navigation:
Use mouse wheel scrolling, page navigation buttons, and keyboard shortcuts to navigate through your PDF.

Zoom In/Out:
Easily adjust the zoom level using on-screen buttons or keyboard shortcuts (+ and -).

Jump to Page:
Direct page navigation with a dedicated page input field and "Go" button.

File Conversion
PDF to Word Conversion:
Convert your PDF files into editable Word documents with threading support for better performance.

Word to PDF Conversion:
Convert DOCX files back into PDFs.

File Security & Permissions
Lock PDF:
Secure your PDF by setting a password with an improved single-dialog interface that includes both password and confirmation fields for better user experience.

Unlock PDF:
Remove password protection from your PDF files (formerly "Remove Password" - renamed for clarity).

**Enhanced Password Handling:
**
Hybrid PyMuPDF and pikepdf library support for better compatibility with various PDF encryption methods

Automatic password prompts for encrypted files

Support for complex encryption schemes

Manage Permissions:
Note: Advanced permissions management is temporarily simplified due to library compatibility issues and will be enhanced in future releases.

Printing
Basic Print Functionality:
Send your PDF file to the printer using Windows OS print command integration.

Theme and Customization
Dark Theme Option:
Toggle between light and dark themes from the View menu. The dark theme provides a comfortable viewing experience in low-light environments with proper canvas background updates.

Keyboard Shortcuts
Ctrl+O: Open PDF file

+/=: Zoom in

-: Zoom out

Arrow Keys / Page Up/Down: Navigate between pages

Mouse Wheel: Scroll through pages

**Installation**
Option 1: Run from Source
Clone this repository

**Install required dependencies:
**
bash
pip install -r requirements.txt
Run the application:

bash
python main.py
Option 2: Download Executable
Download the latest release executable from the repository releases page - no Python installation required.

**Building from Source
**To create a standalone executable:

bash
pyinstaller --onefile --windowed --icon="resources/pdf_file_icon.ico" --add-data "resources;resources" --name="PDF_Viewer" main.py
**Requirements**
Python 3.8+

PyMuPDF (fitz)

pikepdf

pdf2docx

docx2pdf

tkinter (usually included with Python)

**Project Structure
**The application now features a modular architecture with organized code files:

main.py - Application entry point

pdf_viewer.py - Main viewer class

pdf_miner.py - PDF processing and rendering

pdf_security.py - Security and encryption features

pdf_converter.py - Document conversion functionality

ui_components.py - UI layout and theme management

dialogs.py - Custom dialog boxes

**What's New in Version 1.2
**Enhanced Security Features: Improved PDF locking/unlocking with better error handling

Modular Architecture: Restructured codebase for better maintainability

Improved Password Dialog: Single modal window with password confirmation

Better Compatibility: Enhanced support for various PDF encryption methods

Cleaner UI: Renamed buttons and improved user feedback

Build Support: Included PyInstaller configuration for executable creation

**Developed by Molin Dave.
**Contributions, issues, and feature requests are welcome!
If you have any questions or suggestions, feel free to reach out.
