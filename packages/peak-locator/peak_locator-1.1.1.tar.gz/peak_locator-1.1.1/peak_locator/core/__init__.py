"""Core peak detection algorithms."""

from peak_locator.core.count import count_peaks_linear, count_peaks_segment_tree
from peak_locator.core.one_d import (
    find_all_peaks_1d,
    find_peak_binary_1d,
    find_peak_brute_1d,
    find_peak_hybrid_1d,
)
from peak_locator.core.two_d import find_peak_2d

__all__ = [
    "find_peak_brute_1d",
    "find_peak_binary_1d",
    "find_peak_hybrid_1d",
    "find_all_peaks_1d",
    "count_peaks_linear",
    "count_peaks_segment_tree",
    "find_peak_2d",
]

