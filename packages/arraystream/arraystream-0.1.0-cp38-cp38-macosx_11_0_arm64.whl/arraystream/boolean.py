"""Boolean & index-producing operations."""

import array
from typing import Callable, Union
from arraystream._core import check_array_type


def where(arr: array.array, predicate: Callable[[Union[int, float]], bool]) -> array.array:
    """Filter elements by predicate.
    
    Args:
        arr: Input array
        predicate: Function that takes an element and returns bool
        
    Returns:
        New array containing only elements where predicate is True
        
    Raises:
        TypeError: If input is not a supported array.array
    """
    check_array_type(arr)
    
    result = array.array(arr.typecode)
    for val in arr:
        if predicate(val):
            result.append(val)
    return result


def argwhere(arr: array.array, predicate: Callable[[Union[int, float]], bool]) -> array.array:
    """Return indices where condition is true.
    
    Args:
        arr: Input array
        predicate: Function that takes an element and returns bool
        
    Returns:
        New array of type 'L' (unsigned long) containing indices where predicate is True
        
    Raises:
        TypeError: If input is not a supported array.array
    """
    check_array_type(arr)
    
    result = array.array('L')  # unsigned long for indices
    for i, val in enumerate(arr):
        if predicate(val):
            result.append(i)
    return result


def mask(arr: array.array, mask_array: array.array) -> array.array:
    """Apply boolean mask to array.
    
    Args:
        arr: Input array
        mask_array: Boolean mask array (must be array.array with typecode 'B' or 'b')
        
    Returns:
        New array containing only elements where mask is True
        
    Raises:
        TypeError: If inputs are not supported array.array
        ValueError: If mask_array is not boolean or has wrong length
    """
    check_array_type(arr)
    check_array_type(mask_array)
    
    if mask_array.typecode not in 'Bb':
        raise ValueError("mask_array must have typecode 'B' or 'b'")
    
    if len(mask_array) != len(arr):
        raise ValueError("mask_array must have the same length as arr")
    
    result = array.array(arr.typecode)
    for i, val in enumerate(arr):
        if mask_array[i]:
            result.append(val)
    return result

