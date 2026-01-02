"""Input validation utilities for peak detection."""

from typing import Any

import numpy as np

from peak_locator.exceptions import ValidationError


def validate_array(data: Any, min_length: int = 1) -> np.ndarray:
    """
    Validate and convert input to a 1D numpy array.

    Parameters
    ----------
    data : array-like
        Input data to validate. Must be convertible to a 1D numpy array.
    min_length : int, default=1
        Minimum required length of the array.

    Returns
    -------
    np.ndarray
        Validated 1D numpy array.

    Raises
    ------
    ValidationError
        If the input cannot be converted to a valid array or is too short.
    """
    if data is None:
        raise ValidationError("Input data cannot be None")

    try:
        arr = np.asarray(data, dtype=np.float64)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Cannot convert input to array: {e}") from e

    if arr.ndim == 0:
        raise ValidationError("Input must be at least 1-dimensional")

    if arr.ndim > 1:
        arr = arr.flatten()

    if len(arr) < min_length:
        raise ValidationError(
            f"Array must have at least {min_length} element(s), got {len(arr)}"
        )

    return arr


def validate_2d_array(data: Any, min_rows: int = 1, min_cols: int = 1) -> np.ndarray:
    """
    Validate and convert input to a 2D numpy array.

    Parameters
    ----------
    data : array-like
        Input data to validate. Must be convertible to a 2D numpy array.
    min_rows : int, default=1
        Minimum required number of rows.
    min_cols : int, default=1
        Minimum required number of columns.

    Returns
    -------
    np.ndarray
        Validated 2D numpy array.

    Raises
    ------
    ValidationError
        If the input cannot be converted to a valid 2D array or is too small.
    """
    if data is None:
        raise ValidationError("Input data cannot be None")

    try:
        arr = np.asarray(data, dtype=np.float64)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Cannot convert input to array: {e}") from e

    if arr.ndim == 0:
        raise ValidationError("Input must be at least 1-dimensional")

    if arr.ndim == 1:
        raise ValidationError("Input must be 2-dimensional for 2D peak detection")

    if arr.ndim > 2:
        raise ValidationError(
            f"Input has {arr.ndim} dimensions, but 2D peak detection requires exactly 2"
        )

    rows, cols = arr.shape
    if rows < min_rows:
        raise ValidationError(
            f"Array must have at least {min_rows} row(s), got {rows}"
        )
    if cols < min_cols:
        raise ValidationError(
            f"Array must have at least {min_cols} column(s), got {cols}"
        )

    return arr


def has_duplicates(arr: np.ndarray) -> bool:
    """
    Check if an array contains duplicate values.

    Parameters
    ----------
    arr : np.ndarray
        Input array to check.

    Returns
    -------
    bool
        True if the array contains duplicates, False otherwise.
    """
    return len(np.unique(arr)) < len(arr)

