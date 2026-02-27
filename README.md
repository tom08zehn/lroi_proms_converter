# LROI PROMs Converter

A Python application to convert **Patient Reported Outcome Measures (PROMs)** from Excel exports into LROI-compliant XML files for upload to the [LROI Databroker platform](https://www.lroi.nl/) (Dutch national orthopaedic registry).

---

## Quick Start — Running the Demo

The easiest way to see the converter in action is to run the included demo:

```bash
# 1. Set up virtual environment and install dependencies
python -m venv venv
source venv/bin/activate          # macOS/Linux
# OR: venv\Scripts\activate.bat   # Windows CMD
# OR: .\venv\Scripts\Activate.ps1  # Windows PowerShell

pip install -r requirements.txt

# 2. Run the demo
python main.py --cfg demo.config.toml --xls demo/ --lut demo/patient_demographics.xlsx --log 1
```

This converts 15 synthetic questionnaires (8 OKS + 7 OHS) from 5 demo Excel files:
- `demo/oks_export_site_a.xlsx` — 5 OKS rows
- `demo/oks_export_site_b.xlsx` — 3 OKS rows  
- `demo/ohs_export_batch1.xlsx` — 4 OHS rows
- `demo/ohs_export_batch2.xlsx` — 3 OHS rows

**Output:**
- XML file: `demo_output.xml` (XSD-validated ✓)
- Text log: `2026-02-19_main_demo.log`
- Excel log: `2026-02-19_main_demo.xlsx` (double-click to open in Excel)

The demo uses **different column names** than the real config to demonstrate the flexible join column system. See `demo/README.md` for details.

---

## Table of Contents

- [What does this do?](#what-does-this-do)
- [Supported PROMs](#supported-proms)
- [Requirements](#requirements)
- [Installation](#installation)
  - [For beginners: setting up Python](#for-beginners-setting-up-python)
  - [Installing dependencies](#installing-dependencies)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command-line (headless)](#command-line-headless)
  - [Graphical interface (GUI)](#graphical-interface-gui)
  - [Examples](#examples)
- [Building a Windows executable](#building-a-windows-executable)
- [How it works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [For developers](#for-developers)

---

## What does this do?

Healthcare organizations in the Netherlands collect PROMs data (patient questionnaires about outcomes) and must submit it to the LROI. This tool:

1. **Reads** your PROMs data exported from your hospital's system as Excel (`.xlsx` / `.xls`) files
2. **Looks up** missing patient demographics (gender, date of birth, laterality) from a separate lookup table (if needed)
3. **Converts** everything into a single XML file that validates against the official LROI XSD schema (`XSD_LROI_PROMs_v9_2-20210608.xsd`)
4. **Outputs** an XML file ready to upload via the LROI Databroker web interface

**Key features:**
- ✅ Auto-detects PROM type (OKS, OHS, KOOS, HOOS) from column headers
- ✅ Processes multiple Excel files at once (or entire folders)
- ✅ Validates output against XSD schema
- ✅ Both CLI and GUI interfaces
- ✅ Detailed logging for audit trails
- ✅ Can be packaged as a single-file Windows `.exe` (no Python installation needed for end-users)

---

## Supported PROMs

| PROM | Full name | Joint | Status |
|------|-----------|-------|--------|
| **OKS** | Oxford Knee Score | Knee | ✅ **Fully tested** |
| **OHS** | Oxford Hip Score | Hip | ⚠️ Skeleton (needs column mapping validation) |
| **KOOS** | Knee Injury and Osteoarthritis Outcome Score | Knee | ⚠️ **Partial** (item mapping uncertain, [see notes](#koos--hoos-important-notes)) |
| **HOOS** | Hip disability and Osteoarthritis Outcome Score | Hip | ⚠️ **Partial** (item mapping uncertain, [see notes](#koos--hoos-important-notes)) |

### KOOS / HOOS Important Notes

The demo KOOS and HOOS exports use shortened questionnaire variants (KOOS-PS 7 items, HOOS-PS 6 items) that **do not map 1:1** to the standard LROI dictionary items. **Your organization must validate the column-to-XML-field mappings** in `config.toml` before production use.

**To validate:**
1. Compare your export's English question text to the Dutch questions in `Dictionary_LROI_PROMs_v9_2-20240205.xlsx`
2. Update the `koos_item_columns` / `hoos_item_columns` lists in `config.toml` to match your system's exact column names
3. Run a test conversion and verify the XML output against a known-good sample

---

## Requirements

- **Python 3.11 or newer** (uses `tomllib` from the standard library)
  - For Python 3.9 / 3.10: add `tomli` to dependencies in `pyproject.toml`
- **Operating system:** Windows, macOS, or Linux
- **For building .exe:** Windows machine (or Windows VM / GitHub Actions)

---

## Installation

**Quick Setup (3 steps):**

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
source venv/bin/activate          # macOS/Linux
# OR: venv\Scripts\activate.bat   # Windows CMD
# OR: .\venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt
```

**That's it!** Verify with:
```bash
python -c "import openpyxl, lxml; print('✓ Ready to convert!')"
```

📖 **For detailed step-by-step instructions** (Python installation, troubleshooting, Windows-specific guidance), see **[INSTALL.md](INSTALL.md)**.

---


## Configuration

All settings live in **`config.toml`**. You **must** edit this file before first use.

### Essential settings

```toml
[defaults]
# Your hospital's LROI institution code (look it up in the 'Ziekenhuislijst' 
# tab of the LROI PROMs dictionary Excel file)
hospital = 1234   # ← CHANGE THIS to your actual code

# Output file naming pattern (uses datetime placeholders)
xml_file_template = "{yyyy}-{mm}-{dd}_{appname}_output.xml"
```

### PROM definitions

Each `[PROM.<key>]` section defines one questionnaire type. Example (OKS is fully configured):

```toml
[PROM.OKS]
name = "Oxford Knee Score"
detection_column = "Oxford Knee Score"   # Column that triggers auto-detection
col_admission_id = "Admission ID"
col_patient_id   = "Patient ID"
# ... (see file for complete mappings)
```

⚠️ **KOOS and HOOS mappings are incomplete** — see [notes above](#koos--hoos-important-notes). You must validate these before production use.

### Lookup table (LUT) settings

If patient demographics (gender, date of birth, laterality) are missing from your PROMs export, provide a separate Excel file with this data:

```toml
[lut]
join_column = "Admission ID"   # Column used to JOIN PROMs ↔ demographics
col_gender       = "Gender"
col_date_of_birth = "Date of Birth"
col_laterality   = "Laterality"

# Data validation mode (NEW in v1.1)
# Controls behavior when XLS and LUT have conflicting values for the same field
validation_mode = "strict"   # Options: "strict" | "warn" | "silent"

[lut.gender_map]
"Male" = 0
"Female" = 1

[lut.laterality_map]
"Right" = 1
"Left" = 2
```

**Validation modes:**

| Mode | Behavior when XLS ≠ LUT |
|------|-------------------------|
| `strict` | **ERROR** — Skip the row and log the conflict. Use this to enforce data quality. |
| `warn` | **WARNING** — Log the conflict but proceed with the LUT value (LUT is authoritative). |
| `silent` | No check. LUT value silently overrides XLS value (old behavior before v1.1). |

**Recommendation:** Always use `"strict"` in production. This catches data problems early:
- Stale XLS exports that haven't been refreshed
- Database synchronization issues
- Duplicate patient records with different values
- Manual data entry errors

The LUT is treated as the **authoritative source** for demographics. If it's missing mandatory fields (gender, date of birth, laterality), that's also flagged as an error in strict mode.

---

## Usage

### Command-line (headless)

Run the converter without opening a GUI:

```bash
python main.py --xls path/to/OKS_export.xlsx \
               --lut path/to/Demographics.xlsx \
               --output output.xml \
               --hospital 1234
```

**Arguments:**
- `--xls FILE_OR_FOLDER` — One or more Excel files, or a folder containing `.xlsx`/`.xls` files. Can be repeated or space-separated. Folders are walked recursively.
- `--lut FILE` — Optional demographics lookup table (Excel file)
- `--output FILE` — Output XML path (defaults to timestamped file per `config.toml`)
- `--hospital N` — Hospital LROI code (overrides `config.toml`)
- `--log FILE|1` — Log file path, or `1` for auto-named log (from `config.toml` template). When enabled, also creates an Excel log file (see below).
- `--config FILE` — Path to `config.toml` (default: searches next to `main.py`)

**Log files:**

When you use `--log 1`, the app creates **two log files**:

1. **Text log** (`.log`) — Human-readable, for developers/IT staff
   ```
   2026-02-18 14:30:15  INFO      Converted OKS row: admission_id=249227  patient_id=440587  phase=Pre-Op
   2026-02-18 14:30:15  ERROR     VALIDATION FAILED: Laterality mismatch for Admission ID='256123'
   ```

2. **Excel log** (`.xlsx`) — **Double-click to open in Excel**

**Why `.xlsx` instead of `.csv`?**

| Issue | CSV | XLSX |
|-------|-----|------|
| Opens in Excel | Sometimes (file association issues) | ✅ Always |
| Regional delimiters | `,` vs `;` confusion | ✅ No issue (binary format) |
| Date formatting | Text that Excel might misinterpret | ✅ Proper date column |
| Encoding | UTF-8 BOM helps but not foolproof | ✅ No encoding issues |
| Auto-filter | User must enable manually | ✅ Enabled by default |
| Color coding | Not possible | ✅ Red ERROR, yellow WARNING |
| Formatting | Plain text only | ✅ Bold headers, frozen panes |

**The Excel log includes:**
   - Auto-filter enabled on all columns
   - Frozen header row
   - Bold headers with gray background
   - **ERROR rows highlighted in red**
   - **WARNING rows highlighted in yellow**
   - Admission ID extracted into dedicated column
   - Proper date/time column (sortable)

The Excel log is designed for **healthcare professionals** to:
- **Double-click the `.xlsx` file** → opens directly in Excel (no delimiter issues)
- **Click filter dropdowns** in header row → show only ERROR/WARNING rows
- **Sort by any column** → group by Level, Admission ID, or Timestamp
- **Color-coded rows** → red for errors, yellow for warnings, instant visual feedback
- **Share with colleagues** — proper Excel file, no encoding/delimiter confusion

To **disable Excel logging**, edit `config.toml`:
```toml
xlsx_log_file_template = ""   # Empty string disables Excel logs
```

### Graphical interface (GUI)

Launch the GUI:

```bash
python main.py --gui
```

Or with prepopulated fields:

```bash
python main.py --gui \
               --xls path/to/files_or_folder \
               --lut path/to/Demographics.xlsx \
               --hospital 1234
```

Add `--run` to start the conversion immediately without waiting for user interaction:

```bash
python main.py --gui --run --xls data/ --lut Demographics.xlsx
```

**GUI features:**
- **Config file** — browse to load a different `config.toml` file
- **Files…** button — select multiple Excel files (multi-select, additive)
- **Folder…** button — select a folder; all `.xlsx`/`.xls` files inside are included
- **Text log file:**
  - **"Use default"** checkbox — when checked, uses template from config (like `--log 1`)
  - Shows resolved filename (e.g., `2026-02-19_main.log`)
  - When unchecked, browse to choose custom path
- **Excel log file:**
  - **"Use default"** checkbox — when checked, uses template from config
  - Shows resolved filename (e.g., `2026-02-19_main.xlsx`)
  - When unchecked, browse to choose custom path
  - Automatically disabled if config has empty `xlsx_log_file_template`
- **Log output** — real-time conversion progress with color-coded messages
- **Clear Log** — reset the log view between runs

💡 **Tip:** The GUI remembers your settings during the session. Change the config file to switch between different hospital configurations.

---

### Examples

**Process a single file:**
```bash
python main.py --xls OKS_demo_account.xlsx --output oks_output.xml
```

**Process multiple files:**
```bash
python main.py --xls file1.xlsx file2.xlsx file3.xlsx --output combined.xml
```

**Process all Excel files in a folder:**
```bash
python main.py --xls data/ --output combined.xml
```

**Batch conversion: multiple files of the same PROM type:**
```bash
# Convert 3 OKS files from different sites into one XML
python main.py \
  --xls site_a_oks.xlsx site_b_oks.xlsx site_c_oks.xlsx \
  --lut demographics.xlsx \
  --output oks_combined.xml
```

**Batch conversion: mixed PROM types (OKS + OHS):**
```bash
# Convert OKS and OHS files together into one XML
# The converter auto-detects each file's PROM type
python main.py \
  --xls oks_file1.xlsx oks_file2.xlsx ohs_file1.xlsx ohs_file2.xlsx \
  --lut demographics.xlsx \
  --output all_proms.xml \
  --hospital 1234
```

**Batch conversion: entire folder with mixed PROM types:**
```bash
# Processes all .xlsx files in exports/ folder
# Auto-detects OKS, OHS, KOOS, HOOS and combines into one XML
python main.py \
  --xls exports/ \
  --lut demographics.xlsx \
  --output monthly_upload.xml \
  --log 1
```

**💡 Note:** All files must use the **same LUT** (lookup table). If different sites use different LUT files, run separate conversions.

**With demographics lookup and logging:**
```bash
python main.py \
  --xls exports/ \
  --lut Demographics.xlsx \
  --output output.xml \
  --log conversion.log \
  --hospital 1234
```

**Auto-named log file:**
```bash
python main.py --xls exports/ --log 1
# Creates: 2026-02-17_main.log (text)
#      and 2026-02-17_main.xlsx (Excel)
```

**💡 Tip for Excel users:** After running with `--log 1`, find the `.xlsx` file in the same directory and **double-click it**. It opens directly in Excel with:
- **Auto-filter enabled** — click dropdown arrows in header row
- **Color-coded rows** — red for ERROR, yellow for WARNING
- **Frozen header** — header stays visible when scrolling
- **Sortable columns** — click any header to sort

No delimiter confusion, no encoding issues, no manual import steps — just double-click and analyze.

---

## Building a Windows executable

If you want to distribute the app to colleagues who don't have Python installed:

### Prerequisites

- Windows machine (or Windows VM)
- Python 3.11+ installed
- Dependencies installed with build tools:
  ```bash
  pip install ".[build]"
  ```

### Build process

```bash
python build_exe.py
```

This creates:
```
dist/
  lroi_converter/
    lroi_converter.exe   ← Single-file executable
    config.toml          ← Configuration (must be edited before distributing)
```

**To distribute:**
1. Edit `config.toml` to set the correct `hospital =` number for your institution
2. Zip the entire `dist/lroi_converter/` folder
3. Send to end-users with instructions: "Unzip and double-click `lroi_converter.exe`"

**Important:** The `.exe` and `config.toml` **must be in the same folder**. Each hospital should set their own LROI code in `config.toml` before use.

---

## How it works

### Architecture

The application is split into focused modules:

```
lroi_converter/
├── main.py         # CLI argument parsing, entry point
├── converter.py    # Core XLS → XML conversion engine
├── lut.py          # Lookup table loader and query helper
├── logger.py       # Logging setup (console + file)
├── gui.py          # Tkinter GUI (completely isolated)
├── config.toml     # All configuration and PROM definitions
├── pyproject.toml  # Dependencies and project metadata
└── build_exe.py    # PyInstaller build script
```

This design allows:
- **Headless CLI** to work on servers without a display (GUI is only imported when `--gui` is passed)
- **Easy testing** of conversion logic without UI concerns
- **Simple extension** — add a new PROM by creating a `[PROM.XYZ]` section in `config.toml` and a builder function in `converter.py`

### Conversion flow

```mermaid
graph TD
    A[Excel file(s)] --> B{Auto-detect PROM type}
    B -->|OKS| C[OKS builder]
    B -->|KOOS| D[KOOS builder]
    B -->|HOOS| E[HOOS builder]
    B -->|OHS| F[OHS builder]
    C --> G{LUT needed?}
    D --> G
    E --> G
    F --> G
    G -->|Yes| H[Look up demographics]
    G -->|No| I[Skip LUT]
    H --> J[Build XML elements]
    I --> J
    J --> K[Combine into single XML]
    K --> L[Validate against XSD]
    L --> M[Write output.xml]
```

1. **Auto-detection:** The first row (header) is scanned for a `detection_column` (e.g., "Oxford Knee Score"). This identifies the PROM type.
2. **Row processing:** Each data row is converted to a `<questionaire>` XML element.
3. **LUT lookup (optional):** If demographics are missing, they're fetched from the lookup table via a JOIN on `Admission ID`.
4. **XML assembly:** All questionnaire elements are wrapped in `<LROIPROM><questionaires>...</questionaires></LROIPROM>`.
5. **Validation:** The output is validated against `XSD_LROI_PROMs_v9_2-20210608.xsd` (if `lxml` is installed).
6. **Output:** A single XML file ready for upload.

---

## Validating XML Output

After conversion, you can validate the XML against the LROI XSD schema using the standalone validator:

```bash
python validate_xml.py output.xml XSD_LROI_PROMs_v9_2-20210608.xsd
```

**Output if valid:**
```
✓ output.xml is VALID
```

**Output if validation fails:**
```
✗ output.xml validation FAILED:

  Line 45, Column 0:
    Element 'GENDER': This element is not expected...
  
Total errors: 1
```

**Use cases:**
- Verify XML before uploading to LROI website
- Debugging conversion issues
- CI/CD pipeline validation
- Batch validation of multiple XML files

**Note:** The LROI upload website also validates files before submission.

---

## Troubleshooting

### Installation Issues

#### "Cannot import 'setuptools.backends.legacy'"

If you get this error when running `pip install .`, use `requirements.txt` instead:
```bash
pip install -r requirements.txt
```

This is a simpler installation method that doesn't require package building.

#### "ModuleNotFoundError: No module named 'openpyxl'"

You forgot to install dependencies. Make sure your virtual environment is activated, then run:
```bash
pip install -r requirements.txt
```

#### Demo folder structure after download

After extracting the downloaded files, your folder structure should look like:
```
lroi_converter/
├── main.py
├── converter.py
├── config.toml
├── demo.config.toml
├── requirements.txt
├── demo/
│   ├── README.md
│   ├── patient_demographics.xlsx
│   ├── oks_export_site_a.xlsx
│   ├── oks_export_site_b.xlsx
│   ├── ohs_export_batch1.xlsx
│   └── ohs_export_batch2.xlsx
└── ...
```

If the `.xlsx` files are in the wrong location, manually move them into the `demo/` folder.

### Runtime Issues

### "ERROR: Config file not found"

The app looks for `config.toml` next to `main.py` by default. Either:
- Run from the `lroi_converter/` directory: `cd lroi_converter && python main.py ...`
- Or specify the path: `python main.py --config /full/path/to/config.toml ...`

### "Cannot detect PROM type"

The Excel file's header row doesn't contain the `detection_column` defined in `config.toml`. Check:
1. Does your export match the expected format?
2. Is the column name spelled exactly as in the config (case-sensitive)?
3. For KOOS/HOOS: the `detection_column` is `"Interval Score"` — verify this column exists.

### "Row skipped: unknown phase 'X'"

The follow-up phase value (e.g., "Pre-Op", "3 Month") in your Excel doesn't match any key in the `[PROM.XXX.fupk_map]` section of `config.toml`. Add the missing value:
```toml
[PROM.OKS.fupk_map]
"6 weeks" = 3   # ← add your organization's custom phase names
```

### "XSD validation failed"

The generated XML doesn't conform to the LROI schema. Common causes:
- Required fields are empty (e.g., `SIDEPK`, `FUPK`)
- Value out of range (e.g., OKS item = 5, but valid range is 0-4)
- Wrong element order (the XSD is sequence-strict; elements must appear in schema order)

Check the console output for the specific validation error.

### "VALIDATION FAILED: Gender/laterality/DOB mismatch"

The same patient has different values in the XLS export vs the demographics LUT. For example:
- XLS says laterality="Left", but LUT says laterality="Right"
- XLS gender="Female", but LUT gender="Male"

**This is a data quality issue.** Check:
1. Are you using the correct, up-to-date LUT file?
2. Did the export system use the wrong patient ID?
3. Is there a duplicate patient record in your database?
4. Was the surgery laterality changed after the PROMs export?

**If the mismatch is expected** (e.g., during testing with old exports), change `validation_mode = "warn"` in `config.toml` to proceed with warnings instead of errors.

**Never use `validation_mode = "silent"`** in production — it masks data problems.

### GUI doesn't open on Linux

Tkinter isn't installed. On Ubuntu/Debian:
```bash
sudo apt install python3-tk
```

### "Permission denied" when running build_exe.py on Windows

PyInstaller needs write access to the project directory. Run your terminal as Administrator, or move the project folder out of `C:\Program Files`.

---

## For developers

### Project structure philosophy

**Separation of concerns:**
- `converter.py` is pure logic — no I/O, no GUI
- `gui.py` only imports when `--gui` is used (headless CLI doesn't load tkinter)
- `config.toml` is the single source of truth for all mappings

**Why not a single monolithic file?**
- Headless environments (servers, Docker) often don't have `tkinter` → importing GUI would crash
- Testing conversion logic doesn't require a UI
- Adding new PROMs is just config + one builder function, not editing a 1000-line file

### Adding a new PROM

1. **Add config section** in `config.toml`:
   ```toml
   [PROM.MYNEWPROM]
   name = "My New PROM"
   detection_column = "Unique Column Name"
   col_admission_id = "Admission ID"
   # ... define all column mappings
   ```

2. **Write builder function** in `converter.py`:
   ```python
   def _build_mynewprom_questionaire(...) -> Optional[ET.Element]:
       # Convert row dict to XML element
       q = ET.Element("questionaire")
       _sub(q, "DATUMINVUL", ...)
       # ... populate all required fields per XSD
       return q
   ```

3. **Register builder**:
   ```python
   _BUILDERS = {
       "OKS": _build_oks_questionaire,
       "MYNEWPROM": _build_mynewprom_questionaire,
   }
   ```

4. **Test** with sample data.

### Running tests (future)

A `tests/` directory is planned. When ready:
```bash
pip install ".[dev]"
pytest
```

### Code style

The project uses **Ruff** for linting and formatting (config in `pyproject.toml`):
```bash
pip install ".[dev]"
ruff check .
ruff format .
```

---

## Questions or issues?

- Check the `config.toml` comments carefully — most configuration questions are answered there
- Review the LROI PROMs dictionary (`Dictionary_LROI_PROMs_v9_2-20240205.xlsx`) to understand field mappings
- For KOOS/HOOS: verify your export format matches the demo files, or adjust the config accordingly

---

## Answer to your specific question

> Do they provide optional fields PIJNRUSTPK/PIJNACTPK?

**No.** Neither the KOOS nor HOOS demo exports contain `PIJNRUSTPK` (pain at rest) or `PIJNACTPK` (pain during activity) columns. These fields are optional per the XSD schema (`minOccurs="0"`), so they are left empty in the generated XML.

If your organization's export **does** include pain NRS scores, add them to `config.toml`:
```toml
[PROM.KOOS]
col_pain_rest = "Pain at Rest (0-10)"
col_pain_activity = "Pain During Activity (0-10)"
```
Then update `_build_koos_questionaire()` in `converter.py` to read these columns and populate `PIJNRUSTPK` / `PIJNACTPK`.

---

**Version:** 1.0.0  
**Last updated:** 2026-02-17  
**Maintained by:** Your organization  
**LROI:** [https://www.lroi.nl/](https://www.lroi.nl/)
