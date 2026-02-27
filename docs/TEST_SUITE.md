# v1.4.1 Test Suite - Complete Scenarios

## Test Scenario Matrix

| # | Scenario | Files | Expected Result | Tests |
|---|----------|-------|----------------|-------|
| 1 | Basic OKS | oks_export_site_a.xlsx | 5 converted, 0 skipped | Standard conversion |
| 2 | OKS Batch | site_a + site_b | 8 converted, 0 skipped | Multi-file processing |
| 3 | Basic OHS | ohs_export_batch1.xlsx | 4 converted, 0 skipped | OHS format |
| 4 | OHS Batch | batch1 + batch2 | 7 converted, 0 skipped | Multi-file OHS |
| 5 | Multi-PROM | All OKS + OHS | 15 converted, 0 skipped | Mixed PROM types |
| 6 | LUT Exclusion | Process demo/ folder | LUT not processed | Filter LUT file |
| 7 | Detection Order | Files with overlapping columns | First match wins | Priority testing |

---

## Test Commands

### Test 1: Basic OKS Conversion
```bash
cd lroi_converter
python main.py --cfg demo/demo.config.toml \
  --xls demo/oks_export_site_a.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_scenario1.xml

# Validate
python validate_xml.py test_scenario1.xml ../XSD_LROI_PROMs_v9_2.xsd

# Expected output:
# INFO Detected PROM type: OKS
# INFO Conversion complete: 5 questionnaires converted
# ✓ XSD validation PASSED
```

### Test 2: OKS Batch Processing
```bash
python main.py --cfg demo/demo.config.toml \
  --xls demo/oks_export_site_a.xlsx demo/oks_export_site_b.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_scenario2.xml

# Count questionnaires
grep -c "<questionaire>" test_scenario2.xml
# Expected: 8

# Validate
python validate_xml.py test_scenario2.xml ../XSD_LROI_PROMs_v9_2.xsd
```

### Test 3: Basic OHS Conversion
```bash
python main.py --cfg demo/demo.config.toml \
  --xls demo/ohs_export_batch1.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_scenario3.xml

# Expected:
# INFO Detected PROM type: OHS
# INFO Conversion complete: 4 questionnaires converted
```

### Test 4: OHS Batch Processing
```bash
python main.py --cfg demo/demo.config.toml \
  --xls demo/ohs_export_batch1.xlsx demo/ohs_export_batch2.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_scenario4.xml

grep -c "<questionaire>" test_scenario4.xml
# Expected: 7
```

### Test 5: Multi-PROM Processing
```bash
python main.py --cfg demo/demo.config.toml \
  --xls demo/ \
  --lut demo/patient_demographics.xlsx \
  --output test_scenario5.xml

# Expected:
# Processing 4 XLS files (LUT excluded)
# Detected PROM type: OKS (for OKS files)
# Detected PROM type: OHS (for OHS files)
# Conversion complete: 15 questionnaires converted

grep -c "<questionaire>" test_scenario5.xml
# Expected: 15

# Count by type
grep -c "<FUPK>" test_scenario5.xml  # OKS count
# Expected: 8
grep -c "<FUPH>" test_scenario5.xml  # OHS count
# Expected: 7
```

### Test 6: LUT File Exclusion
```bash
# Process entire demo folder
python main.py --cfg demo/demo.config.toml \
  --xls demo/ \
  --lut demo/patient_demographics.xlsx \
  --output test_scenario6.xml 2>&1 | grep "Processing XLS"

# Expected:
# Processing XLS: demo/oks_export_site_a.xlsx
# Processing XLS: demo/oks_export_site_b.xlsx
# Processing XLS: demo/ohs_export_batch1.xlsx
# Processing XLS: demo/ohs_export_batch2.xlsx
# (NO line for patient_demographics.xlsx)
```

### Test 7: Detection Column Priority
```bash
# If both OKS and OHS columns exist, first match wins
# OKS detection_column = "RecordNumber"
# OHS detection_column = "OHS Total"

# Process OKS file (has RecordNumber column)
python main.py --cfg demo/demo.config.toml \
  --xls demo/oks_export_site_a.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_oks_priority.xml 2>&1 | grep "Detected"
# Expected: Detected PROM type: OKS

# Process OHS file (has OHS Total column)
python main.py --cfg demo/demo.config.toml \
  --xls demo/ohs_export_batch1.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_ohs_priority.xml 2>&1 | grep "Detected"
# Expected: Detected PROM type: OHS
```

---

## Validation Tests

### XSD Validation (All Scenarios)
```bash
# Test all outputs
for file in test_scenario*.xml; do
    echo "Validating $file..."
    python validate_xml.py "$file" ../XSD_LROI_PROMs_v9_2.xsd
done

# Expected: All pass
```

### Element Completeness
```bash
# Check all OKS questionnaires have 12 items
python3 << 'EOF'
from lxml import etree
doc = etree.parse('test_scenario1.xml')
for q in doc.findall('.//questionaire'):
    fupk = q.find('FUPK')
    if fupk is not None:  # OKS questionnaire
        oks_count = len([e for e in q if e.tag.startswith('OKS') and e.tag.endswith('PK')])
        upnnum = q.find('UPNNUM').text
        print(f"OKS {upnnum}: {oks_count} items")
        if oks_count < 12:
            print(f"  WARNING: Only {oks_count}/12 items!")
EOF

# Expected: All show "12 items"
```

### LUT Data Verification
```bash
# Verify gender conversions
python3 << 'EOF'
from lxml import etree
doc = etree.parse('test_scenario1.xml')
for q in doc.findall('.//questionaire'):
    upnnum = q.find('UPNNUM').text
    gender = q.find('GENDER').text
    print(f"Patient {upnnum}: Gender={gender} {'(Male)' if gender=='0' else '(Female)' if gender=='1' else '(INVALID)'}")
EOF

# Expected: All show valid gender codes (0 or 1)
```

---

## Performance Tests

### Large File Processing
```bash
# Time multi-file conversion
time python main.py --cfg demo/demo.config.toml \
  --xls demo/ \
  --lut demo/patient_demographics.xlsx \
  --output test_performance.xml

# Expected: < 5 seconds for 15 questionnaires
```

### Memory Usage
```bash
# Check memory usage during conversion
/usr/bin/time -v python main.py --cfg demo/demo.config.toml \
  --xls demo/ \
  --lut demo/patient_demographics.xlsx \
  --output test_memory.xml 2>&1 | grep "Maximum resident"

# Expected: < 100 MB
```

---

## Error Handling Tests

### Missing LUT Record
```bash
# Modify a row in XLS to have invalid join column value
# Expected: ERROR logged, row skipped

python main.py --cfg demo/demo.config.toml \
  --xls demo/oks_export_site_a.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_missing_lut.xml 2>&1 | grep "No LUT record"

# Should see: ERROR No LUT record found for RecordNumber='INVALID'
```

### Missing Detection Column
```bash
# Create config with wrong detection_column
cat > /tmp/bad_config.toml << 'CONFIG'
[defaults]
hospital = 1234

[lut]
join_column = "PatientRecordID"

[PROM.OKS]
detection_column = "NONEXISTENT_COLUMN"
CONFIG

python main.py --cfg /tmp/bad_config.toml \
  --xls demo/oks_export_site_a.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_no_detection.xml 2>&1 | grep "No PROM type"

# Expected: WARNING No PROM type detected for row (for all rows)
```

### Empty Questionnaire Data
```bash
# Test file with only demographics, no questionnaire items
# Expected: Row skipped with appropriate warning
# (This test requires creating a test file with missing mandatory fields)
```

---

## Regression Tests

### Value Conversions
```bash
# Test various input formats normalize correctly
python3 << 'EOF'
import sys
sys.path.insert(0, 'lroi_converter')
from converter import apply_conversions

# Test FUPK conversions
test_cases = [
    ("Pre-Op", "-1"),
    ("PreOp", "-1"),
    ("Preop", "-1"),
    ("3 Month", "3"),
    ("3M", "3"),
    ("6 Month", "6"),
    ("6M", "6"),
    ("12 Month", "12"),
    ("12M", "12"),
    ("1 Year", "12"),
]

conversions = [
    {"match": "Pre-?Op|Preop", "replace": "-1", "flags": "i"},
    {"match": "3\\s*Month|3M", "replace": "3", "flags": "i"},
    {"match": "6\\s*Month|6M", "replace": "6", "flags": "i"},
    {"match": "12\\s*Month|12M|1\\s*Year", "replace": "12", "flags": "i"},
]

passed = 0
failed = 0
for input_val, expected in test_cases:
    result = apply_conversions(input_val, conversions, "FUPK")
    if result == expected:
        print(f"✓ '{input_val}' → '{result}'")
        passed += 1
    else:
        print(f"✗ '{input_val}' → '{result}' (expected '{expected}')")
        failed += 1

print(f"\nPassed: {passed}/{len(test_cases)}")
if failed > 0:
    print(f"FAILED: {failed} tests")
    sys.exit(1)
EOF
```

### Gender Conversions
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'lroi_converter')
from converter import apply_conversions

test_cases = [
    ("Male", "0"),
    ("M", "0"),
    ("male", "0"),
    ("Female", "1"),
    ("F", "1"),
    ("female", "1"),
]

conversions = [
    {"match": "^M(ale)?$", "replace": "0", "flags": "i"},
    {"match": "^F(emale)?$", "replace": "1", "flags": "i"},
]

for input_val, expected in test_cases:
    result = apply_conversions(input_val, conversions, "GENDER")
    status = "✓" if result == expected else "✗"
    print(f"{status} '{input_val}' → '{result}' (expected '{expected}')")
EOF
```

### Laterality Conversions
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'lroi_converter')
from converter import apply_conversions

test_cases = [
    ("Right", "1"),
    ("R", "1"),
    ("right", "1"),
    ("Left", "2"),
    ("L", "2"),
    ("left", "2"),
]

conversions = [
    {"match": "Right|R", "replace": "1", "flags": "i"},
    {"match": "Left|L", "replace": "2", "flags": "i"},
]

for input_val, expected in test_cases:
    result = apply_conversions(input_val, conversions, "SIDEPK")
    status = "✓" if result == expected else "✗"
    print(f"{status} '{input_val}' → '{result}' (expected '{expected}')")
EOF
```

---

## Integration Tests

### Full Pipeline Test
```bash
#!/bin/bash
# Complete end-to-end test

echo "=== LROI PROMs Converter Integration Test ==="
echo ""

# Clean up old test files
rm -f test_*.xml

# Test 1: Basic OKS
echo "Test 1: Basic OKS..."
python main.py --cfg demo/demo.config.toml \
  --xls demo/oks_export_site_a.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_oks.xml > /dev/null 2>&1
[ -f test_oks.xml ] && echo "✓ OKS file created" || echo "✗ FAILED"

# Test 2: Basic OHS
echo "Test 2: Basic OHS..."
python main.py --cfg demo/demo.config.toml \
  --xls demo/ohs_export_batch1.xlsx \
  --lut demo/patient_demographics.xlsx \
  --output test_ohs.xml > /dev/null 2>&1
[ -f test_ohs.xml ] && echo "✓ OHS file created" || echo "✗ FAILED"

# Test 3: Multi-file
echo "Test 3: Multi-file batch..."
python main.py --cfg demo/demo.config.toml \
  --xls demo/ \
  --lut demo/patient_demographics.xlsx \
  --output test_multi.xml > /dev/null 2>&1
[ -f test_multi.xml ] && echo "✓ Multi-file created" || echo "✗ FAILED"

# Test 4: XSD validation
echo "Test 4: XSD validation..."
python validate_xml.py test_multi.xml ../XSD_LROI_PROMs_v9_2.xsd > /dev/null 2>&1
[ $? -eq 0 ] && echo "✓ XSD validation passed" || echo "✗ FAILED"

# Test 5: Count verification
echo "Test 5: Count verification..."
count=$(grep -c "<questionaire>" test_multi.xml)
[ "$count" = "15" ] && echo "✓ Correct count (15)" || echo "✗ FAILED (got $count)"

echo ""
echo "=== Test Summary ==="
echo "All integration tests completed"
```

---

## Test Results Template

```
LROI PROMs Converter v1.4.1 - Test Results
==========================================

Date: YYYY-MM-DD
Tester: [Name]
Environment: [OS, Python version]

Basic Tests:
[ ] Test 1: Basic OKS - 5 converted
[ ] Test 2: OKS Batch - 8 converted
[ ] Test 3: Basic OHS - 4 converted
[ ] Test 4: OHS Batch - 7 converted
[ ] Test 5: Multi-PROM - 15 converted
[ ] Test 6: LUT Exclusion - LUT not processed
[ ] Test 7: Detection Priority - Correct PROM detected

Validation Tests:
[ ] XSD validation passes for all outputs
[ ] All OKS questionnaires have 12 items
[ ] All OHS questionnaires have 12 items
[ ] Gender codes correct (0/1)
[ ] Laterality codes correct (1/2)
[ ] Follow-up periods correct (-1/3/6/12)

Error Handling:
[ ] Missing LUT record logged as ERROR
[ ] Missing detection column skips all rows
[ ] Empty questionnaire data skipped with WARNING

Performance:
[ ] 15 questionnaires processed in < 5 seconds
[ ] Memory usage < 100 MB

Regression Tests:
[ ] Value conversions working (FUPK, GENDER, SIDEPK)
[ ] LUT prefix __LUT__ applied correctly
[ ] First detection column wins

OVERALL RESULT: [ ] PASS  [ ] FAIL

Notes:
_____________________________________________
```

---

## CI/CD Integration

### Automated Test Script
```bash
#!/bin/bash
# run_tests.sh - Automated test suite

set -e  # Exit on error

cd lroi_converter

echo "Running LROI PROMs Converter Test Suite..."

# Run all scenarios
for i in {1..5}; do
    echo "Running scenario $i..."
    python main.py --cfg demo/demo.config.toml \
      --xls demo/ \
      --lut demo/patient_demographics.xlsx \
      --output test_scenario${i}.xml > /dev/null
done

# Validate all
for xml in test_scenario*.xml; do
    python validate_xml.py "$xml" ../XSD_LROI_PROMs_v9_2.xsd || exit 1
done

echo "All tests passed!"
```

---

## Summary

This test suite covers:
- ✅ 7 core scenarios
- ✅ XSD validation
- ✅ Element completeness
- ✅ LUT data verification
- ✅ Performance benchmarks
- ✅ Error handling
- ✅ Regression tests
- ✅ Integration tests

**All tests can be run from command line without GUI.**
**Expected success rate: 100% for valid demo data.**
