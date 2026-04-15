#!/usr/bin/env python3
"""
magic_functions.py - Magic function parser and evaluator for LROI converter

Supports ~60 magic functions for safe, declarative calculations in config.toml.
Can be used as a standalone module in other Python projects.

Usage:
    from magic_functions import evaluate
    
    row_data = {"name": "John", "age": 25}
    result = evaluate("$UPPER(%(name))", row_data)
    # Returns: "JOHN"

Author: Based on ZBEdgeUtils.js by the creator
Version: 1.0.0 for LROI Converter v1.4.9
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

# Date format patterns
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ──────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────────────────────

def _is_null_or_empty(value: Any) -> bool:
    """Check if value is null/None/empty (for $Z function)."""
    if value is None:
        return True
    if value == "":
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True
    if isinstance(value, (int, float)) and value == 0:
        return True
    return False

def _is_non_null(value: Any) -> bool:
    """Check if value is non-null/non-empty (for $N function)."""
    return not _is_null_or_empty(value)

def _to_number(value: Any) -> Union[int, float]:
    """Convert value to number, raise ValueError if impossible."""
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to number")
    raise ValueError(f"Cannot convert {type(value).__name__} to number")

def _to_string(value: Any) -> str:
    """Convert value to string."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    # Handle datetime objects from Excel
    from datetime import datetime, date
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.isoformat()
    return str(value)

def _parse_date(date_str: str, pattern: Optional[str] = None) -> datetime:
    """Parse date string using pattern."""
    if pattern is None or pattern == "" or pattern.lower() == "none":
        # Try common formats
        for fmt in [DEFAULT_DATE_FORMAT, DEFAULT_DATETIME_FORMAT, "%Y-%m-%dT%H:%M:%S.%fZ"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {date_str}")
    return datetime.strptime(date_str, pattern)

# ──────────────────────────────────────────────────────────────────────────────
# Magic Functions Implementation
# ──────────────────────────────────────────────────────────────────────────────

def func_json_parse(arg: Optional[str] = None) -> Any:
    """#(json?) - Parse JSON string, return None if invalid or no arg."""
    if arg is None or arg == "":
        return None
    try:
        return json.loads(arg)
    except (json.JSONDecodeError, TypeError):
        return None

def func_len(obj: Any) -> int:
    """$LEN(obj) - Length of string/list/dict."""
    if isinstance(obj, (str, list, tuple)):
        return len(obj)
    if isinstance(obj, dict):
        return len(obj.keys())
    if isinstance(obj, (int, float)):
        return len(str(obj))
    return 0

def func_in(obj: Any, *items: Any) -> bool:
    """$IN(obj, items...) - Check if obj in items. If 2nd arg is list, use it."""
    if len(items) == 0:
        return False
    
    # If first item is a list, use it
    if isinstance(items[0], (list, tuple)):
        return obj in items[0]
    
    # Otherwise, check against all items
    return obj in items

def func_ini(obj: Any, *items: Any) -> bool:
    """$INI(obj, items...) - Case-insensitive $IN."""
    obj_lower = _to_string(obj).lower()
    
    if len(items) == 0:
        return False
    
    # If first item is a list, use it
    if isinstance(items[0], (list, tuple)):
        return obj_lower in [_to_string(x).lower() for x in items[0]]
    
    # Otherwise, check against all items
    return obj_lower in [_to_string(x).lower() for x in items]

# Date/Time Functions

def func_now(pattern: Optional[str] = None) -> str:
    """$NOW(pattern?) - Current timestamp."""
    now = datetime.now()
    if pattern is None or pattern == "":
        return now.strftime(DEFAULT_DATETIME_FORMAT)
    return now.strftime(pattern)

def func_date(
    date_str: str,
    in_pattern: str,
    in_timezone: Optional[str] = None,
    out_timezone: Optional[str] = None,
    out_pattern: Optional[str] = None
) -> str:
    """$DATE(str, inPat, inTZ?, outTZ?, outPat?) - Parse and format date."""
    # Parse date
    dt = _parse_date(date_str, in_pattern)
    
    # TODO: Timezone conversion if needed (requires pytz)
    # For now, skip timezone conversion
    
    # Format output
    if out_pattern is None or out_pattern == "":
        return dt.strftime(DEFAULT_DATE_FORMAT)
    return dt.strftime(out_pattern)

def func_date_offset(date_str: str, *args: Any) -> str:
    """$DATE_OFFSET(date, n1, unit1, n2, unit2, ...) - Add/subtract time."""
    dt = _parse_date(date_str)
    
    # Process n, unit pairs
    if len(args) % 2 != 0:
        raise ValueError(f"$DATE_OFFSET requires pairs of (n, unit), got {len(args)} args")
    
    for i in range(0, len(args), 2):
        n = _to_number(args[i])
        unit = _to_string(args[i + 1]).lower()
        
        if unit in ['year', 'years']:
            dt = dt.replace(year=dt.year + int(n))
        elif unit in ['month', 'months']:
            # Handle month overflow
            new_month = dt.month + int(n)
            year_offset = (new_month - 1) // 12
            new_month = ((new_month - 1) % 12) + 1
            dt = dt.replace(year=dt.year + year_offset, month=new_month)
        elif unit in ['week', 'weeks']:
            dt = dt + timedelta(weeks=int(n))
        elif unit in ['day', 'days']:
            dt = dt + timedelta(days=int(n))
        elif unit in ['hour', 'hours']:
            dt = dt + timedelta(hours=int(n))
        elif unit in ['minute', 'minutes']:
            dt = dt + timedelta(minutes=int(n))
        elif unit in ['second', 'seconds']:
            dt = dt + timedelta(seconds=int(n))
        else:
            raise ValueError(f"Unknown time unit: {unit}")
    
    return dt.strftime(DEFAULT_DATE_FORMAT)

def func_date_diff(date1_str: str, date2_str: str, unit: str) -> int:
    """$DATE_DIFF(date1, date2, unit) - Calculate difference."""
    date1 = _parse_date(date1_str)
    date2 = _parse_date(date2_str)
    delta = date1 - date2
    
    unit = unit.lower()
    if unit in ['day', 'days']:
        return delta.days
    elif unit in ['week', 'weeks']:
        return delta.days // 7
    elif unit in ['month', 'months']:
        return (date1.year - date2.year) * 12 + (date1.month - date2.month)
    elif unit in ['year', 'years']:
        return date1.year - date2.year
    elif unit in ['hour', 'hours']:
        return int(delta.total_seconds() // 3600)
    elif unit in ['minute', 'minutes']:
        return int(delta.total_seconds() // 60)
    elif unit in ['second', 'seconds']:
        return int(delta.total_seconds())
    else:
        raise ValueError(f"Unknown time unit: {unit}")

# String Functions

def func_upper(s: Any) -> str:
    """$UPPER(s) - Convert to uppercase."""
    return _to_string(s).upper()

def func_lower(s: Any) -> str:
    """$LOWER(s) - Convert to lowercase."""
    return _to_string(s).lower()

def func_trim(s: Any) -> str:
    """$TRIM(s) - Remove leading/trailing whitespace."""
    return _to_string(s).strip()

def func_ltrim(s: Any) -> str:
    """$LTRIM(s) - Remove leading whitespace."""
    return _to_string(s).lstrip()

def func_rtrim(s: Any) -> str:
    """$RTRIM(s) - Remove trailing whitespace."""
    return _to_string(s).rstrip()

def func_substr(s: Any, start: int, length: Optional[int] = None) -> str:
    """$SUBSTR(s, start, len?) - Extract substring."""
    s = _to_string(s)
    start = int(start)
    if length is None:
        return s[start:]
    return s[start:start + int(length)]

def func_concat(*items: Any) -> str:
    """$CONCAT(items...) - Concatenate strings."""
    return ''.join(_to_string(item) for item in items)

def func_chr(code: int) -> str:
    """$CHR(code) - Convert ASCII/Unicode code to character."""
    try:
        return chr(int(code))
    except (ValueError, OverflowError):
        raise ValueError(f"Invalid character code: {code}")

def func_startswith(s: Any, prefix: Any) -> bool:
    """$STARTSWITH(s, prefix) - Check if starts with."""
    return _to_string(s).startswith(_to_string(prefix))

def func_endswith(s: Any, suffix: Any) -> bool:
    """$ENDSWITH(s, suffix) - Check if ends with."""
    return _to_string(s).endswith(_to_string(suffix))

def func_contains(s: Any, substr: Any) -> bool:
    """$CONTAINS(s, substr) - Check if contains substring."""
    return _to_string(substr) in _to_string(s)

def func_match(s: Any, pattern: str) -> bool:
    """$MATCH(s, pattern) - Check if matches regex."""
    return re.search(pattern, _to_string(s)) is not None

def func_split(s: Any, delimiter: str = "|", index: Optional[int] = None) -> Union[List[str], str]:
    """$SPLIT(s, delim?, n?) - Split string into array or return nth element."""
    s = _to_string(s)
    
    # Default delimiter
    if not isinstance(delimiter, str):
        delimiter = "|"
    
    result = s.split(delimiter)
    
    # If index specified, return that element
    if index is not None:
        try:
            idx = int(index)
            return result[idx]
        except (ValueError, IndexError):
            return None
    
    # Otherwise return full array
    return result

def func_join(obj: Any, delim1: str = "|", delim2: Optional[str] = None) -> str:
    """$JOIN(obj, delim1?, delim2?) - Join array/dict into string."""
    # Default delim1
    if not isinstance(delim1, str):
        delim1 = "|"
    
    # For dicts: delim2 defaults to delim1
    # For arrays: delim2 is ignored
    is_array = isinstance(obj, (list, tuple))
    if not is_array and delim2 is None:
        delim2 = delim1
    
    if is_array:
        # Array: just join items
        return delim1.join(_to_string(item) for item in obj)
    elif isinstance(obj, dict):
        # Dict: join key-value pairs
        # Object.entries(obj).map(kv => kv.join(delim2)).join(delim1)
        pairs = [delim2.join([_to_string(k), _to_string(v)]) for k, v in obj.items()]
        return delim1.join(pairs)
    else:
        return _to_string(obj)

# Comparison Functions

def func_eq(a: Any, b: Any) -> bool:
    """$EQ(a, b) - Equal (case-sensitive for strings)."""
    return a == b

def func_ne(a: Any, b: Any) -> bool:
    """$NE(a, b) - Not equal."""
    return a != b

def func_lt(a: Any, b: Any) -> bool:
    """$LT(a, b) - Less than."""
    return a < b

def func_le(a: Any, b: Any) -> bool:
    """$LE(a, b) - Less than or equal."""
    return a <= b

def func_gt(a: Any, b: Any) -> bool:
    """$GT(a, b) - Greater than."""
    return a > b

def func_ge(a: Any, b: Any) -> bool:
    """$GE(a, b) - Greater than or equal."""
    return a >= b

def func_eqi(a: Any, b: Any) -> bool:
    """$EQI(a, b) - Equal, case-insensitive."""
    return _to_string(a).lower() == _to_string(b).lower()

def func_nei(a: Any, b: Any) -> bool:
    """$NEI(a, b) - Not equal, case-insensitive."""
    return _to_string(a).lower() != _to_string(b).lower()

# Logical Functions

def func_if(condition: Any, then_value: Any, else_value: Any) -> Any:
    """$IF(cond, then, else) - Conditional expression."""
    # Truthy check
    if condition:
        return then_value
    return else_value

def func_and(*items: Any) -> bool:
    """$AND(items...) - Logical AND, short-circuit."""
    for item in items:
        if not item:
            return False
    return True

def func_or(*items: Any) -> Any:
    """$OR(items...) - Logical OR, return first truthy value."""
    for item in items:
        if item:  # Truthy
            return item
    return False

def func_not(value: Any) -> bool:
    """$NOT(value) - Logical NOT."""
    return not value

# Null/Empty Checks

def func_z(value: Any = None) -> bool:
    """$Z(value?) - Check if null/empty. No arg returns True."""
    return _is_null_or_empty(value)

def func_n(value: Any) -> bool:
    """$N(value) - Check if non-null/non-empty."""
    return _is_non_null(value)

def func_first_n(*items: Any) -> Any:
    """$FIRST_N(items...) - Return first non-null/non-empty."""
    for item in items:
        if _is_non_null(item):
            return item
    return None

def func_first_z(*items: Any) -> Any:
    """$FIRST_Z(items...) - Return first null/empty."""
    for item in items:
        if _is_null_or_empty(item):
            return item
    return None

# Math Functions

def func_plus(*items: Any) -> Union[int, float]:
    """$PLUS(items...) - Addition (variadic)."""
    if len(items) < 2:
        raise ValueError("$PLUS requires at least 2 arguments")
    result = _to_number(items[0])
    for item in items[1:]:
        result += _to_number(item)
    return result

def func_minus(*items: Any) -> Union[int, float]:
    """$MINUS(items...) - Subtraction (variadic)."""
    if len(items) < 2:
        raise ValueError("$MINUS requires at least 2 arguments")
    result = _to_number(items[0])
    for item in items[1:]:
        result -= _to_number(item)
    return result

def func_multiply(*items: Any) -> Union[int, float]:
    """$MULTIPLY(items...) - Multiplication (variadic)."""
    if len(items) < 2:
        raise ValueError("$MULTIPLY requires at least 2 arguments")
    result = _to_number(items[0])
    for item in items[1:]:
        result *= _to_number(item)
    return result

def func_divide(*items: Any) -> Union[int, float]:
    """$DIVIDE(items...) - Division (variadic)."""
    if len(items) < 2:
        raise ValueError("$DIVIDE requires at least 2 arguments")
    result = _to_number(items[0])
    for item in items[1:]:
        divisor = _to_number(item)
        if divisor == 0:
            raise ValueError("Division by zero")
        result /= divisor
    return result

def func_modulo(a: Any, b: Any) -> Union[int, float]:
    """$MODULO(a, b) - Modulo operation."""
    return _to_number(a) % _to_number(b)

def func_power(*items: Any) -> Union[int, float]:
    """$POWER(items...) - Exponentiation (variadic)."""
    if len(items) < 2:
        raise ValueError("$POWER requires at least 2 arguments")
    result = _to_number(items[0])
    for item in items[1:]:
        result = result ** _to_number(item)
    return result

def func_abs(n: Any) -> Union[int, float]:
    """$ABS(n) - Absolute value."""
    return abs(_to_number(n))

def func_min(*items: Any) -> Union[int, float]:
    """$MIN(items...) - Minimum value."""
    if len(items) == 0:
        raise ValueError("$MIN requires at least 1 argument")
    return min(_to_number(item) for item in items)

def func_max(*items: Any) -> Union[int, float]:
    """$MAX(items...) - Maximum value."""
    if len(items) == 0:
        raise ValueError("$MAX requires at least 1 argument")
    return max(_to_number(item) for item in items)

def func_round(n: Any, decimals: int = 0) -> Union[int, float]:
    """$ROUND(n, decimals?) - Round number."""
    return round(_to_number(n), int(decimals))

def func_even(n: Any) -> bool:
    """$EVEN(n) - Check if number is even."""
    return int(_to_number(n)) % 2 == 0

def func_odd(n: Any) -> bool:
    """$ODD(n) - Check if number is odd."""
    return int(_to_number(n)) % 2 != 0

# Hashing & IDs

def func_md5(*items: Any) -> str:
    """$MD5(items...) - Generate MD5 hash."""
    concatenated = ''.join(_to_string(item) for item in items)
    return hashlib.md5(concatenated.encode()).hexdigest()

def func_uuid() -> str:
    """$UUID() - Generate random UUID."""
    return str(uuid.uuid4())

# Collection Functions

def func_push(arr: Any, item: Any) -> List[Any]:
    """$PUSH(arr, item) - Add item to array (returns new array)."""
    if not isinstance(arr, list):
        arr = [arr]
    return arr + [item]

def func_keys(obj: Any) -> List[str]:
    """$KEYS(obj) - Get object keys."""
    if isinstance(obj, dict):
        return list(obj.keys())
    return []

def func_values(obj: Any) -> List[Any]:
    """$VALUES(obj) - Get object values."""
    if isinstance(obj, dict):
        return list(obj.values())
    return []

def func_entries(obj: Any) -> List[List[Any]]:
    """$ENTRIES(obj) - Get object entries as [key, value] pairs."""
    if isinstance(obj, dict):
        return [[k, v] for k, v in obj.items()]
    return []

# ──────────────────────────────────────────────────────────────────────────────
# Function Registry
# ──────────────────────────────────────────────────────────────────────────────

MAGIC_FUNCTIONS: Dict[str, Callable] = {
    # JSON & Data
    '#': func_json_parse,
    'LEN': func_len,
    'IN': func_in,
    'INI': func_ini,
    
    # Date/Time
    'NOW': func_now,
    'DATE': func_date,
    'DATE_OFFSET': func_date_offset,
    'DATE_DIFF': func_date_diff,
    
    # String - Basic
    'UPPER': func_upper,
    'LOWER': func_lower,
    'TRIM': func_trim,
    'LTRIM': func_ltrim,
    'RTRIM': func_rtrim,
    'SUBSTR': func_substr,
    'CONCAT': func_concat,
    'CHR': func_chr,
    
    # String - Checks
    'STARTSWITH': func_startswith,
    'ENDSWITH': func_endswith,
    'CONTAINS': func_contains,
    'MATCH': func_match,
    
    # String - Arrays
    'SPLIT': func_split,
    'JOIN': func_join,
    
    # Comparison
    'EQ': func_eq,
    'NE': func_ne,
    'LT': func_lt,
    'LE': func_le,
    'GT': func_gt,
    'GE': func_ge,
    'EQI': func_eqi,
    'NEI': func_nei,
    
    # Logical
    'IF': func_if,
    'AND': func_and,
    'OR': func_or,
    'NOT': func_not,
    
    # Null Checks
    'Z': func_z,
    'N': func_n,
    'FIRST_N': func_first_n,
    'FIRST_Z': func_first_z,
    
    # Math
    'PLUS': func_plus,
    'MINUS': func_minus,
    'MULTIPLY': func_multiply,
    'DIVIDE': func_divide,
    'MODULO': func_modulo,
    'POWER': func_power,
    'ABS': func_abs,
    'MIN': func_min,
    'MAX': func_max,
    'ROUND': func_round,
    'EVEN': func_even,
    'ODD': func_odd,
    
    # Hashing
    'MD5': func_md5,
    'UUID': func_uuid,
    
    # Collections
    'PUSH': func_push,
    'KEYS': func_keys,
    'VALUES': func_values,
    'ENTRIES': func_entries,
}

# ──────────────────────────────────────────────────────────────────────────────
# Parser & Evaluator
# ──────────────────────────────────────────────────────────────────────────────

def _interpolate_variables(expression: str, row_data: Dict[str, Any]) -> str:
    """Replace %(column_name) with actual values from row_data."""
    # Find all %(...)
    pattern = r'%\(([^)]+)\)'
    
    def replace_var(match):
        col_name = match.group(1)
        if col_name not in row_data:
            raise ValueError(f"Column not found: {col_name}")
        value = row_data[col_name]
        # Use _to_string helper (handles datetime, bool, None, etc.)
        return _to_string(value)
    
    return re.sub(pattern, replace_var, expression)

def _parse_function_call(expression: str, row_data: Dict[str, Any]) -> Any:
    """Parse and evaluate a function call."""
    # Check if it's a function call
    func_pattern = r'^([#$][A-Z_]+)\((.*)\)$'
    match = re.match(func_pattern, expression, re.DOTALL)
    
    if not match:
        # Not a function call, return as-is
        return expression
    
    func_name = match.group(1)
    args_str = match.group(2)
    
    # Special handling for # (JSON parse)
    if func_name == '#':
        func_key = '#'
    else:
        # Remove $ prefix
        func_key = func_name[1:]
    
    if func_key not in MAGIC_FUNCTIONS:
        raise ValueError(f"Unknown function: {func_name}")
    
    # Parse arguments (split by comma, respecting nested calls)
    args = _parse_arguments(args_str, row_data)
    
    # Execute function
    func = MAGIC_FUNCTIONS[func_key]
    try:
        return func(*args)
    except TypeError as e:
        raise ValueError(f"{func_name}: {str(e)}")

def _parse_arguments(args_str: str, row_data: Dict[str, Any]) -> List[Any]:
    """Parse comma-separated arguments, handling nested function calls."""
    if not args_str.strip():
        return []
    
    args = []
    current_arg = ""
    depth = 0
    
    for char in args_str:
        if char == '(' :
            depth += 1
            current_arg += char
        elif char == ')':
            depth -= 1
            current_arg += char
        elif char == ',' and depth == 0:
            # End of argument
            args.append(current_arg.strip())
            current_arg = ""
        else:
            current_arg += char
    
    # Add last argument
    if current_arg.strip():
        args.append(current_arg.strip())
    
    # Evaluate each argument (could be nested function call or variable)
    evaluated_args = []
    for arg in args:
        # Interpolate variables first
        arg = _interpolate_variables(arg, row_data)
        # Then evaluate if it's a function call
        arg = evaluate(arg, row_data)
        evaluated_args.append(arg)
    
    return evaluated_args

def evaluate(expression: str, row_data: Dict[str, Any]) -> Any:
    """
    Parse and evaluate a magic function expression.
    
    Args:
        expression: Expression string (e.g., "$UPPER(%(name))")
        row_data: Dictionary of column values
    
    Returns:
        Evaluated result
    
    Examples:
        >>> evaluate("$UPPER(%(name))", {"name": "john"})
        'JOHN'
        
        >>> evaluate("$IF($GT(%(age),18),adult,minor)", {"age": 25})
        'adult'
    """
    expression = expression.strip()
    
    # Check if it's a function call
    if expression.startswith(('$', '#')):
        return _parse_function_call(expression, row_data)
    
    # Check if it contains variables
    if '%(' in expression:
        return _interpolate_variables(expression, row_data)
    
    # Plain string
    return expression

# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

__all__ = ['evaluate', 'MAGIC_FUNCTIONS']

if __name__ == '__main__':
    # Simple test
    row_data = {
        "name": "John Doe",
        "age": 25,
        "date": "2024-01-15"
    }
    
    tests = [
        ("$UPPER(%(name))", "JOHN DOE"),
        ("$IF($GT(%(age),18),adult,minor)", "adult"),
        ("$DATE_DIFF(2024-06-15,%(date),months)", 5),
    ]
    
    for expr, expected in tests:
        result = evaluate(expr, row_data)
        status = "✓" if result == expected else "✗"
        print(f"{status} {expr} → {result} (expected: {expected})")
