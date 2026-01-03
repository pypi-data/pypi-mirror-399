"""Numeric stream operations - compute new values."""

import array
from typing import Optional, Union
from arraystream._core import check_array_type, has_arrayops

try:
    from arraystream._arraystream import scan as _scan_rust, diff as _diff_rust, pairwise as _pairwise_rust, clip as _clip_rust
    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False


def scan(arr: array.array, op: str = "sum") -> array.array:
    """Compute prefix reduce (scan) operation.
    
    Args:
        arr: Input array
        op: Operation to perform (currently only "sum" is supported)
        
    Returns:
        New array with prefix reduce results
        
    Raises:
        TypeError: If input is not a supported array.array
        ValueError: If operation is not supported
    """
    check_array_type(arr)
    
    # TODO: Fix Rust implementation - currently has runtime error:
    # TypeError: 'str' object cannot be interpreted as an integer
    # Temporarily using Python fallback until Rust issue is resolved
    # if not _RUST_AVAILABLE:
    #     return _scan_python(arr, op)
    # return _scan_rust(arr, op)
    return _scan_python(arr, op)


def _scan_python(arr: array.array, op: str) -> array.array:
    """Python fallback implementation of scan."""
    if op != "sum":
        raise ValueError(f"Unsupported operation: {op}")
    
    result = array.array(arr.typecode)
    acc = 0 if arr.typecode in "bBhHiIlL" else 0.0
    
    for val in arr:
        if arr.typecode in "bBhHiIlL":
            acc = int(acc) + int(val)
        else:
            acc = float(acc) + float(val)
        result.append(acc)
    
    return result


def diff(arr: array.array) -> array.array:
    """Compute differences between consecutive elements.
    
    Args:
        arr: Input array
        
    Returns:
        New array with differences [arr[1]-arr[0], arr[2]-arr[1], ...]
        
    Raises:
        TypeError: If input is not a supported array.array
    """
    check_array_type(arr)
    
    if len(arr) < 2:
        return array.array(arr.typecode)
    
    # TODO: Fix Rust implementation
    return _diff_python(arr)


def _diff_python(arr: array.array) -> array.array:
    """Python fallback implementation of diff."""
    result = array.array(arr.typecode)
    for i in range(len(arr) - 1):
        result.append(arr[i + 1] - arr[i])
    return result


def pairwise(arr: array.array) -> array.array:
    """Return pairs of consecutive elements.
    
    Args:
        arr: Input array
        
    Returns:
        New array with pairs [arr[0], arr[1], arr[1], arr[2], ...]
        
    Raises:
        TypeError: If input is not a supported array.array
    """
    check_array_type(arr)
    
    if len(arr) < 2:
        return array.array(arr.typecode)
    
    # TODO: Fix Rust implementation
    return _pairwise_python(arr)


def _pairwise_python(arr: array.array) -> array.array:
    """Python fallback implementation of pairwise."""
    result = array.array(arr.typecode)
    for i in range(len(arr) - 1):
        result.append(arr[i])
        result.append(arr[i + 1])
    return result


def clip(arr: array.array, min_val: Union[int, float], max_val: Union[int, float]) -> array.array:
    """Clip values to range [min_val, max_val].
    
    Args:
        arr: Input array
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        New array with clipped values
        
    Raises:
        TypeError: If input is not a supported array.array
        ValueError: If min_val > max_val
    """
    check_array_type(arr)
    
    if min_val > max_val:
        raise ValueError("min_val must be <= max_val")
    
    # TODO: Fix Rust implementation
    return _clip_python(arr, min_val, max_val)


def _clip_python(arr: array.array, min_val: Union[int, float], max_val: Union[int, float]) -> array.array:
    """Python fallback implementation of clip."""
    result = array.array(arr.typecode)
    for val in arr:
        if val < min_val:
            result.append(min_val)
        elif val > max_val:
            result.append(max_val)
        else:
            result.append(val)
    return result

