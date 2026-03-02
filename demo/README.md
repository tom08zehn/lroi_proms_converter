# Demo Files — LROI PROMs Converter

This folder contains synthetic demo data to help you learn how the converter works.

**⚠️ IMPORTANT:** This demo data is **intentionally different** from your real production data to demonstrate the converter's flexibility.

---

## Quick Start

From the project root directory:

```bash
# Windows CMD
python main.py --cfg demo/demo.config.toml --input demo/ --lut demo/patient_demographics.xlsx --log 1

# macOS/Linux
python main.py --cfg demo/demo.config.toml \
  --input demo/ \
  --lut demo/patient_demographics.xlsx \
  --log 1
```

**Output:**
- `2026-02-27-143542_demo_output.xml` — Converted XML (15 questionnaires)
- `2026-02-27-143542_demo.log` — Text log
- `2026-02-27-143542_demo.xlsx` — Excel log (double-click to open)

All files have the same timestamp.

---

## What's In This Demo

### Files

| File | Type | Rows | Description |
|------|------|------|-------------|
| `demo.config.toml` | Config | — | Demo configuration |
| `patient_demographics.xlsx` | LUT | 15 | Demographics lookup table |
| `oks_export_site_a.xlsx` | OKS | 5 | Oxford Knee Score from Site A |
| `oks_export_site_b.xlsx` | OKS | 3 | Oxford Knee Score from Site B |
| `ohs_export_batch1.xlsx` | OHS | 4 | Oxford Hip Score batch 1 |
| `ohs_export_batch2.xlsx` | OHS | 3 | Oxford Hip Score batch 2 |

**Total:** 15 synthetic questionnaires (8 OKS + 7 OHS)

---

### Synthetic Data

All data is **completely fictional**:
- Patient IDs: Random numbers (440587, 449334, etc.)
- Dates: Recent dates (2024-2026)
- Scores: Randomly generated but valid
- Demographics: Plausible but synthetic

**This data cannot be traced to real patients.**

---

## How the Demo Works

### 1. Different Column Names

The demo uses **different column names** than the main `config.toml` to show flexibility:

| XML Element | Main Config | Demo Config |
|-------------|-------------|-------------|
| Patient ID | `"Patient ID"` | `"Patient ID"` (same) |
| Admission ID | `"Admission ID"` | `"PatientRecordID"` (different!) |
| Survey Date | `"Date of Survey Completion"` | `"Survey Date"` (shorter) |
| Follow-up | `"Period"` | `"Follow-up Phase"` (different) |

This demonstrates that you can map **any column names** to LROI XML elements.

---

### 2. Multiple Files Per PROM

The demo shows batch processing:
- **OKS:** 2 files (site_a + site_b) → combined into one XML
- **OHS:** 2 files (batch1 + batch2) → combined into one XML

**In production:** You might have:
- Weekly exports from different locations
- Monthly batches
- Multiple surgeons' exports

The converter handles all of them in one run.

---

### 3. Lookup Table (LUT)

**Demo problem:** Excel PROM files are missing demographics (gender, date of birth, laterality).

**Demo solution:** Separate lookup table `patient_demographics.xlsx`:

```
PatientRecordID | Gender | Date of Birth | Laterality
----------------|--------|---------------|------------
240449         | Male   | 1954-05-15    | Left
249227         | Female | 1963-11-22    | Right
...
```

**How it works:**
1. Converter reads OKS/OHS file
2. For each row, gets `PatientRecordID` value (e.g., `240449`)
3. Looks up that value in `patient_demographics.xlsx`
4. Adds demographics as `__LUT__Gender`, `__LUT__Date of Birth`, `__LUT__Laterality`
5. These prefixed columns are then mapped to XML elements

**Configuration:**
```toml
[PROM.OKS.lookup]
required = true
join_column = "PatientRecordID"  # Column to match on
add_columns = ["Gender", "Date of Birth", "Laterality"]  # Columns to add
```

---

### 4. Value Conversions

The demo shows regex conversions:

**Gender:**
```toml
[[PROM.OKS.GENDER.value]]
match = "^M(ale)?$"    # Matches: M, Male, MALE, male
replace = "0"           # → XML value: 0

[[PROM.OKS.GENDER.value]]
match = "^F(emale)?$"  # Matches: F, Female, FEMALE, female
replace = "1"           # → XML value: 1
```

**Follow-up Period:**
```toml
[[PROM.OKS.FUPK.value]]
match = "Pre-?Op|Preop"  # Matches: Pre-Op, PreOp, Preop
replace = "-1"            # → XML value: -1

[[PROM.OKS.FUPK.value]]
match = "3\\s*Month|3M"  # Matches: 3 Month, 3Month, 3M
replace = "3"             # → XML value: 3
```

**Note:** Case-insensitive matching is **default** (`flags = "i"`). No need to specify unless you want case-sensitive.

---

### 5. PROM Detection

The converter auto-detects PROM type from column headers:

**OKS files** have column:
```
"RecordNumber"
```

**OHS files** have column:
```
"ObservationID"
```

**Configuration:**
```toml
[PROM.OKS]
detection_column = "RecordNumber"  # If this column exists → OKS

[PROM.OHS]
detection_column = "ObservationID"  # If this column exists → OHS
```

**The converter:**
1. Opens Excel file
2. Reads column headers
3. Finds `detection_column`
4. Identifies PROM type
5. Uses corresponding configuration section

---

## Demo Scenarios

### Scenario 1: Basic Conversion

Convert all demo files:
```bash
python main.py --cfg demo/demo.config.toml \
  --input demo/ \
  --lut demo/patient_demographics.xlsx
```

**Result:** 15 questionnaires in output XML

---

### Scenario 2: Single PROM Type

Convert only OKS files:
```bash
python main.py --cfg demo/demo.config.toml \
  --input demo/oks_export_site_a.xlsx demo/oks_export_site_b.xlsx \
  --lut demo/patient_demographics.xlsx
```

**Result:** 8 OKS questionnaires

---

### Scenario 3: With Logging

Enable detailed logging:
```bash
python main.py --cfg demo/demo.config.toml \
  --input demo/ \
  --lut demo/patient_demographics.xlsx \
  --loglevel DEBUG \
  --log 1
```

**Output includes:**
- Text log showing all conversions
- Excel log with sortable, filterable columns

**Debug log shows:**
```
DEBUG  Detected PROM type: OKS
DEBUG  Extracted UPNNUM: "440587" from column "Patient ID"
DEBUG  Converted GENDER: "Male" → "0"
DEBUG  Converted FUPK: "Pre-Op" → "-1"
```

---

### Scenario 4: GUI Mode

Launch GUI with demo files pre-loaded:
```bash
python main.py --gui \
  --cfg demo/demo.config.toml \
  --input demo/ \
  --lut demo/patient_demographics.xlsx
```

**GUI shows:**
- Config: `demo/demo.config.toml`
- Input files: All 5 demo .xlsx files
- Lookup table: `patient_demographics.xlsx`
- Click "Run Conversion"

---

### Scenario 5: Validation

Validate output against XSD:
```bash
# Run conversion
python main.py --cfg demo/demo.config.toml \
  --input demo/ \
  --lut demo/patient_demographics.xlsx \
  --output demo_output.xml

# Validate
python validate_xml.py demo_output.xml ../example/XSD_LROI_PROMs_v9_2-20210608.xsd
```

**Expected:** `✓ demo_output.xml is VALID`

---

## Expected Output

### Console Output

```
INFO      Detected PROM type: OKS
INFO      Converted OKS questionnaire: UPNNUM=440587
INFO      Converted OKS questionnaire: UPNNUM=449334
...
INFO      Detected PROM type: OHS
INFO      Converted OHS questionnaire: UPNNUM=440587
INFO      Converted OHS questionnaire: UPNNUM=449334
...
INFO      Conversion complete: 15 questionnaires converted
INFO      XML written to: 2026-02-27-143542_demo_output.xml
INFO      Output file: 2026-02-27-143542_demo_output.xml
```

---

### XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<BATCH>
  <questionaire>
    <DATUMINVUL>2024-01-15</DATUMINVUL>
    <HOSPITAL>9999</HOSPITAL>
    <UPNNUM>440587</UPNNUM>
    <GENDER>0</GENDER>
    <DATBIRTH>1954-05-15</DATBIRTH>
    <FUPK>-1</FUPK>
    <SIDEPK>2</SIDEPK>
    <OKS1PK>4</OKS1PK>
    <OKS2PK>3</OKS2PK>
    ...
  </questionaire>
  <questionaire>
    ...
  </questionaire>
  <!-- 15 total -->
</BATCH>
```

---

### Excel Log

**Double-click `2026-02-27-143542_demo.xlsx` to open:**

| Timestamp | Level | Message | Admission ID |
|-----------|-------|---------|--------------|
| 14:35:42 | INFO | Detected PROM type: OKS | — |
| 14:35:42 | INFO | Converted OKS questionnaire: UPNNUM=440587 | 240449 |
| 14:35:42 | DEBUG | Converted GENDER: "Male" → "0" | 240449 |
| 14:35:42 | DEBUG | Converted FUPK: "Pre-Op" → "-1" | 240449 |

**Features:**
- ✅ Auto-filter enabled (click dropdown in headers)
- ✅ Frozen header row (header stays visible when scrolling)
- ✅ Color-coded: Red = ERROR, Yellow = WARNING
- ✅ Sortable by any column
- ✅ Searchable/filterable

---

## Differences from Production

| Aspect | Demo | Your Production |
|--------|------|-----------------|
| **Column names** | `"PatientRecordID"`, `"Survey Date"` | Your hospital's column names |
| **Hospital code** | `9999` | Your real LROI code |
| **Detection columns** | `"RecordNumber"`, `"ObservationID"` | Your Excel column names |
| **LUT join column** | `"PatientRecordID"` | Your join column (e.g., `"Participant ID"`) |
| **File names** | `oks_export_site_a.xlsx` | Your export file names |

**To use with your data:**
1. Copy `demo/demo.config.toml` to `config.toml` (root)
2. Edit `config.toml`:
   - Change `hospital = 9999` to your code
   - Update all `column = "..."` values to match your Excel
   - Update `detection_column` to match your files
   - Update `join_column` to match your lookup table
3. Test with a small file first

---

## Common Demo Questions

### Why different column names?

To demonstrate that the converter is **flexible**. You can map any Excel column to any XML element.

**Your hospital might have:**
- `"PatID"` instead of `"Patient ID"`
- `"CompletionDate"` instead of `"Survey Date"`
- `"AdmissionNumber"` instead of `"PatientRecordID"`

**The converter doesn't care** — just configure the mapping in `config.toml`.

---

### Why separate lookup table?

Many hospitals have:
- **PROMs system** (questionnaires, scores)
- **EPR system** (demographics, patient master data)

These are often **separate databases/exports**. The lookup table simulates this scenario.

**Your setup might:**
- Have demographics in the same Excel file (no lookup needed)
- Have demographics in a separate file (use lookup like demo)
- Have demographics in a database (export to Excel, then use lookup)

---

### Why synthetic data?

**Privacy:** Real patient data cannot be included in public repos.

**Flexibility:** Synthetic data can show diverse scenarios:
- Different dates
- Various scores
- Edge cases (missing data, malformed values)
- Multiple sites/batches

**Your data:** Will have real values, but the **process is identical**.

---

### Can I use demo config for my data?

**Short answer:** No, you'll need to edit it.

**Steps:**
1. Copy `demo/demo.config.toml` to root as `config.toml`
2. Change `hospital = 9999` to your code
3. Update **every** `column = "..."` to match your Excel columns
4. Update `detection_column` for each PROM
5. Update `join_column` in `[lut]`
6. Test with a small file

See [README.md#configuration](../README.md#configuration) for complete guide.

---

## Testing Your Configuration

After adapting the demo config for your data:

```bash
# Test with DEBUG logging
python main.py --cfg config.toml \
  --input your_test_file.xlsx \
  --loglevel DEBUG \
  --log test.log

# Check log for column detection
grep "Detected PROM type" test.log
grep "Extracted" test.log
grep "Converted" test.log

# Validate output
python validate_xml.py output.xml ../example/XSD_LROI_PROMs_v9_2-20210608.xsd
```

---

## Next Steps

1. ✅ **Run the demo** to see how it works
2. ✅ **Review demo.config.toml** to understand structure
3. ✅ **Copy and edit config.toml** for your data
4. ✅ **Test with one small file** from your hospital
5. ✅ **Review DEBUG log** to verify mappings
6. ✅ **Validate XML** against XSD
7. ✅ **Process real data** in batches

---

## File Details

### demo.config.toml

Complete configuration file showing:
- Hospital settings
- Lookup table configuration
- OKS PROM definition (12 questions)
- OHS PROM definition (12 questions)
- Gender, laterality, and period conversions

**Size:** ~8 KB  
**Format:** TOML (human-readable)

---

### patient_demographics.xlsx

Lookup table with 15 synthetic patients:
- **PatientRecordID:** Join column (matches PROM files)
- **Gender:** "Male" or "Female"
- **Date of Birth:** Various dates (1954-1980)
- **Laterality:** "Left" or "Right"

**Size:** ~9 KB  
**Format:** Excel 2007+ (.xlsx)

---

### oks_export_site_a.xlsx

OKS questionnaires from "Site A":
- **Rows:** 5 questionnaires
- **Columns:** 16 (ID, date, 12 questions, phase, laterality)
- **Detection column:** "RecordNumber"

---

### oks_export_site_b.xlsx

OKS questionnaires from "Site B":
- **Rows:** 3 questionnaires
- **Same structure** as site_a
- **Different patients** (demonstrates multi-site)

---

### ohs_export_batch1.xlsx

OHS questionnaires batch 1:
- **Rows:** 4 questionnaires
- **Columns:** 16 (ID, date, 12 questions, phase, laterality)
- **Detection column:** "ObservationID"

---

### ohs_export_batch2.xlsx

OHS questionnaires batch 2:
- **Rows:** 3 questionnaires
- **Same structure** as batch1
- **Different collection period** (demonstrates batching)

---

## Summary

The demo shows:
- ✅ **Multiple files** → Single XML
- ✅ **Multiple PROMs** → Combined output (OKS + OHS)
- ✅ **Lookup table** → Demographics from separate file
- ✅ **Regex conversions** → Excel values → LROI codes
- ✅ **Auto-detection** → PROM type from column headers
- ✅ **Logging** → Text and Excel logs
- ✅ **Validation** → XSD compliance

**Use the demo to:**
1. Learn how the converter works
2. Understand configuration structure
3. See value conversions in action
4. Test your Python setup
5. Verify XSD validation
6. Explore logging features

**Then adapt for your hospital:**
- Edit `config.toml` with your column names
- Use your real LROI hospital code
- Test with your Excel exports
- Validate against XSD

---

**Demo Version:** v1.4.7 (2026-02-27)
