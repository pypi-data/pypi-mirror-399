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

- Addition (`add`)
- Subtraction (`subtract`)
- Multiplication (`multiply`)
- Division (`divide`)
- Power calculation (`power`)
- Square root calculation (`sqrt`)
- Absolute value (`abs`)
- Check even or odd (`is_even_or_odd`)
- Remainder (`remainder`)
- Percent of 100 (`percent`)
- Percent of two numbers (`percent_two_num`)
- Average of a list (`avrage`)
- Factorial (`factorial`)

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
from math_tols import add, subtract, multiply, divide, power, sqrt, abs, is_even_or_odd, remainder, percent, percent_two_num, avrage, factorial
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

### Absolute Value

```python
abs(-5)
```
**Output**
```text
5
```

---

### Even or Odd Check

```python
is_even_or_odd(7)
```
**Output**
```text
Odd
```

---

### Remainder

```python
remainder(10, 3)
```
**Output**
```text
1
```

---

### Percent of 100

```python
percent(50)
```
**Output**
```text
0.5
```

---

### Percent of Two Numbers

```python
percent_two_num(50, 80)
```
**Output**
```text
62.5
```

---

### Average

```python
avrage([2, 4, 6])
```
**Output**
```text
4.0
```

---

### Factorial

```python
factorial(5)
```
**Output**
```text
120
```

---

## API Reference

| Function  | Description |
|---------|------------|
| `add(x, y)` | Returns the sum of x and y |
| `subtract(x, y)` | Returns x minus y |
| `multiply(x, y)` | Returns the multiplication of x and y |
| `divide(x, y)` | Returns x divided by y; raises `ValueError` if y is 0 |
| `power(x, y)` | Returns x raised to the power y |
| `sqrt(x)` | Returns the square root of x |
| `abs(x)` | Returns the absolute value of x |
| `is_even_or_odd(x)` | Returns "Even" or "Odd" depending on x |
| `remainder(x, y)` | Returns the remainder of x divided by y |
| `percent(x)` | Returns x as a percentage of 100 |
| `percent_two_num(x, y)` | Returns x as a percentage of y |
| `avrage(list_of_numbers)` | Returns the average of a list of numbers |
| `factorial(x)` | Returns the factorial of x |

---

## Notes and Warnings

- Division by zero is handled and raises a `ValueError`.
- Inputs must be numeric (`int` or `float`) or a list of numerics for `avrage`.
- Factorial only works for non-negative integers.

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

