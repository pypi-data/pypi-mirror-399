# ExplainMath

**ExplainMath** is a small Python library that catches invalid numeric operations (like division by zero, undefined results, or bad power operations) and explains **why it went wrong** in plain English — instead of silently giving `NaN` or `inf`.

This is useful in machine learning, simulations, finance, or any code where one wrong number can poison the whole pipeline without you noticing.

---

## 🔥 Why This Library Exists

In Python, many invalid numeric operations do **not** crash your program. Instead, they produce `NaN`, `inf`, or a complex number — and these values spread quietly through your code.

Example of a real problem:

\`\`\`python
result = model(data)
print(result)   # nan ... now what?
# Traditional debugging tells you where the error happened,
# but not why the math became invalid.

# ExplainMath catches the failure at the moment it happens and tells you the reason.
\`\`\`

## ✨ Features

*   Tracks invalid math operations
*   Supports addition, subtraction, multiplication, division, and power
*   Marks invalid values explicitly (no hidden NaNs or silent errors)
*   Preserves the reason for the failure
*   Propagates invalid state safely through further calculations
*   Optional `.require()` strict mode that raises an exception

## 🚀 Quick Start

\`\`\`python
from core.value import Value

a = Value(10)
b = Value(0)

c = a.div(b)

print(c.is_valid())      # False
print(c.explanation)     # "Division by zero while evaluating 10 / 0"
\`\`\`

## 🔒 Strict Mode Example (Fail Fast)

Useful when you want invalid math to stop execution immediately.

\`\`\`python
from core.value import Value

a = Value(10)
b = Value(0)

c = a.div(b)

c.require()   # Raises SemanticError with explanation
\`\`\`

## 🧪 Running Tests

Unit tests ensure math behavior is safe, predictable, and stable:

\`\`\`bash
python -m unittest discover -v
\`\`\`

## 📌 Project Status

This is version **v0.1**.
It is intentionally small and focused:

*   A single numeric type
*   Basic arithmetic
*   Error explanation
*   Safe propagation

Future versions will include:

*   Operation history
*   Provenance tracking
*   Better debugging reports
*   Optional integration with NumPy/PyTorch

## 🗂 Folder Structure

\`\`\`text
core/       → implementation
examples/   → usage demos
tests/      → unit tests
docs/       → (reserved for future)
\`\`\`

## License

This project is licensed under the **MIT License**.

---

*Made with curiosity, logic, and a desire to reduce silent math bugs.*
