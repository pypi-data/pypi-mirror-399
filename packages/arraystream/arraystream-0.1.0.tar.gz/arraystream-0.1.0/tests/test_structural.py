"""Tests for structural transforms."""

import array
import pytest
from arraystream.structural import chunked, windowed, take, drop, interleave, repeat_each


class TestChunked:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5, 6])
        chunks = list(chunked(arr, 2))
        assert len(chunks) == 3
        assert list(chunks[0]) == [1, 2]
        assert list(chunks[1]) == [3, 4]
        assert list(chunks[2]) == [5, 6]
    
    def test_uneven_chunks(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        chunks = list(chunked(arr, 2))
        assert len(chunks) == 3
        assert list(chunks[0]) == [1, 2]
        assert list(chunks[1]) == [3, 4]
        assert list(chunks[2]) == [5]
    
    def test_empty_array(self):
        arr = array.array('i')
        chunks = list(chunked(arr, 2))
        assert len(chunks) == 0
    
    def test_invalid_size(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            list(chunked(arr, 0))
        with pytest.raises(ValueError):
            list(chunked(arr, -1))
    
    def test_all_typecodes(self):
        for typecode in 'bBhHiIlLfd':
            arr = array.array(typecode, [1, 2, 3, 4] if typecode in 'bBhHiIlL' else [1.0, 2.0, 3.0, 4.0])
            chunks = list(chunked(arr, 2))
            assert len(chunks) == 2


class TestWindowed:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        windows = list(windowed(arr, 3))
        assert len(windows) == 3
        assert list(windows[0]) == [1, 2, 3]
        assert list(windows[1]) == [2, 3, 4]
        assert list(windows[2]) == [3, 4, 5]
    
    def test_with_step(self):
        arr = array.array('i', [1, 2, 3, 4, 5, 6, 7])
        windows = list(windowed(arr, 3, step=2))
        assert len(windows) == 3
        assert list(windows[0]) == [1, 2, 3]
        assert list(windows[1]) == [3, 4, 5]
        assert list(windows[2]) == [5, 6, 7]
    
    def test_empty_array(self):
        arr = array.array('i')
        windows = list(windowed(arr, 3))
        assert len(windows) == 0
    
    def test_invalid_size(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            list(windowed(arr, 0))
    
    def test_invalid_step(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            list(windowed(arr, 2, step=0))


class TestTake:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        result = take(arr, 3)
        assert list(result) == [1, 2, 3]
    
    def test_take_more_than_length(self):
        arr = array.array('i', [1, 2, 3])
        result = take(arr, 10)
        assert list(result) == [1, 2, 3]
    
    def test_take_zero(self):
        arr = array.array('i', [1, 2, 3])
        result = take(arr, 0)
        assert len(result) == 0
    
    def test_empty_array(self):
        arr = array.array('i')
        result = take(arr, 5)
        assert len(result) == 0
    
    def test_invalid_n(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            take(arr, -1)


class TestDrop:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3, 4, 5])
        result = drop(arr, 2)
        assert list(result) == [3, 4, 5]
    
    def test_drop_more_than_length(self):
        arr = array.array('i', [1, 2, 3])
        result = drop(arr, 10)
        assert len(result) == 0
    
    def test_drop_zero(self):
        arr = array.array('i', [1, 2, 3])
        result = drop(arr, 0)
        assert list(result) == [1, 2, 3]
    
    def test_empty_array(self):
        arr = array.array('i')
        result = drop(arr, 5)
        assert len(result) == 0
    
    def test_invalid_n(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            drop(arr, -1)


class TestInterleave:
    def test_basic(self):
        a = array.array('i', [1, 3, 5])
        b = array.array('i', [2, 4, 6])
        result = interleave(a, b)
        assert list(result) == [1, 2, 3, 4, 5, 6]
    
    def test_different_typecodes(self):
        a = array.array('i', [1, 2])
        b = array.array('f', [3.0, 4.0])
        with pytest.raises(ValueError):
            interleave(a, b)
    
    def test_different_lengths(self):
        a = array.array('i', [1, 2, 3])
        b = array.array('i', [4, 5])
        with pytest.raises(ValueError):
            interleave(a, b)
    
    def test_empty_arrays(self):
        a = array.array('i')
        b = array.array('i')
        result = interleave(a, b)
        assert len(result) == 0


class TestRepeatEach:
    def test_basic(self):
        arr = array.array('i', [1, 2, 3])
        result = repeat_each(arr, 2)
        assert list(result) == [1, 1, 2, 2, 3, 3]
    
    def test_repeat_zero(self):
        arr = array.array('i', [1, 2, 3])
        result = repeat_each(arr, 0)
        assert len(result) == 0
    
    def test_empty_array(self):
        arr = array.array('i')
        result = repeat_each(arr, 5)
        assert len(result) == 0
    
    def test_invalid_n(self):
        arr = array.array('i', [1, 2, 3])
        with pytest.raises(ValueError):
            repeat_each(arr, -1)

