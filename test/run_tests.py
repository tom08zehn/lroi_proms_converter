#!/usr/bin/env python3
"""
run_tests.py — Test suite for the LROI PROMs Converter.

Runs the converter on test data and compares the output XML against a
pre-generated reference file.  Any difference indicates a regression.

Usage:
    python run_tests.py                     # compare against reference
    python run_tests.py --update-reference  # regenerate reference XML

Exit codes:
    0 = all tests passed
    1 = differences found (regression)
    2 = reference file missing (run with --update-reference first)
"""

from __future__ import annotations

import difflib
import logging
import sys
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_DIR / "config.toml"

TEST_INPUT_FILES = [
    SCRIPT_DIR / "test_hoos.xlsx",
    SCRIPT_DIR / "test_koos.xlsx",
    SCRIPT_DIR / "test_oks.xlsx",
    SCRIPT_DIR / "test_eq5d5l.xlsx",
]
TEST_LUT_FILE    = SCRIPT_DIR / "test_demographics.xlsx"
REFERENCE_XML    = SCRIPT_DIR / "reference_output.xml"
ACTUAL_XML       = SCRIPT_DIR / "actual_output.xml"


def load_config():
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef]
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def run_conversion(config, output_path: Path):
    """Run the converter and return (n_converted, n_skipped)."""
    # Add project dir to path so converter module is importable
    if str(PROJECT_DIR) not in sys.path:
        sys.path.insert(0, str(PROJECT_DIR))

    from logger import setup_logger
    from converter import convert

    setup_logger(level=logging.WARNING)

    _, n_converted, n_skipped = convert(
        xls_paths=[str(p) for p in TEST_INPUT_FILES],
        config=config,
        lut_path=str(TEST_LUT_FILE),
        output_path=str(output_path),
    )
    return n_converted, n_skipped


def normalize_xml(xml_path: Path) -> list[str]:
    """Read XML and return normalized lines for comparison."""
    text = xml_path.read_text(encoding="utf-8")
    # Normalize line endings and strip trailing whitespace
    return [line.rstrip() for line in text.splitlines()]


def main():
    update_mode = "--update-reference" in sys.argv

    # ── Check prerequisites ──────────────────────────────────────────────
    missing = [p for p in TEST_INPUT_FILES + [TEST_LUT_FILE, CONFIG_PATH] if not p.exists()]
    if missing:
        print("ERROR: Missing test files:")
        for p in missing:
            print(f"  {p}")
        return 2

    if not update_mode and not REFERENCE_XML.exists():
        print(f"ERROR: Reference file not found: {REFERENCE_XML}")
        print(f"Run with --update-reference to generate it.")
        return 2

    # ── Run conversion ───────────────────────────────────────────────────
    config = load_config()
    output_path = REFERENCE_XML if update_mode else ACTUAL_XML
    n_conv, n_skip = run_conversion(config, output_path)

    print(f"Converted: {n_conv}  Skipped: {n_skip}")

    if update_mode:
        print(f"Reference updated: {REFERENCE_XML}")
        print(f"Commit this file to track future regressions.")
        return 0

    # ── Compare against reference ────────────────────────────────────────
    ref_lines  = normalize_xml(REFERENCE_XML)
    act_lines  = normalize_xml(ACTUAL_XML)

    if ref_lines == act_lines:
        print("PASSED: Output matches reference exactly.")
        # Clean up actual output on success
        ACTUAL_XML.unlink(missing_ok=True)
        return 0

    # Show diff
    diff = list(difflib.unified_diff(
        ref_lines, act_lines,
        fromfile="reference_output.xml",
        tofile="actual_output.xml",
        lineterm="",
    ))
    print(f"FAILED: {len(diff)} diff lines. Showing first 60:")
    print()
    for line in diff[:60]:
        print(line)
    if len(diff) > 60:
        print(f"... ({len(diff) - 60} more lines)")

    print()
    print(f"Full actual output saved to: {ACTUAL_XML}")
    print(f"Compare manually:  diff {REFERENCE_XML} {ACTUAL_XML}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
