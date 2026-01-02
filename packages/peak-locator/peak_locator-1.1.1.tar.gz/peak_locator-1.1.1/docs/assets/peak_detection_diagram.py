#!/usr/bin/env python3
"""
Generate a copyright-free visualization diagram for PeakFinder.

This script creates a simple diagram showing peak detection in action.
Run with: python docs/assets/peak_detection_diagram.py

Requirements: matplotlib and numpy (install with: pip install matplotlib numpy)
"""

import os
import sys

# Add parent directory to path to allow importing peakfinder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

try:
    import matplotlib.pyplot as plt
    import numpy as np

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # 1D Peak Detection Visualization
    x = np.linspace(0, 10, 100)
    y = np.sin(x) * np.exp(-x / 10) + 0.3 * np.sin(3 * x)
    peaks_indices = []
    for i in range(1, len(y) - 1):
        if y[i] >= y[i - 1] and y[i] >= y[i + 1]:
            peaks_indices.append(i)

    ax1.plot(x, y, "b-", linewidth=2, label="Signal", alpha=0.7)
    ax1.scatter(
        x[peaks_indices],
        y[peaks_indices],
        c="red",
        s=100,
        marker="^",
        label="Peaks",
        zorder=5,
        edgecolors="darkred",
        linewidths=2,
    )
    ax1.set_xlabel("Index", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Value", fontsize=12, fontweight="bold")
    ax1.set_title("1D Peak Detection", fontsize=14, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # 2D Peak Detection Visualization
    matrix = np.random.rand(20, 20) * 0.5
    # Add some peaks
    matrix[5, 8] = 1.0
    matrix[12, 15] = 0.9
    matrix[8, 3] = 0.85

    im = ax2.imshow(matrix, cmap="viridis", aspect="auto", origin="lower")
    
    # Find and mark peaks (try to use PeakDetector if available)
    try:
        from peak_locator import PeakDetector
        detector = PeakDetector(matrix)
        row, col = detector.find_peak_2d()
        ax2.scatter(
            [col],
            [row],
            c="red",
            s=300,
            marker="*",
            label="Peak",
            zorder=5,
            edgecolors="white",
            linewidths=2,
        )
    except ImportError:
        # Fallback: mark the maximum manually
        max_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
        ax2.scatter(
            [max_idx[1]],
            [max_idx[0]],
            c="red",
            s=300,
            marker="*",
            label="Peak",
            zorder=5,
            edgecolors="white",
            linewidths=2,
        )

    plt.colorbar(im, ax=ax2, label="Intensity")
    ax2.set_xlabel("Column", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Row", fontsize=12, fontweight="bold")
    ax2.set_title("2D Peak Detection", fontsize=14, fontweight="bold")
    ax2.legend(fontsize=10)

    plt.suptitle("PeakFinder: Multi-Dimensional Peak Detection", 
                 fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    
    output_path = os.path.join(os.path.dirname(__file__), "peak_detection_diagram.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ Diagram saved to {output_path}")
    plt.close()

except ImportError as e:
    print(f"Error: {e}")
    print("\nPlease install required dependencies:")
    print("  pip install matplotlib numpy")
    print("\nOr use the ASCII art version in the README.")
    sys.exit(1)
except Exception as e:
    print(f"Error generating diagram: {e}")
    print("\nUsing ASCII art version in README instead.")
    sys.exit(1)

