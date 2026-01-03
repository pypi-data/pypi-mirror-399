"""Grouping & segmentation operations."""

import array
from typing import List, Dict, Any
from arraystream._core import check_array_type

try:
    from arraystream._arraystream import run_length_encode as _rle_rust, groupby_runs as _groupby_runs_rust
    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False


def run_length_encode(arr: array.array) -> Dict[str, array.array]:
    """Run-length encode an array.
    
    Args:
        arr: Input array
        
    Returns:
        Dictionary with keys:
            - 'values': array.array of unique values
            - 'counts': array.array('L') of run lengths
            
    Raises:
        TypeError: If input is not a supported array.array
    """
    check_array_type(arr)
    
    # TODO: Fix Rust implementation
    return _rle_python(arr)


def _rle_python(arr: array.array) -> Dict[str, array.array]:
    """Python fallback implementation of run-length encode."""
    if len(arr) == 0:
        return {
            'values': array.array(arr.typecode),
            'counts': array.array('L'),
        }
    
    values = array.array(arr.typecode)
    counts = array.array('L')
    
    current = arr[0]
    count = 1
    
    for i in range(1, len(arr)):
        if arr[i] == current:
            count += 1
        else:
            values.append(current)
            counts.append(count)
            current = arr[i]
            count = 1
    
    values.append(current)
    counts.append(count)
    
    return {
        'values': values,
        'counts': counts,
    }


def groupby_runs(arr: array.array) -> List[array.array]:
    """Group consecutive equal elements.
    
    Args:
        arr: Input array
        
    Returns:
        List of array.array objects, each containing a run of equal elements
        
    Raises:
        TypeError: If input is not a supported array.array
    """
    check_array_type(arr)
    
    if len(arr) == 0:
        return []
    
    # TODO: Fix Rust implementation
    return _groupby_runs_python(arr)


def _groupby_runs_python(arr: array.array) -> List[array.array]:
    """Python fallback implementation of groupby_runs."""
    if len(arr) == 0:
        return []
    
    groups = []
    start = 0
    current = arr[0]
    
    for i in range(1, len(arr)):
        if arr[i] != current:
            groups.append(array.array(arr.typecode, arr[start:i]))
            start = i
            current = arr[i]
    
    groups.append(array.array(arr.typecode, arr[start:]))
    return groups


def segment_by(arr: array.array, boundaries: array.array) -> List[array.array]:
    """Split array at boundary indices.
    
    Args:
        arr: Input array
        boundaries: Array of type 'L' (unsigned long) containing boundary indices
        
    Returns:
        List of array.array objects representing segments
        
    Raises:
        TypeError: If inputs are not supported array.array
        ValueError: If boundaries are not sorted or out of range
    """
    check_array_type(arr)
    check_array_type(boundaries)
    
    if boundaries.typecode != 'L':
        raise ValueError("boundaries must have typecode 'L'")
    
    if len(boundaries) == 0:
        return [arr]
    
    # Validate boundaries
    prev = -1
    for b in boundaries:
        if b <= prev:
            raise ValueError("boundaries must be sorted and strictly increasing")
        if b > len(arr):
            raise ValueError(f"boundary {b} is out of range (array length: {len(arr)})")
        prev = b
    
    segments = []
    start = 0
    
    for boundary in boundaries:
        segments.append(array.array(arr.typecode, arr[start:boundary]))
        start = boundary
    
    # Add final segment
    if start < len(arr):
        segments.append(array.array(arr.typecode, arr[start:]))
    
    return segments

