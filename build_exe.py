#!/usr/bin/env python3
"""
build_exe.py – Build a self-contained Windows .exe for the LROI PROMs Converter.

Run this script on a Windows machine (or Wine/cross-compile environment):
    python build_exe.py

What it does
------------
1.  Verifies PyInstaller is installed (offers to install it if not).
2.  Runs PyInstaller to produce a single-file executable:
        dist/lroi_converter/lroi_converter.exe
3.  Copies config.toml next to the .exe so hospitals can edit it without
    rebuilding the binary.
4.  Prints a short summary of what to ship to end-users.

Why a Python build script instead of a .spec or shell script?
-------------------------------------------------------------
* Works identically on Windows, macOS and Linux.
* Can be run from any directory.
* Easy to extend (e.g. code-signing, version stamping, zip packaging).
* The logic is readable and version-controlled alongside the source.

Requirements
------------
    pip install ".[build]"      # installs pyinstaller (see pyproject.toml)
    # or:
    pip install pyinstaller

PyInstaller must be run on Windows to produce a Windows .exe.
Use a Windows machine, a Windows VM, or GitHub Actions with windows-latest.
"""

from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

# Root of the project (directory this script lives in)
PROJECT_DIR  = Path(__file__).parent.resolve()

# The CLI/GUI entry point
ENTRY_POINT  = PROJECT_DIR / "main.py"

# Application name – becomes the .exe filename
APP_NAME     = "lroi_converter"

# Output directory for the built artefacts
DIST_DIR     = PROJECT_DIR / "dist" / APP_NAME

# Files that must sit next to the .exe at runtime
#   (key = source path, value = destination filename inside DIST_DIR)
EXTRA_FILES: dict[Path, str] = {
    PROJECT_DIR / "config.toml": "config.toml",
}

# Optional application icon (.ico file).  Set to None if you have no icon.
ICON_FILE: Path | None = PROJECT_DIR / "icon.ico"  # ignored if file absent

# Hidden imports that PyInstaller's static analysis sometimes misses
HIDDEN_IMPORTS = [
    "openpyxl",
    "openpyxl.styles.stylesheet",   # often missed
    "lxml",
    "lxml.etree",
    "tkinter",
    "tomllib",                       # stdlib Python 3.11+
]

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _header(msg: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {msg}")
    print(f"{'─' * 60}")


def _check_pyinstaller() -> None:
    """Abort with a helpful message if PyInstaller is not installed."""
    if importlib.util.find_spec("PyInstaller") is not None:
        import PyInstaller
        print(f"  PyInstaller {PyInstaller.__version__} found.")
        return

    print("  PyInstaller is not installed.", file=sys.stderr)
    print("  Install it with one of:", file=sys.stderr)
    print('      pip install ".[build]"', file=sys.stderr)
    print("      pip install pyinstaller", file=sys.stderr)
    sys.exit(1)


def _warn_platform() -> None:
    if platform.system() != "Windows":
        print(
            f"\n  WARNING: You are running on {platform.system()}.  "
            "PyInstaller can only produce a Windows .exe when run on Windows.\n"
            "  The build will proceed, but the output will target the current OS.\n"
            "  Use a Windows machine or GitHub Actions (windows-latest) for a "
            "real .exe.",
            file=sys.stderr,
        )


def _build_pyinstaller_command() -> list[str]:
    """Assemble the PyInstaller command-line arguments."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",          # overwrite previous build without asking
        "--clean",              # start fresh (removes cached .pyc etc.)
        "--onefile",            # single self-contained .exe  ← key flag
        "--windowed",           # suppress the console window when launched via GUI
                                # (remove this flag if you want the console visible)
        "--console",            # BUT keep a console so CLI usage still works.
                                # NOTE: on Windows --windowed + --console = console
                                # hidden unless opened from cmd.  If you want the
                                # CLI to always show a terminal, remove --windowed.
        f"--name={APP_NAME}",
        f"--distpath={DIST_DIR.parent}",  # PyInstaller puts output in distpath/<name>/
    ]

    # ── Hidden imports ────────────────────────────────────────────────────────
    for hi in HIDDEN_IMPORTS:
        cmd += ["--hidden-import", hi]

    # ── Icon ──────────────────────────────────────────────────────────────────
    if ICON_FILE and ICON_FILE.exists():
        cmd += [f"--icon={ICON_FILE}"]
    elif ICON_FILE:
        print(f"  Note: icon file not found ({ICON_FILE}), skipping.")

    # ── openpyxl data files (required: it ships XML templates internally) ─────
    try:
        import openpyxl
        openpyxl_dir = Path(openpyxl.__file__).parent
        # Syntax: "source_path{os.pathsep}dest_folder_inside_bundle"
        cmd += ["--add-data", f"{openpyxl_dir}{os.pathsep}openpyxl"]
    except ImportError:
        print("  WARNING: openpyxl not found; .exe may fail at runtime.", file=sys.stderr)

    # ── Entry point ───────────────────────────────────────────────────────────
    cmd.append(str(ENTRY_POINT))

    return cmd


# ─────────────────────────────────────────────────────────────────────────────
# Main build steps
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    _header("LROI PROMs Converter – EXE build")
    _warn_platform()

    # ── Pre-flight checks ─────────────────────────────────────────────────────
    _header("Step 1 / 4 – Checking requirements")
    _check_pyinstaller()

    if not ENTRY_POINT.exists():
        print(f"  ERROR: entry point not found: {ENTRY_POINT}", file=sys.stderr)
        return 1

    # ── Clean previous dist ───────────────────────────────────────────────────
    _header("Step 2 / 4 – Cleaning previous build artefacts")
    for d in [PROJECT_DIR / "dist", PROJECT_DIR / "build"]:
        if d.exists():
            shutil.rmtree(d)
            print(f"  Removed: {d}")

    # Remove any leftover .spec generated by a previous run
    spec_file = PROJECT_DIR / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"  Removed: {spec_file}")

    # ── Run PyInstaller ───────────────────────────────────────────────────────
    _header("Step 3 / 4 – Running PyInstaller")
    cmd = _build_pyinstaller_command()
    print("  Command:")
    print("    " + " \\\n      ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    if result.returncode != 0:
        print(
            "\n  ERROR: PyInstaller exited with code "
            f"{result.returncode}.  Check output above.",
            file=sys.stderr,
        )
        return result.returncode

    # ── Copy extra runtime files ──────────────────────────────────────────────
    _header("Step 4 / 4 – Copying runtime data files")

    exe_suffix = ".exe" if platform.system() == "Windows" else ""
    exe_path   = DIST_DIR / f"{APP_NAME}{exe_suffix}"

    # PyInstaller --onefile puts the exe directly in distpath/<name>/
    # Confirm it's there
    if not exe_path.exists():
        # Try flat distpath (some PyInstaller versions)
        exe_path = DIST_DIR.parent / f"{APP_NAME}{exe_suffix}"

    for src, dest_name in EXTRA_FILES.items():
        if not src.exists():
            print(f"  WARNING: extra file not found, skipping: {src}", file=sys.stderr)
            continue
        dest = DIST_DIR / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"  Copied: {src.name}  →  {dest}")

    # ── Summary ───────────────────────────────────────────────────────────────
    _header("Build complete")
    print(f"  Executable : {exe_path}")
    print(f"  Output dir : {DIST_DIR}")
    print()
    print("  Ship the following files to end-users:")
    print(f"    {exe_path.name}   ← the application")
    for dest_name in EXTRA_FILES.values():
        print(f"    {dest_name}         ← edit HOSPITAL number before distributing")
    print()
    print("  The config.toml MUST be in the same folder as the .exe.")
    print("  Each hospital should set 'hospital = <their LROI code>' before use.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
