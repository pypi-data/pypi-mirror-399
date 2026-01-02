"""Range Maximum Query (RMQ) data structure for efficient peak queries."""

import numpy as np


class RMQ:
    """
    Range Maximum Query data structure using sparse table.

    Preprocesses an array to answer maximum queries in O(1) time
    after O(n log n) preprocessing.

    Time complexity:
        - Preprocessing: O(n log n)
        - Query: O(1)
    Space complexity: O(n log n)
    """

    def __init__(self, arr: np.ndarray) -> None:
        """
        Initialize RMQ structure.

        Parameters
        ----------
        arr : np.ndarray
            1D array to build RMQ structure for.
        """
        self.arr = np.asarray(arr)
        self.n = len(arr)
        self.log_n = int(np.log2(self.n)) + 1

        # sparse_table[i][j] = index of max in range [j, j + 2^i - 1]
        self.sparse_table: list[list[int]] = [
            [0] * self.n for _ in range(self.log_n)
        ]

        # Initialize for length 1
        for i in range(self.n):
            self.sparse_table[0][i] = i

        # Build table for increasing powers of 2
        for i in range(1, self.log_n):
            j = 0
            while j + (1 << i) - 1 < self.n:
                left_max_idx = self.sparse_table[i - 1][j]
                right_max_idx = self.sparse_table[i - 1][j + (1 << (i - 1))]

                if self.arr[left_max_idx] >= self.arr[right_max_idx]:
                    self.sparse_table[i][j] = left_max_idx
                else:
                    self.sparse_table[i][j] = right_max_idx
                j += 1

    def query(self, left: int, right: int) -> int:
        """
        Query the maximum value index in range [left, right].

        Parameters
        ----------
        left : int
            Left boundary of the range (inclusive).
        right : int
            Right boundary of the range (inclusive).

        Returns
        -------
        int
            Index of the maximum value in the range.

        Examples
        --------
        >>> arr = np.array([1, 3, 2, 5, 4])
        >>> rmq = RMQ(arr)
        >>> rmq.query(0, 4)
        3
        """
        if left < 0 or right >= self.n or left > right:
            raise ValueError(f"Invalid range: [{left}, {right}]")

        length = right - left + 1
        k = int(np.log2(length))

        # Query two overlapping ranges of length 2^k
        left_max_idx = self.sparse_table[k][left]
        right_max_idx = self.sparse_table[k][right - (1 << k) + 1]

        if self.arr[left_max_idx] >= self.arr[right_max_idx]:
            return left_max_idx
        return right_max_idx

    def query_value(self, left: int, right: int) -> float:
        """
        Query the maximum value in range [left, right].

        Parameters
        ----------
        left : int
            Left boundary of the range (inclusive).
        right : int
            Right boundary of the range (inclusive).

        Returns
        -------
        float
            Maximum value in the range.
        """
        idx = self.query(left, right)
        return float(self.arr[idx])

