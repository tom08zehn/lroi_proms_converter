# GUI Features — LROI PROMs Converter

## Enhanced GUI (v1.2.0)

The GUI now provides full control over all conversion options, matching CLI functionality.

---

## GUI Layout

```
┌─ LROI PROMs Converter ────────────────────────────────────────────────────┐
│                                                                            │
│  Input XLS file(s) / folder(s):  [____________________] [Files…] [Folder…]│
│  Lookup table (LUT):              [____________________] [Browse…]        │
│  Output XML file:                 [____________________] [Browse…]        │
│  Hospital number:                 [1234]                                  │
│  Config file:                     [config.toml_________] [Browse…]        │
│                                                                            │
│  Text log file (optional):                                                │
│    ☑ Use default  [2026-02-19_main.log_________________] [Browse…]        │
│                                                                            │
│  Excel log file (optional):                                               │
│    ☑ Use default  [2026-02-19_main.xlsx________________] [Browse…]        │
│                                                                            │
│ ┌─ Log ───────────────────────────────────────────────────────────────┐  │
│ │ 14:30:15  INFO      LROI PROMs Converter starting                   │  │
│ │ 14:30:15  INFO      Processing XLS: demo/oks_site_a.xlsx            │  │
│ │ 14:30:15  INFO      Detected PROM type: OKS                         │  │
│ │ 14:30:15  DEBUG     Converted FUPK: 'Pre-Op' → '-1'                 │  │
│ │ 14:30:15  INFO      Converted OKS row: join_value=REC001            │  │
│ │ ...                                                                  │  │
│ └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  [▶ Run Conversion]  [Clear Log]                 Ready.          [Quit]   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Feature Details

### 1. Config File Selection

**Location:** Row after Hospital number  
**Controls:** `[Entry field] [Browse…]`

**Behavior:**
- Browse to load a different `config.toml` file
- Automatically reloads configuration
- Updates:
  - Hospital number (from new config)
  - Log file templates (resolved paths)
  - Excel log template (resolved path)

**Use case:** Switch between configurations for different hospitals or testing scenarios.

---

### 2. Text Log File (`.log`)

**Location:** Row 5 (after Config file)  
**Controls:** `☑ Use default | [Entry field] | [Browse…]`

**Behavior:**

**When "Use default" is checked (default state):**
- Entry field shows: `2026-02-19_main.log` (resolved from config template)
- Entry field is **disabled** (grayed out)
- Browse button is **disabled**
- Acts like CLI `--log 1`

**When "Use default" is unchecked:**
- Entry field is **enabled** and **automatically cleared**
- Browse button is **enabled**
- User can type a path or browse to select custom log file location
- **Leaving the field empty = no log file created**

**To disable logging entirely:**
1. Uncheck "Use default" checkbox
2. Field is automatically cleared
3. Leave empty — no log file will be created

**Template resolution:**
```toml
# config.toml
[defaults]
log_file_template = "{yyyy}-{mm}-{dd}_{appname}.log"
```
Resolves to: `2026-02-19_main.log`

---

### 3. Excel Log File (`.xlsx`)

**Location:** Row 6 (after Text log)  
**Controls:** `☑ Use default | [Entry field] | [Browse…]`

**Behavior:** Same as Text log, but for Excel files.

**Special case — Excel logging disabled in config:**
```toml
xlsx_log_file_template = ""   # Empty = disabled
```
- Entry field shows: `(disabled in config)`
- Checkbox remains checked
- Entry and browse button remain disabled
- No Excel log will be created

**When enabled:**
```toml
xlsx_log_file_template = "{yyyy}-{mm}-{dd}_{appname}.xlsx"
```
Resolves to: `2026-02-19_main.xlsx`

**To disable Excel logging:**
1. Uncheck "Use default" checkbox
2. Field is automatically cleared
3. Leave empty — no Excel log file will be created

---

## Workflow Examples

### Example 1: Use All Defaults

1. Load GUI: `python main.py --gui`
2. Select input files: **Files…** or **Folder…**
3. Select LUT: **Browse…**
4. Leave checkboxes **checked** ☑
5. Click **▶ Run Conversion**

**Result:**
- Text log: `2026-02-19_main.log`
- Excel log: `2026-02-19_main.xlsx`
- Both files in current directory

---

### Example 2: Custom Log Locations

1. Load GUI
2. Select files/LUT
3. **Uncheck** ☐ "Use default" for Text log
4. **Browse…** to select: `C:\Hospital\Logs\conversion.log`
5. **Uncheck** ☐ "Use default" for Excel log
6. **Browse…** to select: `C:\Hospital\Logs\conversion.xlsx`
7. Click **▶ Run Conversion**

**Result:**
- Text log: `C:\Hospital\Logs\conversion.log`
- Excel log: `C:\Hospital\Logs\conversion.xlsx`

---

### Example 3: Switch Hospitals Mid-Session

**Scenario:** You work with multiple hospitals and need different configs.

1. Load GUI with Hospital A config: `python main.py --gui --cfg hospital_a.toml`
2. Convert Hospital A data
3. **Browse…** in Config file row
4. Select `hospital_b.toml`
5. Hospital number updates automatically
6. Log templates update automatically
7. Convert Hospital B data

**Result:** Seamlessly switch between hospital configurations without restarting.

---

## Technical Details

### Template Placeholders

Both log file templates support these placeholders:

| Placeholder | Resolves to | Example |
|-------------|-------------|---------|
| `{yyyy}` | 4-digit year | `2026` |
| `{mm}` | 2-digit month | `02` |
| `{dd}` | 2-digit day | `19` |
| `{HH}` | 2-digit hour | `14` |
| `{MM}` | 2-digit minute | `30` |
| `{SS}` | 2-digit second | `45` |
| `{appname}` | Application name | `main` |

**Example template:**
```toml
log_file_template = "logs/{yyyy}/{mm}/conversion_{dd}_{HH}{MM}.log"
```
Resolves to: `logs/2026/02/conversion_19_1430.log`

### Config Reload Behavior

When you browse to load a new config file:

1. **Validates** the config file can be loaded (TOML syntax)
2. **Reloads** the entire configuration
3. **Updates GUI fields:**
   - Hospital number
   - Text log resolved path (if "use default" checked)
   - Excel log resolved path (if "use default" checked)
4. **Shows error** if config is invalid

---

## Keyboard Shortcuts

- **Tab** — Navigate between fields
- **Space** — Toggle checkboxes
- **Enter** (in any field) — Trigger **Run Conversion**
- **Alt+F4** (Windows) / **Cmd+Q** (Mac) — Quit

---

## Comparison: CLI vs GUI

| Feature | CLI | GUI |
|---------|-----|-----|
| Load custom config | `--cfg file.toml` | Browse button |
| Use default log | `--log 1` | ☑ "Use default" checkbox |
| Custom log path | `--log path.log` | ☐ Uncheck + Browse |
| Excel log | Auto (if enabled in config) | ☑ "Use default" checkbox |
| Real-time progress | Console output | Log panel with colors |
| Switch config | Restart with `--cfg` | Browse + auto-reload |

**Both interfaces** provide the same functionality — choose based on your workflow preference!
