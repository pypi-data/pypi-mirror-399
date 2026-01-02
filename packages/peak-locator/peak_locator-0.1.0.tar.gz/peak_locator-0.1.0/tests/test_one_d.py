"""Tests for 1D peak detection algorithms."""

import numpy as np

from peakfinder.core.one_d import (
    find_all_peaks_1d,
    find_peak_binary_1d,
    find_peak_brute_1d,
    find_peak_hybrid_1d,
)


class TestFindPeakBrute1D:
    """Tests for brute force 1D peak detection."""

    def test_single_element(self):
        """Test array with single element."""
        arr = np.array([5])
        peak = find_peak_brute_1d(arr)
        assert peak == 0

    def test_simple_peak(self):
        """Test simple peak in middle."""
        arr = np.array([1, 3, 2])
        peak = find_peak_brute_1d(arr)
        assert peak == 1
        assert arr[peak] == 3

    def test_peak_at_start(self):
        """Test peak at the start."""
        arr = np.array([5, 3, 2, 1])
        peak = find_peak_brute_1d(arr)
        assert peak == 0

    def test_peak_at_end(self):
        """Test peak at the end."""
        arr = np.array([1, 2, 3, 5])
        peak = find_peak_brute_1d(arr)
        assert peak == 3

    def test_multiple_peaks_returns_any(self):
        """Test that any peak is returned when multiple exist."""
        arr = np.array([1, 5, 2, 6, 3])
        peak = find_peak_brute_1d(arr)
        assert peak in [1, 3]
        assert arr[peak] >= arr[peak - 1] if peak > 0 else True
        assert arr[peak] >= arr[peak + 1] if peak < len(arr) - 1 else True

    def test_plateau(self):
        """Test array with plateau (equal values)."""
        arr = np.array([1, 3, 3, 3, 2])
        peak = find_peak_brute_1d(arr)
        # Should return a valid peak index
        assert 0 <= peak < len(arr)


class TestFindPeakBinary1D:
    """Tests for binary search 1D peak detection."""

    def test_single_element(self):
        """Test array with single element."""
        arr = np.array([5])
        peak = find_peak_binary_1d(arr)
        assert peak == 0

    def test_simple_peak(self):
        """Test simple peak in middle."""
        arr = np.array([1, 3, 2])
        peak = find_peak_binary_1d(arr)
        assert peak == 1

    def test_peak_at_start(self):
        """Test peak at the start."""
        arr = np.array([5, 3, 2, 1])
        peak = find_peak_binary_1d(arr)
        assert peak == 0

    def test_peak_at_end(self):
        """Test peak at the end."""
        arr = np.array([1, 2, 3, 5])
        peak = find_peak_binary_1d(arr)
        assert peak == 3

    def test_larger_array(self):
        """Test with larger array."""
        arr = np.array([1, 2, 3, 4, 5, 4, 3, 2, 1])
        peak = find_peak_binary_1d(arr)
        assert peak == 4
        assert arr[peak] == 5


class TestFindPeakHybrid1D:
    """Tests for hybrid 1D peak detection."""

    def test_single_element(self):
        """Test array with single element."""
        arr = np.array([5])
        peak = find_peak_hybrid_1d(arr)
        assert peak == 0

    def test_with_duplicates(self):
        """Test array with consecutive duplicates."""
        arr = np.array([1, 2, 2, 2, 3, 2, 1])
        peak = find_peak_hybrid_1d(arr)
        # Peak should be at index 4 (value 3)
        assert peak == 4

    def test_all_same_values(self):
        """Test array with all same values."""
        arr = np.array([5, 5, 5, 5])
        peak = find_peak_hybrid_1d(arr)
        assert peak == 0  # Returns first index

    def test_no_duplicates(self):
        """Test array without duplicates."""
        arr = np.array([1, 3, 2, 5, 4])
        peak = find_peak_hybrid_1d(arr)
        # Should find a valid peak
        assert 0 <= peak < len(arr)


class TestFindAllPeaks1D:
    """Tests for finding all peaks in 1D array."""

    def test_single_element(self):
        """Test array with single element."""
        arr = np.array([5])
        peaks = find_all_peaks_1d(arr)
        assert peaks == [0]

    def test_single_peak(self):
        """Test array with single peak."""
        arr = np.array([1, 3, 2])
        peaks = find_all_peaks_1d(arr)
        assert peaks == [1]

    def test_multiple_peaks(self):
        """Test array with multiple peaks."""
        arr = np.array([1, 5, 2, 6, 3])
        peaks = find_all_peaks_1d(arr)
        assert 1 in peaks
        assert 3 in peaks
        assert len(peaks) == 2

    def test_peaks_at_boundaries(self):
        """Test peaks at array boundaries."""
        arr = np.array([5, 3, 2, 1, 4])
        peaks = find_all_peaks_1d(arr)
        assert 0 in peaks  # Start is a peak
        assert 4 in peaks  # End is a peak

    def test_plateau(self):
        """Test array with plateau."""
        arr = np.array([1, 3, 3, 3, 2])
        peaks = find_all_peaks_1d(arr)
        # All elements in plateau should be peaks
        assert len(peaks) >= 1

    def test_all_increasing(self):
        """Test strictly increasing array."""
        arr = np.array([1, 2, 3, 4, 5])
        peaks = find_all_peaks_1d(arr)
        assert peaks == [4]  # Only last element is a peak

    def test_all_decreasing(self):
        """Test strictly decreasing array."""
        arr = np.array([5, 4, 3, 2, 1])
        peaks = find_all_peaks_1d(arr)
        assert peaks == [0]  # Only first element is a peak

