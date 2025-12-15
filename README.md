Contact Manager

A simple, user-friendly contact manager desktop application built with Python and Tkinter. Save, edit, search, export and manage contacts — all stored locally in contacts.json (created next to the script). Lightweight and perfect for learning GUI development or as a small personal tool.

Features

Add, edit and delete contacts (soft-delete stored in JSON).

Search by name, phone or across all fields (live filtering).

Export contacts to a timestamped text file.

Contact details view with date added / last modified.

Input validation for phone numbers and email addresses.

Works out-of-the-box with standard Python (no third-party packages required).

Project structure ContactManager/ ├─ app.py # Main app

contacts.json is created automatically in the same folder as contact_manager.py when you first run the app.
Requirements

Python 3.8+ (recommended)

Tkinter (usually included with official Python installers)

No additional pip packages required

If Tkinter is missing on your system:

On Debian/Ubuntu: sudo apt install python3-tk

On Windows/macOS: install Python from python.org which includes Tcl/Tk.

Quick start — run locally

Clone or download this repository and cd into the project folder.

(Optional but recommended) Create and activate a virtual environment:

macOS / Linux:

python3 -m venv .venv source .venv/bin/activate

Windows (PowerShell):

python -m venv .venv ..venv\Scripts\Activate.ps1

Run the app:

python contact_manager.py

The GUI window will open and contacts.json will be created next to contact_manager.py.

PyCharm setup (brief)

Open PyCharm → Open → choose project folder.

Configure interpreter: File → Settings → Project → Python Interpreter → create/select a virtualenv (recommended: .venv).

Add a Run configuration:

Add → Python → Script path: contact_manager.py

Working directory: project root

Run or Debug using the Run/Debug buttons.

(See the in-app comments or repository README for more detailed PyCharm tips if needed.)

Usage

Fill Name and Phone (required). Email and Address are optional.

Press Add Contact or hit Enter in an input field to add.

Select a row and click View Details, Edit Contact or Delete Contact.

Use the search box and radio options to filter contacts.

Click Export Contacts to save a human-readable .txt export.

Click Clear All to soft-delete all contacts (confirmation required).

Note: Deleting sets a deleted flag in the JSON so data can be preserved if you want to implement recovery later. If you prefer to remove the file, delete contacts.json (or remove entries manually).

Data file location

contacts.json is created and read from the same directory as contact_manager.py. This ensures the app behaves the same regardless of PyCharm's working directory or how you run the script.

Troubleshooting

Window does not appear: confirm interpreter is Python 3.x and Tkinter is installed.

ImportError: No module named tkinter: Install Tk (see Requirements above) or use an installer which bundles Tk.

contacts.json errors: If the JSON file becomes corrupted, delete contacts.json and restart the app — a fresh file will be created.

Packaging (optional)

To create a standalone executable (Windows/macOS/Linux) you can use PyInstaller:

pip install pyinstaller pyinstaller --onefile --windowed contact_manager.py

The executable will be in dist/. Packaging GUI apps may require additional tweaks for icons or resources.

.gitignore (recommended)

Add a .gitignore to avoid committing local state and virtual environments:

pycache/ *.pyc .Python .venv/ venv/ contacts.json .idea/ dist/ build/ *.spec

TODO / Ideas

Convert storage to SQLite for better scalability.

Add import (CSV / vCard) and export (CSV / vCard) options.

Add contact groups / tags.

Add undo / recovery for deletes.

Add unit tests for validation functions.

License

This project is released under the MIT License — feel free to use and modify it.

Developer: Abhishuman Roy (abhishuman18) & Arushi Sengupta (arushi23git)

Contributing

Contributions, suggestions and bug reports are welcome. Please open an issue or create a pull request describing your change.
