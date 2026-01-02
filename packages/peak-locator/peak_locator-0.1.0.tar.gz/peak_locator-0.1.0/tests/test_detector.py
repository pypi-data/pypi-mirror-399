"""Tests for PeakDetector class."""

import numpy as np
import pytest

from peakfinder import PeakDetector
from peakfinder.exceptions import DimensionError, ValidationError


class TestPeakDetector:
    """Tests for PeakDetector class."""

    def test_1d_basic(self):
        """Test basic 1D peak detection."""
        arr = np.array([1, 3, 2, 5, 4])
        detector = PeakDetector(arr)
        peak = detector.find_any_peak()
        assert isinstance(peak, int)
        assert 0 <= peak < len(arr)

    def test_1d_auto_mode(self):
        """Test auto mode selection."""
        arr = np.array([1, 2, 3, 4, 5, 4, 3, 2, 1])
        detector = PeakDetector(arr, mode="auto")
        peak = detector.find_any_peak()
        assert peak == 4

    def test_1d_brute_mode(self):
        """Test brute force mode."""
        arr = np.array([1, 5, 2, 6, 3])
        detector = PeakDetector(arr, mode="brute")
        peak = detector.find_any_peak()
        assert peak in [1, 3]

    def test_1d_binary_mode(self):
        """Test binary search mode."""
        arr = np.array([1, 2, 3, 4, 5, 4, 3, 2, 1])
        detector = PeakDetector(arr, mode="binary")
        peak = detector.find_any_peak()
        assert peak == 4

    def test_1d_hybrid_mode(self):
        """Test hybrid mode."""
        arr = np.array([1, 2, 2, 2, 3, 2, 1])
        detector = PeakDetector(arr, mode="hybrid")
        peak = detector.find_any_peak()
        assert peak == 4

    def test_1d_find_all_peaks(self):
        """Test finding all peaks in 1D."""
        arr = np.array([1, 5, 2, 6, 3])
        detector = PeakDetector(arr)
        peaks = detector.find_all_peaks()
        assert isinstance(peaks, list)
        assert len(peaks) >= 1
        assert all(isinstance(p, int) for p in peaks)

    def test_1d_count_peaks(self):
        """Test counting peaks in 1D."""
        arr = np.array([1, 5, 2, 6, 3])
        detector = PeakDetector(arr)
        count = detector.count_peaks()
        assert isinstance(count, int)
        assert count >= 1

    def test_2d_basic(self):
        """Test basic 2D peak detection."""
        matrix = np.array([[1, 2, 3], [4, 9, 5], [6, 7, 8]])
        detector = PeakDetector(matrix)
        peak = detector.find_peak_2d()
        assert isinstance(peak, tuple)
        assert len(peak) == 2
        row, col = peak
        assert 0 <= row < matrix.shape[0]
        assert 0 <= col < matrix.shape[1]

    def test_2d_find_any_peak(self):
        """Test find_any_peak for 2D."""
        matrix = np.array([[1, 2, 3], [4, 9, 5], [6, 7, 8]])
        detector = PeakDetector(matrix)
        peak = detector.find_any_peak()
        assert isinstance(peak, tuple)
        assert len(peak) == 2

    def test_nd_basic(self):
        """Test N-dimensional peak detection."""
        tensor = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        detector = PeakDetector(tensor)
        peak = detector.find_peak_nd()
        assert isinstance(peak, tuple)
        assert len(peak) == 3

    def test_invalid_input_none(self):
        """Test that None input raises error."""
        with pytest.raises(ValidationError):
            PeakDetector(None)

    def test_invalid_input_empty(self):
        """Test that empty input raises error."""
        with pytest.raises(ValidationError):
            PeakDetector([])

    def test_1d_find_all_peaks_not_supported_for_2d(self):
        """Test that find_all_peaks raises error for 2D."""
        matrix = np.array([[1, 2], [3, 4]])
        detector = PeakDetector(matrix)
        with pytest.raises(DimensionError):
            detector.find_all_peaks()

    def test_1d_count_peaks_not_supported_for_2d(self):
        """Test that count_peaks raises error for 2D."""
        matrix = np.array([[1, 2], [3, 4]])
        detector = PeakDetector(matrix)
        with pytest.raises(DimensionError):
            detector.count_peaks()

    def test_properties(self):
        """Test detector properties."""
        arr = np.array([1, 2, 3, 4, 5])
        detector = PeakDetector(arr)
        assert detector.ndim == 1
        assert detector.shape == (5,)
        assert np.array_equal(detector.data, arr)

    def test_duplicates_handling(self):
        """Test handling of duplicate values."""
        arr = np.array([1, 2, 2, 2, 3, 2, 1])
        detector = PeakDetector(arr, allow_duplicates=True)
        peak = detector.find_any_peak()
        assert 0 <= peak < len(arr)

