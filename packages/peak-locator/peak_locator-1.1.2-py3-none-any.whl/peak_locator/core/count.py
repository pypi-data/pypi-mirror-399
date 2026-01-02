"""Peak counting algorithms."""

from typing import Optional

import numpy as np

from peak_locator.core.one_d import find_all_peaks_1d
from peak_locator.structures.segment_tree import SegmentTree
from peak_locator.utils.validation import validate_array


def count_peaks_linear(arr: np.ndarray) -> int:
    """
    Count the number of peaks in a 1D array using linear scan.

    Time complexity: O(n)
    Space complexity: O(1)

    Parameters
    ----------
    arr : np.ndarray
        1D array to count peaks in.

    Returns
    -------
    int
        Number of peaks in the array.
    """
    arr = validate_array(arr, min_length=1)
    peaks = find_all_peaks_1d(arr)
    return len(peaks)


def count_peaks_segment_tree(
    arr: np.ndarray, queries: Optional[list[tuple]] = None
) -> int:
    """
    Count peaks using segment tree for efficient range queries.

    This is useful when you need to count peaks in multiple subarrays
    of the same array. For a single count, use count_peaks_linear instead.

    Time complexity:
        - Initialization: O(n)
        - Query: O(log n) per query
        - Single count: O(n) (use count_peaks_linear for single counts)

    Parameters
    ----------
    arr : np.ndarray
        1D array to count peaks in.
    queries : Optional[list[tuple]], default=None
        List of (start, end) tuples for range queries.
        If None, counts all peaks in the array.

    Returns
    -------
    int
        Number of peaks. If queries are provided, returns the count
        for the entire array (use the segment tree directly for range queries).

    Examples
    --------
    >>> arr = np.array([1, 3, 2, 5, 4])
    >>> count_peaks_segment_tree(arr)
    2
    """
    arr = validate_array(arr, min_length=1)

    if queries is None or len(queries) == 0:
        # For single count, linear is simpler
        return count_peaks_linear(arr)

    # Build segment tree for range queries
    # For now, we'll use it for the full array
    # In a full implementation, you'd query specific ranges
    tree = SegmentTree(arr)
    return tree.count_peaks_in_range(0, len(arr) - 1)

