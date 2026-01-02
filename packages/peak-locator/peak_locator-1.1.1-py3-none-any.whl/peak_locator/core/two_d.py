"""2D peak detection algorithms."""

import numpy as np

from peak_locator.exceptions import AlgorithmError
from peak_locator.utils.validation import validate_2d_array


def find_peak_2d(
    matrix: np.ndarray, allow_duplicates: bool = True
) -> tuple[int, int]:
    """
    Find any peak in a 2D matrix.

    Uses a divide-and-conquer approach:
    1. Find the maximum in the middle column
    2. Check if it's a peak (compare with left and right neighbors)
    3. If not, recurse on the side with the larger neighbor

    Time complexity: O(n * log(m)) where n is rows and m is columns
    Space complexity: O(log(m)) for recursion stack

    Parameters
    ----------
    matrix : np.ndarray
        2D array (matrix) to search for peaks.
    allow_duplicates : bool, default=True
        If True, handles matrices with duplicate values.

    Returns
    -------
    tuple[int, int]
        (row, column) indices of a peak in the matrix.

    Raises
    ------
    AlgorithmError
        If no peak is found (should not happen for valid inputs).

    Examples
    --------
    >>> matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> find_peak_2d(matrix)
    (2, 2)
    """
    matrix = validate_2d_array(matrix, min_rows=1, min_cols=1)

    rows, cols = matrix.shape

    if rows == 1 and cols == 1:
        return (0, 0)

    def _find_peak_recursive(
        start_col: int, end_col: int
    ) -> tuple[int, int]:
        """Recursive helper function."""
        mid_col = (start_col + end_col) // 2

        # Find maximum in the middle column
        max_row = 0
        max_val = matrix[0, mid_col]

        for i in range(1, rows):
            if matrix[i, mid_col] > max_val:
                max_val = matrix[i, mid_col]
                max_row = i

        # Check if this is a peak
        is_peak = True
        if mid_col > 0 and matrix[max_row, mid_col] < matrix[max_row, mid_col - 1]:
            is_peak = False
        elif (
            mid_col < cols - 1
            and matrix[max_row, mid_col] < matrix[max_row, mid_col + 1]
        ):
            is_peak = False

        if is_peak:
            return (max_row, mid_col)

        # Recurse on the side with the larger neighbor
        if mid_col > 0 and matrix[max_row, mid_col - 1] > matrix[max_row, mid_col]:
            return _find_peak_recursive(start_col, mid_col - 1)
        else:
            return _find_peak_recursive(mid_col + 1, end_col)

    try:
        return _find_peak_recursive(0, cols - 1)
    except RecursionError:
        raise AlgorithmError(
            "Recursion depth exceeded. Matrix may be too large or malformed."
        )

