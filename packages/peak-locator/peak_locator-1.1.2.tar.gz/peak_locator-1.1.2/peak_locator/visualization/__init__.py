"""Visualization utilities for peak detection."""

try:
    from peak_locator.visualization.plot_1d import plot_1d_peaks
    from peak_locator.visualization.plot_2d import plot_2d_peak

    __all__ = ["plot_1d_peaks", "plot_2d_peak"]
except ImportError:
    # Visualization requires matplotlib and numpy
    __all__ = []

