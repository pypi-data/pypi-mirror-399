"""Tests for boolean & index operations."""

import array
import pytest
from arraystream.boolean import where, argwhere, mask


class TestWhere:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        result = where(arr, lambda x: x > 3)
        assert list(result) == [4, 5]
    
    def test_all_match(self):
        arr = array.array('i', [1, 2, 3])
        result = where(arr, lambda x: x > 0)
        assert list(result) == [1, 2, 3]
    
    def test_none_match(self):
        arr = array.array('i', [1, 2, 3])
        result = where(arr, lambda x: x > 10)
        assert len(result) == 0
    
    def test_empty_array(self):
        arr = array.array('i')
        result = where(arr, lambda x: x > 0)
        assert len(result) == 0
    
    def test_float_array(self):
        arr = array.array('f', [1.5, 2.5, 3.5, 4.5])
        result = where(arr, lambda x: x > 3.0)
        assert len(result) == 2
        assert result[0] == 3.5
        assert result[1] == 4.5


class TestArgwhere:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        result = argwhere(arr, lambda x: x > 3)
        assert list(result) == [3, 4]
    
    def test_all_match(self):
        arr = array.array('i', [1, 2, 3])
        result = argwhere(arr, lambda x: x > 0)
        assert list(result) == [0, 1, 2]
    
    def test_none_match(self):
        arr = array.array('i', [1, 2, 3])
        result = argwhere(arr, lambda x: x > 10)
        assert len(result) == 0
    
    def test_empty_array(self):
        arr = array.array('i')
        result = argwhere(arr, lambda x: x > 0)
        assert len(result) == 0
    
    def test_result_typecode(self):
        arr = array.array('i', [1, 2, 3])
        result = argwhere(arr, lambda x: x > 1)
        assert result.typecode == 'L'  # unsigned long


class TestMask:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        mask_arr = array.array('B', [1, 0, 1, 0, 1])
        result = mask(arr, mask_arr)
        assert list(result) == [1, 3, 5]
    
    def test_all_true(self):
        arr = array.array('i', [1, 2, 3])
        mask_arr = array.array('B', [1, 1, 1])
        result = mask(arr, mask_arr)
        assert list(result) == [1, 2, 3]
    
    def test_all_false(self):
        arr = array.array('i', [1, 2, 3])
        mask_arr = array.array('B', [0, 0, 0])
        result = mask(arr, mask_arr)
        assert len(result) == 0
    
    def test_wrong_length(self):
        arr = array.array('i', [1, 2, 3])
        mask_arr = array.array('B', [1, 0])
        with pytest.raises(ValueError):
            mask(arr, mask_arr)
    
    def test_wrong_typecode(self):
        arr = array.array('i', [1, 2, 3])
        mask_arr = array.array('i', [1, 0, 1])
        with pytest.raises(ValueError):
            mask(arr, mask_arr)
    
    def test_empty_arrays(self):
        arr = array.array('i')
        mask_arr = array.array('B')
        result = mask(arr, mask_arr)
        assert len(result) == 0
    
    def test_signed_mask(self):
        arr = array.array('i', [1, 2, 3])
        mask_arr = array.array('b', [1, 0, -1])  # -1 is truthy
        result = mask(arr, mask_arr)
        assert list(result) == [1, 3]

