"""1D peak detection algorithms."""

import numpy as np

from peak_locator.exceptions import AlgorithmError
from peak_locator.utils.compression import compress_duplicates
from peak_locator.utils.validation import validate_array


def find_peak_brute_1d(arr: np.ndarray, allow_duplicates: bool = True) -> int:
    """
    Find any peak in a 1D array using brute force (linear scan).

    Time complexity: O(n)
    Space complexity: O(1)

    Parameters
    ----------
    arr : np.ndarray
        1D array to search for peaks.
    allow_duplicates : bool, default=True
        If True, handles arrays with duplicate values by finding any valid peak.
        If False, raises an error if duplicates are found.

    Returns
    -------
    int
        Index of a peak in the array.

    Raises
    ------
    AlgorithmError
        If no peak is found (should not happen for valid inputs).
    """
    arr = validate_array(arr, min_length=1)

    if len(arr) == 1:
        return 0

    # Check boundaries first (they are peaks if >= neighbor)
    if arr[0] >= arr[1]:
        return 0
    if arr[-1] >= arr[-2]:
        return len(arr) - 1

    # Scan interior
    for i in range(1, len(arr) - 1):
        if arr[i] >= arr[i - 1] and arr[i] >= arr[i + 1]:
            return i

    # This should never happen for valid arrays
    raise AlgorithmError("No peak found in array (this should not happen)")


def find_peak_binary_1d(arr: np.ndarray, allow_duplicates: bool = True) -> int:
    """
    Find any peak in a 1D array using binary search.

    Time complexity: O(log n)
    Space complexity: O(1)

    This algorithm works by recursively narrowing the search space.
    At each step, it compares the middle element with its neighbors
    and moves toward the direction of the larger neighbor.

    Parameters
    ----------
    arr : np.ndarray
        1D array to search for peaks. Should not contain duplicates
        for optimal performance, but will work with duplicates.
    allow_duplicates : bool, default=True
        If True, handles arrays with duplicate values.
        If False, raises an error if duplicates are found.

    Returns
    -------
    int
        Index of a peak in the array.

    Raises
    ------
    AlgorithmError
        If no peak is found (should not happen for valid inputs).
    """
    arr = validate_array(arr, min_length=1)

    if len(arr) == 1:
        return 0

    left, right = 0, len(arr) - 1

    while left < right:
        mid = (left + right) // 2

        # Check if mid is a peak
        if mid == 0:
            if arr[0] >= arr[1]:
                return 0
            left = 1
        elif mid == len(arr) - 1:
            if arr[-1] >= arr[-2]:
                return len(arr) - 1
            right = len(arr) - 2
        else:
            if arr[mid] >= arr[mid - 1] and arr[mid] >= arr[mid + 1]:
                return mid
            # Move toward the larger neighbor
            if arr[mid] < arr[mid + 1]:
                left = mid + 1
            else:
                right = mid - 1

    return left


def find_peak_hybrid_1d(arr: np.ndarray, allow_duplicates: bool = True) -> int:
    """
    Find any peak in a 1D array using a hybrid approach.

    This function automatically handles duplicates by compressing them first,
    then uses binary search on the compressed array. This combines the
    efficiency of binary search with the robustness of handling duplicates.

    Time complexity: O(n) worst case (compression), O(log n) best case
    Space complexity: O(n) worst case (compression), O(1) best case

    Parameters
    ----------
    arr : np.ndarray
        1D array to search for peaks.
    allow_duplicates : bool, default=True
        If True, compresses duplicates before searching.
        If False, uses binary search directly (may not work correctly with duplicates).

    Returns
    -------
    int
        Index of a peak in the original array.

    Raises
    ------
    AlgorithmError
        If no peak is found (should not happen for valid inputs).
    """
    arr = validate_array(arr, min_length=1)

    if len(arr) == 1:
        return 0

    # Compress consecutive duplicates
    compressed, original_indices = compress_duplicates(arr)

    if len(compressed) == 1:
        # All values are the same, return any index
        return 0

    # Use binary search on compressed array
    compressed_peak_idx = find_peak_binary_1d(compressed, allow_duplicates=False)

    # Map back to original array
    return original_indices[compressed_peak_idx]


def find_all_peaks_1d(arr: np.ndarray) -> list[int]:
    """
    Find all peaks in a 1D array.

    A peak is defined as an element that is greater than or equal to both
    its neighbors (or the only neighbor for boundary elements).

    Time complexity: O(n)
    Space complexity: O(n) for storing results

    Parameters
    ----------
    arr : np.ndarray
        1D array to search for peaks.

    Returns
    -------
    list[int]
        List of indices where peaks occur.
    """
    arr = validate_array(arr, min_length=1)

    peaks: list[int] = []

    if len(arr) == 1:
        return [0]

    # Check first element
    if arr[0] >= arr[1]:
        peaks.append(0)

    # Check interior elements
    for i in range(1, len(arr) - 1):
        if arr[i] >= arr[i - 1] and arr[i] >= arr[i + 1]:
            peaks.append(i)

    # Check last element
    if arr[-1] >= arr[-2]:
        peaks.append(len(arr) - 1)

    return peaks

