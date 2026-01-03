# math_tols

**math_tols** is a lightweight, fast, and dependency-free Python library that provides essential mathematical operations with a clean and simple API.
It is ideal for beginners, educational purposes, scripting, and projects that require basic math utilities without external dependencies.

---

## Why math_tols?

- Minimal and easy to use
- Zero external dependencies
- Clean and readable source code
- Suitable for learning and real-world usage
- PyPI-ready structure

---

## Features

- Addition
- Subtraction
- Multiplication
- Division
- Power calculation
- Square root calculation

---

## Installation

Install directly from PyPI using pip:

```bash
pip install math_tols
```

Upgrade to the latest version:

```bash
pip install --upgrade math_tols
```

---

## Quick Start

Import the library:

```python
import math_tols
```

Or import specific functions:

```python
from math_tols import add, subtract, multiply, divide, power, sqrt
```

---

## Usage Examples

### Addition

```python
add(5, 3)
```
**Output**
```text
8
```

---

### Subtraction

```python
subtract(10, 4)
```
**Output**
```text
6
```

---

### Multiplication

```python
multiply(6, 7)
```
**Output**
```text
42
```

---

### Division

```python
divide(8, 2)
```
**Output**
```text
4.0
```

---

### Power

```python
power(2, 3)
```
**Output**
```text
8
```

---

### Square Root

```python
sqrt(16)
```
**Output**
```text
4.0
```

---

## API Reference

| Function  | Description |
|---------|------------|
| `add(x, y)` | Returns the sum of x and y |
| `subtract(x, y)` | Returns the subtraction of y from x |
| `multiply(x, y)` | Returns the multiplication of x and y |
| `divide(x, y)` | Returns the division of x by y; raises `ValueError` if y is 0 |
| `power(x, y)` | Returns x raised to the power y |
| `sqrt(x)` | Returns the square root of x |

---

## Notes and Warnings

- Division by zero is handled and raises a `ValueError`.
- Inputs must be numeric (`int` or `float`).

---

## Project Structure

```text
math_tols/
├── math_tols.py
└── README.md
```

---

## License

This project is released under the MIT License.
You are free to use, modify, and distribute it.

---

## Author

Developed with Python and published for educational and practical use.

