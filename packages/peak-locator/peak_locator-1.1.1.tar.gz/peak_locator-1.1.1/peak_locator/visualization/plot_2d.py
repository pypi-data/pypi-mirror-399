"""2D peak visualization utilities."""

from typing import Optional

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    raise ImportError(
        "Visualization requires matplotlib and numpy. "
        "Install with: pip install peakfinder[viz]"
    )

from peak_locator.core.two_d import find_peak_2d
from peak_locator.utils.validation import validate_2d_array


def plot_2d_peak(
    matrix: np.ndarray,
    peak: Optional[tuple[int, int]] = None,
    title: Optional[str] = None,
    figsize: tuple = (10, 8),
    cmap: str = "viridis",
) -> None:
    """
    Plot a 2D matrix with peak highlighted.

    Parameters
    ----------
    matrix : np.ndarray
        2D array (matrix) to plot.
    peak : Optional[Tuple[int, int]], default=None
        (row, column) indices of peak to highlight. If None,
        automatically finds a peak.
    title : Optional[str], default=None
        Plot title. If None, uses a default title.
    figsize : tuple, default=(10, 8)
        Figure size (width, height) in inches.
    cmap : str, default="viridis"
        Colormap for the heatmap.

    Examples
    --------
    >>> import numpy as np
    >>> from peak_locator.visualization import plot_2d_peak
    >>>
    >>> matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> plot_2d_peak(matrix)
    """
    matrix = validate_2d_array(matrix, min_rows=1, min_cols=1)

    if peak is None:
        peak = find_peak_2d(matrix)

    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    im = ax.imshow(matrix, cmap=cmap, aspect="auto", origin="lower")

    # Highlight peak
    row, col = peak
    ax.scatter(
        [col],
        [row],
        c="red",
        s=200,
        marker="*",
        label="Peak",
        zorder=5,
        edgecolors="white",
        linewidths=2,
    )

    # Add colorbar
    plt.colorbar(im, ax=ax, label="Value")

    ax.set_xlabel("Column", fontsize=12)
    ax.set_ylabel("Row", fontsize=12)
    ax.set_title(
        title or f"2D Peak Detection (Peak at ({row}, {col}))",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend()

    plt.tight_layout()
    plt.show()

