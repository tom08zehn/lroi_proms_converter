# Demo Scenarios for LROI PROMs Converter

This document describes all demo scenarios included in the `demo/` folder.

## Scenario Overview

Each scenario demonstrates a specific use case or edge case:

| Scenario | File | Purpose |
|----------|------|---------|
| 1 | `oks_export_site_a.xlsx` | Basic OKS conversion (5 rows) |
| 2 | `oks_export_site_b.xlsx` | OKS batch processing (3 rows, same LUT) |
| 3 | `ohs_export_batch1.xlsx` | Basic OHS conversion (4 rows) |
| 4 | `ohs_export_batch2.xlsx` | OHS batch processing (3 rows) |
| 5 | `patient_demographics.xlsx` | LUT file for all scenarios |

---

## Scenario Details

### Scenario 1: Basic OKS Conversion
**File:** `oks_export_site_a.xlsx`  
**Rows:** 5 questionnaires  
**Features:**
- Standard OKS questionnaire format
- Mix of Pre-Op and 3 Month follow-ups
- All mandatory fields present
- Uses LUT for demographics

**Expected Output:**
- 5 questionnaires converted
- 0 skipped
- All 12 OKS items populated
- Gender, DOB, Laterality from LUT
- XSD validation passes

**Config Section:** `[PROM.OKS]`

---

### Scenario 2: OKS Batch Processing
**File:** `oks_export_site_b.xlsx`  
**Rows:** 3 questionnaires  
**Features:**
- Same format as Scenario 1
- Different patient records
- Demonstrates batch processing with same LUT
- Tests 6 Month and 12 Month follow-ups

**Expected Output:**
- 3 questionnaires converted
- 0 skipped
- Combined with Scenario 1 = 8 total OKS questionnaires
- XSD validation passes

**Usage:**
```bash
python main.py --cfg demo.config.toml \
  --xls demo/oks_export_site_a.xlsx demo/oks_export_site_b.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_oks_batch.xml
```

---

### Scenario 3: Basic OHS Conversion
**File:** `ohs_export_batch1.xlsx`  
**Rows:** 4 questionnaires  
**Features:**
- Oxford Hip Score format
- Different detection column (OHS Total)
- Different follow-up codes (FUPH vs FUPK)
- Different laterality field (SIDEP vs SIDEPK)

**Expected Output:**
- 4 questionnaires converted
- 0 skipped
- All 12 OHS items populated
- XSD validation passes

**Config Section:** `[PROM.OHS]`

---

### Scenario 4: OHS Batch Processing
**File:** `ohs_export_batch2.xlsx`  
**Rows:** 3 questionnaires  
**Features:**
- Same format as Scenario 3
- Different patients
- Combined demonstrates multi-file OHS processing

**Expected Output:**
- 3 questionnaires converted
- 0 skipped
- Combined with Scenario 3 = 7 total OHS questionnaires

---

### Scenario 5: Multi-PROM Batch
**Files:** All OKS + OHS files  
**Features:**
- Processes both PROM types in single run
- Tests detection_column uniqueness
- Validates LUT works across PROM types

**Expected Output:**
- 15 total questionnaires (8 OKS + 7 OHS)
- 0 skipped
- XSD validation passes
- Demonstrates first-match-wins when detection columns overlap

**Usage:**
```bash
python main.py --cfg demo.config.toml \
  --xls demo/ \
  --lut demo/patient_demographics.xlsx \
  --output test_all.xml
```

---

## Test Matrix

| Test | OKS | OHS | Total | Skipped | XSD |
|------|-----|-----|-------|---------|-----|
| Single OKS | 5 | 0 | 5 | 0 | ✓ |
| Batch OKS | 8 | 0 | 8 | 0 | ✓ |
| Single OHS | 0 | 4 | 4 | 0 | ✓ |
| Batch OHS | 0 | 7 | 7 | 0 | ✓ |
| Multi-PROM | 8 | 7 | 15 | 0 | ✓ |

---

## Edge Cases Covered

### 1. ✅ LUT File Exclusion
**Test:** Process `demo/` folder containing LUT file  
**Expected:** LUT file not processed as questionnaire  
**Result:** Only .xlsx files with detection columns are processed

### 2. ✅ Missing Mandatory Fields
**Test:** Row without UPNNUM or DATUMINVUL  
**Expected:** Row skipped with WARNING  
**Result:** Logged as WARNING, not included in output

### 3. ✅ Detection Column Uniqueness
**Test:** Files with overlapping column names  
**Expected:** First matching detection_column wins  
**Result:** OKS uses "RecordNumber", OHS uses "OHS Total"

### 4. ✅ LUT Lookup Failures
**Test:** Join column value not in LUT  
**Expected:** ERROR logged, row skipped  
**Result:** "No LUT record found" error

### 5. ✅ Value Conversions
**Test:** Various input formats (Pre-Op, pre-op, Preop, 3M, 3 Month)  
**Expected:** All normalize to correct codes  
**Result:** Regex patterns handle variations

### 6. ✅ Empty Elements
**Test:** Optional fields with no data  
**Expected:** Elements omitted from XML (except GENDER)  
**Result:** Clean XML without empty elements

---

## Running All Tests

### Quick Test (Single File)
```bash
python main.py --cfg demo.config.toml \
  --xls demo/oks_export_site_a.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test.xml

# Validate
python validate_xml.py test.xml XSD_LROI_PROMs_v9_2.xsd
```

### Full Test (All Scenarios)
```bash
# Process all files
python main.py --cfg demo.config.toml \
  --xls demo/ \
  --lut demo/patient_demographics.xlsx \
  --output test_all.xml

# Validate
python validate_xml.py test_all.xml XSD_LROI_PROMs_v9_2.xsd

# Check counts
grep -c "<questionaire>" test_all.xml
# Expected: 15
```

### Individual PROM Tests
```bash
# OKS only
python main.py --cfg demo.config.toml \
  --xls demo/oks_export_site_a.xlsx demo/oks_export_site_b.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_oks.xml

# OHS only
python main.py --cfg demo.config.toml \
  --xls demo/ohs_export_batch1.xlsx demo/ohs_export_batch2.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_ohs.xml
```

---

## Success Criteria

A successful conversion should:
1. ✅ Convert expected number of questionnaires
2. ✅ Skip 0 rows (all test data is valid)
3. ✅ Pass XSD validation
4. ✅ Populate all mandatory elements
5. ✅ Correctly merge LUT data with `__LUT__` prefix
6. ✅ Apply value conversions correctly
7. ✅ Handle both OKS and OHS formats
8. ✅ Exclude LUT file from processing

---

## Extending Scenarios

To add new scenarios:

1. Create XLS file in `demo/` folder
2. Add config section in `demo.config.toml`
3. Set unique `detection_column`
4. Define element mappings
5. Add entry to this document
6. Test with `validate_xml.py`

---

## Common Issues

### Issue: "No PROM type detected"
**Cause:** detection_column not found in XLS  
**Fix:** Update detection_column in config to match actual column name

### Issue: "No LUT record found"
**Cause:** join_column value doesn't match LUT  
**Fix:** Check join_column values in both XLS and LUT

### Issue: "Row skipped: missing UPNNUM"
**Cause:** Patient ID column not mapped  
**Fix:** Check UPNNUM column mapping in config

### Issue: XSD validation fails
**Cause:** Missing mandatory elements or wrong order  
**Fix:** Check XSD_ELEMENT_ORDER in converter.py

---

## Summary

The demo scenarios provide comprehensive coverage of:
- ✅ Basic conversion (OKS, OHS)
- ✅ Batch processing (multiple files)
- ✅ Multi-PROM processing (mixed types)
- ✅ LUT lookups and merging
- ✅ Value conversions
- ✅ Edge cases and error handling

All test data is valid and should convert successfully with 0 rows skipped.
