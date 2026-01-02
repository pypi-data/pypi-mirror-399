"""Tests for percentile calculations."""

import pytest

from latency_lens.stats.percentiles import calculate_basic_stats, calculate_percentiles


def test_basic_stats_empty():
    """Test basic stats with empty list."""
    result = calculate_basic_stats([])
    assert result["min"] == 0.0
    assert result["max"] == 0.0
    assert result["avg"] == 0.0
    assert result["count"] == 0


def test_basic_stats_single():
    """Test basic stats with single value."""
    result = calculate_basic_stats([42.0])
    assert result["min"] == 42.0
    assert result["max"] == 42.0
    assert result["avg"] == 42.0
    assert result["count"] == 1


def test_basic_stats_multiple():
    """Test basic stats with multiple values."""
    values = [10.0, 20.0, 30.0, 40.0, 50.0]
    result = calculate_basic_stats(values)
    assert result["min"] == 10.0
    assert result["max"] == 50.0
    assert result["avg"] == 30.0
    assert result["count"] == 5


def test_percentiles_empty():
    """Test percentiles with empty list."""
    result = calculate_percentiles([], [0.5, 0.9, 0.95, 0.99])
    assert result[0.5] == 0.0
    assert result[0.9] == 0.0
    assert result[0.95] == 0.0
    assert result[0.99] == 0.0


def test_percentiles_single():
    """Test percentiles with single value."""
    result = calculate_percentiles([42.0], [0.5, 0.9, 0.95, 0.99])
    assert result[0.5] == 42.0
    assert result[0.9] == 42.0
    assert result[0.95] == 42.0
    assert result[0.99] == 42.0


def test_percentiles_100_values():
    """Test percentiles with 100 values."""
    values = list(range(1, 101))
    result = calculate_percentiles(values, [0.5, 0.9, 0.95, 0.99])
    assert 49 <= result[0.5] <= 51
    assert 89 <= result[0.9] <= 91
    assert 94 <= result[0.95] <= 96
    assert 98 <= result[0.99] <= 100


def test_percentiles_p50():
    """Test p50 (median) calculation."""
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = calculate_percentiles(values, [0.5])
    assert result[0.5] == 3.0


def test_percentiles_p99():
    """Test p99 calculation."""
    values = list(range(1, 101))
    result = calculate_percentiles(values, [0.99])
    assert result[0.99] >= 98.0

