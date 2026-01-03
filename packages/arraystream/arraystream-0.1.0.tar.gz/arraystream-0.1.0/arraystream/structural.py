"""Structural transforms - operations that rearrange or expose structure."""

import array
from typing import Iterator, Union, Any
from arraystream._core import check_array_type, create_view


def chunked(arr: array.array, size: int) -> Iterator[memoryview]:
    """Return views of chunks of the array.
    
    Args:
        arr: Input array
        size: Chunk size
        
    Yields:
        memoryview objects representing chunks (zero-copy views)
        
    Raises:
        TypeError: If input is not a supported array.array
        ValueError: If size <= 0
    """
    check_array_type(arr)
    if size <= 0:
        raise ValueError("size must be > 0")
    
    for i in range(0, len(arr), size):
        yield create_view(arr, i, min(i + size, len(arr)))


def windowed(arr: array.array, size: int, step: int = 1) -> Iterator[memoryview]:
    """Return sliding windows over the array.
    
    Args:
        arr: Input array
        size: Window size
        step: Step size between windows (default: 1)
        
    Yields:
        memoryview objects representing windows (zero-copy views)
        
    Raises:
        TypeError: If input is not a supported array.array
        ValueError: If size <= 0 or step <= 0
    """
    check_array_type(arr)
    if size <= 0:
        raise ValueError("size must be > 0")
    if step <= 0:
        raise ValueError("step must be > 0")
    
    for i in range(0, len(arr) - size + 1, step):
        yield create_view(arr, i, i + size)


def take(arr: array.array, n: int) -> memoryview:
    """Return a view of the first n elements.
    
    Args:
        arr: Input array
        n: Number of elements to take
        
    Returns:
        memoryview of first n elements (zero-copy view)
        
    Raises:
        TypeError: If input is not a supported array.array
        ValueError: If n < 0
    """
    check_array_type(arr)
    if n < 0:
        raise ValueError("n must be >= 0")
    
    n = min(n, len(arr))
    return create_view(arr, 0, n)


def drop(arr: array.array, n: int) -> memoryview:
    """Return a view skipping the first n elements.
    
    Args:
        arr: Input array
        n: Number of elements to drop
        
    Returns:
        memoryview skipping first n elements (zero-copy view)
        
    Raises:
        TypeError: If input is not a supported array.array
        ValueError: If n < 0
    """
    check_array_type(arr)
    if n < 0:
        raise ValueError("n must be >= 0")
    
    start = min(n, len(arr))
    return create_view(arr, start, len(arr))


def interleave(a: array.array, b: array.array) -> array.array:
    """Interleave two arrays.
    
    Args:
        a: First array
        b: Second array
        
    Returns:
        New array with interleaved elements [a[0], b[0], a[1], b[1], ...]
        
    Raises:
        TypeError: If inputs are not supported array.array or have different typecodes
        ValueError: If arrays have different lengths
    """
    check_array_type(a)
    check_array_type(b)
    
    if a.typecode != b.typecode:
        raise ValueError("Arrays must have the same typecode")
    
    if len(a) != len(b):
        raise ValueError("Arrays must have the same length")
    
    result = array.array(a.typecode)
    for i in range(len(a)):
        result.append(a[i])
        result.append(b[i])
    
    return result


def repeat_each(arr: array.array, n: int) -> array.array:
    """Repeat each element n times.
    
    Args:
        arr: Input array
        n: Number of times to repeat each element
        
    Returns:
        New array with each element repeated n times
        
    Raises:
        TypeError: If input is not a supported array.array
        ValueError: If n < 0
    """
    check_array_type(arr)
    if n < 0:
        raise ValueError("n must be >= 0")
    
    result = array.array(arr.typecode)
    for val in arr:
        for _ in range(n):
            result.append(val)
    
    return result

