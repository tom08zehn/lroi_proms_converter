# Installation Guide — LROI PROMs Converter

## For Windows Users (Step-by-Step)

### 1. Check Python Version

Open Command Prompt (`Win+R` → type `cmd` → Enter) and run:
```cmd
python --version
```

You should see `Python 3.11.x` or higher (3.13.5 works fine).

If Python is not installed:
- Download from https://www.python.org/downloads/
- ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation

---

### 2. Extract the Downloaded Files

Extract the downloaded ZIP to a folder, for example:
```
C:\Users\YourName\lroi_converter\
```

**Verify the folder structure looks like this:**
```
lroi_converter/
├── main.py
├── converter.py
├── config.toml
├── demo.config.toml
├── requirements.txt          ← This file is important!
├── pyproject.toml
├── demo/
│   ├── README.md
│   ├── patient_demographics.xlsx
│   ├── oks_export_site_a.xlsx
│   ├── oks_export_site_b.xlsx
│   ├── ohs_export_batch1.xlsx
│   └── ohs_export_batch2.xlsx
└── (other files)
```

⚠️ **IMPORTANT: Check that all `.xlsx` files are inside the `demo/` subfolder!**

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

**Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**PowerShell:**
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
- `openpyxl` (for Excel file handling)
- `lxml` (for XML validation)

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
python main.py --cfg demo.config.toml --xls demo/ --lut demo/patient_demographics.xlsx --log 1
```

**Expected output:**
- Console shows conversion progress
- Creates `demo_output.xml` (the converted XML file)
- Creates `2026-02-XX_main_demo.log` (text log)
- Creates `2026-02-XX_main_demo.xlsx` (Excel log — double-click to open)

---

## Troubleshooting

### "python is not recognized"
- Python is not in your PATH
- Reinstall Python and check "Add Python to PATH"

### "Cannot import 'setuptools.backends.legacy'"
- You tried `pip install .` instead of `pip install -r requirements.txt`
- **Solution:** Use `requirements.txt` as shown in Step 5

### "ModuleNotFoundError: No module named 'openpyxl'"
- Virtual environment not activated, or dependencies not installed
- **Solution:** 
  1. Activate venv: `venv\Scripts\activate.bat`
  2. Install: `pip install -r requirements.txt`

### Demo files missing
- Check that all `.xlsx` files are in the `demo/` subfolder
- If not, manually move them there

### "Config file not found"
- Make sure you're running the command from the `lroi_converter` folder
- Use `cd` to navigate to the correct folder first

---

## Next Steps

After the demo works:

1. **Edit `config.toml`:**
   - Set your hospital's LROI code: `hospital = 1234`
   - Update column names to match your export system

2. **Test with real data:**
   ```cmd
   python main.py --xls your_data.xlsx --lut your_demographics.xlsx --log 1
   ```

3. **Build a .exe file (optional):**
   ```cmd
   pip install pyinstaller
   python build_exe.py
   ```
   This creates `dist/lroi_converter/lroi_converter.exe`

---

## Deactivating the Virtual Environment

When you're done working:
```cmd
deactivate
```

The `(venv)` prefix disappears from your prompt.

---

## Daily Usage

Every time you want to use the converter:

1. Open Command Prompt in the `lroi_converter` folder
2. Activate: `venv\Scripts\activate.bat`
3. Run: `python main.py ...`
4. Deactivate when done: `deactivate`
