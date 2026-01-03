"""arraystream: Iterator-style transformations for numeric arrays."""

__version__ = "0.1.0"

from arraystream.structural import (
    chunked,
    windowed,
    take,
    drop,
    interleave,
    repeat_each,
)
from arraystream.numeric import scan, diff, pairwise, clip
from arraystream.boolean import where, argwhere, mask
from arraystream.grouping import run_length_encode, groupby_runs, segment_by

__all__ = [
    # Structural transforms
    "chunked",
    "windowed",
    "take",
    "drop",
    "interleave",
    "repeat_each",
    # Numeric stream operations
    "scan",
    "diff",
    "pairwise",
    "clip",
    # Boolean & index operations
    "where",
    "argwhere",
    "mask",
    # Grouping & segmentation
    "run_length_encode",
    "groupby_runs",
    "segment_by",
]

