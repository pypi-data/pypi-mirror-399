"""Main PeakDetector class with automatic algorithm selection."""

from typing import Any, Literal, Optional, Union

import numpy as np

from peak_locator.core.count import count_peaks_linear, count_peaks_segment_tree
from peak_locator.core.n_d import find_peak_nd
from peak_locator.core.one_d import (
    find_all_peaks_1d,
    find_peak_binary_1d,
    find_peak_brute_1d,
    find_peak_hybrid_1d,
)
from peak_locator.core.two_d import find_peak_2d
from peak_locator.exceptions import DimensionError, ValidationError
from peak_locator.utils.validation import has_duplicates, validate_2d_array, validate_array


class PeakDetector:
    """
    Main interface for peak detection with automatic algorithm selection.

    This class provides a unified API for finding peaks in 1D, 2D, and N-dimensional
    data, automatically selecting the best algorithm based on data properties.

    Parameters
    ----------
    data : array-like
        Input data (1D, 2D, or N-dimensional array).
    allow_duplicates : bool, default=True
        Whether to handle arrays with duplicate values.
    mode : str, default="auto"
        Algorithm selection mode:
        - "auto": Automatically select the best algorithm
        - "brute": Use brute force (linear scan)
        - "binary": Use binary search (requires no duplicates for correctness)
        - "hybrid": Use hybrid approach (compresses duplicates then binary search)
        - "rmq": Use Range Maximum Query structure (for repeated queries)

    Examples
    --------
    >>> import numpy as np
    >>> from peak_locator import PeakDetector
    >>>
    >>> # 1D peak detection
    >>> arr = np.array([1, 3, 2, 5, 4])
    >>> detector = PeakDetector(arr)
    >>> peak_idx = detector.find_any_peak()
    >>> print(f"Peak at index: {peak_idx}")
    >>>
    >>> # 2D peak detection
    >>> matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> detector = PeakDetector(matrix)
    >>> row, col = detector.find_peak_2d()
    >>> print(f"Peak at ({row}, {col})")
    """

    def __init__(
        self,
        data: Any,
        allow_duplicates: bool = True,
        mode: Literal["auto", "brute", "binary", "hybrid", "rmq"] = "auto",
    ) -> None:
        """Initialize PeakDetector with data and configuration."""
        if data is None:
            raise ValidationError("Data cannot be None")

        self._original_data = data
        self.allow_duplicates = allow_duplicates
        self.mode = mode

        # Convert to numpy array and determine dimensionality
        try:
            self._data = np.asarray(data, dtype=np.float64)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Cannot convert input to array: {e}") from e

        self._ndim = self._data.ndim
        self._shape = self._data.shape

        # Validate based on dimensionality
        if self._ndim == 0:
            raise ValidationError("Input must be at least 1-dimensional")
        if self._ndim == 1:
            self._data_1d = validate_array(self._data, min_length=1)
        elif self._ndim == 2:
            self._data_2d = validate_2d_array(self._data, min_rows=1, min_cols=1)
        # For N-D, we'll validate on-demand

        # Pre-compute properties for algorithm selection
        self._has_dups: Optional[bool] = None
        if self._ndim == 1:
            self._has_dups = has_duplicates(self._data_1d)

    def find_any_peak(self) -> Union[int, tuple[int, ...]]:
        """
        Find any peak in the data.

        Returns
        -------
        Union[int, tuple[int, ...]]
            For 1D: index of a peak
            For 2D: (row, column) tuple
            For N-D: tuple of indices

        Raises
        ------
        DimensionError
            If data is 0-dimensional.
        """
        if self._ndim == 1:
            return self._find_peak_1d()
        elif self._ndim == 2:
            row, col = find_peak_2d(self._data_2d, self.allow_duplicates)
            return (row, col)
        else:
            result = find_peak_nd(self._data, self.allow_duplicates)
            if result is None:
                raise DimensionError("Could not find peak in N-dimensional data")
            return result

    def _find_peak_1d(self) -> int:
        """Internal method to find peak in 1D data with algorithm selection."""
        if self.mode == "auto":
            # Auto-select based on data properties
            if self._has_dups and self.allow_duplicates:
                # Use hybrid for arrays with duplicates
                return find_peak_hybrid_1d(self._data_1d, self.allow_duplicates)
            else:
                # Use binary search for arrays without duplicates
                return find_peak_binary_1d(self._data_1d, self.allow_duplicates)
        elif self.mode == "brute":
            return find_peak_brute_1d(self._data_1d, self.allow_duplicates)
        elif self.mode == "binary":
            return find_peak_binary_1d(self._data_1d, self.allow_duplicates)
        elif self.mode == "hybrid":
            return find_peak_hybrid_1d(self._data_1d, self.allow_duplicates)
        elif self.mode == "rmq":
            # For RMQ mode, we still use binary search for single queries
            # RMQ is more useful for repeated queries
            return find_peak_binary_1d(self._data_1d, self.allow_duplicates)
        else:
            raise ValidationError(f"Unknown mode: {self.mode}")

    def find_all_peaks(self) -> list[Union[int, tuple[int, ...]]]:
        """
        Find all peaks in the data.

        Currently only supported for 1D data.

        Returns
        -------
        List[Union[int, Tuple[int, ...]]]
            List of peak indices. For 1D, returns list of integers.
            For higher dimensions, returns list of tuples.

        Raises
        ------
        DimensionError
            If data is not 1-dimensional.
        """
        if self._ndim == 1:
            return find_all_peaks_1d(self._data_1d)
        else:
            raise DimensionError(
                "find_all_peaks() is currently only supported for 1D data"
            )

    def count_peaks(self, use_segment_tree: bool = False) -> int:
        """
        Count the number of peaks in the data.

        Currently only supported for 1D data.

        Parameters
        ----------
        use_segment_tree : bool, default=False
            If True, use segment tree (useful for repeated range queries).
            If False, use linear scan (faster for single count).

        Returns
        -------
        int
            Number of peaks in the data.

        Raises
        ------
        DimensionError
            If data is not 1-dimensional.
        """
        if self._ndim == 1:
            if use_segment_tree:
                return count_peaks_segment_tree(self._data_1d)
            else:
                return count_peaks_linear(self._data_1d)
        else:
            raise DimensionError(
                "count_peaks() is currently only supported for 1D data"
            )

    def find_peak_2d(self) -> tuple[int, int]:
        """
        Find a peak in 2D data.

        Returns
        -------
        tuple[int, int]
            (row, column) indices of a peak.

        Raises
        ------
        DimensionError
            If data is not 2-dimensional.
        """
        if self._ndim != 2:
            raise DimensionError(
                f"find_peak_2d() requires 2D data, got {self._ndim}D"
            )
        return find_peak_2d(self._data_2d, self.allow_duplicates)

    def find_peak_nd(self) -> tuple[int, ...]:
        """
        Find a peak in N-dimensional data.

        Returns
        -------
        Tuple[int, ...]
            Tuple of indices representing peak location.

        Raises
        ------
        DimensionError
            If data is 0-dimensional or 1-dimensional.
        """
        if self._ndim == 0:
            raise DimensionError("Cannot find peaks in 0-dimensional array")
        if self._ndim == 1:
            raise DimensionError(
                "Use find_any_peak() or find_all_peaks() for 1D data"
            )

        result = find_peak_nd(self._data, self.allow_duplicates)
        if result is None:
            raise DimensionError("Could not find peak in N-dimensional data")
        return result

    @property
    def data(self) -> np.ndarray:
        """Get the underlying data array."""
        return self._data

    @property
    def shape(self) -> tuple[int, ...]:
        """Get the shape of the data."""
        return self._shape

    @property
    def ndim(self) -> int:
        """Get the number of dimensions."""
        return self._ndim

