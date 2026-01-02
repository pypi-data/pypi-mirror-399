"""Tests for RMQ (Range Maximum Query) structure."""

import numpy as np

from peak_locator.structures.rmq import RMQ


class TestRMQ:
    """Tests for RMQ class."""

    def test_basic_query(self):
        """Test basic RMQ query."""
        arr = np.array([1, 3, 2, 5, 4])
        rmq = RMQ(arr)
        idx = rmq.query(0, 4)
        assert idx == 3  # Maximum is at index 3 (value 5)

    def test_query_value(self):
        """Test query_value method."""
        arr = np.array([1, 3, 2, 5, 4])
        rmq = RMQ(arr)
        val = rmq.query_value(0, 4)
        assert val == 5

    def test_single_element(self):
        """Test RMQ with single element."""
        arr = np.array([5])
        rmq = RMQ(arr)
        idx = rmq.query(0, 0)
        assert idx == 0

    def test_range_query(self):
        """Test query on a subrange."""
        arr = np.array([1, 3, 2, 5, 4, 6, 3])
        rmq = RMQ(arr)
        idx = rmq.query(0, 2)
        assert idx == 1  # Maximum in [0:3] is at index 1 (value 3)

    def test_invalid_range(self):
        """Test that invalid range raises error."""
        arr = np.array([1, 2, 3, 4, 5])
        rmq = RMQ(arr)
        with np.testing.assert_raises(ValueError):
            rmq.query(3, 1)  # left > right
        with np.testing.assert_raises(ValueError):
            rmq.query(-1, 2)  # left < 0
        with np.testing.assert_raises(ValueError):
            rmq.query(0, 10)  # right >= n

