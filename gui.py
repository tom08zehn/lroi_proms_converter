# Version: v1.4.5
"""
gui.py – Tkinter GUI for the LROI PROMs converter.

Can be launched stand-alone or prepopulated via CLI arguments.
The GUI allows the user to select input files, configure options,
run the conversion and view log output inline.
"""

from __future__ import annotations

import logging
import os
import queue
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk
except ImportError:
    print("ERROR: tkinter is not available on this system.", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Queue handler – funnels log records to the GUI text widget
# ─────────────────────────────────────────────────────────────────────────────


class _QueueHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue) -> None:
        super().__init__()
        self._queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        self._queue.put(self.format(record))


# ─────────────────────────────────────────────────────────────────────────────
# Main GUI window
# ─────────────────────────────────────────────────────────────────────────────


class ConverterGUI:
    """Main application window."""

    _TITLE   = "LROI PROMs Converter"
    _PAD     = 8
    _WIDTH   = 900
    _HEIGHT  = 680

    def __init__(
        self,
        config: Dict[str, Any],
        prepopulate: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Parameters
        ----------
        config:
            Parsed config.toml dict (passed from main.py).
        prepopulate:
            Optional dict with keys: ``xls_paths``, ``lut_path``,
            ``output_path``, ``log_path``, ``hospital``.
        """
        self._config = config
        self._prepopulate = prepopulate or {}
        self._log_queue: queue.Queue = queue.Queue()
        self._running = False

        # ── Root window ───────────────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title(self._TITLE)
        self.root.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.root.resizable(True, True)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self._build_ui()
        self._connect_logger()
        self._apply_prepopulate()

    # ─────────────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        p = self._PAD

        # ── Top frame: inputs ─────────────────────────────────────────────────
        top = ttk.LabelFrame(self.root, text="Input / Output", padding=p)
        top.grid(row=0, column=0, sticky="ew", padx=p, pady=p)
        top.columnconfigure(1, weight=1)

        # XLS files / folders
        ttk.Label(top, text="Input XLS file(s) / folder(s):").grid(
            row=0, column=0, sticky="w", pady=2)
        self._xls_var = tk.StringVar()
        ttk.Entry(top, textvariable=self._xls_var).grid(
            row=0, column=1, sticky="ew", padx=(4, 0))
        btn_frame = ttk.Frame(top)
        btn_frame.grid(row=0, column=2, padx=(4, 0))
        ttk.Button(btn_frame, text="Files…",  command=self._browse_xls_files).pack(side="left")
        ttk.Button(btn_frame, text="Folder…", command=self._browse_xls_folder).pack(side="left", padx=(2, 0))

        # LUT file
        ttk.Label(top, text="Lookup table (LUT):").grid(
            row=1, column=0, sticky="w", pady=2)
        self._lut_var = tk.StringVar()
        ttk.Entry(top, textvariable=self._lut_var).grid(
            row=1, column=1, sticky="ew", padx=(4, 0))
        ttk.Button(top, text="Browse…", command=self._browse_lut).grid(
            row=1, column=2, padx=(4, 0))

        # Hospital number
        ttk.Label(top, text="Hospital number:").grid(
            row=2, column=0, sticky="w", pady=2)
        self._hospital_var = tk.StringVar(
            value=str(self._config.get("defaults", {}).get("hospital", "")))
        ttk.Entry(top, textvariable=self._hospital_var, width=10).grid(
            row=2, column=1, sticky="w", padx=(4, 0))

        # Config file (editable with browse button)
        ttk.Label(top, text="Config file:").grid(
            row=3, column=0, sticky="w", pady=2)
        config_path = self._prepopulate.get("config_path", "config.toml") if self._prepopulate else "config.toml"
        self._config_var = tk.StringVar(value=config_path)
        ttk.Entry(top, textvariable=self._config_var).grid(
            row=3, column=1, sticky="ew", padx=(4, 0))
        ttk.Button(top, text="Browse…", command=self._browse_config).grid(
            row=3, column=2, padx=(4, 0))

        # Text log file (.log) with "Use default" checkbox
        ttk.Label(top, text="Text log file (optional):").grid(
            row=4, column=0, sticky="w", pady=2)
        
        log_frame = ttk.Frame(top)
        log_frame.grid(row=4, column=1, sticky="ew", padx=(4, 0))
        log_frame.columnconfigure(1, weight=1)
        
        self._log_use_default = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_frame, text="Use default", variable=self._log_use_default,
                       command=self._toggle_log_default).grid(row=0, column=0, sticky="w")
        
        self._log_var = tk.StringVar()
        self._log_entry = ttk.Entry(log_frame, textvariable=self._log_var, state="disabled")
        self._log_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
        self._log_browse_btn = ttk.Button(top, text="Browse…", command=self._browse_log, state="disabled")
        self._log_browse_btn.grid(row=4, column=2, padx=(4, 0))

        # Excel log file (.xlsx) with "Use default" checkbox
        ttk.Label(top, text="Excel log file (optional):").grid(
            row=5, column=0, sticky="w", pady=2)
        
        xlsx_log_frame = ttk.Frame(top)
        xlsx_log_frame.grid(row=5, column=1, sticky="ew", padx=(4, 0))
        xlsx_log_frame.columnconfigure(1, weight=1)
        
        self._xlsx_log_use_default = tk.BooleanVar(value=True)
        ttk.Checkbutton(xlsx_log_frame, text="Use default", variable=self._xlsx_log_use_default,
                       command=self._toggle_xlsx_log_default).grid(row=0, column=0, sticky="w")
        
        self._xlsx_log_var = tk.StringVar()
        self._xlsx_log_entry = ttk.Entry(xlsx_log_frame, textvariable=self._xlsx_log_var, state="disabled")
        self._xlsx_log_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
        self._xlsx_log_browse_btn = ttk.Button(top, text="Browse…", command=self._browse_xlsx_log, state="disabled")
        self._xlsx_log_browse_btn.grid(row=5, column=2, padx=(4, 0))
        
        # Log level dropdown
        ttk.Label(top, text="Log level:").grid(
            row=6, column=0, sticky="w", pady=2)
        self._loglevel_var = tk.StringVar(value="INFO")
        loglevel_combo = ttk.Combobox(
            top, 
            textvariable=self._loglevel_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10
        )
        loglevel_combo.grid(row=6, column=1, sticky="w", padx=(4, 0))
        ttk.Label(top, text="(DEBUG shows PII/PHI data)", font=("TkDefaultFont", 8)).grid(
            row=6, column=2, sticky="w", padx=(4, 0))
        
        # Output XML file with "Use default" checkbox
        ttk.Label(top, text="Output XML file:").grid(
            row=7, column=0, sticky="w", pady=2)
        
        output_frame = ttk.Frame(top)
        output_frame.grid(row=7, column=1, sticky="ew", padx=(4, 0))
        output_frame.columnconfigure(1, weight=1)
        
        self._output_use_default = tk.BooleanVar(value=True)
        ttk.Checkbutton(output_frame, text="Use default", variable=self._output_use_default,
                       command=self._toggle_output_default).grid(row=0, column=0, sticky="w")
        
        self._output_var = tk.StringVar()
        self._output_entry = ttk.Entry(output_frame, textvariable=self._output_var, state="disabled")
        self._output_entry.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
        self._output_browse_btn = ttk.Button(top, text="Browse…", command=self._browse_output, state="disabled")
        self._output_browse_btn.grid(row=7, column=2, padx=(4, 0))
        
        # Initialize all templates with same timestamp
        self._update_all_templates()

        mid = ttk.LabelFrame(self.root, text="Log", padding=p)
        mid.grid(row=1, column=0, sticky="nsew", padx=p, pady=(0, p))
        mid.rowconfigure(0, weight=1)
        mid.columnconfigure(0, weight=1)

        self._log_text = scrolledtext.ScrolledText(
            mid, state="disabled", wrap="word",
            font=("Courier", 9), background="#1e1e1e", foreground="#d4d4d4",
        )
        self._log_text.grid(row=0, column=0, sticky="nsew")

        # Tag colours
        self._log_text.tag_config("INFO",    foreground="#6db6ff")
        self._log_text.tag_config("WARNING", foreground="#f5a623")
        self._log_text.tag_config("ERROR",   foreground="#f44747")
        self._log_text.tag_config("DEBUG",   foreground="#808080")

        # ── Bottom frame: action buttons ──────────────────────────────────────
        bot = ttk.Frame(self.root, padding=(p, 0, p, p))
        bot.grid(row=2, column=0, sticky="ew")

        self._run_btn = ttk.Button(
            bot, text="▶  Run Conversion", command=self._run)
        self._run_btn.pack(side="left")

        ttk.Button(bot, text="Clear Log", command=self._clear_log).pack(
            side="left", padx=(p, 0))
        ttk.Button(bot, text="Quit", command=self.root.destroy).pack(
            side="right")

        self._status_var = tk.StringVar(value="Ready.")
        ttk.Label(bot, textvariable=self._status_var).pack(
            side="left", padx=(p * 2, 0))

    # ─────────────────────────────────────────────────────────────────────────
    # Logger integration
    # ─────────────────────────────────────────────────────────────────────────

    def _connect_logger(self) -> None:
        """Attach a queue handler so GUI can display log records."""
        handler = _QueueHandler(self._log_queue)
        handler.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                              datefmt="%H:%M:%S")
        )
        logging.getLogger("lroi").addHandler(handler)
        # Poll queue every 100 ms
        self.root.after(100, self._poll_log_queue)

    def _poll_log_queue(self) -> None:
        while True:
            try:
                msg = self._log_queue.get_nowait()
            except queue.Empty:
                break
            self._append_log(msg)
        self.root.after(100, self._poll_log_queue)

    def _append_log(self, msg: str) -> None:
        self._log_text.configure(state="normal")
        # Pick colour tag based on level keyword in message
        tag = "INFO"
        for level in ("ERROR", "WARNING", "DEBUG"):
            if level in msg:
                tag = level
                break
        self._log_text.insert("end", msg + "\n", tag)
        self._log_text.see("end")
        self._log_text.configure(state="disabled")

    def _clear_log(self) -> None:
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")

    # ─────────────────────────────────────────────────────────────────────────
    # File dialogs
    # ─────────────────────────────────────────────────────────────────────────

    def _browse_xls_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select input XLS / XLSX file(s)",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*")],
        )
        if paths:
            existing = self._xls_var.get().strip()
            new_entries = list(paths)
            combined = (existing + ";" if existing else "") + ";".join(new_entries)
            self._xls_var.set(combined)

    def _browse_xls_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select folder containing XLS/XLSX files")
        if folder:
            existing = self._xls_var.get().strip()
            combined = (existing + ";" if existing else "") + folder
            self._xls_var.set(combined)

    def _browse_lut(self) -> None:
        path = filedialog.askopenfilename(
            title="Select lookup table (LUT) Excel file",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*")],
        )
        if path:
            self._lut_var.set(path)


    def _browse_log(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save log file as",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*")],
        )
        if path:
            self._log_var.set(path)

    def _browse_xlsx_log(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save Excel log file as",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*")],
        )
        if path:
            self._xlsx_log_var.set(path)

    def _browse_config(self) -> None:
        path = filedialog.askopenfilename(
            title="Select config TOML file",
            filetypes=[("TOML files", "*.toml"), ("All files", "*")],
        )
        if path:
            self._config_var.set(path)
            # Reload config and update templates
            try:
                import tomllib
                with open(path, "rb") as f:
                    self._config = tomllib.load(f)
                self._update_all_templates()
                # Update hospital number from new config
                hospital = self._config.get("defaults", {}).get("hospital", "")
                self._hospital_var.set(str(hospital))
            except Exception as e:
                messagebox.showerror("Config Error", f"Failed to load config: {e}")

    def _toggle_log_default(self) -> None:
        """Toggle between default template and custom log file path."""
        use_default = self._log_use_default.get()
        if use_default:
            self._log_entry.configure(state="disabled")
            self._log_browse_btn.configure(state="disabled")
            self._update_log_template()
        else:
            self._log_entry.configure(state="normal")
            self._log_browse_btn.configure(state="normal")
            self._log_var.set("")  # Clear to let user choose

    def _toggle_xlsx_log_default(self) -> None:
        """Toggle between default template and custom Excel log file path."""
        use_default = self._xlsx_log_use_default.get()
        if use_default:
            self._xlsx_log_entry.configure(state="disabled")
            self._xlsx_log_browse_btn.configure(state="disabled")
            self._update_xlsx_log_template()
        else:
            self._xlsx_log_entry.configure(state="normal")
            self._xlsx_log_browse_btn.configure(state="normal")
            self._xlsx_log_var.set("")  # Clear to let user choose

    def _generate_timestamp(self) -> None:
        """Generate a timestamp to be used for all template resolutions."""
        from datetime import datetime
        self._timestamp = datetime.now()
    
    def _resolve_log_template(self, template: str) -> str:
        """Resolve placeholders in log file template using stored timestamp."""
        if not hasattr(self, '_timestamp'):
            self._generate_timestamp()
        
        return template.format(
            yyyy=self._timestamp.strftime("%Y"),
            mm=self._timestamp.strftime("%m"),
            dd=self._timestamp.strftime("%d"),
            HH=self._timestamp.strftime("%H"),
            MM=self._timestamp.strftime("%M"),
            SS=self._timestamp.strftime("%S"),
            appname="lroi_converter"
        )

    def _update_all_templates(self) -> None:
        """Update all template fields with same timestamp."""
        self._generate_timestamp()  # Generate once for all templates
        self._update_log_template()
        self._update_xlsx_log_template()
        self._update_output_template()

    def _update_log_template(self) -> None:
        """Update log file field with resolved template from config."""
        template = self._config.get("defaults", {}).get(
            "log_file_template", "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.log"
        )
        resolved = self._resolve_log_template(template)
        self._log_var.set(resolved)

    def _update_xlsx_log_template(self) -> None:
        """Update Excel log file field with resolved template from config."""
        template = self._config.get("defaults", {}).get(
            "xlsx_log_file_template", "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_{appname}.xlsx"
        )
        if template and template.strip():
            resolved = self._resolve_log_template(template)
            self._xlsx_log_var.set(resolved)
        else:
            # Excel logging disabled in config
            self._xlsx_log_var.set("(disabled in config)")
            self._xlsx_log_use_default.set(True)
            self._xlsx_log_entry.configure(state="disabled")
            self._xlsx_log_browse_btn.configure(state="disabled")

    def _update_output_template(self) -> None:
        """Update output XML file field with resolved template from config."""
        template = self._config.get("defaults", {}).get(
            "output_xml_file", "{yyyy}-{mm}-{dd}-{HH}{MM}{SS}_output.xml"
        )
        resolved = self._resolve_log_template(template)
        self._output_var.set(resolved)
    
    def _toggle_output_default(self) -> None:
        """Toggle between default template and custom output file path."""
        use_default = self._output_use_default.get()
        if use_default:
            self._output_entry.configure(state="disabled")
            self._output_browse_btn.configure(state="disabled")
            self._update_output_template()
        else:
            self._output_entry.configure(state="normal")
            self._output_browse_btn.configure(state="normal")
            self._output_var.set("")  # Clear to let user choose
    
    def _browse_output(self) -> None:
        """Browse for output XML file location."""
        path = filedialog.asksaveasfilename(
            title="Save output XML as",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*")],
        )
        if path:
            self._output_var.set(path)

    # ─────────────────────────────────────────────────────────────────────────
    # Pre-populate from CLI
    # ─────────────────────────────────────────────────────────────────────────

    def _apply_prepopulate(self) -> None:
        pp = self._prepopulate
        if "xls_paths" in pp:
            self._xls_var.set(";".join(str(p) for p in pp["xls_paths"]))
        if "lut_path" in pp and pp["lut_path"]:
            self._lut_var.set(str(pp["lut_path"]))
        
        # Output path: if provided from CLI, use it and uncheck default
        if "output_path" in pp and pp["output_path"]:
            self._output_use_default.set(False)
            self._output_entry.configure(state="normal")
            self._output_browse_btn.configure(state="normal")
            self._output_var.set(str(pp["output_path"]))
        
        # Log path: if provided from CLI (not "1"), use it and uncheck default
        if "log_path" in pp and pp["log_path"] and pp["log_path"] != "1":
            self._log_use_default.set(False)
            self._log_entry.configure(state="normal")
            self._log_browse_btn.configure(state="normal")
            self._log_var.set(str(pp["log_path"]))
        
        # Excel log path: if provided from CLI (not "1"), use it and uncheck default  
        if "xlsx_log_path" in pp and pp["xlsx_log_path"] and pp["xlsx_log_path"] != "1":
            self._xlsx_log_use_default.set(False)
            self._xlsx_log_entry.configure(state="normal")
            self._xlsx_log_browse_btn.configure(state="normal")
            self._xlsx_log_var.set(str(pp["xlsx_log_path"]))
        
        if "hospital" in pp and pp["hospital"]:
            self._hospital_var.set(str(pp["hospital"]))

    # ─────────────────────────────────────────────────────────────────────────
    # Run conversion
    # ─────────────────────────────────────────────────────────────────────────

    def _run(self) -> None:
        if self._running:
            return

        xls_raw = self._xls_var.get().strip()
        if not xls_raw:
            messagebox.showerror("Input required", "Please select at least one input XLS file or folder.")
            return

        raw_entries = [p.strip() for p in xls_raw.split(";") if p.strip()]

        # Reuse the same expansion logic as the CLI
        from main import _expand_xls_inputs
        xls_paths = [str(p) for p in _expand_xls_inputs(raw_entries)]

        if not xls_paths:
            messagebox.showerror(
                "No files found",
                "No .xlsx/.xls files were found at the specified paths.\n"
                "Please check your selection.",
            )
            return
        
        # Load config (user might have changed it via browse)
        config_path = self._config_var.get().strip()
        try:
            import tomllib
            with open(config_path, "rb") as f:
                cfg = tomllib.load(f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to load config from '{config_path}': {e}")
            return
        
        lut_path = self._lut_var.get().strip() or None
        
        # Get output path from GUI field (use template if "use default" checked)
        if self._output_use_default.get():
            output_path = self._output_var.get().strip()  # Resolved template
        else:
            output_path = self._output_var.get().strip() or None
        
        # Handle log file: if "use default" is checked, pass "1" to trigger template
        if self._log_use_default.get():
            log_path = "1"  # Signals to use template from config
        else:
            log_path = self._log_var.get().strip() or None
        
        # Handle Excel log: if "use default" is checked, pass "1" to trigger template
        if self._xlsx_log_use_default.get():
            xlsx_log_template = cfg.get("defaults", {}).get("xlsx_log_file_template", "")
            if xlsx_log_template and xlsx_log_template.strip():
                xlsx_log_path = "1"  # Signals to use template from config
            else:
                xlsx_log_path = None  # Excel logging disabled in config
        else:
            xlsx_log_path = self._xlsx_log_var.get().strip() or None

        hospital_str = self._hospital_var.get().strip()
        try:
            hospital = int(hospital_str)
        except ValueError:
            messagebox.showerror("Invalid input", f"Hospital number must be an integer, got: '{hospital_str}'")
            return

        # Patch hospital into config
        cfg.setdefault("defaults", {})["hospital"] = hospital

        self._run_btn.configure(state="disabled")
        self._status_var.set("Running…")
        self._running = True

        thread = threading.Thread(
            target=self._run_in_thread,
            args=(xls_paths, lut_path, output_path, log_path, xlsx_log_path, cfg),
            daemon=True,
        )
        thread.start()

    def _run_in_thread(
        self,
        xls_paths: List[str],
        lut_path: Optional[str],
        output_path: Optional[str],
        log_path: Optional[str],
        xlsx_log_path: Optional[str],
        config: Dict[str, Any],
    ) -> None:
        try:
            # Deferred imports to keep GUI startup fast
            from logger import setup_logger
            from converter import convert

            # Resolve "1" to actual template paths (like CLI does)
            if log_path == "1":
                template = config.get("defaults", {}).get(
                    "log_file_template", "{yyyy}-{mm}-{dd}_{appname}.log"
                )
                log_path = self._resolve_log_template(template)
            
            if xlsx_log_path == "1":
                template = config.get("defaults", {}).get(
                    "xlsx_log_file_template", "{yyyy}-{mm}-{dd}_{appname}.xlsx"
                )
                if template and template.strip():
                    xlsx_log_path = self._resolve_log_template(template)
                else:
                    xlsx_log_path = None

            # Get log level from GUI
            loglevel_str = self._loglevel_var.get()
            log_level = getattr(logging, loglevel_str, logging.INFO)
            
            logger = setup_logger(log_file=log_path, xlsx_file=xlsx_log_path, level=log_level)

            # Re-attach GUI queue handler after setup_logger (which clears handlers)
            # This ensures GUI receives all log messages during conversion
            lroi_logger = logging.getLogger("lroi")
            gui_handler = None
            
            # Find and preserve the GUI queue handler if it exists
            for handler in lroi_logger.handlers[:]:
                if isinstance(handler, _QueueHandler):
                    gui_handler = handler
                    break
            
            # If no GUI handler found, it was cleared by setup_logger - re-add it
            if gui_handler is None:
                gui_handler = _QueueHandler(self._log_queue)
                gui_handler.setFormatter(
                    logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                                    datefmt="%Y-%m-%d %H:%M:%S")
                )
            
            # Ensure GUI handler is attached
            if gui_handler not in lroi_logger.handlers:
                lroi_logger.addHandler(gui_handler)

            # LUT path (loading is handled by converter)
            lut_path_obj = Path(lut_path) if lut_path else None

            _, n_conv, n_skip = convert(
                xls_paths=xls_paths,
                config=config,
                lut_path=lut_path_obj,
                output_path=output_path,
            )

            msg = (
                f"Done. {n_conv} questionnaires converted, "
                f"{n_skip} rows skipped."
                + (f"  Output: {output_path}" if output_path else "")
            )
            self.root.after(0, lambda: self._status_var.set(msg))
            if output_path:
                self.root.after(0, lambda: messagebox.showinfo("Success", msg))

        except Exception as exc:
            import traceback
            err = traceback.format_exc()
            logging.getLogger("lroi").error("Unexpected error:\n%s", err)
            self.root.after(
                0,
                lambda: messagebox.showerror("Error", str(exc)),
            )
            self.root.after(0, lambda: self._status_var.set("Error – see log."))

        finally:
            self.root.after(0, lambda: self._run_btn.configure(state="normal"))
            self._running = False

    # ─────────────────────────────────────────────────────────────────────────
    # Entry point
    # ─────────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start the Tk main loop."""
        self.root.mainloop()
