#!/usr/bin/env python3
"""
test_magic_parser.py - Focused tests for the magic expression parser.

Run:  python -m unittest test_magic_parser -v      (or: pytest test_magic_parser.py)

Behavior is cloned from ZBEdgeUtils.js `magic()`; deliberate differences are
listed in the "Parser & Evaluator" comment block in magic_functions.py.
"""
import unittest

import magic_functions
from magic_functions import evaluate, MagicSyntaxError, NESTING_LIMIT

ROW = {
    "name": "John Doe",
    "age": 25,
    "flag_false": False,
    "flag_true": True,
    "foo (bar)": "BAR",
    "1. How are you today (1 = good, 2 = ok, 3 = bad)?": "good",
    "  padded  ": "P",
    "json_str": '{"a": 1, "b": [1, 2]}',
    "tricky": "$UUID()",          # data that looks like an expression
    "tricky_var": "%(name)",
    "empty": "",
}


class VariableTests(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(evaluate("%(name)", ROW), "John Doe")

    def test_type_preserved(self):
        self.assertEqual(evaluate("%(age)", ROW), 25)
        self.assertIs(evaluate("%(flag_false)", ROW), False)

    def test_balanced_brackets_in_name(self):
        self.assertEqual(evaluate("%(foo (bar))", ROW), "BAR")

    def test_name_with_brackets_commas_and_question_mark(self):
        key = "%(1. How are you today (1 = good, 2 = ok, 3 = bad)?)"
        self.assertEqual(evaluate(key, ROW), "good")

    def test_whitespace_in_name_is_significant(self):
        self.assertEqual(evaluate("%(  padded  )", ROW), "P")
        with self.assertRaises(ValueError):
            evaluate("%(padded)", ROW)

    def test_whitespace_around_expression_ignored(self):
        self.assertEqual(evaluate("  %(name)\n", ROW), "John Doe")

    def test_missing_variable_raises(self):
        with self.assertRaisesRegex(ValueError, "Column not found: nope"):
            evaluate("%(nope)", ROW)

    def test_variable_as_argument_in_function(self):
        self.assertEqual(evaluate("$UPPER(%(foo (bar)))", ROW), "BAR")
        self.assertEqual(evaluate("$EQ(%(1. How are you today (1 = good, 2 = ok, 3 = bad)?),good)", ROW), True)

    def test_no_interpolation_inside_text(self):
        # Text mixed with an expression is a static string
        self.assertEqual(evaluate("Hello %(name) x", ROW), "Hello %(name) x")
        self.assertEqual(evaluate("50% done", ROW), "50% done")


class FunctionTests(unittest.TestCase):
    def test_simple_and_nested(self):
        self.assertEqual(evaluate("$UPPER(%(name))", ROW), "JOHN DOE")
        self.assertEqual(evaluate("$IF($GT(%(age),18),adult,minor)", ROW), "adult")
        self.assertEqual(evaluate("$UPPER($LOWER($TRIM(  Ab  )))", ROW), "AB")

    def test_literal_argument_whitespace_preserved(self):
        captured = {}
        magic_functions.MAGIC_FUNCTIONS["FOO"] = lambda *a: captured.setdefault("args", a)
        try:
            evaluate("$FOO(bar, baz )", ROW)
        finally:
            del magic_functions.MAGIC_FUNCTIONS["FOO"]
        self.assertEqual(captured["args"], ("bar", " baz "))

    def test_concat_keeps_space_argument(self):
        self.assertEqual(evaluate("$CONCAT(a, ,b)", ROW), "a b")

    def test_whitespace_around_nested_expression_ignored(self):
        self.assertEqual(evaluate("$CONCAT( %(name) , $UPPER(x) )", ROW), "John DoeX")

    def test_empty_parentheses_pass_no_arguments(self):
        self.assertEqual(len(evaluate("$UUID()", ROW)), 36)   # takes no args -> would fail with ("",)
        self.assertIs(evaluate("$Z()", ROW), True)

    def test_empty_arguments(self):
        self.assertEqual(evaluate("$FIRST_N(,%(name),default)", ROW), "John Doe")
        self.assertEqual(evaluate("$CONCAT(,,)", ROW), "")

    def test_function_name_with_underscore(self):
        self.assertEqual(evaluate("$FIRST_N(,abc)", ROW), "abc")
        # Function names containing digits do not match the configured syntax.
        self.assertEqual(evaluate("$MD5_1(abc)", ROW), "$MD5_1(abc)")

    def test_variable_type_preserved_as_argument(self):
        self.assertEqual(evaluate("$IF(%(flag_false),yes,no)", ROW), "no")
        self.assertEqual(evaluate("$IF(%(flag_true),yes,no)", ROW), "yes")

    def test_unknown_function(self):
        with self.assertRaisesRegex(ValueError, "Unknown function: \\$NOPE"):
            evaluate("$NOPE(x)", ROW)

    def test_lowercase_or_unparenthesised_is_static(self):
        self.assertEqual(evaluate("$upper(x)", ROW), "$upper(x)")
        self.assertEqual(evaluate("$UPPER", ROW), "$UPPER")
        self.assertEqual(evaluate("cost $5 (est)", ROW), "cost $5 (est)")

    def test_wrong_argument_count(self):
        with self.assertRaises(ValueError):
            evaluate("$UPPER(a,b)", ROW)

    def test_percent_in_plain_arguments(self):
        # strftime patterns must not be mistaken for variables
        self.assertEqual(evaluate("$DATE(2024-01-15,%Y-%m-%d,None,None,%d/%m/%Y)", ROW), "15/01/2024")

    def test_balanced_brackets_in_plain_argument(self):
        self.assertIs(evaluate("$MATCH(xyz,(a|b)c)", ROW), False)
        self.assertIs(evaluate("$MATCH(bc,(a|b)c)", ROW), True)


class JsonTests(unittest.TestCase):
    def test_variable_payload(self):
        self.assertEqual(evaluate("#(%(json_str))", ROW), {"a": 1, "b": [1, 2]})

    def test_literal_with_commas(self):
        self.assertEqual(evaluate('#({"a":1,"b":2})', ROW), {"a": 1, "b": 2})
        self.assertEqual(evaluate("#([1,2,3])", ROW), [1, 2, 3])

    def test_nested_function_piece_is_resolved(self):
        self.assertEqual(evaluate("#([1,$PLUS(1,1),3])", ROW), [1, 2, 3])

    def test_simple_types(self):
        self.assertIs(evaluate("#(true)", ROW), True)
        self.assertEqual(evaluate("#(1)", ROW), 1)
        self.assertIsNone(evaluate("#(null)", ROW))
        self.assertIs(evaluate("#(%(flag_true))", ROW), True)
        self.assertIs(evaluate("#(%(flag_false))", ROW), False)

    def test_invalid_or_empty_returns_none(self):
        self.assertIsNone(evaluate("#(invalid)", ROW))
        self.assertIsNone(evaluate("#()", ROW))
        self.assertIsNone(evaluate("#(%(empty))", ROW))

    def test_json_as_function_argument(self):
        self.assertEqual(evaluate('$LEN(#({"a":1,"b":2}))', ROW), 2)
        self.assertEqual(evaluate("$IF(%(flag_false),#(1),#(false))", ROW), False)

    def test_unevaluated_inside_json_text(self):
        # Only whole pieces are expressions; this piece is plain text -> invalid JSON -> None
        self.assertIsNone(evaluate('#({"b":$UPPER(x)})', ROW))


class DataIsNotReEvaluatedTests(unittest.TestCase):
    def test_variable_value_that_looks_like_function(self):
        self.assertEqual(evaluate("%(tricky)", ROW), "$UUID()")
        self.assertEqual(evaluate("$CONCAT(%(tricky),!)", ROW), "$UUID()!")

    def test_variable_value_that_looks_like_variable(self):
        self.assertEqual(evaluate("%(tricky_var)", ROW), "%(name)")
        self.assertEqual(evaluate("$UPPER(%(tricky_var))", ROW), "%(NAME)")


class MalformedTests(unittest.TestCase):
    def assertSyntaxError(self, expr):
        with self.assertRaises(MagicSyntaxError, msg=expr):
            evaluate(expr, ROW)

    def test_missing_closing_bracket(self):
        self.assertSyntaxError("$UPPER(abc")
        self.assertSyntaxError("%(foo (bar)")
        self.assertSyntaxError("%(1. How are you today (1 = good, 2 = ok, 3 = bad?)")
        self.assertSyntaxError("$EQ(%(1. How are you today (1 = good, 2 = ok, 3 = bad?,nope)")
        self.assertSyntaxError("#({\"a\":\"(\"})")

    def test_unbalanced_in_plain_argument(self):
        self.assertSyntaxError("$CONCAT(smile :(,x)")
        self.assertSyntaxError("$CONCAT(smile :),x)")

    def test_extra_closing_bracket(self):
        self.assertSyntaxError("%(name))")
        self.assertSyntaxError("$UPPER(a))")

    def test_trailing_text(self):
        self.assertSyntaxError("$UPPER(a) and $UPPER(b)")
        self.assertSyntaxError("%(name) tail")

    def test_error_is_value_error(self):
        # the application catches Exception/ValueError
        self.assertTrue(issubclass(MagicSyntaxError, ValueError))


class MultiLineTests(unittest.TestCase):
    def test_multiline_after_converter_line_strip(self):
        # converter.py strips each line but keeps the "\n"
        expr = "$IF(\n$GT(%(age),18),\nadult,\nminor\n)\n"
        self.assertEqual(evaluate(expr, ROW), "adult")

    def test_multiline_with_indentation(self):
        expr = "\n$IF(\n   $GT(%(age),18),\n   adult,\n   minor\n)\n"
        self.assertEqual(evaluate(expr, ROW), "adult")

    def test_multiline_numeric_literals(self):
        expr = "$IF(\n$LT(%(age),18),\n-1,\n$IF(\n$GE(%(age),12),\n12,\n0\n)\n)"
        self.assertEqual(evaluate(expr, ROW), "12")

    def test_spaces_on_a_single_line_are_kept(self):
        self.assertEqual(evaluate("$CONCAT(a,\n b ,c)", ROW), "ab c")


class NestingLimitTests(unittest.TestCase):
    @staticmethod
    def nested(depth):
        return "$TRIM(" * depth + "x" + ")" * depth

    def test_limit_value(self):
        self.assertEqual(NESTING_LIMIT, 32)

    def test_at_limit_ok(self):
        # the innermost *argument* is evaluated at depth == NESTING_LIMIT
        self.assertEqual(evaluate(self.nested(NESTING_LIMIT), ROW), "x")

    def test_beyond_limit_raises(self):
        with self.assertRaisesRegex(MagicSyntaxError, "NESTING_LIMIT"):
            evaluate(self.nested(NESTING_LIMIT + 1), ROW)

    def test_limit_is_configurable(self):
        old = magic_functions.NESTING_LIMIT
        try:
            magic_functions.NESTING_LIMIT = 2
            self.assertEqual(evaluate(self.nested(2), ROW), "x")
            with self.assertRaises(MagicSyntaxError):
                evaluate(self.nested(3), ROW)
        finally:
            magic_functions.NESTING_LIMIT = old

    def test_deep_input_does_not_hit_python_recursion_limit(self):
        with self.assertRaises(MagicSyntaxError):
            evaluate(self.nested(5000), ROW)


if __name__ == "__main__":
    unittest.main(verbosity=2)
