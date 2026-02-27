#!/usr/bin/env python3
# Version: v1.4.5
"""
main.py – CLI / GUI entry point for the LROI PROMs Converter.

Usage examples
--------------
# Run immediately (no GUI):
python main.py --xls OKS.xlsx --lut Demographics.xlsx \\
               --output output.xml --hospital 1234

# Open GUI with prepopulated values, wait for user:
python main.py --gui \\
               --xls OKS.xlsx --lut Demographics.xlsx \\
               --output output.xml --hospital 1234

# Open GUI, run immediately without waiting:
python main.py --gui --run \\
               --xls OKS.xlsx --lut Demographics.xlsx \\
               --output output.xml

# Log to auto-named file:
python main.py --xls OKS.xlsx --log 1

# Log to specific file:
python main.py --xls OKS.xlsx --log my_run.log
"""

from __future__ import annotations

import argparse
import datetime
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Locate config.toml relative to executable (handles PyInstaller) ────────────

def _get_application_dir() -> Path:
    """
    Get the directory where the application is located.
    
    Handles both:
    - Normal Python script execution: Returns script directory
    - PyInstaller bundled executable: Returns executable directory (not temp _MEI directory)
    """
    if getattr(sys, 'frozen', False):
        # Running as bundled executable (PyInstaller)
        # sys.executable points to the .exe file
        return Path(sys.executable).parent.resolve()
    else:
        # Running as normal Python script
        return Path(__file__).parent.resolve()

_SCRIPT_DIR = _get_application_dir()

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]


def _load_config(config_path: Path) -> Dict[str, Any]:
    """Parse config.toml and return as nested dict."""
    if tomllib is None:
        # Fall back to a minimal hand-rolled TOML reader isn't practical;
        # inform the user clearly.
        try:
            import tomli as tomllib2  # type: ignore
            with open(config_path, "rb") as f:
                return tomllib2.load(f)
        except ImportError:
            pass
        print(
            "ERROR: No TOML parser available.  Install one:\n"
            "  pip install tomli          (Python < 3.11)\n"
            "Python 3.11+ includes tomllib in the standard library.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def _expand_xls_inputs(raw_inputs: List[str]) -> List[Path]:
    """
    Expand a mixed list of file paths and/or folder paths into a deduplicated,
    sorted list of .xlsx / .xls file paths.

    Rules
    -----
    - A path that is a file  → include it directly (regardless of extension, so
      the converter can emit a clear error for bad files rather than silently
      skipping them).
    - A path that is a folder → recursively collect every *.xlsx / *.xls file
      within it, sorted alphabetically.
    - Duplicates (e.g. a file listed twice, or a file inside a folder that was
      also listed explicitly) are removed while preserving order.
    """
    seen:   set   = set()
    result: List[Path] = []

    for raw in raw_inputs:
        p = Path(raw).expanduser().resolve()
        if p.is_dir():
            files = sorted(
                f for f in p.rglob("*")
                if f.suffix.lower() in {".xlsx", ".xls"} and f.is_file()
            )
            if not files:
                print(f"WARNING: No .xlsx/.xls files found in folder: {p}", file=sys.stderr)
            for f in files:
                if f not in seen:
                    seen.add(f)
                    result.append(f)
        elif p.is_file():
            if p not in seen:
                seen.add(p)
                result.append(p)
        else:
            print(f"WARNING: Path not found, skipping: {p}", file=sys.stderr)

    return result


def _resolve_log_path(log_arg: str, config: Dict[str, Any]) -> Optional[str]:
    """
    Resolve the --log argument to a file path (or None for console-only).

    '1'  → auto-named from config template
    else → treat as a literal path
    """
    if not log_arg:
        return None
    if log_arg == "1":
        template: str = (
            config.get("defaults", {})
            .get("log_file_template", "{yyyy}-{mm}-{dd}_{appname}.log")
        )
        return _expand_template(template)
    return log_arg


def _resolve_xlsx_log_path(log_arg: str, config: Dict[str, Any]) -> Optional[str]:
    """
    Resolve the Excel log path from config template.

    Returns None if Excel logging is disabled in config or if no log requested.
    """
    if not log_arg:
        return None
    
    template: str = (
        config.get("defaults", {})
        .get("xlsx_log_file_template", "")
    )
    
    # If template is empty or commented out, Excel logging is disabled
    if not template or not template.strip():
        return None
    
    return _expand_template(template)


def _resolve_output_path(
    output_arg: Optional[str], config: Dict[str, Any]
) -> Optional[str]:
    """Resolve the output XML path, applying template if not given."""
    if output_arg:
        return output_arg
    template: str = (
        config.get("defaults", {})
        .get("xml_file_template", "{yyyy}-{mm}-{dd}_{appname}_output.xml")
    )
    out_dir = config.get("defaults", {}).get("output_dir", ".")
    return str(Path(out_dir) / _expand_template(template))


def _expand_template(template: str) -> str:
    """Replace datetime and appname placeholders in *template*."""
    now  = datetime.datetime.now()
    name = Path(sys.argv[0]).stem
    return (
        template
        .replace("{yyyy}",    now.strftime("%Y"))
        .replace("{mm}",      now.strftime("%m"))
        .replace("{dd}",      now.strftime("%d"))
        .replace("{HH}",      now.strftime("%H"))
        .replace("{MM}",      now.strftime("%M"))
        .replace("{SS}",      now.strftime("%S"))
        .replace("{appname}", name)
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lroi_converter",
        description=(
            "Convert PROMs Excel exports to LROI-compliant XML for upload to "
            "the LROI Databroker platform."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--xls",
        metavar="FILE_OR_FOLDER",
        nargs="+",
        help=(
            "One or more input XLS/XLSX files and/or folders.  "
            "When a folder is given, all *.xlsx/*.xls files in it "
            "(recursively) are included."
        ),
    )
    parser.add_argument(
        "--lut",
        metavar="FILE",
        help="Optional lookup-table (demographics) Excel file.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help=(
            "Output XML file path.  Defaults to a timestamped file in the "
            "directory configured in config.toml."
        ),
    )
    parser.add_argument(
        "--log",
        metavar="FILE|1",
        default="",
        help=(
            "Log file path, or '1' to use the auto-named template from "
            "config.toml.  Omit to log to console only."
        ),
    )
    parser.add_argument(
        "--hospital",
        metavar="N",
        type=int,
        help="Hospital number (overrides config.toml).",
    )
    parser.add_argument(
        "--loglevel",
        metavar="LEVEL",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level: DEBUG (shows PII/PHI), INFO (default), WARNING, ERROR.",
    )
    parser.add_argument(
        "--cfg",
        metavar="FILE",
        default=str(_SCRIPT_DIR / "config.toml"),
        help="Path to config.toml (default: config.toml next to executable).",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Open the graphical user interface.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help=(
            "When --gui is set, start the conversion immediately without "
            "waiting for user interaction."
        ),
    )
    return parser


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args   = parser.parse_args(argv)

    # ── Load config ──────────────────────────────────────────────────────────
    config_path = Path(args.cfg)
    
    if not config_path.exists():
        # Config file not found
        if args.gui:
            # GUI mode: Allow GUI to open, user can browse for config
            print(f"INFO: Config file not found: {config_path}", file=sys.stderr)
            print(f"INFO: GUI will open - you can select a config file manually.", file=sys.stderr)
            # Create minimal default config for GUI
            config = {
                "defaults": {
                    "hospital": 0,
                    "lut_column_prefix": "__LUT__",
                    "log_file_template": "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log",
                    "xlsx_log_file_template": "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx",
                },
                "lut": {
                    "join_column": "Admission ID",
                },
                "PROM": {},  # Empty - user must provide config
            }
        else:
            # CLI mode: Show helpful error
            print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
            print(f"\nExpected location: {config_path.resolve()}", file=sys.stderr)
            print(f"\nTo fix this:", file=sys.stderr)
            print(f"  1. Copy config.toml to the same directory as the executable", file=sys.stderr)
            print(f"  2. Or use --config to specify a different path:", file=sys.stderr)
            print(f"     {Path(sys.argv[0]).name} --config /path/to/config.toml ...", file=sys.stderr)
            print(f"\nFor GUI mode (doesn't require config):", file=sys.stderr)
            print(f"  {Path(sys.argv[0]).name} --gui", file=sys.stderr)
            return 1
    else:
        config = _load_config(config_path)

    # Apply CLI hospital override
    if args.hospital is not None:
        config.setdefault("defaults", {})["hospital"] = args.hospital

    # ── Resolve paths ─────────────────────────────────────────────────────────
    log_path     = _resolve_log_path(args.log, config)
    xlsx_log_path = _resolve_xlsx_log_path(args.log, config)
    output_path  = _resolve_output_path(args.output, config)
    raw_xls: List[str] = args.xls or []
    xls_paths = _expand_xls_inputs(raw_xls)

    # ── GUI mode ──────────────────────────────────────────────────────────────
    if args.gui:
        from gui import ConverterGUI

        prepopulate = {
            "xls_paths":    [str(p) for p in xls_paths],
            "lut_path":     args.lut,
            "output_path":  output_path,
            "log_path":     log_path,
            "xlsx_log_path": xlsx_log_path,
            "hospital":     config.get("defaults", {}).get("hospital"),
            "config_path":  config_path,
        }
        gui = ConverterGUI(config=config, prepopulate=prepopulate)

        if args.run and xls_paths:
            gui.root.after(500, gui._run)

        gui.run()
        return 0

    # ── Headless CLI mode ─────────────────────────────────────────────────────
    if not xls_paths:
        parser.error(
            "At least one --xls file or folder is required (or use --gui)."
        )

    # Set up logger
    from logger import setup_logger
    
    # Convert loglevel string to logging constant
    log_level = getattr(logging, args.loglevel, logging.INFO)
    logger = setup_logger(log_file=log_path, xlsx_file=xlsx_log_path, level=log_level)

    logger.info("LROI PROMs Converter starting")
    logger.info("Config: %s", config_path)
    logger.info("Input files: %s", [str(p) for p in xls_paths])
    logger.info("LUT: %s", args.lut or "(none)")
    logger.info("Output: %s", output_path)

    # LUT path (loading is handled by converter)
    lut_path = Path(args.lut) if args.lut else None

    # Run conversion
    from converter import convert
    _, n_converted, n_skipped = convert(
        xls_paths=xls_paths,
        config=config,
        lut_path=lut_path,
        output_path=output_path,
    )

    # Note: Detailed conversion summary already logged by converter.py
    # including INFO for converted and WARNING for skipped
    if output_path:
        logger.info("Output file: %s", output_path)
    
    return 0 if n_converted > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
