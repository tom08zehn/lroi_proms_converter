# Demo Files — LROI PROMs Converter

This folder contains synthetic demo data to demonstrate the converter's capabilities.

## Files

| File | Description | Rows | PROM Type |
|------|-------------|------|-----------|
| `patient_demographics.xlsx` | Lookup table with 15 fake patients | 15 | N/A (LUT) |
| `oks_export_site_a.xlsx` | OKS export from Site A (2 pre-op + 2 follow-up) | 5 | OKS |
| `oks_export_site_b.xlsx` | OKS export from Site B (3 pre-op) | 3 | OKS |
| `ohs_export_batch1.xlsx` | OHS export batch 1 (4 pre-op) | 4 | OHS |
| `ohs_export_batch2.xlsx` | OHS export batch 2 (1 pre-op + 2 follow-up) | 3 | OHS |

**Total:** 15 questionnaires across 2 PROM types (OKS + OHS)

## Key Differences from Real Config

The demo uses **different column names** than `config.toml` to demonstrate the flexible join column system:

| Column Purpose | LUT File | OKS Files | OHS Files |
|----------------|----------|-----------|-----------|
| **Join column** | `PatientRecordID` | `RecordNumber` | `CaseID` |
| Patient ID | — | `Patient ID` | `Patient ID` |
| Survey date | — | `Survey Date` | `Completion Date` |
| Follow-up phase | — | `Follow-up Phase` | `Assessment Phase` |
| Laterality | `Laterality` | `Side` | `Hip Side` |

This demonstrates that:
- The LUT join column (`PatientRecordID`) is configured once in `[lut].join_column`
- Each PROM's XLS join column is configured separately in `[PROM.<key>.lut_lookup].join_column`
- Column names in XLS files don't need to match LUT column names
- Different PROM types can use completely different column naming schemes

## Running the Demo

From the `lroi_converter/` directory:

```bash
# Single command to convert all demo files
python main.py --cfg demo.config.toml --xls demo/ --lut demo/patient_demographics.xlsx --log 1
```

Expected output:
- **15 questionnaires** converted (8 OKS + 7 OHS)
- XML file: `demo_output.xml` (or timestamped name per config)
- Text log: `2026-02-19_main_demo.log`
- Excel log: `2026-02-19_main_demo.xlsx`

## What Gets Converted

### OKS (8 questionnaires)
- Site A: 3 pre-op + 2 follow-up (3 month)
- Site B: 3 pre-op

### OHS (7 questionnaires)
- Batch 1: 4 pre-op
- Batch 2: 1 pre-op + 2 follow-up (3 month)

## Patient Data

All data is **completely synthetic**:
- Names: Generic (Alice, Bob, Carol, etc.)
- IDs: Sequential (REC001–REC015)
- Dates: 2024-2025
- Scores: Random but realistic values

**This data cannot be traced to any real patients.**

## Validation

The demo output validates successfully against the official LROI XSD schema (`XSD_LROI_PROMs_v9_2-20210608.xsd`).

## Adapting for Your Organization

1. Copy `demo.config.toml` to `my_hospital.config.toml`
2. Update `hospital = 9999` to your LROI institution code
3. Update all column names to match **your** export system's actual column headers
4. Test with a small sample of real (but anonymized) data
5. Run: `python main.py --cfg my_hospital.config.toml --xls your_data/ --lut your_lut.xlsx --log 1`
