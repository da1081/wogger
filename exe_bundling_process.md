# Wogger - EXE Compilation Guide

This guide outlines the steps to generate a single `.exe` that includes all dependencies and resource files.

## Prerequisites

- Python 3.7 or higher
- Familiarity with command-line usage
- Basic knowledge of creating virtual environments
- Administrative privileges on the system

---

## 1. Create a Virtual Environment
```bash
python -m venv venv
```
Activate the venv:
- Windows (CMD):
```bash
venv\Scripts\activate
```
- Windows (PowerShell):
```bash
.\venv\Scripts\activate
```
- macOS/Linux:
```bash	
source venv/bin/activate
```

---

## 2. Install Dependencies
```bash
pip install pyinstaller
pip install -r requirements.txt
```

---

## 3. Build the Executable
```bash
python -m PyInstaller --onefile --noconsole --icon=src/resources/wogger.ico --add-data "src/resources/*;resources" --clean main.py --name wogger
```

### Explanation:
- `--onefile`: Generates a single executable file.
- `--noconsole`: Hides the console window when the executable is run.
- `--icon`: Sets the icon for the executable.
- `--add-data`: Includes the resource files in the executable.
- `--clean`: Deletes the temporary files created during the compilation process.
- `main.py`: The entry point of the application.
- `--name wogger`: Sets the name of the executable.

The packaged `wogger.exe` will appear in the `dist` folder.

---

## 4. (Optional) Deactivate the Venv
```bash
deactivate
```

The executable includes all required resources and dependencies in one file making it a standalone portable wogger distribution.
