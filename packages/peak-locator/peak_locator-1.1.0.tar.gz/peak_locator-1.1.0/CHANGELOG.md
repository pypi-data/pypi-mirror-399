# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-29

### Added

#### Core Functionality
- **1D Peak Detection**: Implementation of multiple algorithms for one-dimensional peak detection
  - Brute force algorithm (`mode="brute"`) with O(n) time complexity
  - Binary search algorithm (`mode="binary"`) with O(log n) time complexity
  - Hybrid algorithm (`mode="hybrid"`) that handles duplicates efficiently
  - Automatic algorithm selection (`mode="auto"`) based on data properties

- **2D Peak Detection**: Divide-and-conquer algorithm for two-dimensional matrices
  - O(n log m) time complexity for n×m matrices
  - Efficient peak finding in image and matrix data

- **N-Dimensional Support**: Conceptual implementation for higher-dimensional peak detection
  - Support for 3D, 4D, and higher-dimensional tensors
  - Greedy maximum approach with neighbor verification

#### Peak Counting
- Linear scan method for single peak count queries
- Segment tree implementation for efficient range queries
- O(n) preprocessing with O(log n) query time for repeated operations

#### Data Structures
- **RMQ (Range Maximum Query)**: Sparse table implementation
  - O(n log n) preprocessing, O(1) query time
  - Efficient for range maximum queries

- **Segment Tree**: For peak counting in subarrays
  - O(n) build time, O(log n) query time
  - Optimized for multiple range queries

#### Utilities
- Input validation with comprehensive error handling
- Duplicate compression utilities for efficient processing
- Type-safe validation functions for 1D and 2D arrays

#### Visualization
- 1D peak visualization with matplotlib integration
- 2D peak visualization with heatmap support
- Optional visualization dependencies (`peakfinder[viz]`)

#### API
- **PeakDetector** class: Unified interface for all peak detection operations
  - Automatic algorithm selection
  - Support for multiple dimensions
  - Thread-safe read-only operations
  - Deterministic algorithms

#### Documentation
- Comprehensive README with installation and usage examples
- SDK-style documentation in `docs/` directory:
  - Quick Start Guide
  - 1D Peak Detection Examples
  - 2D Peak Detection Examples
  - Peak Counting Guide
  - Segment Tree Usage
  - N-Dimensional Concepts

#### Testing
- Comprehensive test suite with pytest
- Unit tests for all core algorithms
- Edge case coverage (empty arrays, single elements, duplicates, boundaries)
- Validation and error handling tests
- Test coverage for data structures

#### Developer Experience
- Full type annotations throughout the codebase
- `py.typed` marker for type checking support
- PEP-8 compliant code formatting
- Configuration for black, ruff, and mypy
- Development dependencies and setup instructions

### Technical Details
- Python 3.9+ support
- NumPy as core dependency
- Optional matplotlib for visualization
- MIT License
- Zero external dependencies for core functionality (except NumPy)

[0.1.0]: https://github.com/chiraagkakar/peak_locator/releases/tag/v0.1.0

