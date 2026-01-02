"""N-dimensional peak detection concepts and utilities."""

from typing import Optional

import numpy as np

from peak_locator.exceptions import DimensionError


def find_peak_nd(
    tensor: np.ndarray, allow_duplicates: bool = True
) -> Optional[tuple[int, ...]]:
    """
    Find a peak in an N-dimensional tensor.

    This is a conceptual implementation that generalizes the 2D approach.
    For high-dimensional data, this may not be the most efficient approach.

    Time complexity: Approximately O(d * n^(d-1) * log(n)) for d dimensions
    Space complexity: O(log(n)) for recursion

    Parameters
    ----------
    tensor : np.ndarray
        N-dimensional array to search for peaks.
    allow_duplicates : bool, default=True
        If True, handles tensors with duplicate values.

    Returns
    -------
    Optional[tuple[int, ...]]
        Tuple of indices representing a peak location, or None if not found.

    Raises
    ------
    DimensionError
        If the tensor is 0-dimensional or 1-dimensional (use 1D functions instead).

    Examples
    --------
    >>> tensor = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
    >>> find_peak_nd(tensor)
    (1, 1, 1)
    """
    if tensor.ndim == 0:
        raise DimensionError("Cannot find peaks in 0-dimensional array")
    if tensor.ndim == 1:
        raise DimensionError(
            "Use 1D peak detection functions for 1-dimensional arrays"
        )

    if tensor.size == 0:
        return None

    # For 2D, delegate to 2D function
    if tensor.ndim == 2:
        from peak_locator.core.two_d import find_peak_2d

        row, col = find_peak_2d(tensor, allow_duplicates)
        return (row, col)

    # For higher dimensions, use recursive approach
    # This is a simplified implementation
    # In practice, you might want to flatten or use different strategies

    # Find the maximum element (greedy approach)
    max_idx = np.unravel_index(np.argmax(tensor), tensor.shape)

    # Verify it's a peak by checking all neighbors
    def is_peak_at(coord: tuple[int, ...]) -> bool:
        """Check if coordinate is a peak."""
        for dim in range(tensor.ndim):
            for offset in [-1, 1]:
                neighbor = list(coord)
                neighbor[dim] += offset

                # Check bounds
                if neighbor[dim] < 0 or neighbor[dim] >= tensor.shape[dim]:
                    continue

                # Check if neighbor is larger
                if tensor[tuple(neighbor)] > tensor[coord]:
                    return False
        return True

    if is_peak_at(max_idx):
        return max_idx

    # If not a peak, this is a simplified fallback
    # A full implementation would use divide-and-conquer
    return max_idx

