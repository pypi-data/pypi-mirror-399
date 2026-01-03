"""Tests for grouping & segmentation operations."""

import array
import pytest
from arraystream.grouping import run_length_encode, groupby_runs, segment_by


class TestRunLengthEncode:
    def test_basic(self):
        arr = array.array('i', [1, 1, 1, 2, 2, 3, 3, 3, 3])
        result = run_length_encode(arr)
        assert 'values' in result
        assert 'counts' in result
        assert list(result['values']) == [1, 2, 3]
        assert list(result['counts']) == [3, 2, 4]
    
    def test_all_same(self):
        arr = array.array('i', [5, 5, 5])
        result = run_length_encode(arr)
        assert list(result['values']) == [5]
        assert list(result['counts']) == [3]
    
    def test_all_different(self):
        arr = array.array('i', [1, 2, 3])
        result = run_length_encode(arr)
        assert list(result['values']) == [1, 2, 3]
        assert list(result['counts']) == [1, 1, 1]
    
    def test_empty_array(self):
        arr = array.array('i')
        result = run_length_encode(arr)
        assert len(result['values']) == 0
        assert len(result['counts']) == 0
    
    def test_single_element(self):
        arr = array.array('i', [42])
        result = run_length_encode(arr)
        assert list(result['values']) == [42]
        assert list(result['counts']) == [1]
    
    def test_float_array(self):
        arr = array.array('f', [1.0, 1.0, 2.0])
        result = run_length_encode(arr)
        assert len(result['values']) == 2
        assert result['values'][0] == 1.0
        assert result['values'][1] == 2.0


class TestGroupbyRuns:
    def test_basic(self):
        arr = array.array('i', [1, 1, 1, 2, 2, 3, 3, 3, 3])
        result = groupby_runs(arr)
        assert len(result) == 3
        assert list(result[0]) == [1, 1, 1]
        assert list(result[1]) == [2, 2]
        assert list(result[2]) == [3, 3, 3, 3]
    
    def test_all_same(self):
        arr = array.array('i', [5, 5, 5])
        result = groupby_runs(arr)
        assert len(result) == 1
        assert list(result[0]) == [5, 5, 5]
    
    def test_all_different(self):
        arr = array.array('i', [1, 2, 3])
        result = groupby_runs(arr)
        assert len(result) == 3
        assert list(result[0]) == [1]
        assert list(result[1]) == [2]
        assert list(result[2]) == [3]
    
    def test_empty_array(self):
        arr = array.array('i')
        result = groupby_runs(arr)
        assert len(result) == 0
    
    def test_single_element(self):
        arr = array.array('i', [42])
        result = groupby_runs(arr)
        assert len(result) == 1
        assert list(result[0]) == [42]


class TestSegmentBy:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5, 6, 7, 8])
        boundaries = array.array('L', [3, 6])
        result = segment_by(arr, boundaries)
        assert len(result) == 3
        assert list(result[0]) == [1, 2, 3]
        assert list(result[1]) == [4, 5, 6]
        assert list(result[2]) == [7, 8]
    
    def test_single_boundary(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        boundaries = array.array('L', [2])
        result = segment_by(arr, boundaries)
        assert len(result) == 2
        assert list(result[0]) == [1, 2]
        assert list(result[1]) == [3, 4, 5]
    
    def test_no_boundaries(self):
        arr = array.array('i', [1, 2, 3])
        boundaries = array.array('L')
        result = segment_by(arr, boundaries)
        assert len(result) == 1
        assert list(result[0]) == [1, 2, 3]
    
    def test_boundary_at_end(self):
        arr = array.array('i', [1, 2, 3])
        boundaries = array.array('L', [3])
        result = segment_by(arr, boundaries)
        assert len(result) == 1
        assert list(result[0]) == [1, 2, 3]
    
    def test_empty_array(self):
        arr = array.array('i')
        boundaries = array.array('L', [])
        result = segment_by(arr, boundaries)
        assert len(result) == 1
        assert len(result[0]) == 0
    
    def test_wrong_typecode(self):
        arr = array.array('i', [1, 2, 3])
        boundaries = array.array('i', [1, 2])
        with pytest.raises(ValueError):
            segment_by(arr, boundaries)
    
    def test_unsorted_boundaries(self):
        arr = array.array('i', [1, 2, 3, 4])
        boundaries = array.array('L', [3, 2])
        with pytest.raises(ValueError):
            segment_by(arr, boundaries)
    
    def test_out_of_range_boundary(self):
        arr = array.array('i', [1, 2, 3])
        boundaries = array.array('L', [5])
        with pytest.raises(ValueError):
            segment_by(arr, boundaries)
    
    def test_duplicate_boundaries(self):
        arr = array.array('i', [1, 2, 3, 4])
        boundaries = array.array('L', [2, 2])
        with pytest.raises(ValueError):
            segment_by(arr, boundaries)

