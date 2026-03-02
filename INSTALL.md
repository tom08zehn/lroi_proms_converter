# Installation Guide — LROI PROMs Converter v1.4.7

Complete step-by-step installation instructions for Windows, macOS, and Linux.

---

## For Windows Users (Step-by-Step)

### 1. Check Python Version

Open Command Prompt (`Win+R` → type `cmd` → Enter) and run:
```cmd
python --version
```

You should see `Python 3.11.x` or higher (3.13.x works fine).

**If Python is not installed:**
- Download from https://www.python.org/downloads/
- ⚠️ **IMPORTANT:** Check **"Add Python to PATH"** during installation
- Restart Command Prompt after installation

---

### 2. Extract the Downloaded Files

Extract the downloaded ZIP to a folder, for example:
```
C:\Users\YourName\lroi_converter\
```

**Verify the folder structure:**
```
lroi_converter/
├── main.py
├── converter.py
├── gui.py
├── logger.py
├── validate_xml.py
├── config.toml               ← Main configuration file
├── requirements.txt          ← This file is important!
├── build_exe.py
├── VERSION.txt
├── README.md
├── INSTALL.md
├── demo/
│   ├── demo.config.toml      ← Demo configuration
│   ├── README.md
│   ├── patient_demographics.xlsx
│   ├── oks_export_site_a.xlsx
│   ├── oks_export_site_b.xlsx
│   ├── ohs_export_batch1.xlsx
│   └── ohs_export_batch2.xlsx
└── example/
    ├── OKS_demo_account.xlsx
    ├── HOOS_demo_account.xlsx
    ├── KOOS_demo_account.xlsx
    ├── Demographics_demo_account.xlsx
    ├── Dictionary_LROI_PROMs_v9_2-20240205.xlsx
    └── XSD_LROI_PROMs_v9_2-20210608.xsd
```

⚠️ **IMPORTANT:**
- All `.xlsx` files must be inside `demo/` and `example/` subfolders
- `demo.config.toml` must be inside `demo/` folder
- `config.toml` must be in root folder

---

### 3. Create Virtual Environment

Open Command Prompt in the `lroi_converter` folder:

**Option A: Using File Explorer**
1. Open the `lroi_converter` folder in File Explorer
2. Type `cmd` in the address bar and press Enter
3. A Command Prompt opens in that folder

**Option B: Using cd command**
```cmd
cd C:\Users\YourName\lroi_converter
```

Then create the virtual environment:
```cmd
python -m venv venv
```

This creates a `venv` folder inside `lroi_converter`.

---

### 4. Activate Virtual Environment

**Windows Command Prompt (PRIMARY METHOD):**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**If PowerShell gives an error** about execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

**After activation**, your prompt should look like:
```
(venv) C:\Users\YourName\lroi_converter>
```

The `(venv)` prefix means the virtual environment is active.

---

### 5. Install Dependencies

With the virtual environment active, run:
```cmd
pip install -r requirements.txt
```

This installs:
- `openpyxl` (Excel file handling)
- `lxml` (XML validation)

**Expected output:**
```
Collecting openpyxl>=3.1.0
...
Successfully installed openpyxl-3.1.x lxml-5.x.x
```

---

### 6. Verify Installation

Run this test command:
```cmd
python -c "import openpyxl, lxml; print('✓ Dependencies installed successfully')"
```

If you see `✓ Dependencies installed successfully`, everything is ready!

---

### 7. Run the Demo

With the virtual environment still active:
```cmd
python main.py --cfg demo/demo.config.toml --input demo/ --lut demo/patient_demographics.xlsx --log 1
```

**Expected output:**
- Console shows conversion progress
- Creates `2026-02-27-143542_demo_output.xml` (converted XML file)
- Creates `2026-02-27-143542_demo.log` (text log)
- Creates `2026-02-27-143542_demo.xlsx` (Excel log — double-click to open)

**Note:** All files have the same timestamp (YYYY-MM-DD-HHMMSS) to group related outputs.

---

## For macOS/Linux Users

### 1. Check Python Version

```bash
python3 --version
```

Should show Python 3.11 or higher.

**If not installed:**
- **macOS:** Install from https://www.python.org or use Homebrew: `brew install python@3.11`
- **Linux:** `sudo apt install python3.11 python3.11-venv` (Ubuntu/Debian)

---

### 2. Extract Files

```bash
unzip lroi_converter.zip
cd lroi_converter
```

---

### 3. Create Virtual Environment

```bash
python3 -m venv venv
```

---

### 4. Activate Virtual Environment

```bash
source venv/bin/activate
```

Your prompt should show `(venv)` prefix.

---

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 6. Verify Installation

```bash
python -c "import openpyxl, lxml; print('✓ Ready to use')"
```

---

### 7. Run the Demo

```bash
python main.py --cfg demo/demo.config.toml \
  --input demo/ \
  --lut demo/patient_demographics.xlsx \
  --log 1
```

---

## Troubleshooting

### "python is not recognized" (Windows)

**Problem:** Python is not in your system PATH.

**Solution:**
1. Uninstall Python
2. Reinstall from https://www.python.org/downloads/
3. ⚠️ **Check "Add Python to PATH"** during installation
4. Restart Command Prompt
5. Test: `python --version`

---

### "No module named 'openpyxl'"

**Problem:** Dependencies not installed or wrong Python environment.

**Solution:**
```cmd
# Make sure virtual environment is active (should see "(venv)" in prompt)
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

---

### "Config file not found"

**Problem:** `config.toml` or `demo/demo.config.toml` not in expected location.

**Solution:**
```cmd
# Check files exist
dir config.toml
dir demo\demo.config.toml

# If missing, ensure you extracted all files correctly
# config.toml should be in root directory
# demo.config.toml should be inside demo/ folder
```

---

### Virtual Environment Won't Activate (PowerShell)

**Problem:** Execution policy prevents script execution.

**Solution:**
```powershell
# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\Activate.ps1
```

---

### "No module named 'tkinter'" (Linux)

**Problem:** Tkinter not installed (needed for GUI).

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Then test
python -c "import tkinter; print('✓ Tkinter available')"
```

---

### Permission Denied (macOS/Linux)

**Problem:** Script files not executable.

**Solution:**
```bash
chmod +x main.py
python main.py --gui
```

---

## Next Steps

### 1. Edit Configuration

Copy the main config and customize for your hospital:
```cmd
copy config.toml myhospital.config.toml
notepad myhospital.config.toml
```

**Essential settings to change:**
```toml
[defaults]
hospital = 1234  # ← Change to your LROI hospital code
```

**Map your Excel columns:**
```toml
[PROM.OKS]
detection_column = "Your column name here"

[PROM.OKS.UPNNUM]
column = "Your patient ID column"
```

See [README.md](README.md#configuration) for complete configuration guide.

---

### 2. Test with Your Data

Start with a small test file:
```cmd
python main.py --cfg myhospital.config.toml ^
  --input your_test_file.xlsx ^
  --loglevel DEBUG ^
  --output test_output.xml
```

Check the DEBUG log to verify column mappings:
```
DEBUG  Detected PROM type: OKS
DEBUG  Extracted UPNNUM: "P12345" from column "Patient ID"
DEBUG  Converted GENDER: "Male" → "0"
```

---

### 3. Build a .exe File (Optional)

Create a standalone Windows executable for users without Python:

**Prerequisites:**
```cmd
pip install pyinstaller
```

**Build:**
```cmd
python build_exe.py
```

**Output:** `dist/lroi_converter/lroi_converter.exe`

**Custom Icon:**
1. Create or obtain `your_icon.ico` (256x256 recommended)
2. Place in project root folder
3. Edit `build_exe.py` at line 67:
   ```python
   ICON_FILE: Path | None = PROJECT_DIR / "your_icon.ico"
   ```
4. Run: `python build_exe.py`

**Test:**
```cmd
cd dist\lroi_converter
lroi_converter.exe --gui
```

**Distribute:**
- Copy entire `dist/lroi_converter/` folder
- Users need `lroi_converter.exe` and `config.toml` only
- No Python installation required on user machines

---

### 4. Validate Output

Always validate your XML output against the XSD schema:

```cmd
python validate_xml.py output.xml XSD_LROI_PROMs_v9_2-20210608.xsd
```

**Expected output:**
```
✓ output.xml is VALID
```

**If validation fails:**
- Check date formats (should be YYYY-MM-DD)
- Verify all required elements present
- Review regex conversions in config
- Check DEBUG log for conversion details

---

## Quick Reference

### Activate Environment

**Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Run Conversion

**CLI:**
```cmd
python main.py --input data.xlsx --lut demographics.xlsx --output output.xml
```

**GUI:**
```cmd
python main.py --gui
```

### Deactivate Environment

```cmd
deactivate
```

### Update Dependencies

```cmd
pip install --upgrade -r requirements.txt
```

---

## Common Usage Patterns

### Daily Production Use

```cmd
# Activate environment
venv\Scripts\activate.bat

# Run conversion
python main.py --cfg config.toml ^
  --input C:\exports\ ^
  --lut C:\demographics.xlsx ^
  --loglevel INFO ^
  --log 1

# Check Excel log for errors/warnings
start 2026-02-27-143542_lroi_converter.xlsx

# Validate XML
python validate_xml.py 2026-02-27-143542_output.xml XSD_LROI_PROMs_v9_2-20210608.xsd

# Upload to LROI Databroker
# (manual step via web interface)
```

### Testing New Configuration

```cmd
# Use DEBUG to see all conversions
python main.py --cfg test.config.toml ^
  --input small_test.xlsx ^
  --loglevel DEBUG ^
  --log test.log

# Review log
notepad test.log
```

### GUI for Non-Technical Users

```cmd
# Just launch GUI
python main.py --gui

# Or build .exe and share
python build_exe.py
cd dist
# ZIP the lroi_converter folder and share
```

---

## System Requirements

**Minimum:**
- Python 3.11+
- 100 MB disk space
- 512 MB RAM
- Windows 10 / macOS 10.15 / Ubuntu 20.04

**Recommended:**
- Python 3.13
- 500 MB disk space (for virtual environment)
- 1 GB RAM
- Windows 11 / macOS 13+ / Ubuntu 22.04+

**For .exe building:**
- PyInstaller: `pip install pyinstaller`
- 200 MB additional disk space

---

## File Size Estimates

- Virtual environment: ~100 MB
- Dependencies installed: ~20 MB
- Built .exe: ~30 MB (standalone, includes Python runtime)
- Demo files: ~500 KB
- Example files: ~2 MB

---

## Getting Help

**Installation issues?**
1. Check this guide first
2. Verify Python version: `python --version`
3. Verify PATH: `where python` (Windows) or `which python` (macOS/Linux)
4. Try reinstalling Python with "Add to PATH" checked

**Configuration issues?**
See [README.md](README.md#configuration) for complete configuration guide.

**Conversion errors?**
Use `--loglevel DEBUG` to see detailed processing information.

**Still stuck?**
- Check [README.md#troubleshooting](README.md#troubleshooting)
- Review demo files for working examples
- Test with demo first to verify installation

---

## Version Information

**Current Version:** v1.4.7 (2026-02-27)

**What's New in v1.4.7:**
- Renamed `--xls` to `--input` (breaking change)
- Complete documentation rewrite
- Updated folder structure
- Windows-first installation instructions
- Custom icon support for .exe documented

See [VERSION.txt](VERSION.txt) for complete changelog.

---

**Last Updated:** v1.4.7 (2026-02-27)
