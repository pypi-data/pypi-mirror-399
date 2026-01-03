# core/value.py

from enum import Enum


class Status(Enum):
    VALID = "valid"
    INVALID = "invalid"


class Reason(Enum):
    DivisionByZero = "division_by_zero"
    InvalidOperation = "invalid_operation"
    Overflow = "overflow"
    Indeterminate = "indeterminate"


class SemanticError(Exception):
    pass


class Value:
    def __init__(self, number):
        self._value = number
        self._status = Status.VALID
        self._reason = None
        self._explanation = None

    @property
    def value(self):
        return self._value if self._status == Status.VALID else None

    @property
    def status(self):
        return self._status

    @property
    def reason(self):
        return self._reason

    @property
    def explanation(self):
        return self._explanation

    def is_valid(self):
        return self._status == Status.VALID

    def require(self):
        if self._status == Status.VALID:
            return self._value
        raise SemanticError(self._explanation)

    @staticmethod
    def _invalid(reason, explanation):
        v = Value(0)
        v._value = None
        v._status = Status.INVALID
        v._reason = reason
        v._explanation = explanation
        return v

    def add(self, other):
        if not self.is_valid():
            return self
        if not other.is_valid():
            return other
        return Value(self._value + other._value)

    def sub(self, other):
        if not self.is_valid():
            return self
        if not other.is_valid():
            return other
        return Value(self._value - other._value)

    def mul(self, other):
        if not self.is_valid():
            return self
        if not other.is_valid():
            return other
        return Value(self._value * other._value)

    def div(self, other):
        if not self.is_valid():
            return self
        if not other.is_valid():
            return other
        if other._value == 0:
            return Value._invalid(
                Reason.DivisionByZero,
                f"Division by zero while evaluating {self._value} / {other._value}"
            )
        return Value(self._value / other._value)

    def pow(self, other):
        if not self.is_valid():
            return self
        if not other.is_valid():
            return other
        try:
            result = self._value ** other._value
            # Reject complex numbers / unsupported results
            if isinstance(result, complex):
                return Value._invalid(
                    Reason.InvalidOperation,
                    f"Invalid power operation (complex result): {self._value} ** {other._value}"
                )
            return Value(result)
        except Exception:
            return Value._invalid(
                Reason.InvalidOperation,
                f"Invalid power operation: {self._value} ** {other._value}"
            )

