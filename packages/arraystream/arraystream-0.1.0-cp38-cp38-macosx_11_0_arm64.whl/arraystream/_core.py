"""Core buffer protocol utilities."""

import array
from typing import Union, Any

# Supported numeric typecodes (matching arrayops)
SUPPORTED_TYPECODES = frozenset("bBhHiIlLfd")


def is_array_array(obj: Any) -> bool:
    """Check if object is an array.array instance."""
    return isinstance(obj, array.array)


def is_supported_typecode(typecode: str) -> bool:
    """Check if typecode is supported."""
    return typecode in SUPPORTED_TYPECODES


def check_array_type(arr: Any) -> None:
    """Validate that input is a supported array.array with valid typecode.
    
    Raises:
        TypeError: If input is not an array.array or uses unsupported typecode.
    """
    if not is_array_array(arr):
        raise TypeError("Expected array.array")
    
    if not is_supported_typecode(arr.typecode):
        raise TypeError(f"Unsupported typecode: '{arr.typecode}'")


def check_buffer_protocol(obj: Any) -> bool:
    """Check if object supports the buffer protocol."""
    return hasattr(obj, "__buffer__") or isinstance(obj, (array.array, memoryview, bytes))


def create_view(arr: array.array, start: int = 0, stop: int = None) -> memoryview:
    """Create a zero-copy view of an array slice.
    
    Args:
        arr: Input array
        start: Start index (default: 0)
        stop: Stop index (default: len(arr))
        
    Returns:
        memoryview of the array slice
    """
    if stop is None:
        stop = len(arr)
    return memoryview(arr)[start:stop]


def has_arrayops() -> bool:
    """Check if arrayops is available.
    
    Returns:
        True if arrayops can be imported, False otherwise
    """
    try:
        import arrayops  # noqa: F401
        return True
    except ImportError:
        return False


def get_arrayops_sum(arr: array.array) -> Union[int, float]:
    """Get sum using arrayops if available, otherwise None.
    
    Args:
        arr: Input array
        
    Returns:
        Sum value if arrayops is available, None otherwise
    """
    if has_arrayops():
        import arrayops
        return arrayops.sum(arr)
    return None

