"""1D peak visualization utilities."""

from typing import Optional

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    raise ImportError(
        "Visualization requires matplotlib and numpy. "
        "Install with: pip install peakfinder[viz]"
    )

from peak_locator.core.one_d import find_all_peaks_1d
from peak_locator.utils.validation import validate_array


def plot_1d_peaks(
    arr: np.ndarray,
    peaks: Optional[list[int]] = None,
    show_all: bool = False,
    title: Optional[str] = None,
    figsize: tuple = (10, 6),
) -> None:
    """
    Plot a 1D array with peaks highlighted.

    Parameters
    ----------
    arr : np.ndarray
        1D array to plot.
    peaks : Optional[List[int]], default=None
        List of peak indices to highlight. If None and show_all=True,
        automatically finds all peaks.
    show_all : bool, default=False
        If True, automatically find and show all peaks.
    title : Optional[str], default=None
        Plot title. If None, uses a default title.
    figsize : tuple, default=(10, 6)
        Figure size (width, height) in inches.

    Examples
    --------
    >>> import numpy as np
    >>> from peak_locator.visualization import plot_1d_peaks
    >>>
    >>> arr = np.array([1, 3, 2, 5, 4, 6, 3])
    >>> plot_1d_peaks(arr, show_all=True)
    """
    arr = validate_array(arr, min_length=1)

    if peaks is None and show_all:
        peaks = find_all_peaks_1d(arr)
    elif peaks is None:
        peaks = []

    fig, ax = plt.subplots(figsize=figsize)

    # Plot the array
    ax.plot(arr, "b-", linewidth=2, label="Data", alpha=0.7)
    ax.scatter(range(len(arr)), arr, c="blue", s=30, alpha=0.5, zorder=3)

    # Highlight peaks
    if peaks:
        peak_values = [arr[i] for i in peaks]
        ax.scatter(
            peaks,
            peak_values,
            c="red",
            s=100,
            marker="^",
            label="Peaks",
            zorder=5,
            edgecolors="darkred",
            linewidths=2,
        )

    ax.set_xlabel("Index", fontsize=12)
    ax.set_ylabel("Value", fontsize=12)
    ax.set_title(title or "1D Peak Detection", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.show()

