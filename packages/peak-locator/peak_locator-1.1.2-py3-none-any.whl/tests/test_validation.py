"""Tests for validation utilities."""

import numpy as np
import pytest

from peak_locator.exceptions import ValidationError
from peak_locator.utils.validation import has_duplicates, validate_2d_array, validate_array


class TestValidateArray:
    """Tests for validate_array function."""

    def test_valid_list(self):
        """Test validation with a valid list."""
        arr = validate_array([1, 2, 3, 4, 5])
        assert isinstance(arr, np.ndarray)
        assert len(arr) == 5

    def test_valid_numpy_array(self):
        """Test validation with a valid numpy array."""
        arr = validate_array(np.array([1, 2, 3]))
        assert isinstance(arr, np.ndarray)
        assert len(arr) == 3

    def test_2d_array_flattened(self):
        """Test that 2D arrays are flattened."""
        arr = validate_array([[1, 2], [3, 4]])
        assert arr.ndim == 1
        assert len(arr) == 4

    def test_none_raises_error(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_array(None)

    def test_empty_array_raises_error(self):
        """Test that empty array raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_array([])

    def test_min_length_enforced(self):
        """Test that min_length is enforced."""
        with pytest.raises(ValidationError):
            validate_array([1], min_length=2)

    def test_scalar_raises_error(self):
        """Test that scalar raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_array(5)


class TestValidate2DArray:
    """Tests for validate_2d_array function."""

    def test_valid_2d_list(self):
        """Test validation with a valid 2D list."""
        arr = validate_2d_array([[1, 2], [3, 4]])
        assert isinstance(arr, np.ndarray)
        assert arr.ndim == 2
        assert arr.shape == (2, 2)

    def test_valid_2d_numpy_array(self):
        """Test validation with a valid 2D numpy array."""
        arr = validate_2d_array(np.array([[1, 2], [3, 4]]))
        assert isinstance(arr, np.ndarray)
        assert arr.ndim == 2

    def test_1d_raises_error(self):
        """Test that 1D array raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_2d_array([1, 2, 3])

    def test_3d_raises_error(self):
        """Test that 3D array raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_2d_array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

    def test_none_raises_error(self):
        """Test that None raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_2d_array(None)

    def test_empty_2d_raises_error(self):
        """Test that empty 2D array raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_2d_array([[]])


class TestHasDuplicates:
    """Tests for has_duplicates function."""

    def test_no_duplicates(self):
        """Test array with no duplicates."""
        arr = np.array([1, 2, 3, 4, 5])
        assert has_duplicates(arr) is False

    def test_has_duplicates(self):
        """Test array with duplicates."""
        arr = np.array([1, 2, 2, 3, 4])
        assert has_duplicates(arr) is True

    def test_all_same(self):
        """Test array with all same values."""
        arr = np.array([5, 5, 5, 5])
        assert has_duplicates(arr) is True

