import unittest
import sys
import os

# Ensure project root is accessible
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.value import Value, Status, Reason, SemanticError


class TestValue(unittest.TestCase):

    def test_valid_addition_produces_valid_value(self):
        a = Value(2)
        b = Value(3)
        c = a.add(b)
        self.assertTrue(c.is_valid())
        self.assertEqual(c.value, 5)

    def test_division_by_zero_produces_invalid(self):
        a = Value(10)
        b = Value(0)
        c = a.div(b)

        self.assertFalse(c.is_valid())
        self.assertEqual(c.status, Status.INVALID)
        self.assertEqual(c.reason, Reason.DivisionByZero)
    
    def test_invalid_value_has_no_numeric_value(self):
        a = Value(10)
        b = Value(0)
        c = a.div(b)

        self.assertIsNone(c.value)

    def test_invalid_propagates_through_operations(self):
        a = Value(10)
        b = Value(0)
        c = a.div(b)
        d = c.add(Value(5))

        self.assertFalse(d.is_valid())
        self.assertEqual(d.reason, Reason.DivisionByZero)

    def test_first_invalid_reason_is_preserved(self):
        a = Value(10)
        b = Value(0)
        c = a.div(b)
        d = c.mul(Value(999))
        e = d.pow(Value(2))

        self.assertEqual(e.reason, Reason.DivisionByZero)

    def test_invalid_has_human_readable_explanation(self):
        a = Value(10)
        b = Value(0)
        c = a.div(b)

        self.assertIsNotNone(c.explanation)
        self.assertIsInstance(c.explanation, str)
        self.assertTrue(len(c.explanation) > 0)

    def test_require_returns_value_when_valid(self):
        a = Value(7)
        b = Value(6)
        c = a.mul(b)

        self.assertEqual(c.require(), 42)

    def test_require_raises_semantic_error_when_invalid(self):
        a = Value(10)
        b = Value(0)
        c = a.div(b)

        with self.assertRaises(SemanticError):
            c.require()

    def test_power_invalid_operation(self):
        a = Value(-1)
        b = Value(0.5)
        c = a.pow(b)

        self.assertFalse(c.is_valid())
        self.assertEqual(c.reason, Reason.InvalidOperation)

    def test_invalid_status_is_stable(self):
        a = Value(10)
        b = Value(0)

        c = a.div(b)

        for _ in range(100):
            c = c.add(Value(1))

        self.assertFalse(c.is_valid())
        self.assertEqual(c.reason, Reason.DivisionByZero)



if __name__ == "__main__":
    unittest.main()
