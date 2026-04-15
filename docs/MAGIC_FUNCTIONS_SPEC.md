# Magic Functions Specification for v1.4.9

**Planned Release:** v1.4.9  
**Status:** Specification Phase  
**Total Functions:** ~60

---

## Overview

Magic functions provide safe, declarative calculations in config.toml without arbitrary Python code execution.

### Key Features
- ✅ **Safe:** Controlled function set (no eval/exec)
- ✅ **Powerful:** ~60 functions covering dates, strings, math, logic
- ✅ **Clear:** Readable syntax with variable interpolation
- ✅ **Maintainable:** Separate `magic_functions.py` module
- ✅ **Extensible:** Easy to add new functions

---

## Syntax

### Variable Interpolation
```toml
%(column_name)  # Insert value from current row
```

### Function Calls
```toml
$FUNCTION_NAME(arg1,arg2,arg3)  # No spaces after commas!
```

### Nested Functions
```toml
$IF($GT(%(age),18),adult,minor)
```

### Multi-Line (Recommended for Readability)
```toml
__computed = """
$IF(
  $GT(%(age),18),
  adult,
  minor
)
"""
# Leading/trailing whitespace auto-trimmed per line
```

---

## ⚠️ Critical: Comma Spacing

**WRONG:**
```toml
$FUNC(arg1, arg2, arg3)  # Spaces after commas = broken!
# Parser sees: ["arg1", " arg2", " arg3"]
#                        ^        ^
#                   Leading spaces!
```

**CORRECT:**
```toml
# Single-line: No spaces
$FUNC(arg1,arg2,arg3)

# Multi-line: Spaces OK (trimmed)
"""
$FUNC(
  arg1,
  arg2,
  arg3
)
"""
```

---

## Virtual Columns

Define computed columns with `__` prefix:

```toml
[PROM.OKS.FUPK]
# Compute months difference
__diff_months = "$DATE_DIFF(%(Date of Survey Completion),%(Surgery Date),months)"

# Use computed value
__period = """
$IF(
  $LT(%(__diff_months),0),
  -1,
  $IF(
    $GE(%(__diff_months),12),
    12,
    $IF(
      $GE(%(__diff_months),6),
      6,
      $IF(
        $GE(%(__diff_months),3),
        3,
        %(Period)
      )
    )
  )
)
"""

# Final value (uses computed or fallback)
column = "$FIRST_N(%(__period),%(Period),-1)"
```

### Rules
- **Read-only:** Original columns cannot be overwritten
- **Order:** Processed in definition order, `column` always last
- **Logging:** INFO if attempting to overwrite existing column
- **Scope:** Only current row data accessible

---

## Complete Function Reference

### JSON & Data

#### `#(json_string)`
Parse JSON string to object/array.
```toml
__data = "#(%(json_field))"
__value = "$GET(%(__data),key)"
```
**Returns:** Parsed object/array or None if invalid JSON

---

#### `$LEN(obj)`
Length of string, array, or object (key count).
```toml
__name_len = "$LEN(%(patient_name))"
__tag_count = "$LEN(%(tags))"
```
**Returns:** Integer length

---

#### `$IN(obj,item1,item2,...,itemN)`
Check if obj equals any of the items.
```toml
__is_valid = "$IN(%(status),active,pending,approved)"
```
**Returns:** Boolean (true/false)

---

### Date/Time

#### `$NOW(pattern?)`
Current timestamp, optionally formatted.
```toml
__timestamp = "$NOW()"  # ISO format
__date_only = "$NOW(%Y-%m-%d)"
__custom = "$NOW(%d/%m/%Y %H:%M:%S)"
```
**Args:**
- `pattern` (optional): strftime format string
**Returns:** Formatted timestamp string

---

#### `$DATE(str,inPattern,inTimezone?,outTimezone?,outPattern?)`
Parse date string and optionally convert timezone/format.
```toml
# Parse only
__parsed = "$DATE(%(date_str),%Y-%m-%d,UTC)"

# Parse and convert timezone
__local = "$DATE(%(utc_date),%Y-%m-%d %H:%M:%S,UTC,Europe/Amsterdam)"

# Parse and reformat
__reformatted = "$DATE(%(date),% Y-%m-%d,None,None,%d-%m-%Y)"
```
**Args:**
- `str`: Date string to parse
- `inPattern`: Input format (strftime syntax)
- `inTimezone` (optional): Input timezone or None for UTC
- `outTimezone` (optional): Output timezone
- `outPattern` (optional): Output format

**Returns:** Parsed/formatted date string

---

#### `$DATE_OFFSET(date,n1,unit1,n2,unit2,...)`
Add/subtract time periods (can combine multiple units).
```toml
# Add 3 months
__future = "$DATE_OFFSET(%(surgery_date),3,months)"

# Subtract 1 year
__past = "$DATE_OFFSET(%(survey_date),-1,years)"

# Combined
__complex = "$DATE_OFFSET(%(date),1,years,2,months,-5,days)"
```
**Args:**
- `date`: Date to modify
- `n`, `unit` pairs: Amount and unit (years, months, weeks, days, hours, minutes, seconds)

**Returns:** Modified date string

---

#### `$DATE_DIFF(date1,date2,unit)`
Calculate difference between dates.
```toml
__months = "$DATE_DIFF(%(survey_date),%(surgery_date),months)"
__days = "$DATE_DIFF(%(end_date),%(start_date),days)"
__years = "$DATE_DIFF(%(today),%(birth_date),years)"
```
**Args:**
- `date1`: Later date
- `date2`: Earlier date
- `unit`: Unit for result (days, weeks, months, years, hours, minutes, seconds)

**Returns:** Integer difference (can be negative)

---

### String - Basic

#### `$UPPER(str)`
Convert to uppercase.
```toml
__upper_gender = "$UPPER(%(gender))"  # "male" → "MALE"
```

#### `$LOWER(str)`
Convert to lowercase.
```toml
__lower_code = "$LOWER(%(hospital_code))"  # "ABC" → "abc"
```

#### `$TRIM(str)`
Remove leading and trailing whitespace.
```toml
__clean = "$TRIM(%(  spaced  ))"  # "  spaced  " → "spaced"
```

#### `$LTRIM(str)`
Remove leading whitespace only.
```toml
__left_clean = "$LTRIM(%(  left))"  # "  left" → "left"
```

#### `$RTRIM(str)`
Remove trailing whitespace only.
```toml
__right_clean = "$RTRIM(%(right  ))"  # "right  " → "right"
```

#### `$SUBSTR(str,start,length?)`
Extract substring.
```toml
__first_5 = "$SUBSTR(%(patient_id),0,5)"
__from_10 = "$SUBSTR(%(text),10)"  # From position 10 to end
```
**Args:**
- `str`: Source string
- `start`: Starting index (0-based)
- `length` (optional): Number of characters (omit for rest of string)

#### `$CONCAT(item1,item2,...,itemN)`
Concatenate strings.
```toml
__full_name = "$CONCAT(%(first_name), ,%(last_name))"
__code = "$CONCAT(%(hospital),-,%(patient_id))"
```

---

### String - Checks

#### `$STARTSWITH(str,prefix)`
Check if string starts with prefix.
```toml
__is_temp = "$STARTSWITH(%(code),TEMP)"
```
**Returns:** Boolean

#### `$ENDSWITH(str,suffix)`
Check if string ends with suffix.
```toml
__is_xml = "$ENDSWITH(%(filename),.xml)"
```
**Returns:** Boolean

#### `$CONTAINS(str,substring)`
Check if string contains substring.
```toml
__has_urgent = "$CONTAINS(%(notes),urgent)"
```
**Returns:** Boolean

#### `$MATCH(str,pattern)`
Check if string matches regex pattern.
```toml
__is_preop = "$MATCH(%(period),Pre-?Op)"
__is_date = "$MATCH(%(value),^\d{4}-\d{2}-\d{2}$)"
```
**Returns:** Boolean

---

### String - Array Operations

#### `$SPLIT(str,delimiter)`
Split string into array.
```toml
__tags = "$SPLIT(%(tag_string),;)"  # "a;b;c" → ["a", "b", "c"]
```

#### `$JOIN(array,delimiter)`
Join array into string.
```toml
__csv = "$JOIN(%(items),,)"  # ["a", "b", "c"] → "a,b,c"
```

---

### Comparison - Regular

#### `$EQ(a,b)`
Equal (case-sensitive for strings).
```toml
__is_male = "$EQ(%(gender),M)"
```

#### `$NE(a,b)`
Not equal (case-sensitive).
```toml
__not_invalid = "$NE(%(status),invalid)"
```

#### `$LT(a,b)`
Less than (numeric or lexicographic).
```toml
__is_child = "$LT(%(age),18)"
```

#### `$LE(a,b)`
Less than or equal.
```toml
__valid_score = "$LE(%(score),100)"
```

#### `$GT(a,b)`
Greater than.
```toml
__is_old = "$GT(%(months),12)"
```

#### `$GE(a,b)`
Greater than or equal.
```toml
__is_adult = "$GE(%(age),18)"
```

---

### Comparison - Case-Insensitive

#### `$EQI(a,b)`
Equal, ignoring case.
```toml
__is_male = "$EQI(%(gender),male)"  # Matches "MALE", "Male", "male"
```

#### `$NEI(a,b)`
Not equal, ignoring case.
```toml
__not_pending = "$NEI(%(status),PENDING)"
```

---

### Logical

#### `$IF(condition,then_value,else_value)`
Conditional expression.
```toml
__category = "$IF($LT(%(age),18),minor,adult)"

# Nested
__period = """
$IF(
  $LT(%(months),0),
  -1,
  $IF(
    $GE(%(months),12),
    12,
    3
  )
)
"""
```

#### `$AND(expr1,expr2,...,exprN)`
Logical AND (all must be true).
```toml
__valid = "$AND($GT(%(age),0),$LT(%(age),120),$N(%(name)))"
```

#### `$OR(expr1,expr2,...,exprN)`
Logical OR (any must be true).
```toml
__is_special = "$OR($EQ(%(code),A),$EQ(%(code),B),$EQ(%(code),C))"
```

#### `$NOT(expr)`
Logical NOT (invert boolean).
```toml
__is_valid = "$NOT($Z(%(required_field)))"
```

---

### Null/Empty Checks

#### `$Z(value)`
Check if null/None/empty.
```toml
__is_empty = "$Z(%(optional_field))"
```
**Returns:** true if value is None, "", [], {}, or 0

#### `$N(value)`
Check if non-null/non-empty.
```toml
__has_value = "$N(%(required_field))"
```
**Returns:** true if value is not None, not "", not [], not {}, and not 0

#### `$FIRST_N(item1,item2,...,itemN)`
Return first non-null/non-empty item (runs $N on each).
```toml
__period = "$FIRST_N(%(computed_period),%(Period),Pre-Op)"
# Uses computed_period if not empty, else Period, else "Pre-Op"
```

#### `$FIRST_Z(item1,item2,...,itemN)`
Return first null/empty item (runs $Z on each).
```toml
__missing = "$FIRST_Z(%(field1),%(field2),%(field3))"
```

---

### Math - Basic

#### `$PLUS(a,b)`
Addition.
```toml
__total = "$PLUS(%(score1),%(score2))"
```

#### `$MINUS(a,b)`
Subtraction.
```toml
__net = "$MINUS(%(gross),%(tax))"
```

#### `$MULTIPLY(a,b)`
Multiplication.
```toml
__total = "$MULTIPLY(%(quantity),%(price))"
```

#### `$DIVIDE(a,b)`
Division.
```toml
__average = "$DIVIDE(%(sum),%(count))"
```
**Note:** Returns error if b = 0

#### `$MODULO(a,b)`
Modulo (remainder).
```toml
__remainder = "$MODULO(%(patient_id),10)"
```

---

### Math - Advanced

#### `$ABS(n)`
Absolute value.
```toml
__distance = "$ABS(%(diff))"
```

#### `$MIN(n1,n2,...,nN)`
Minimum value.
```toml
__lowest = "$MIN(%(a),%(b),%(c))"
```

#### `$MAX(n1,n2,...,nN)`
Maximum value.
```toml
__highest = "$MAX(%(score),0)"  # At least 0
```

#### `$ROUND(n,decimals?)`
Round number.
```toml
__rounded = "$ROUND(%(value),2)"  # 2 decimal places
__integer = "$ROUND(%(value))"  # No decimals (default 0)
```

#### `$EVEN(n)`
Check if number is even.
```toml
__is_even = "$EVEN(%(count))"
```

#### `$ODD(n)`
Check if number is odd.
```toml
__is_odd = "$ODD(%(id))"
```

---

### Hashing & IDs

#### `$MD5(item1,item2,...,itemN)`
Generate MD5 hash.
```toml
# Single value
__hash = "$MD5(%(patient_id))"

# Multiple values (concatenated first)
__combined_hash = "$MD5(%(patient_id),%(date),%(hospital))"
```
**Returns:** 32-character hex string

#### `$UUID()`
Generate random UUID.
```toml
__unique_id = "$UUID()"
```
**Returns:** UUID v4 string (e.g., "550e8400-e29b-41d4-a716-446655440000")

---

### Collections

#### `$PUSH(array,item)`
Add item to array (returns new array).
```toml
__new_tags = "$PUSH(%(tags),new_tag)"
```

#### `$KEYS(object)`
Get object keys as array.
```toml
__fields = "$KEYS(%(data))"
```

#### `$VALUES(object)`
Get object values as array.
```toml
__vals = "$VALUES(%(data))"
```

#### `$ENTRIES(object)`
Get object entries as array of [key, value] pairs.
```toml
__pairs = "$ENTRIES(%(data))"
```

---

## Complete Example

```toml
[PROM.OKS.FUPK]
# Step 1: Calculate months between dates
__diff_months = """
$DATE_DIFF(
  %(Date of Survey Completion),
  %(Surgery Date),
  months
)
"""

# Step 2: Map months to LROI periods
__computed_period = """
$IF(
  $LT(%(__diff_months),0),
  -1,
  $IF(
    $GE(%(__diff_months),12),
    12,
    $IF(
      $GE(%(__diff_months),6),
      6,
      $IF(
        $GE(%(__diff_months),3),
        3,
        $FIRST_N(%(Period),-1)
      )
    )
  )
)
"""

# Step 3: Generate unique tracking ID
__tracking_id = """
$MD5(
  %(Patient ID),
  %(Date of Survey Completion),
  $UUID()
)
"""

# Final column value (use computed or direct)
column = "$FIRST_N(%(__computed_period),%(Period))"

# Regex conversions still work (applied after magic functions)
[[PROM.OKS.FUPK.value]]
match = "Pre-?Op|Preop"
replace = "-1"

[[PROM.OKS.FUPK.value]]
match = "3\\s*Month|3M"
replace = "3"
```

---

## Implementation Plan

### Phase 1: Parser (`magic_functions.py`)
- Tokenizer (split by commas, handle quotes)
- Variable interpolation `%(col)`
- Function call parser (recursive)
- Multi-line whitespace handling

### Phase 2: Core Functions
- String functions (20)
- Date functions (4)
- Comparison functions (8)
- Logical functions (4)
- Null checks (4)

### Phase 3: Advanced Functions
- Math functions (10)
- Hashing/IDs (2)
- Collections (4)
- JSON parsing (1)

### Phase 4: Integration
- Virtual column processing in `converter.py`
- Read-only enforcement
- Error handling
- DEBUG logging

### Phase 5: Testing
- Unit tests for each function
- Integration tests
- Error case handling
- Performance testing

### Phase 6: Documentation
- README section
- Function reference
- Examples
- Migration guide

---

## Error Handling

### Invalid Function
```toml
__bad = "$UNKNOWN_FUNC(arg)"
```
**Result:** ERROR logged, row skipped, shows available functions

### Wrong Argument Count
```toml
__bad = "$IF(condition)"  # Missing then/else
```
**Result:** ERROR logged, row skipped, shows expected arguments

### Type Mismatch
```toml
__bad = "$PLUS(text,another)"  # Can't add strings as numbers
```
**Result:** ERROR logged, row skipped, shows type error

### Read-Only Violation
```toml
[PROM.OKS.FUPK]
Period = "value"  # Trying to overwrite original column
```
**Result:** INFO logged "Ignoring 'Period' - column already exists", key skipped

---

## Performance Considerations

- **Caching:** Parse expressions once, reuse for all rows
- **Lazy evaluation:** Only compute when needed
- **Short-circuit:** $AND/$OR stop early when result determined
- **Type hints:** Help Python JIT optimize

---

## Security

### Safe
- ✅ No eval/exec
- ✅ No imports
- ✅ No file system access
- ✅ No network access
- ✅ Controlled function set
- ✅ Type validation

### Unsafe (Not Allowed)
- ❌ `$FUNC()` - arbitrary function calls
- ❌ `$IMPORT()` - module imports
- ❌ `$EXEC()` - code execution
- ❌ `$SYSTEM()` - OS commands

---

## Migration from v1.4.8

**Fully backward compatible!**

Old configs continue working:
```toml
[PROM.OKS.FUPK]
column = "Period"

[[PROM.OKS.FUPK.value]]
match = "Pre-?Op"
replace = "-1"
```

New configs can add magic functions:
```toml
[PROM.OKS.FUPK]
__computed = "$DATE_DIFF(...)"
column = "$FIRST_N(%(__computed),%(Period))"

[[PROM.OKS.FUPK.value]]
match = "Pre-?Op"
replace = "-1"
```

---

## Questions for Review

1. **Function naming:**
   - `$DATE_OFFSET()` or `$DATE_MOD()`? (User prefers MOD)
   - `$MODULO()` or `$MOD()`? (Shorter vs. clearer)
   - `$UUID()` or `$GUID()`? (Standard vs. Windows term)

2. **Type coercion:**
   - Auto-convert strings to numbers in math functions?
   - Strict typing with errors, or permissive with warnings?

3. **Array syntax:**
   - How to represent arrays in config? `[1,2,3]` or `1;2;3`?

4. **Error recovery:**
   - Skip entire row on any error?
   - Or use fallback values when possible?

---

**Specification Version:** 1.0  
**Last Updated:** 2026-02-27  
**Target Release:** v1.4.9
