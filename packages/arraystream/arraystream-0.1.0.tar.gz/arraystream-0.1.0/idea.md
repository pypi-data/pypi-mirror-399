# Array-Oriented Stream Transformations for Python

## Overview

This document proposes a **complementary Python package to `arrayops`** that provides
*iterator-style transformations for numeric arrays*, in the same spirit that
`itertools` provides combinators for iterables.

Where `arrayops` https://github.com/eddiethedean/arrayops focuses on **fast, Rust-backed numeric kernels for `array.array`**,
this package focuses on **structural, composable, and allocation-aware transformations**
over contiguous numeric buffers.

> **Mental model:**  
> *itertools, but for numeric arrays and memory buffers.*

---

## Goals

- Operate on **`array.array` and buffer-protocol objects**
- Favor **zero-copy views** where possible
- Avoid Python scalar iteration
- Be **small, predictable, and fast**
- Compose naturally with `arrayops`
- No dependency on NumPy or Pandas

---

## Non-Goals

This package is explicitly **not**:

- A NumPy replacement
- Multi-dimensional
- Broadcasting-aware
- Symbolic or lazy in the Python-generator sense
- Focused on linear algebra or statistics

---

## Design Principles

1. **Buffer-first**
   - Functions accept contiguous numeric buffers
   - Prefer `array.array`, optionally `memoryview`

2. **Allocation-aware**
   - Use views and striding when possible
   - Copy only when semantics require it

3. **Numeric-only**
   - Assumes homogeneous numeric types
   - Rejects object arrays

4. **Composable**
   - Functions chain naturally
   - Optional fluent wrapper API

5. **Rust where it matters**
   - Structural operations in Python
   - Numeric and scanning operations in Rust (via PyO3)

---

## Relationship to `arrayops`

| arrayops | This package |
|--------|---------------|
| Numeric kernels | Structural & stream transforms |
| In-place math | Shape-changing operations |
| Minimal API | Rich combinators |
| Low-level | Expressive |

`arrayops` acts as the **execution engine**  
This package acts as the **transformation language**

---

## Functional Categories

### 1. Structural Transforms

Operations that rearrange or expose structure without computing new values.

- `chunked(arr, size)`
- `windowed(arr, size, step=1)`
- `take(arr, n)`
- `drop(arr, n)`
- `interleave(a, b)`
- `repeat_each(arr, n)`

Where possible, these return **views**, not copies.

---

### 2. Numeric Stream Operations

Operations that compute new values, often leveraging Rust kernels.

- `scan(arr, op="sum")` (prefix reduce)
- `diff(arr)`
- `pairwise(arr)`
- `clip(arr, min, max)`

---

### 3. Boolean & Index-Producing Operations

Operations that return arrays instead of Python iterators.

- `where(arr, predicate)`
- `argwhere(arr)`
- `mask(arr, mask_array)`

---

### 4. Grouping & Segmentation

High-value operations that are difficult to do efficiently in Python.

- `run_length_encode(arr)`
- `groupby_runs(arr)`
- `segment_by(arr, boundaries)`

---

## API Style

### Functional (itertools-style)

```python
from arraypkg import windowed, scan, diff

result = scan(diff(data))

Performance Strategy
	•	Structural operations: Python + buffer protocol
	•	Numeric transforms: Rust (PyO3)
	•	Zero-copy wherever semantics allow
	•	Explicit copies when safety or clarity requires them

⸻

Ideal Use Cases
	•	Streaming numeric pipelines
	•	Signal processing
	•	Sensor data preprocessing
	•	Embedded or constrained environments
	•	ETL micro-kernels
	•	Teaching numeric programming without NumPy
