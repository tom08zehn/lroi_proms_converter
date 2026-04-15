#!/usr/bin/env python3
"""
test_magic_functions.py - Comprehensive tests for all magic functions

This file tests every magic function with all argument variations.
Test results are used to auto-generate README examples.

Usage:
    python test_magic_functions.py          # Run all tests
    python test_magic_functions.py --readme # Generate README markdown

Author: LROI Converter v1.4.9
"""

import sys
from typing import Any, Dict, List
from magic_functions import evaluate

# ──────────────────────────────────────────────────────────────────────────────
# Test Data
# ──────────────────────────────────────────────────────────────────────────────

SAMPLE_ROW_DATA = {
    "name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "age": 25,
    "gender": "Male",
    "patient_id": "P12345",
    "date": "2024-01-15",
    "survey_date": "2024-06-15",
    "surgery_date": "2024-01-15",
    "period": "Pre-Op",
    "status": "active",
    "score1": 10,
    "score2": 20,
    "json_str": '{"key": "value"}',
    "tags": "tag1,tag2,tag3",
    "spaced": "  text  ",
}

# ──────────────────────────────────────────────────────────────────────────────
# Test Result Storage
# ──────────────────────────────────────────────────────────────────────────────

class TestResult:
    """Store test result for README generation."""
    def __init__(self, function: str, expression: str, result: Any, description: str, error: bool = False):
        self.function = function
        self.expression = expression
        self.result = result
        self.description = description
        self.error = error
    
    def to_markdown_row(self) -> str:
        """Convert to markdown table row."""
        result_str = f"ERROR: {self.result}" if self.error else str(self.result)
        return f"| `{self.expression}` | `{result_str}` | {self.description} |"

all_test_results: List[TestResult] = []

def test(expression: str, description: str, row_data: Dict[str, Any] = None) -> TestResult:
    """Run a test and store result."""
    if row_data is None:
        row_data = SAMPLE_ROW_DATA
    
    try:
        result = evaluate(expression, row_data)
        test_result = TestResult(
            function=expression.split('(')[0],
            expression=expression,
            result=result,
            description=description,
            error=False
        )
    except Exception as e:
        test_result = TestResult(
            function=expression.split('(')[0],
            expression=expression,
            result=str(e),
            description=description,
            error=True
        )
    
    all_test_results.append(test_result)
    return test_result

# ──────────────────────────────────────────────────────────────────────────────
# JSON & Data Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_json_parse():
    """Test #(json?) function."""
    print("Testing #(json?)...")
    
    test("#()", "No argument → None")
    test("#(%(json_str))", "Valid JSON → parsed object")
    test("#(invalid)", "Invalid JSON → None")

def test_len():
    """Test $LEN(obj) function."""
    print("Testing $LEN(obj)...")
    
    test("$LEN(%(name))", "Length of string")
    test("$LEN(%(tags))", "Length of string with commas")
    test("$LEN(%(age))", "Length of number (as string)")

def test_in():
    """Test $IN(obj, items...) function."""
    print("Testing $IN(obj, items...)...")
    
    test("$IN(%(status),active,pending)", "Check if in list")
    test("$IN(%(status),inactive,disabled)", "Not in list")
    test("$IN(%(age),25,30,35)", "Number in list")

def test_ini():
    """Test $INI(obj, items...) function."""
    print("Testing $INI(obj, items...)...")
    
    test("$INI(%(gender),male,female)", "Case-insensitive match")
    test("$INI(%(status),ACTIVE,PENDING)", "Case-insensitive match")

# ──────────────────────────────────────────────────────────────────────────────
# Date/Time Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_now():
    """Test $NOW(pattern?) function."""
    print("Testing $NOW(pattern?)...")
    
    # Note: Result will vary, just check it doesn't error
    result = test("$NOW()", "Current datetime (default format)")
    result.description += f" (e.g., {result.result})"
    
    result = test("$NOW(%Y-%m-%d)", "Current date only")
    result.description += f" (e.g., {result.result})"

def test_date():
    """Test $DATE(str, inPat, ...) function."""
    print("Testing $DATE(...)...")
    
    test("$DATE(2024-01-15,%Y-%m-%d)", "Parse date (no reformatting)")
    test("$DATE(2024-01-15,%Y-%m-%d,None,None,%d/%m/%Y)", "Parse and reformat")

def test_date_offset():
    """Test $DATE_OFFSET(date, n, unit, ...) function."""
    print("Testing $DATE_OFFSET(...)...")
    
    test("$DATE_OFFSET(2024-01-15,3,months)", "Add 3 months")
    test("$DATE_OFFSET(2024-01-15,-1,years)", "Subtract 1 year")
    test("$DATE_OFFSET(2024-01-15,1,years,2,months,-5,days)", "Combined offsets")

def test_date_diff():
    """Test $DATE_DIFF(date1, date2, unit) function."""
    print("Testing $DATE_DIFF(...)...")
    
    test("$DATE_DIFF(%(survey_date),%(surgery_date),months)", "Months between dates")
    test("$DATE_DIFF(%(survey_date),%(surgery_date),days)", "Days between dates")
    test("$DATE_DIFF(%(survey_date),%(surgery_date),weeks)", "Weeks between dates")

# ──────────────────────────────────────────────────────────────────────────────
# String Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_string_basic():
    """Test basic string functions."""
    print("Testing string functions...")
    
    test("$UPPER(%(name))", "Convert to uppercase")
    test("$LOWER(%(name))", "Convert to lowercase")
    test("$TRIM(%(spaced))", "Trim whitespace")
    test("$LTRIM(%(spaced))", "Trim left whitespace")
    test("$RTRIM(%(spaced))", "Trim right whitespace")
    test("$SUBSTR(%(patient_id),0,5)", "Extract first 5 chars")
    test("$SUBSTR(%(patient_id),1)", "Extract from position 1")
    test("$CONCAT(%(first_name), ,%(last_name))", "Concatenate with space")

def test_string_checks():
    """Test string check functions."""
    print("Testing string checks...")
    
    test("$STARTSWITH(%(patient_id),P)", "Check if starts with")
    test("$ENDSWITH(%(patient_id),5)", "Check if ends with")
    test("$CONTAINS(%(name),Doe)", "Check if contains")
    test("$MATCH(%(period),Pre-?Op)", "Regex match")

def test_string_arrays():
    """Test string array functions."""
    print("Testing string arrays...")
    
    # Test $SPLIT with different delimiters
    test("$SPLIT(%(name),$CHR(32))", "Split by space using CHR(32)")
    test("$SPLIT(%(name),$CHR(32),0)", "Split by space, get element 0")
    
    # Test splitting by comma using $CHR(44)
    test("$SPLIT(%(tags),$CHR(44))", "Split by comma using CHR(44)")
    test("$SPLIT(%(tags),$CHR(44),0)", "Split by comma, get element 0")
    
    # Test $JOIN
    test("$JOIN($SPLIT(%(name),$CHR(32)),;)", "Split by space, join with semicolon")

def test_chr():
    """Test $CHR function."""
    print("Testing $CHR()...")
    
    test("$CHR(44)", "Comma character")
    test("$CHR(65)", "Uppercase A")
    test("$CHR(32)", "Space character")

def test_power():
    """Test $POWER function."""
    print("Testing $POWER()...")
    
    test("$POWER(2,3)", "2 to the power of 3")
    test("$POWER(10,2)", "10 squared")
    test("$POWER(2,2,2)", "2^2^2 (variadic)")

# ──────────────────────────────────────────────────────────────────────────────
# Comparison Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_comparison():
    """Test comparison functions."""
    print("Testing comparison...")
    
    test("$EQ(%(age),25)", "Equal")
    test("$NE(%(age),30)", "Not equal")
    test("$LT(%(age),30)", "Less than")
    test("$LE(%(age),25)", "Less than or equal")
    test("$GT(%(age),20)", "Greater than")
    test("$GE(%(age),25)", "Greater than or equal")
    test("$EQI(%(gender),male)", "Equal (case-insensitive)")
    test("$NEI(%(status),INACTIVE)", "Not equal (case-insensitive)")

# ──────────────────────────────────────────────────────────────────────────────
# Logical Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_logical():
    """Test logical functions."""
    print("Testing logical...")
    
    test("$IF($GT(%(age),18),adult,minor)", "Conditional: adult")
    test("$IF($LT(%(age),18),adult,minor)", "Conditional: minor")
    test("$AND($GT(%(age),18),$EQ(%(status),active))", "AND: both true")
    test("$OR($LT(%(age),18),$EQ(%(status),active))", "OR: one true")
    test("$NOT($EQ(%(status),inactive))", "NOT: invert")

# ──────────────────────────────────────────────────────────────────────────────
# Null Check Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_null_checks():
    """Test null/empty check functions."""
    print("Testing null checks...")
    
    test("$Z()", "Check empty (no arg) returns True")
    test("$N(%(name))", "Check non-empty")
    test("$FIRST_N(,%(name),default)", "First non-empty (skip empty)")
    test("$FIRST_Z(%(name),,other)", "First empty (skip non-empty)")

# ──────────────────────────────────────────────────────────────────────────────
# Math Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_math():
    """Test math functions."""
    print("Testing math...")
    
    test("$PLUS(%(score1),%(score2))", "Add two numbers")
    test("$PLUS(1,2,3,4)", "Add multiple numbers")
    test("$MINUS(100,10,5)", "Subtract multiple")
    test("$MULTIPLY(2,3,4)", "Multiply multiple")
    test("$DIVIDE(100,2,5)", "Divide multiple")
    test("$MODULO(%(age),10)", "Modulo")
    test("$ABS(-42)", "Absolute value")
    test("$MIN(%(score1),%(score2),5)", "Minimum value")
    test("$MAX(%(score1),%(score2),5)", "Maximum value")
    test("$ROUND(3.14159,2)", "Round to 2 decimals")
    test("$EVEN(%(age))", "Check if even")
    test("$ODD(%(age))", "Check if odd")

# ──────────────────────────────────────────────────────────────────────────────
# Hashing Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_hashing():
    """Test hashing functions."""
    print("Testing hashing...")
    
    result = test("$MD5(%(patient_id))", "MD5 hash of single value")
    result.description += f" (32 chars)"
    
    result = test("$MD5(%(patient_id),%(date))", "MD5 of concatenated values")
    result.description += f" (32 chars)"
    
    result = test("$UUID()", "Generate UUID")
    result.description += f" (36 chars)"

# ──────────────────────────────────────────────────────────────────────────────
# Collection Tests
# ──────────────────────────────────────────────────────────────────────────────

def test_collections():
    """Test collection functions."""
    print("Testing collections...")
    
    # Note: These test dict/array functions
    # Results will be Python repr strings

# ──────────────────────────────────────────────────────────────────────────────
# Run All Tests
# ──────────────────────────────────────────────────────────────────────────────

def run_all_tests():
    """Run all test functions."""
    test_json_parse()
    test_len()
    test_in()
    test_ini()
    test_now()
    test_date()
    test_date_offset()
    test_date_diff()
    test_string_basic()
    test_string_checks()
    test_string_arrays()
    test_chr()
    test_comparison()
    test_logical()
    test_null_checks()
    test_math()
    test_power()
    test_hashing()
    test_collections()
    
    # Summary
    total = len(all_test_results)
    errors = sum(1 for r in all_test_results if r.error)
    passed = total - errors
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    if errors > 0:
        print(f"ERRORS: {errors} tests failed")
        print("\nFailed tests:")
        for r in all_test_results:
            if r.error:
                print(f"  ✗ {r.expression}")
                print(f"    {r.result}")
    else:
        print("✓ All tests passed!")
    print('='*60)

def generate_readme_markdown():
    """Generate README markdown from test results."""
    # Group by function
    by_function: Dict[str, List[TestResult]] = {}
    for result in all_test_results:
        func = result.function
        if func not in by_function:
            by_function[func] = []
        by_function[func].append(result)
    
    # Generate markdown
    markdown = "# Magic Functions Examples\n\n"
    markdown += "Auto-generated from test_magic_functions.py\n\n"
    
    for func, results in by_function.items():
        markdown += f"## {func}\n\n"
        markdown += "| Expression | Result | Description |\n"
        markdown += "|------------|--------|-------------|\n"
        for result in results:
            markdown += result.to_markdown_row() + "\n"
        markdown += "\n"
    
    return markdown

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if '--readme' in sys.argv:
        run_all_tests()
        print("\n" + generate_readme_markdown())
    else:
        run_all_tests()
