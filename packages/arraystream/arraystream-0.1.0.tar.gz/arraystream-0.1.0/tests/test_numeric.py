"""Tests for numeric stream operations."""

import array
import pytest
from arraystream.numeric import scan, diff, pairwise, clip


class TestScan:
    def test_basic_sum(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        result = scan(arr, op="sum")
        assert list(result) == [1, 3, 6, 10, 15]
    
    def test_empty_array(self):
        arr = array.array('i')
        result = scan(arr, op="sum")
        assert len(result) == 0
    
    def test_single_element(self):
        arr = array.array('i', [5])
        result = scan(arr, op="sum")
        assert list(result) == [5]
    
    def test_float_array(self):
        arr = array.array('f', [1.0, 2.0, 3.0])
        result = scan(arr, op="sum")
        assert list(result) == [1.0, 3.0, 6.0]
    
    def test_unsupported_operation(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            scan(arr, op="product")
    
    def test_all_typecodes(self):
        for typecode in 'bBhHiIlL':
            arr = array.array(typecode, [1, 2, 3])
            result = scan(arr, op="sum")
            assert len(result) == 3


class TestDiff:
    def test_basic(self):
        arr = array.array('i', [1, 3, 5, 7, 9])
        result = diff(arr)
        assert list(result) == [2, 2, 2, 2]
    
    def test_empty_array(self):
        arr = array.array('i')
        result = diff(arr)
        assert len(result) == 0
    
    def test_single_element(self):
        arr = array.array('i', [5])
        result = diff(arr)
        assert len(result) == 0
    
    def test_float_array(self):
        arr = array.array('f', [1.0, 2.5, 4.0])
        result = diff(arr)
        assert abs(result[0] - 1.5) < 1e-6
        assert abs(result[1] - 1.5) < 1e-6
    
    def test_all_typecodes(self):
        for typecode in 'bBhHiIlLfd':
            arr = array.array(typecode, [1, 3, 5] if typecode in 'bBhHiIlL' else [1.0, 3.0, 5.0])
            result = diff(arr)
            assert len(result) == 2


class TestPairwise:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4])
        result = pairwise(arr)
        assert list(result) == [1, 2, 2, 3, 3, 4]
    
    def test_empty_array(self):
        arr = array.array('i')
        result = pairwise(arr)
        assert len(result) == 0
    
    def test_single_element(self):
        arr = array.array('i', [5])
        result = pairwise(arr)
        assert len(result) == 0
    
    def test_float_array(self):
        arr = array.array('f', [1.0, 2.0, 3.0])
        result = pairwise(arr)
        assert list(result) == [1.0, 2.0, 2.0, 3.0]
    
    def test_all_typecodes(self):
        for typecode in 'bBhHiIlLfd':
            arr = array.array(typecode, [1, 2, 3] if typecode in 'bBhHiIlL' else [1.0, 2.0, 3.0])
            result = pairwise(arr)
            assert len(result) == 4


class TestClip:
    def test_basic(self):
        arr = array.array('i', [1, 5, 10, 15, 20])
        result = clip(arr, 5, 15)
        assert list(result) == [5, 5, 10, 15, 15]
    
    def test_all_below_min(self):
        arr = array.array('i', [1, 2, 3])
        result = clip(arr, 5, 10)
        assert list(result) == [5, 5, 5]
    
    def test_all_above_max(self):
        arr = array.array('i', [10, 20, 30])
        result = clip(arr, 5, 15)
        assert list(result) == [10, 15, 15]
    
    def test_empty_array(self):
        arr = array.array('i')
        result = clip(arr, 0, 10)
        assert len(result) == 0
    
    def test_float_array(self):
        arr = array.array('f', [1.5, 2.5, 3.5])
        result = clip(arr, 2.0, 3.0)
        assert abs(result[0] - 2.0) < 1e-6
        assert abs(result[1] - 2.5) < 1e-6
        assert abs(result[2] - 3.0) < 1e-6
    
    def test_invalid_range(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            clip(arr, 10, 5)
    
    def test_all_typecodes(self):
        for typecode in 'bBhHiIlL':
            arr = array.array(typecode, [1, 5, 10])
            result = clip(arr, 2, 8)
            assert len(result) == 3

