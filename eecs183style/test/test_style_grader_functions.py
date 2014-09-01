import unittest

from eecs183style.style_grader_functions import check_operator_spacing_around


class TestOperatorRegex(unittest.TestCase):
    """Test the `check_operator_spacing_around` function."""

    def test_parentheses(self):
        """Ensure `check_operator_spacing_around` is okay with parentheses."""
        self._run_code("(foo @ 3)", None)

    def test_invalid_spacing(self):
        """Ensure `check_operator_spacing_around` catches invalid spacing."""
        # Invalid code and the columns where the operator is. We replace '@'
        # with each operator. `check_operator_spacing_around` /should/ work
        # fine independent of the actual operator, but we check just in case.
        invalid_code = [
            ("foo @3", 4),
            ("foo@ 3", 3),
            ("foo@3", 3),
            ("foo  @ bar", 5),
            ("foo@   bar", 3),
        ]

        for code, column in invalid_code:
            self._run_code(code, column)

    def _run_code(self, code, expected_result):
        """Checks the given code with many operators and yields the results.

        Asserts that the actual result is the same as the expected result.

        :param str code: The code to run, with @s instead of operators, such as
                         'foo @ bar'.
        :param mixed expected_result: The expected result of checking the code.
        """
        operators = ["+", "-", "/", "%"]
        operators = operators + [i + "=" for i in operators]
        for i in operators:
            result = check_operator_spacing_around(code.replace("@", i), i)
            self.assertEqual(result, expected_result)

    def test_in_long_line(self):
        """Ensure `check_operator_spacing_around` handles multiple tokens."""
        self._run_code("foo bar @ baz", None)
        self._run_code("foo bar    @ baz", 11)
