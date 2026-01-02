"""Tests for 2D peak detection algorithms."""

import numpy as np

from peakfinder.core.two_d import find_peak_2d


class TestFindPeak2D:
    """Tests for 2D peak detection."""

    def test_single_element(self):
        """Test matrix with single element."""
        matrix = np.array([[5]])
        row, col = find_peak_2d(matrix)
        assert row == 0
        assert col == 0

    def test_simple_peak(self):
        """Test simple peak in middle."""
        matrix = np.array([[1, 2, 3], [4, 9, 5], [6, 7, 8]])
        row, col = find_peak_2d(matrix)
        # Peak should be at (1, 1) with value 9
        assert row == 1
        assert col == 1
        assert matrix[row, col] == 9

    def test_peak_at_corner(self):
        """Test peak at corner."""
        matrix = np.array([[10, 2, 3], [4, 5, 6], [7, 8, 9]])
        row, col = find_peak_2d(matrix)
        # Should find a valid peak
        assert 0 <= row < matrix.shape[0]
        assert 0 <= col < matrix.shape[1]

    def test_peak_at_edge(self):
        """Test peak at edge."""
        matrix = np.array([[1, 2, 10], [4, 5, 6], [7, 8, 9]])
        row, col = find_peak_2d(matrix)
        assert 0 <= row < matrix.shape[0]
        assert 0 <= col < matrix.shape[1]

    def test_larger_matrix(self):
        """Test with larger matrix."""
        matrix = np.array(
            [
                [1, 2, 3, 4, 5],
                [6, 7, 8, 9, 10],
                [11, 12, 20, 13, 14],
                [15, 16, 17, 18, 19],
            ]
        )
        row, col = find_peak_2d(matrix)
        # Should find a valid peak
        assert 0 <= row < matrix.shape[0]
        assert 0 <= col < matrix.shape[1]
        # Verify it's actually a peak
        val = matrix[row, col]
        if row > 0:
            assert val >= matrix[row - 1, col]
        if row < matrix.shape[0] - 1:
            assert val >= matrix[row + 1, col]
        if col > 0:
            assert val >= matrix[row, col - 1]
        if col < matrix.shape[1] - 1:
            assert val >= matrix[row, col + 1]

    def test_all_same_values(self):
        """Test matrix with all same values."""
        matrix = np.array([[5, 5, 5], [5, 5, 5], [5, 5, 5]])
        row, col = find_peak_2d(matrix)
        # Should return a valid index
        assert 0 <= row < matrix.shape[0]
        assert 0 <= col < matrix.shape[1]

    def test_single_row(self):
        """Test matrix with single row."""
        matrix = np.array([[1, 5, 3, 2, 4]])
        row, col = find_peak_2d(matrix)
        assert row == 0
        assert 0 <= col < matrix.shape[1]

    def test_single_column(self):
        """Test matrix with single column."""
        matrix = np.array([[1], [5], [3], [2], [4]])
        row, col = find_peak_2d(matrix)
        assert col == 0
        assert 0 <= row < matrix.shape[0]

