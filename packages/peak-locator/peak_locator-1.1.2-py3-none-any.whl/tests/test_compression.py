"""Tests for compression utilities."""

import numpy as np

from peak_locator.utils.compression import compress_duplicates, expand_peak_indices


class TestCompressDuplicates:
    """Tests for compress_duplicates function."""

    def test_no_duplicates(self):
        """Test array with no consecutive duplicates."""
        arr = np.array([1, 2, 3, 4, 5])
        compressed, indices = compress_duplicates(arr)
        assert np.array_equal(compressed, arr)
        assert indices == [0, 1, 2, 3, 4]

    def test_consecutive_duplicates(self):
        """Test array with consecutive duplicates."""
        arr = np.array([1, 2, 2, 2, 3, 3, 4])
        compressed, indices = compress_duplicates(arr)
        assert np.array_equal(compressed, np.array([1, 2, 3, 4]))
        assert indices == [0, 3, 5, 6]

    def test_all_same(self):
        """Test array with all same values."""
        arr = np.array([5, 5, 5, 5])
        compressed, indices = compress_duplicates(arr)
        assert len(compressed) == 1
        assert compressed[0] == 5
        assert indices == [3]

    def test_empty_array(self):
        """Test empty array."""
        arr = np.array([])
        compressed, indices = compress_duplicates(arr)
        assert len(compressed) == 0
        assert indices == []


class TestExpandPeakIndices:
    """Tests for expand_peak_indices function."""

    def test_basic_expansion(self):
        """Test basic index expansion."""
        original_indices = [0, 3, 5, 6]
        peak_indices = [1, 3]
        expanded = expand_peak_indices(peak_indices, original_indices)
        assert expanded == [3, 6]

    def test_single_index(self):
        """Test expansion of single index."""
        original_indices = [0, 2, 4, 6]
        peak_indices = [2]
        expanded = expand_peak_indices(peak_indices, original_indices)
        assert expanded == [4]

    def test_all_indices(self):
        """Test expansion of all indices."""
        original_indices = [0, 1, 2, 3]
        peak_indices = [0, 1, 2, 3]
        expanded = expand_peak_indices(peak_indices, original_indices)
        assert expanded == [0, 1, 2, 3]

