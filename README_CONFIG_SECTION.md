# Configuration Section for README.md (v1.4.5+)

## Configuration

All settings are in **`config.toml`**. This is a simple mapping file that tells the converter:
1. Which Excel columns contain which patient data
2. How to transform values to match LROI requirements
3. Where to find demographic data

**You are responsible for configuring this correctly** to match your hospital's data export format.

---

### File Structure

```toml
[defaults]           # Required: Hospital ID and file naming
[lut]                # Optional: Demographics lookup settings
[PROM.<TYPE>]        # One section per questionnaire type (OKS, OHS, KOOS, HOOS)
```

---

### Essential Settings (`[defaults]`)

**Required fields:**

```toml
[defaults]
hospital = 1234  # MANDATORY: Your hospital's LROI code
```

**Optional fields (with defaults):**

```toml
lut_column_prefix = "__LUT__"  # Default: "__LUT__"
  # Prefix added to LUT columns to avoid naming conflicts with Excel columns

log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log"  
  # Default: "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log"
  # Template for auto-named log files (when using --log 1)

xlsx_log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx"
  # Default: "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx"
  # Template for auto-named Excel log files
  # Set to empty string "" to disable Excel logs

output_xml_file = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_output.xml"
  # Default: "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_output.xml"
  # Template for output XML filename when not specified via --output
```

**Template placeholders:**
- `{yyyy}` - 4-digit year (e.g., 2026)
- `{mm}` - 2-digit month (e.g., 02)
- `{dd}` - 2-digit day (e.g., 27)
- `{HH}` - 2-digit hour, 24h format (e.g., 14)
- `{MM}` - 2-digit minute (e.g., 35)
- `{SS}` - 2-digit second (e.g., 42)
- `{appname}` - Script/executable name without extension
  - `main` when running `python main.py`
  - `lroi_converter` when running `lroi_converter.exe`

**Example output:** `2026-02-27-143542_lroi_converter.xml`

---

### Lookup Table Settings (`[lut]`)

Used when patient demographics (gender, date of birth, laterality) are in a separate file:

```toml
[lut]
join_column = "Admission ID"
  # Column name used to JOIN Excel PROMs file with demographics LUT
  # Must exist in BOTH files but can have a different name per Excel PROMs file
```

**How it works:**
1. Converter reads Excel PROMs file (e.g., OKS export)
2. For each row, extracts the `join_column` value (e.g., `Admission ID = "54321"`)
3. Looks up that value in the LUT file
4. Adds requested demographics columns from LUT to that row
5. Prefixes added columns with `__LUT__` (e.g., `__LUT__Gender`, `__LUT__Date of Birth`)

---

### PROM Definitions (`[PROM.<TYPE>]`)

Each questionnaire type (OKS, OHS, KOOS, HOOS) needs its own section.

#### Basic Structure

```toml
[PROM.OKS]
detection_column = "Oxford Knee Score"
  # Column that identifies this file as OKS
  # When converter sees this column name in Excel headers, it knows: "This is OKS"
  # Auto-detection happens once per file

[PROM.OKS.lookup]
  # Optional: Demographics lookup configuration
required = true
  # If true, conversion fails when LUT file is missing
  # If false, continues without LUT (assumes demographics are in Excel)

join_column = "Admission ID"
  # Column name to match Excel rows with LUT rows
  # Can be different from [lut].join_column if needed

add_columns = ["Gender", "Date of Birth", "Laterality"]
  # Which columns to fetch from LUT
  # These will be added as __LUT__Gender, __LUT__Date of Birth, etc.
```

#### Element Mappings

Each XML element needs a mapping to tell converter which Excel column contains that data:

```toml
[PROM.OKS.UPNNUM]
column = "Patient ID"
  # Maps XML element <UPNNUM> to Excel column "Patient ID"
  # Simple 1:1 mapping, no transformation
```

#### Value Conversions (Optional)

When Excel values don't match LROI requirements, use regex conversions:

```toml
[PROM.OKS.GENDER]
column = "__LUT__Gender"
  # Get value from LUT Gender column

[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"
  # Regex pattern to match input value
  # Matches: "M", "Male", "MALE", "male"
replace = "0"
  # Replacement value for XML
  # Male → 0 (required by LROI XSD)

[[PROM.OKS.GENDER.value]]
match = "^F(emale)?$"
  # Second conversion rule
  # Matches: "F", "Female", "FEMALE", "female"
replace = "1"
  # Female → 1
```

**How conversions work:**
1. **No conversions defined?** → Use value as-is from Excel
2. **Conversions defined?** → Apply regex in order, **first match wins**
3. **No match found?** → **SKIP this row** (logged as ERROR)

**Regex flags (hidden by default):**
```toml
[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"
replace = "0"
flags = "i"  # Optional: regex flags (i = case-insensitive)
  # Default: Case-sensitive matching
  # Common flags: "i" (ignore case), "m" (multiline), "s" (dotall)
```

---

### Complete Example

```toml
# ========================================
# Essential Settings
# ========================================

[defaults]
hospital = 1234  # MANDATORY: Your LROI hospital code

# Optional - defaults shown in comments
lut_column_prefix = "__LUT__"  
log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log"
xlsx_log_file_template = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx"
output_xml_file = "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_output.xml"

# ========================================
# Demographics Lookup
# ========================================

[lut]
join_column = "Admission ID"

# ========================================
# Oxford Knee Score (OKS)
# ========================================

[PROM.OKS]
detection_column = "1. How would you describe the pain..."
  # First question text from Oxford Knee Score questionnaire

[PROM.OKS.lookup]
required = true
join_column = "Admission ID"
add_columns = ["Gender", "Date of Birth", "Laterality"]

# Patient identifiers
[PROM.OKS.UPNNUM]
column = "Patient ID"

[PROM.OKS.DATUMINVUL]
column = "Date of Survey Completion"

# Demographics (from LUT)
[PROM.OKS.GENDER]
column = "__LUT__Gender"
[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"
replace = "0"
flags = "i"
[[PROM.OKS.GENDER.value]]
match = "^F(emale)?$"
replace = "1"
flags = "i"

[PROM.OKS.DATBIRTH]
column = "__LUT__Date of Birth"

# Follow-up period
[PROM.OKS.FUPK]
column = "Period"
[[PROM.OKS.FUPK.value]]
match = "Pre-?Op|Preop"
replace = "-1"
flags = "i"
[[PROM.OKS.FUPK.value]]
match = "3\\s*Month|3M"
replace = "3"
flags = "i"
[[PROM.OKS.FUPK.value]]
match = "12\\s*Month|12M|1\\s*Year"
replace = "12"
flags = "i"

# Laterality
[PROM.OKS.SIDEPK]
column = "__LUT__Laterality"
[[PROM.OKS.SIDEPK.value]]
match = "Right|R"
replace = "1"
flags = "i"
[[PROM.OKS.SIDEPK.value]]
match = "Left|L"
replace = "2"
flags = "i"

# OKS Questions (12 items)
[PROM.OKS.OKS1PK]
column = "1. How would you describe the pain..."

[PROM.OKS.OKS2PK]
column = "2. Have you had any trouble with washing..."

# ... (continue for all 12 OKS questions)

[PROM.OKS.OKS12PK]
column = "12. Could you kneel down and get up..."
```

---

### How It Works

1. **File Detection:**
   - Converter reads Excel headers
   - Finds `detection_column` in headers → identifies PROM type
   - Uses corresponding `[PROM.<TYPE>]` configuration

2. **For Each Row:**
   - Extracts all column values
   - If `[PROM.<TYPE>.lookup]` defined: fetches demographics from LUT
   - For each XML element:
     - Gets value from specified `column`
     - Applies regex conversions (if defined)
     - Validates against XSD requirements
   - Builds XML `<questionnaire>` element

3. **Value Conversions:**
   - Applied in order (first match wins)
   - If no match and conversions defined → row SKIPPED (ERROR logged)
   - If no conversions defined → value used as-is

4. **Validation:**
   - Dates converted to YYYY-MM-DD format automatically
   - Missing required fields → row SKIPPED
   - Invalid values (no regex match) → row SKIPPED
   - Final XML validated against XSD schema

---

### Configuration Tips

**1. Start with demo config:**
```bash
cp demo/demo.config.toml myhos pital.config.toml
# Edit to match your column names
```

**2. Test with small file first:**
```bash
python main.py --cfg myhospital.config.toml \
  --xls test_file.xlsx \
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
- ❌ Detection column not unique: same column in OKS and OHS files
- ❌ Regex too strict: `"Male"` requires exact case unless using `flags = "i"`
- ❌ Missing LUT columns: `add_columns = ["Gender"]` but LUT has "Sex"

---

### Validation & Testing

```bash
# Step 1: Convert with DEBUG logging
python main.py --cfg config.toml \
  --xls test.xlsx \
  --loglevel DEBUG \
  --output test.xml

# Step 2: Check conversion results
# Look for: "Converted <TYPE> questionnaire: UPNNUM=..."
# Warnings: "No PROM type detected" = wrong detection_column

# Step 3: Validate XML against XSD
python validate_xml.py test.xml XSD_LROI_PROMs_v9_2-20210608.xsd

# Step 4: Fix any XSD validation errors
# Common: Date format, missing required elements, invalid enum values
```

---

### Getting Help

**Column name issues?**
```python
import openpyxl
wb = openpyxl.load_workbook("yourfile.xlsx")
ws = wb.active
headers = next(ws.iter_rows(values_only=True))
print(headers)  # Shows exact column names
```

**Regex testing:**
- Use https://regex101.com
- Select Python flavor
- Test your `match` patterns

**Still stuck?**
- Check `demo/demo.config.toml` for working example
- Enable `--loglevel DEBUG` to see exact values
- Verify LUT `join_column` values exist in both files

---

