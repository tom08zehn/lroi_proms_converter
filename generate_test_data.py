#!/usr/bin/env python3
"""Generate test data for LROI PROMs Converter test suite.

Creates five Excel files in the same directory as this script:
  - test_demographics.xlsx
  - test_hoos.xlsx
  - test_koos.xlsx
  - test_oks.xlsx
  - test_eq5d5l.xlsx

Each PROM file covers boundary conditions for the follow-up period (FUP)
windows, plus edge cases (missing Patient ID, missing demographics lookup,
detection column empty).
"""
import openpyxl
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants ────────────────────────────────────────────────────────────
SURGERY_DATE = datetime(2025, 6, 15, 0, 0)
ADMISSION_DATE = datetime(2025, 5, 1, 10, 0, 0)
DOB = datetime(1970, 3, 15, 0, 0)
SURGEON = "Dr. Test"


# ── Helpers ──────────────────────────────────────────────────────────────
def comp_date(days):
    """Survey completion date = surgery date + days."""
    return SURGERY_DATE + timedelta(days=days)


def assign_date(days):
    """Survey assignment date = completion date - 5 days."""
    return comp_date(days) - timedelta(days=5)


def period_str(days):
    """Pre-Op if days <= 0, else Post-Op."""
    return "Pre-Op" if days <= 0 else "Post-Op"


def grouped_phase(fup_val, days):
    """Human-readable grouped phase from expected FUP value."""
    if fup_val == "-1":
        return "Pre-Op"
    mapping = {"3": "3-months", "6": "6-months", "12": "12-months"}
    if fup_val in mapping:
        return mapping[fup_val]
    return "Post-Op" if days > 0 else "Pre-Op"


def write_xlsx(filepath, headers, rows, sheet_name="Export"):
    """Create an Excel workbook with one sheet containing *headers* + *rows*."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(filepath)
    return len(rows)


# ── Demographics collection ──────────────────────────────────────────────
demo_entries = []


def add_demo(admission_id, patient_id, procedure_type, row_idx):
    """Register one demographics row."""
    demo_entries.append({
        "first_name": "Test",
        "last_name": f"Patient{patient_id}",
        "surgeon": SURGEON,
        "patient_id": str(patient_id),
        "admission_id": str(admission_id),
        "mrn": None,
        "dob": DOB,
        "gender": "Male" if row_idx % 2 == 1 else "Female",
        "procedure_type": procedure_type,
        "laterality": "Right" if row_idx % 2 == 1 else "Left",
        "surgery_date": SURGERY_DATE,
        "enrolled_date": ADMISSION_DATE,
        "activated_date": ADMISSION_DATE,
        "admission_date": ADMISSION_DATE,
        "discharge_date": ADMISSION_DATE,
        "zb_implant": False,
        "persona_iq": False,
        "rosa": False,
    })


# ======================================================================
# HOOS  (hip — FUPH windows: -1, 3, 12)
# ======================================================================
HOOS_HEADERS = [
    "First Name", "Last Name", "Operating Surgeon", "Patient ID",
    "Admission ID", "MRN", "Period", "Admission Date", "Surgery Date",
    "Date of Survey Assignment", "Date of Survey Completion",
    "Days to Survey Completion", "Procedure Type", "Laterality",
    "1. Going up or down stairs",
    "2. Walking on an uneven surface",
    "3. Rising from sitting",
    "4. Bending to floor/pick up an object",
    "5. Lying in bed (turning over, maintaining hip position)",
    "6. Sitting",
    "Interval Score", "Raw Score",
    "Test Comment", "Expected Result",
]

HOOS_PROC = "Total Hip Arthroplasty"
HOOS_PID_BASE = 90000
HOOS_AID_BASE = 80000

#  (row#, days, expected_fup, result, comment, overrides)
hoos_scenarios = [
    (1,  -182, "-1",  "valid",   "Pre-op lower boundary",                     {}),
    (2,    -1, "-1",  "valid",   "Pre-op near zero",                           {}),
    (3,     0, "-1",  "valid",   "Pre-op upper boundary",                      {}),
    (4,     1, "oor", "skipped", "Gap: between pre-op and 3mo",                {}),
    (5,    62, "oor", "skipped", "Just below 3-month",                         {}),
    (6,    63, "3",   "valid",   "3-month lower boundary",                     {}),
    (7,   110, "3",   "valid",   "3-month upper boundary",                     {}),
    (8,   111, "oor", "skipped", "Just above 3-month",                         {}),
    (9,   322, "oor", "skipped", "Just below 12-month",                        {}),
    (10,  323, "12",  "valid",   "12-month lower boundary",                    {}),
    (11,  407, "12",  "valid",   "12-month upper boundary",                    {}),
    (12,  408, "oor", "skipped", "Just above 12-month",                        {}),
    (13,    0, "-1",  "skipped", "Patient ID blank",                           {"patient_id_none": True}),
    (14,    0, "-1",  "skipped", "Admission ID not in demographics",           {"bad_aid": "99999"}),
    (15,    0, "n/a", "skipped", "Detection column empty - all PROM q None",   {"prom_none": True}),
]

hoos_rows = []
for rn, days, efup, eres, comment, ov in hoos_scenarios:
    pid = None if ov.get("patient_id_none") else str(HOOS_PID_BASE + rn)
    aid = ov.get("bad_aid", str(HOOS_AID_BASE + rn))

    if ov.get("prom_none"):
        qvals = [None] * 6
        iscore, rscore = None, None
    else:
        qvals = [2] * 6
        iscore, rscore = 50.0, 12

    lat = "Right" if rn % 2 == 1 else "Left"

    row = [
        "Test", f"Patient{HOOS_PID_BASE + rn}",
        SURGEON, pid, aid, None,
        period_str(days), ADMISSION_DATE, SURGERY_DATE,
        assign_date(days), comp_date(days), days,
        HOOS_PROC, lat,
    ] + qvals + [iscore, rscore, comment, eres]

    hoos_rows.append(row)

    # Add demographics unless this is the "missing demographics" row
    if "bad_aid" not in ov:
        add_demo(aid, HOOS_PID_BASE + rn, HOOS_PROC, rn)


# ======================================================================
# KOOS  (knee — FUPK windows: -1, 3, 6, 12)
# ======================================================================
KOOS_HEADERS = [
    "First Name", "Last Name", "Operating Surgeon", "Patient ID",
    "Admission ID", "MRN", "Period", "Admission Date", "Surgery Date",
    "Date of Survey Assignment", "Date of Survey Completion",
    "Days to Survey Completion", "Procedure Type", "Laterality",
    "1. How severe is your knee stiffness after first wakening in the morning?",
    "2. Twisting/pivoting on your knee",
    "3. Straightening knee fully",
    "4. Going up or down stairs",
    "5. Standing upright",
    "6. Rising from sitting",
    "7. Bending to floor/pick up an object",
    "Interval Score", "Raw Score",
    "Test Comment", "Expected Result",
]

KOOS_PROC = "Total Knee Arthroplasty"
KOOS_PID_BASE = 91000
KOOS_AID_BASE = 81000

koos_scenarios = [
    (1,  -182, "-1",  "valid",   "Pre-op lower boundary",                     {}),
    (2,    -1, "-1",  "valid",   "Pre-op near zero",                           {}),
    (3,     0, "-1",  "valid",   "Pre-op upper boundary",                      {}),
    (4,     1, "oor", "skipped", "Gap: pre-op to 3mo",                         {}),
    (5,    62, "oor", "skipped", "Just below 3-month",                         {}),
    (6,    63, "3",   "valid",   "3-month lower boundary",                     {}),
    (7,   110, "3",   "valid",   "3-month upper boundary",                     {}),
    (8,   111, "oor", "skipped", "Just above 3-month",                         {}),
    (9,   153, "oor", "skipped", "Just below 6-month",                         {}),
    (10,  154, "6",   "valid",   "6-month lower boundary",                     {}),
    (11,  210, "6",   "valid",   "6-month upper boundary",                     {}),
    (12,  211, "oor", "skipped", "Just above 6-month",                         {}),
    (13,  322, "oor", "skipped", "Just below 12-month",                        {}),
    (14,  323, "12",  "valid",   "12-month lower boundary",                    {}),
    (15,  407, "12",  "valid",   "12-month upper boundary",                    {}),
    (16,  408, "oor", "skipped", "Just above 12-month",                        {}),
    (17,    0, "-1",  "skipped", "Patient ID blank",                           {"patient_id_none": True}),
    (18,    0, "-1",  "skipped", "Admission ID not in demographics",           {"bad_aid": "99998"}),
    (19,    0, "n/a", "skipped", "Detection column empty - all PROM q None",   {"prom_none": True}),
]

koos_rows = []
for rn, days, efup, eres, comment, ov in koos_scenarios:
    pid = None if ov.get("patient_id_none") else str(KOOS_PID_BASE + rn)
    aid = ov.get("bad_aid", str(KOOS_AID_BASE + rn))

    if ov.get("prom_none"):
        qvals = [None] * 7
        iscore, rscore = None, None
    else:
        qvals = [2] * 7
        iscore, rscore = 50.0, 14

    lat = "Right" if rn % 2 == 1 else "Left"

    row = [
        "Test", f"Patient{KOOS_PID_BASE + rn}",
        SURGEON, pid, aid, None,
        period_str(days), ADMISSION_DATE, SURGERY_DATE,
        assign_date(days), comp_date(days), days,
        KOOS_PROC, lat,
    ] + qvals + [iscore, rscore, comment, eres]

    koos_rows.append(row)

    if "bad_aid" not in ov:
        add_demo(aid, KOOS_PID_BASE + rn, KOOS_PROC, rn)


# ======================================================================
# OKS  (knee — FUPK windows: -1, 3, 6, 12)
# ======================================================================
OKS_Q_HEADERS = [
    "How would you describe the pain you usually have from your knee?",
    "Have you had any trouble with washing and drying yourself (all over) because of your knee?",
    "Have you had any trouble getting in and out of a car or using public transportation because of your knee?",
    "For how long have you been able to walk before pain from your knee becomes severe? (with or without a cane)",
    "After a meal (sitting at a table), how painful has it been for you to stand up from a chair because of your knee?",
    "Have you been limping when walking because of your knee?",
    "Could you kneel down and get up again afterwards?",
    "Have you been troubled by pain from your knee in bed at night?",
    "How much has pain from your knee interfered with your usual work (including housework)?",
    "Have you felt that your knee might suddenly give out or let you down?",
    "Could you do the household shopping on your own?",
    "Could you walk down one flight of stairs?",
]

OKS_HEADERS = [
    "First Name", "Last Name", "Operating Surgeon", "Patient ID",
    "Admission ID", "MRN", "Period", "Admission Date", "Surgery Date",
    "Date of Survey Assignment", "Date of Survey Completion",
    "Days to Survey Completion", "test", "Procedure Type", "Laterality",
    "Grouped Phase",
] + OKS_Q_HEADERS + [
    "Oxford Knee Score",
    "Test Comment", "Expected Result",
]

OKS_PROC = "Total Knee Arthroplasty"
OKS_PID_BASE = 92000
OKS_AID_BASE = 82000

oks_scenarios = [
    (1,  -182, "-1",  "valid",   "Pre-op lower boundary",                     {}),
    (2,    -1, "-1",  "valid",   "Pre-op near zero",                           {}),
    (3,     0, "-1",  "valid",   "Pre-op upper boundary",                      {}),
    (4,     1, "oor", "skipped", "Gap: pre-op to 3mo",                         {}),
    (5,    62, "oor", "skipped", "Just below 3-month",                         {}),
    (6,    63, "3",   "valid",   "3-month lower boundary",                     {}),
    (7,   110, "3",   "valid",   "3-month upper boundary",                     {}),
    (8,   111, "oor", "skipped", "Just above 3-month",                         {}),
    (9,   153, "oor", "skipped", "Just below 6-month",                         {}),
    (10,  154, "6",   "valid",   "6-month lower boundary",                     {}),
    (11,  210, "6",   "valid",   "6-month upper boundary",                     {}),
    (12,  211, "oor", "skipped", "Just above 6-month",                         {}),
    (13,  322, "oor", "skipped", "Just below 12-month",                        {}),
    (14,  323, "12",  "valid",   "12-month lower boundary",                    {}),
    (15,  407, "12",  "valid",   "12-month upper boundary",                    {}),
    (16,  408, "oor", "skipped", "Just above 12-month",                        {}),
    (17,    0, "-1",  "skipped", "Patient ID blank",                           {"patient_id_none": True}),
    (18,    0, "-1",  "skipped", "Admission ID not in demographics",           {"bad_aid": "99997"}),
    (19,    0, "n/a", "skipped", "Detection column empty - all PROM q None",   {"prom_none": True}),
]

oks_rows = []
for rn, days, efup, eres, comment, ov in oks_scenarios:
    pid = None if ov.get("patient_id_none") else str(OKS_PID_BASE + rn)
    aid = ov.get("bad_aid", str(OKS_AID_BASE + rn))

    if ov.get("prom_none"):
        qvals = [None] * 12
        oks_total = None
        test_val = None
    else:
        qvals = [3] * 12       # valid OKS answer = 3
        oks_total = 36          # 12 * 3
        test_val = -13.5        # matches real data pattern

    gphase = grouped_phase(efup, days)
    lat = "Right" if rn % 2 == 1 else "Left"

    row = [
        "Test", f"Patient{OKS_PID_BASE + rn}",
        SURGEON, pid, aid, None,
        period_str(days), ADMISSION_DATE, SURGERY_DATE,
        assign_date(days), comp_date(days), days,
        test_val, OKS_PROC, lat, gphase,
    ] + qvals + [oks_total, comment, eres]

    oks_rows.append(row)

    if "bad_aid" not in ov:
        add_demo(aid, OKS_PID_BASE + rn, OKS_PROC, rn)


# ======================================================================
# EQ-5D-5L  (joint-dependent FUP: knee → FUPK, hip → FUPH, shoulder → FUPS)
# ======================================================================
EQ5D_Q_HEADERS = [
    "Your mobility TODAY",
    "Your self-care TODAY",
    "Your usual activities TODAY",
    "Your pain / discomfort TODAY",
    "Your anxiety / depression TODAY",
    "We would like to know how good or bad your health is TODAY",
]

EQ5D_HEADERS = [
    "First Name", "Last Name", "Patient ID", "Admission ID", "MRN",
    "Period", "Admission Date", "Operating Surgeon", "Surgery Date",
    "Discharge Date",
    "Date of Survey Assignment", "Date of Survey Completion",
    "Days to Survey Completion", "Grouped Phase", "Procedure Type",
    "Laterality",
] + EQ5D_Q_HEADERS + [
    "EQ-5D-5L Score", "EQ VAS Score",
    "Test Comment", "Expected Result",
]

EQ5D_PID_BASE = 93000
EQ5D_AID_BASE = 83000

#  (row#, days, procedure_type, fup_type, fup_val, result, comment, overrides)
eq5d_scenarios = [
    # ── Knee ──
    (1,  -182, "Total Knee Arthroplasty",     "FUPK", "-1",  "valid",   "Knee pre-op lower",                   {}),
    (2,     0, "Total Knee Arthroplasty",     "FUPK", "-1",  "valid",   "Knee pre-op upper",                   {}),
    (3,     1, "Total Knee Arthroplasty",     "FUPK", "oor", "skipped", "Knee out of range",                   {}),
    (4,    63, "Total Knee Arthroplasty",     "FUPK", "3",   "valid",   "Knee 3mo lower",                      {}),
    (5,   110, "Total Knee Arthroplasty",     "FUPK", "3",   "valid",   "Knee 3mo upper",                      {}),
    (6,   154, "Total Knee Arthroplasty",     "FUPK", "6",   "valid",   "Knee 6mo lower",                      {}),
    (7,   210, "Total Knee Arthroplasty",     "FUPK", "6",   "valid",   "Knee 6mo upper",                      {}),
    (8,   323, "Total Knee Arthroplasty",     "FUPK", "12",  "valid",   "Knee 12mo lower",                     {}),
    (9,   407, "Total Knee Arthroplasty",     "FUPK", "12",  "valid",   "Knee 12mo upper",                     {}),
    (10,  408, "Total Knee Arthroplasty",     "FUPK", "oor", "skipped", "Knee out of range",                   {}),
    (11,    0, "Partial Knee Arthroplasty",   "FUPK", "-1",  "valid",   "Partial knee (contains 'knee')",      {}),
    # ── Hip ──
    (12, -182, "Total Hip Arthroplasty",      "FUPH", "-1",  "valid",   "Hip pre-op lower",                    {}),
    (13,    0, "Total Hip Arthroplasty",      "FUPH", "-1",  "valid",   "Hip pre-op upper",                    {}),
    (14,   63, "Total Hip Arthroplasty",      "FUPH", "3",   "valid",   "Hip 3mo lower",                       {}),
    (15,  110, "Total Hip Arthroplasty",      "FUPH", "3",   "valid",   "Hip 3mo upper",                       {}),
    (16,  111, "Total Hip Arthroplasty",      "FUPH", "oor", "skipped", "Hip out of range (no 6mo for hip)",   {}),
    (17,  154, "Total Hip Arthroplasty",      "FUPH", "oor", "skipped", "Hip 6mo not valid for hip",           {}),
    (18,  323, "Total Hip Arthroplasty",      "FUPH", "12",  "valid",   "Hip 12mo lower",                      {}),
    (19,  407, "Total Hip Arthroplasty",      "FUPH", "12",  "valid",   "Hip 12mo upper",                      {}),
    # ── Shoulder ──
    (20,    0, "Total Shoulder Arthroplasty", "FUPS", "-1",  "valid",   "Shoulder pre-op",                     {}),
    (21,   63, "Total Shoulder Arthroplasty", "FUPS", "3",   "valid",   "Shoulder 3mo",                        {}),
    (22,  323, "Total Shoulder Arthroplasty", "FUPS", "12",  "valid",   "Shoulder 12mo",                       {}),
    (23,  111, "Total Shoulder Arthroplasty", "FUPS", "oor", "skipped", "Shoulder out of range",               {}),
    # ── Edge cases ──
    (24,    0, "Total Ankle Arthroplasty",    "n/a",  "n/a", "skipped", "Unknown procedure (no joint match)",  {}),
    (25,    0, None,                           "n/a",  "n/a", "skipped", "Procedure Type is None",              {}),
    (26,    0, "Total Knee Arthroplasty",     "FUPK", "-1",  "skipped", "Detection column empty",              {"prom_none": True}),
    (27,    0, "Total Knee Arthroplasty",     "FUPK", "-1",  "skipped", "Patient ID blank",                    {"patient_id_none": True}),
    (28,    0, "Total Knee Arthroplasty",     "FUPK", "-1",  "skipped", "Admission ID not in demographics",    {"bad_aid": "99996"}),
]

eq5d_rows = []
for rn, days, proc, fup_type, fup_val, eres, comment, ov in eq5d_scenarios:
    pid = None if ov.get("patient_id_none") else str(EQ5D_PID_BASE + rn)
    aid = ov.get("bad_aid", str(EQ5D_AID_BASE + rn))

    if ov.get("prom_none"):
        # All PROM question columns + scores empty → detection fails
        qvals = [None] * 6
        eq_score, vas_score = None, None
    else:
        qvals = [2, 1, 1, 2, 1, 84]
        eq_score, vas_score = 21121, 84

    gphase = grouped_phase(fup_val, days)
    lat = "Right" if rn % 2 == 1 else "Left"

    row = [
        "Test", f"Patient{EQ5D_PID_BASE + rn}",
        pid, aid, None,
        period_str(days), ADMISSION_DATE, SURGEON, SURGERY_DATE,
        ADMISSION_DATE,                      # Discharge Date
        assign_date(days), comp_date(days), days,
        gphase, proc, lat,
    ] + qvals + [eq_score, vas_score, comment, eres]

    eq5d_rows.append(row)

    if "bad_aid" not in ov:
        add_demo(aid, EQ5D_PID_BASE + rn, proc, rn)


# ======================================================================
# Write PROM files
# ======================================================================
counts = {}
counts["test_hoos.xlsx"] = write_xlsx(
    OUTPUT_DIR / "test_hoos.xlsx", HOOS_HEADERS, hoos_rows)
counts["test_koos.xlsx"] = write_xlsx(
    OUTPUT_DIR / "test_koos.xlsx", KOOS_HEADERS, koos_rows)
counts["test_oks.xlsx"] = write_xlsx(
    OUTPUT_DIR / "test_oks.xlsx", OKS_HEADERS, oks_rows)
counts["test_eq5d5l.xlsx"] = write_xlsx(
    OUTPUT_DIR / "test_eq5d5l.xlsx", EQ5D_HEADERS, eq5d_rows)


# ======================================================================
# Demographics
# ======================================================================
DEMO_HEADERS = [
    "First Name", "Last Name", "Operating Surgeon", "Patient ID",
    "Admission ID", "MRN", "Date of Birth", "Gender", "Procedure Type",
    "Laterality", "Surgery Date", "Enrolled Date", "Activated Date",
    "Admission Date", "Discharge Date", "ZB Implant",
    "Persona IQ Implant", "ROSA",
]

demo_data_rows = []
for d in demo_entries:
    demo_data_rows.append([
        d["first_name"], d["last_name"], d["surgeon"],
        d["patient_id"], d["admission_id"], d["mrn"],
        d["dob"], d["gender"], d["procedure_type"], d["laterality"],
        d["surgery_date"], d["enrolled_date"], d["activated_date"],
        d["admission_date"], d["discharge_date"],
        d["zb_implant"], d["persona_iq"], d["rosa"],
    ])

counts["test_demographics.xlsx"] = write_xlsx(
    OUTPUT_DIR / "test_demographics.xlsx", DEMO_HEADERS, demo_data_rows)


# ======================================================================
# Summary
# ======================================================================
print("\n=== Test Data Generation Complete ===")
for fname, count in sorted(counts.items()):
    print(f"  {fname}: {count} data rows")
print(f"\n  Total demographics entries: {len(demo_entries)}")
print(f"  Files written to: {OUTPUT_DIR}")
