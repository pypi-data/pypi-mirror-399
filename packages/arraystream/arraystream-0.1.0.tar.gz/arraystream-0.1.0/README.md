# arraystream

Iterator-style transformations for numeric arrays, similar to `itertools` but optimized for `array.array` and buffer-protocol objects.

## Overview

`arraystream` provides composable, allocation-aware transformations for numeric arrays, complementing [arrayops](https://github.com/eddiethedean/arrayops) which focuses on fast, Rust-backed numeric kernels.

**Mental model:** *itertools, but for numeric arrays and memory buffers.*

Where `arrayops` provides the **execution engine** (numeric kernels), `arraystream` provides the **transformation language** (structural & stream transforms).

## Features

- Operate on `array.array` and buffer-protocol objects
- Favor zero-copy views where possible
- Avoid Python scalar iteration
- Small, predictable, and fast
- Composes naturally with `arrayops`
- No dependency on NumPy or Pandas

## Installation

```bash
pip install arraystream
```

For development:

```bash
git clone https://github.com/eddiethedean/arraystream
cd arraystream
pip install -r requirements-dev.txt
maturin develop
```

## Quick Start

```python
import array
from arraystream import windowed, scan, diff

# Create an array
data = array.array('i', [1, 2, 3, 4, 5, 6, 7, 8])

# Sliding windows
for window in windowed(data, size=3):
    print(list(window))  # [1, 2, 3], [2, 3, 4], ...

# Differences between consecutive elements
diffs = diff(data)
print(list(diffs))  # [1, 1, 1, 1, 1, 1, 1]

# Prefix sum (scan)
prefix_sums = scan(data, op="sum")
print(list(prefix_sums))  # [1, 3, 6, 10, 15, 21, 28, 36]
```

## Relationship to arrayops

| arrayops | arraystream |
|----------|-------------|
| Numeric kernels | Structural & stream transforms |
| In-place math | Shape-changing operations |
| Minimal API | Rich combinators |
| Low-level | Expressive |

`arrayops` acts as the **execution engine**  
`arraystream` acts as the **transformation language**

## API Categories

### Structural Transforms

Operations that rearrange or expose structure without computing new values:

- `chunked(arr, size)` - Return views of chunks
- `windowed(arr, size, step=1)` - Sliding windows
- `take(arr, n)` - First n elements (view)
- `drop(arr, n)` - Skip first n elements (view)
- `interleave(a, b)` - Interleave two arrays
- `repeat_each(arr, n)` - Repeat each element n times

### Numeric Stream Operations

Operations that compute new values:

- `scan(arr, op="sum")` - Prefix reduce
- `diff(arr)` - Differences between consecutive elements
- `pairwise(arr)` - Return pairs of consecutive elements
- `clip(arr, min, max)` - Clip values to range

### Boolean & Index Operations

- `where(arr, predicate)` - Filter elements by predicate
- `argwhere(arr)` - Return indices where condition is true
- `mask(arr, mask_array)` - Apply boolean mask

### Grouping & Segmentation

- `run_length_encode(arr)` - Run-length encoding
- `groupby_runs(arr)` - Group consecutive equal elements
- `segment_by(arr, boundaries)` - Split at boundary indices

## Supported Types

Supports the same 10 typecodes as `arrayops`:
- `b` - signed char
- `B` - unsigned char
- `h` - signed short
- `H` - unsigned short
- `i` - signed int
- `I` - unsigned int
- `l` - signed long
- `L` - unsigned long
- `f` - float
- `d` - double

## Performance

- Structural operations: Python + buffer protocol (zero-copy views)
- Numeric transforms: Rust (PyO3) for performance
- Zero-copy wherever semantics allow
- Explicit copies when safety or clarity requires them

## Use Cases

- Streaming numeric pipelines
- Signal processing
- Sensor data preprocessing
- Embedded or constrained environments
- ETL micro-kernels
- Teaching numeric programming without NumPy

## Development

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=arraystream --cov-report=html

# Format code
ruff format .

# Lint code
ruff check .

# Type checking
mypy arraystream tests
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [PyO3](https://pyo3.rs/) for Python-Rust interop
- Built with [maturin](https://github.com/PyO3/maturin) for packaging
- Complements [arrayops](https://github.com/eddiethedean/arrayops)

