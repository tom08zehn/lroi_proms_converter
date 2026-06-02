# LROI PROMs Converter

A Python application to convert **Patient Reported Outcome Measures (PROMs)** from Excel exports into LROI-compliant XML files for upload to the [LROI Databroker platform](https://www.lroi.nl/) (Dutch national orthopaedic registry).

**Version:** v1.5.0

---

## Quick Start

```bash
# 1. Set up Python environment
python -m venv venv
venv\Scripts\activate.bat         # Windows CMD
# OR: source venv/bin/activate    # macOS/Linux
# OR: .\venv\Scripts\Activate.ps1 # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the demo
python main.py --cfg demo/demo.config.toml \
  --input demo/ \
  --lut demo/patient_demographics.xlsx \
  --log 1
```

**Output:**
- `2026-02-27-143542_demo_output.xml` - XSD-validated XML
- `2026-02-27-143542_demo.log` - Text log
- `2026-02-27-143542_demo.xlsx` - Excel log (double-click to open)

All files share the same timestamp for easy grouping.

---

## Table of Contents

- [What This Does](#what-this-does)
- [Supported PROMs](#supported-proms)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Line (CLI)](#command-line-cli)
  - [Graphical Interface (GUI)](#graphical-interface-gui)
  - [Examples](#examples)
- [Building Windows Executable](#building-windows-executable)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)

---

## What This Does

Healthcare organizations in the Netherlands collect PROMs data (patient questionnaires) and submit it to LROI. This tool:

1. **Reads** PROMs data from Excel (`.xlsx` / `.xls`) files
2. **Looks up** missing demographics (gender, date of birth, body side) from a lookup table
3. **Converts** data into LROI XML format
4. **Validates** output against XSD schema (`XSD_LROI_PROMs_v9_2-20210608.xsd`)
5. **Outputs** XML ready for LROI Databroker upload

**Key Features:**
- ✅ Auto-detects PROM type (OKS, OHS, KOOS, HOOS, EQ-5D-5L per joint) from column headers
- ✅ Processes multiple files or entire folders at once
- ✅ XSD validation
- ✅ Both CLI and GUI interfaces
- ✅ Detailed logging with Excel export
- ✅ Can be packaged as single-file Windows `.exe`

---

## Supported PROMs

| PROM | Full Name | Joint | Questions | Status |
|------|-----------|-------|-----------|--------|
| **OKS** | Oxford Knee Score | Knee | 12 | ✅ Fully configured |
| **OHS** | Oxford Hip Score | Hip | 12 | ✅ Fully configured |
| **KOOS** | Knee Injury and Osteoarthritis Outcome Score | Knee | 7 | ✅ Fully configured |
| **HOOS** | Hip Disability and Osteoarthritis Outcome Score | Hip | 5 | ✅ Fully configured |
| **EQ-5D-5L** | EuroQol 5-Dimension 5-Level | Hip / Knee / Shoulder | 6 | ✅ Fully configured |

All include lookup table support for demographics (gender, date of birth, laterality).

**Note:** EQ-5D-5L is a cross-joint questionnaire.  LROI requires different XML element names per joint.  A single `[PROM.EQ5D5L]` config section handles all joints using [conditional element skip](#conditional-element-skip-v150) — the `Procedure Type` column determines which joint-specific XML elements are emitted.

---

## Requirements

- **Python 3.11+** (3.13 works fine)
- **Windows, macOS, or Linux**
- **Dependencies:**
  - `openpyxl` - Excel file handling
  - `lxml` - XML validation
  - `tkinter` - GUI (usually included with Python)

---

## Installation

### Quick Setup (3 steps)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate.bat         # Windows CMD
# OR: source venv/bin/activate    # macOS/Linux
# OR: .\venv\Scripts\Activate.ps1 # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import openpyxl, lxml; print('✓ Ready to use')"
```

**Detailed instructions:** See [INSTALL.md](INSTALL.md)

---

## Configuration

All settings are in **`config.toml`**. This file maps your Excel columns to LROI XML elements.

### Essential Settings

```toml
[defaults]
hospital = 1234  # MANDATORY: Your LROI hospital code
```

**Optional settings (with defaults):**

```toml
lut_column_prefix = "__LUT__"
  # Default: "__LUT__"
  # Prefix added to lookup table columns to avoid naming conflicts

log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log"
  # Default: "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log"
  # Template for auto-named log files

xlsx_log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx"
  # Default: "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx"
  # Template for Excel log files (set to "" to disable)

output_xml_file = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_output.xml"
  # Default: "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_output.xml"
  # Template for output XML filename
```

**Template placeholders:**
- `{yyyy}` = 4-digit year (2026)
- `{mm}` = 2-digit month (02)
- `{dd}` = 2-digit day (27)
- `{HH}` = 2-digit hour, 24h (14)
- `{MM}` = 2-digit minute (35)
- `{SS}` = 2-digit second (42)
- `{appname}` = Script/executable name
  - `main` when running `python main.py`
  - `lroi_converter` when running `lroi_converter.exe`

---

### Lookup Table (Demographics)

When patient demographics are in a separate Excel file:

```toml
[lut]
join_column = "Participant ID"
  # Column name used to match Excel rows with lookup table rows
  # Must exist in BOTH files
```

**How it works:**
1. Converter reads PROM file (e.g., OKS export)
2. For each row, gets `join_column` value (e.g., `"Participant ID" = "12345"`)
3. Looks up that value in demographics file
4. Adds requested columns from lookup table
5. Prefixes added columns with `__LUT__` (e.g., `__LUT__Gender`)

---

### PROM Definitions

Each questionnaire type needs a `[PROM.<TYPE>]` section.

**Note:** `<TYPE>` is a **free text identifier** you choose (e.g., `OKS`, `OHS`, `MyCustomPROM`). It's not tied to XML elements.

#### Basic Structure

```toml
[PROM.OKS]
detection_column = "1. How would you describe the pain..."
  # Column that identifies this file as OKS
  # When this column name appears in Excel headers, converter knows: "This is OKS"

[PROM.OKS.lookup]
  # Optional: Demographics lookup configuration
required = true
  # If true, conversion fails when lookup table file is missing
  # If false, continues without lookup (assumes demographics in Excel)

join_column = "Participant ID"
  # Column to match Excel rows with lookup table rows

add_columns = ["Gender", "Date of Birth", "Body Side"]
  # Columns to fetch from lookup table
  # Added as: __LUT__Gender, __LUT__Date of Birth, __LUT__Body Side
```

#### Element Mappings

Map XML elements to Excel columns:

```toml
[PROM.OKS.UPNNUM]
column = "Patient ID"
  # XML <UPNNUM> gets value from Excel column "Patient ID"
  # Simple 1:1 mapping, no transformation
```

#### Value Conversions

Transform Excel values to match LROI requirements using regex:

```toml
[PROM.OKS.GENDER]
column = "__LUT__Gender"
  # Get value from lookup table Gender column

[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"
  # Regex pattern: matches "M", "Male", "MALE", "male"
replace = "0"
  # Male → 0 (required by LROI XSD)

[[PROM.OKS.GENDER.value]]
match = "^F(emale)?$"
  # Matches: "F", "Female", "FEMALE", "female"
replace = "1"
  # Female → 1
```

**How conversions work:**
1. **No conversions defined?** Value used as-is
2. **Conversions defined?** Applied in order, **first match wins**
3. **No match found?** Row **SKIPPED** (logged as ERROR)

**Conversion modes:**

```toml
# Mode 1: Match + Replace (transformation)
[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"
replace = "0"

# Mode 2: Match only (validation)
[[PROM.OKS.DATUMINVUL.value]]
match = "^\d{4}-\d{2}-\d{2}$"  # Must be YYYY-MM-DD
# No replace = validation only
# Row skipped if doesn't match
```

**Regex flags:**

```toml
[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"
replace = "0"
flags = "i"  # Optional: case-insensitive (DEFAULT)
  # Default: flags = "i" (case-insensitive matching)
  # For case-sensitive: explicitly set flags = ""
  # Other flags: "m" (multiline), "s" (dotall)
```

**Note:** Case-insensitive matching (`flags = "i"`) is the **default**. You don't need to specify it unless you want different flags.

---

### Magic Expression Detection (v1.5.0)

Some PROMs like **EQ-5D-5L** are used across multiple joints (hip, knee, shoulder), but LROI requires different XML element names per joint.  Standard `detection_column` only matches a single column name, which can't distinguish between joints.

**Solution:** `detection_column` now supports **magic expressions**.  When the value contains `$` or `%(`, it is evaluated as a magic expression instead of a column-name lookup.  If the expression evaluates to **boolean `true`**, the PROM type is detected.

#### Example: EQ-5D-5L per Joint

```toml
# ── Hip variant ──
[PROM.EQ5D5L_HIP]
detection_column = "$AND($N(%(EQ-5D-5L Score)),$EQI(%(Joint),Hip))"
#                        ↑ column has a value      ↑ Joint column = "Hip"

# ── Knee variant ──
[PROM.EQ5D5L_KNEE]
detection_column = "$AND($N(%(EQ-5D-5L Score)),$EQI(%(Joint),Knee))"
```

Each variant has its own `[PROM.<NAME>.<ELEMENT>]` sections with the correct LROI XML element names (e.g., `FUPH`/`SIDEP` for hip, `FUPK`/`SIDEPK` for knee).

#### How It Works

| `detection_column` value | Mode | Detected when... |
|---|---|---|
| `"Oxford Knee Score"` | Column name (original) | Column exists and has a non-empty value |
| `"$AND($N(%(EQ-5D-5L Score)),$EQI(%(Joint),Hip))"` | Magic expression (v1.5.0) | Expression evaluates to `true` |

**Rules:**
1. If `detection_column` contains `$` or `%(` → evaluated as magic expression
2. Otherwise → original column-name detection (unchanged)
3. First matching PROM type wins (same as before)
4. Missing columns evaluate to empty/`None` — they won't cause errors, just `false`

#### PROM-Level Virtual Columns

You can define `__variables` at the `[PROM.<NAME>]` level for reuse in detection and XML elements:

```toml
[PROM.EQ5D5L_HIP]
__is_hip = "$EQI(%(Joint),Hip)"
__has_eq5d = "$N(%(EQ-5D-5L Score))"
detection_column = "$AND(%(__has_eq5d),%(__is_hip))"

[PROM.EQ5D5L_HIP.FUPH]
# __is_hip is available here too
column = "$IF(%(__is_hip),%(follow_up_period),#(false))"
```

PROM-level virtual columns:
- Must start with `__` (double underscore)
- Are evaluated in definition order
- Are available to **all** XML element sections within the same PROM
- Can reference each other and row data

#### Conditional Element Skip (v1.5.0)

If an XML element's `column` is a magic expression that evaluates to **boolean `false`**, the element is silently skipped (no XML tag emitted).  This is useful for conditional output:

```toml
[PROM.MIXED.FUPH]
# Only emit FUPH for hip patients; skip for others
column = "$IF($EQI(%(Joint),Hip),%(follow_up_period),#(false))"

[PROM.MIXED.FUPK]
# Only emit FUPK for knee patients; skip for others
column = "$IF($EQI(%(Joint),Knee),%(follow_up_period),#(false))"
```

#### Available Functions for Detection

Any magic function can be used.  Commonly useful ones:

| Function | Example | Description |
|---|---|---|
| `$N(val)` | `$N(%(Col))` | True if column has a non-empty value |
| `$Z(val)` | `$Z(%(Col))` | True if column is empty/missing |
| `$EQ(a,b)` | `$EQ(%(Type),Hip)` | Exact equality (case-sensitive) |
| `$EQI(a,b)` | `$EQI(%(Type),hip)` | Case-insensitive equality |
| `$AND(…)` | `$AND($N(%(A)),$N(%(B)))` | All conditions must be true |
| `$OR(…)` | `$OR($EQ(%(X),1),$EQ(%(X),2))` | At least one must be true |
| `$CONTAINS(s,sub)` | `$CONTAINS(%(Name),Hip)` | Substring check |
| `$MATCH(s,pat)` | `$MATCH(%(Col),^EQ.*)` | Regex check |
| `#(true)` / `#(false)` | `$IF(cond,#(true),#(false))` | Boolean literals |

See `magic_functions.py` for the full list of ~60 functions.

---

### Complete Example

```toml
# ========================================
# Essential Settings
# ========================================

[defaults]
hospital = 1234  # MANDATORY

# Optional - defaults shown in comments
lut_column_prefix = "__LUT__"
log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log"
xlsx_log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx"
output_xml_file = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_output.xml"

# ========================================
# Demographics Lookup
# ========================================

[lut]
join_column = "Participant ID"

# ========================================
# Oxford Knee Score (OKS)
# ========================================

[PROM.OKS]
detection_column = "1. How would you describe the pain..."

[PROM.OKS.lookup]
required = true
join_column = "Participant ID"
add_columns = ["Gender", "Date of Birth", "Body Side"]

# Patient identifiers
[PROM.OKS.UPNNUM]
column = "Patient ID"

[PROM.OKS.DATUMINVUL]
column = "Date of Survey Completion"

# Demographics (from lookup table)
[PROM.OKS.GENDER]
column = "__LUT__Gender"
[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"
replace = "0"
# No flags needed - case-insensitive is default
[[PROM.OKS.GENDER.value]]
match = "^F(emale)?$"
replace = "1"

[PROM.OKS.DATBIRTH]
column = "__LUT__Date of Birth"

# Follow-up period
[PROM.OKS.FUPK]
column = "Period"
[[PROM.OKS.FUPK.value]]
match = "Pre-?Op|Preop"
replace = "-1"
[[PROM.OKS.FUPK.value]]
match = "3\\s*Month|3M"
replace = "3"
[[PROM.OKS.FUPK.value]]
match = "12\\s*Month|12M|1\\s*Year"
replace = "12"

# Body side (laterality)
[PROM.OKS.SIDEPK]
column = "__LUT__Body Side"
[[PROM.OKS.SIDEPK.value]]
match = "Right|R"
replace = "1"
[[PROM.OKS.SIDEPK.value]]
match = "Left|L"
replace = "2"

# OKS Questions (12 items)
[PROM.OKS.OKS1PK]
column = "1. How would you describe the pain..."

[PROM.OKS.OKS2PK]
column = "2. Have you had any trouble with washing..."

# ... (continue for all 12 questions)
```

---

### How It Works

1. **File Detection:**
   - Reads Excel headers
   - Finds `detection_column` → identifies PROM type (plain column name or magic expression)
   - Uses corresponding `[PROM.<TYPE>]` configuration

2. **For Each Row:**
   - Extracts column values
   - If `[PROM.<TYPE>.lookup]` defined: fetches demographics from lookup table
   - For each XML element (in config.toml definition order):
     - Gets value from specified `column` (may be a magic expression)
     - If expression evaluates to boolean `false` → element skipped
     - Applies regex conversions (if defined)
     - Validates format
   - Builds XML `<questionnaire>` element

   **Important:** The order of `[PROM.<TYPE>.<ELEMENT>]` sections in config.toml determines the XML element order.  This must match the LROI XSD sequence (typically: DATUMINVUL, HOSPITAL, UPNNUM, GENDER, DATBIRTH, then PROM-specific elements).  If `HOSPITAL` is not explicitly defined as a section, it is auto-inserted after `DATUMINVUL`.

3. **Value Conversions:**
   - Applied in order (first match wins)
   - If no match and conversions defined → row SKIPPED (ERROR logged)
   - If no conversions → value used as-is

4. **Date Handling:**
   - **Automatic:** Python `datetime` objects from Excel → YYYY-MM-DD strings
   - **Regex:** Use conversions for string date format transformations
   - **Validation:** Use `python validate_xml.py output.xml schema.xsd` (separate tool)

---

### Configuration Tips

**1. Start with demo config:**
```bash
cp demo/demo.config.toml myhospital.config.toml
# Edit to match your column names
```

**2. Test with small file + DEBUG logging:**
```bash
python main.py --cfg myhospital.config.toml \
  --input test_file.xlsx \
  --loglevel DEBUG
```

**3. Check DEBUG log for column matching:**
```
DEBUG  Detected PROM type: OKS
DEBUG  Extracted UPNNUM: "P12345" from column "Patient ID"
DEBUG  Converted GENDER: "Male" → "0"
```

**4. Common issues:**
- ❌ Column name typo: `"Patient ID"` vs `"PatientID"`
- ❌ Detection column not unique: same column in different PROM files
- ❌ Regex needs case-insensitive: default is already case-insensitive
- ❌ Missing lookup columns: `add_columns = ["Gender"]` but lookup has "Sex"

---

## Usage

### Command Line (CLI)

Run conversion without GUI:

```bash
python main.py --input file.xlsx \
               --lut demographics.xlsx \
               --output output.xml \
               --hospital 1234
```

**Arguments:**
- `--input FILE_OR_FOLDER` — Excel file(s) or folder. Can be repeated. Folders searched recursively.
- `--lut FILE` — Optional demographics lookup table (Excel file)
- `--output FILE` — Output XML path (default: timestamped from config)
- `--hospital N` — Hospital LROI code (overrides config)
- `--log FILE|1` — Log file path, or `1` for auto-named (creates both .log and .xlsx)
- `--loglevel LEVEL` — Log level: DEBUG (shows PII/PHI), INFO (default, safe), WARNING, ERROR
- `--cfg FILE` — Path to config.toml (default: looks next to main.py)

**Log files:**

When using `--log 1`, creates **two log files**:

1. **Text log** (`.log`) — Human-readable for developers
2. **Excel log** (`.xlsx`) — **Double-click to open in Excel**
   - Auto-filter enabled
   - Color-coded rows (red = ERROR, yellow = WARNING)
   - Frozen headers
   - Sortable columns

---

### Graphical Interface (GUI)

Launch GUI:

```bash
python main.py --gui
```

Or with pre-filled fields:

```bash
python main.py --gui \
               --input path/to/files \
               --lut demographics.xlsx \
               --output custom_output.xml
```

**GUI Features:**
- **Config file** — Browse to load different config
- **Input files** — Select multiple files or folder
- **Lookup table** — Select demographics file
- **Log level** — Choose DEBUG, INFO, WARNING, or ERROR
- **Output XML file** — Specify output filename (or use template)
- **Log files** — Text and Excel logs with "Use default" checkboxes
- **Real-time log** — Color-coded conversion progress
- **Clear Log** — Reset view between runs

---

### Examples

**Single file:**
```bash
python main.py --input OKS_export.xlsx --output oks.xml
```

**Multiple files:**
```bash
python main.py --input file1.xlsx file2.xlsx file3.xlsx --output combined.xml
```

**Entire folder:**
```bash
python main.py --input data/ --output combined.xml
```

**With demographics lookup:**
```bash
python main.py --input exports/ \
               --lut demographics.xlsx \
               --output output.xml \
               --log 1
```

**Production mode (PII/PHI safe logging):**
```bash
python main.py --input exports/ \
               --lut demographics.xlsx \
               --loglevel INFO \
               --log 1
```

**Development mode (see value conversions):**
```bash
python main.py --input test.xlsx \
               --loglevel DEBUG \
               --log 1
```

---

## Building Windows Executable

Create standalone `.exe` for users without Python:

### Prerequisites

- Windows machine (or Windows VM)
- Python 3.11+ installed
- PyInstaller: `pip install pyinstaller`

### Build

```bash
python build_exe.py
```

**Output:** `dist/lroi_converter/lroi_converter.exe`

### Custom Icon

1. Create or obtain `your_icon.ico` (256x256 recommended)
2. Place in project root
3. Edit `build_exe.py` line 67:
   ```python
   ICON_FILE: Path | None = PROJECT_DIR / "your_icon.ico"
   ```
4. Run: `python build_exe.py`

### Distribution

Ship `dist/lroi_converter/` folder containing:
- `lroi_converter.exe`
- `config.toml` (users edit this)

**Usage:**
```cmd
lroi_converter.exe --input data\ --lut demographics.xlsx
```

---

## How It Works

### Architecture

```
Excel Files → Converter → LROI XML
     ↓            ↓
Lookup Table   Config
```

### Processing Flow

1. **Load configuration** from `config.toml`
2. **Read Excel files** (`.xlsx` / `.xls`)
3. **Detect PROM type** from `detection_column`
4. **For each row:**
   - Extract all column values
   - Lookup demographics (if configured)
   - Map columns to XML elements
   - Apply regex conversions
   - Validate values
5. **Build XML** in XSD-compliant order
6. **Write output** file
7. **Log results** (text + Excel)

### Data Validation

- **Required fields:** Skips row if missing
- **Regex conversions:** Validates format, transforms values
- **Date conversion:** Automatic `datetime` → YYYY-MM-DD
- **XSD validation:** Use `validate_xml.py` to verify output

---

## Troubleshooting

### "python is not recognized"
Python not in PATH. Reinstall and check "Add Python to PATH".

### "No module named 'openpyxl'"
Dependencies not installed. Run: `pip install -r requirements.txt`

### "Config file not found"
- CLI: Copy `config.toml` to same directory as script/exe
- Or use: `--cfg /path/to/config.toml`
- GUI: Opens anyway, browse for config

### "No PROM type detected"
`detection_column` not found in Excel headers.
- Check column name spelling (case-sensitive)
- Use `--loglevel DEBUG` to see column detection

### "Validation failed for GENDER"
Value doesn't match any regex pattern.
- Check Excel values: "Male" vs "M" vs "male"
- Default is case-insensitive (`flags = "i"`)
- Add more patterns or fix data

### XSD Validation Errors

Run validation separately:
```bash
python validate_xml.py output.xml XSD_LROI_PROMs_v9_2-20210608.xsd
```

Common errors:
- Date format: ensure YYYY-MM-DD (automatic for `datetime` objects)
- Missing required elements: check config mappings
- Invalid enum values: check regex conversions

### Column Name Issues

Check exact column names in your Excel file:
```python
import openpyxl
wb = openpyxl.load_workbook("yourfile.xlsx")
ws = wb.active
headers = next(ws.iter_rows(values_only=True))
print(headers)  # Shows exact column names
```

### Regex Testing

Test patterns at [regex101.com](https://regex101.com):
1. Select Python flavor
2. Test your `match` patterns
3. Verify replacements work

---

## Getting Help

**Check logs:**
```bash
python main.py --input test.xlsx --loglevel DEBUG --log 1
```

**Verify config:**
- Compare your config with `demo/demo.config.toml`
- Check column names match exactly
- Test regex patterns online

**Common patterns:**
- Gender: `^M(ale)?$` and `^F(emale)?$`
- Dates: `^\d{4}-\d{2}-\d{2}$` (YYYY-MM-DD)
- Periods: `Pre-?Op|Preop` for "Pre-Op", "PreOp", "Preop"

**Still stuck?**
- Enable `--loglevel DEBUG` to see exact values
- Check demo files for working examples
- Verify lookup table `join_column` values exist in both files

---

## Project Structure

```
lroi_converter/
├── main.py                    # CLI/GUI entry point
├── converter.py               # Core conversion logic
├── gui.py                     # GUI interface
├── logger.py                  # Logging configuration
├── validate_xml.py            # XSD validation tool
├── config.toml                # Main configuration
├── requirements.txt           # Python dependencies
├── build_exe.py               # Windows .exe builder
├── VERSION.txt                # Version information
├── README.md                  # This file
├── INSTALL.md                 # Installation guide
├── demo/
│   ├── demo.config.toml       # Demo configuration
│   ├── README.md              # Demo usage guide
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

---

## Version History

**v1.5.0** (2026-06-01)
- **Magic expression detection:** `detection_column` now supports magic expressions for multi-condition PROM detection
- **PROM-level virtual columns:** Define `__variables` at `[PROM.<NAME>]` level, reusable across detection and all XML elements
- **Conditional element skip:** XML elements whose `column` expression evaluates to boolean `false` are silently omitted
- **EQ-5D-5L fully configured:** Single unified config section handles hip, knee, and shoulder using conditional skip on `Procedure Type`
- **Element order from config:** Removed hardcoded `XSD_ELEMENT_ORDER` — XML element order is now derived from the key order in config.toml. New PROM types no longer require code changes.
- **Type preservation:** Pure `%(variable)` references inside magic functions now preserve their original Python type (bool, int, etc.) instead of being stringified
- **GUI loglevel fix:** `--loglevel` CLI argument now correctly pre-populates the GUI dropdown

**v1.4.7** (2026-02-27)
- Renamed --xls to --input (breaking change)
- Complete documentation rewrite
- All configuration clarifications

**v1.4.6** (2026-02-27)
- Fixed GUI "Use default" checkbox
- Updated documentation

**v1.4.5** (2026-02-27)
- Fixed KOOS/HOOS element order
- Fixed timestamp consistency
- Fixed GUI prepopulate

**v1.4.4** (2026-02-27)
- Added log level control (PII/PHI protection)
- Added output XML file configuration
- Added HOOS and KOOS support

See [VERSION.txt](VERSION.txt) for complete changelog.

---

## License

[Your license here]

---

## Contact

[Your contact information here]

---

**Last Updated:** v1.5.0 (2026-06-01)
