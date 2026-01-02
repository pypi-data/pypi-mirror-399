"""Percentile calculations for timing data."""

from typing import Optional


def percentile_linear(values: list[float], p: float) -> float:
    """Calculate percentile using linear interpolation."""
    if not values:
        return 0.0
    xs = sorted(values)
    n = len(xs)
    if n == 1:
        return xs[0]
    idx = p * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return xs[lo] + (xs[hi] - xs[lo]) * frac


def percentile_linear_sorted(xs: list[float], p: float) -> float:
    """Calculate percentile using linear interpolation (assumes sorted input)."""
    if not xs:
        return 0.0
    n = len(xs)
    if n == 1:
        return xs[0]
    idx = p * (n - 1)
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return xs[lo] + (xs[hi] - xs[lo]) * frac


def calculate_percentiles(values: list[float], quantiles: list[float]) -> dict[float, float]:
    """Calculate multiple percentiles from a list of values."""
    if not values:
        return {q: 0.0 for q in quantiles}

    result = {}
    for q in quantiles:
        result[q] = percentile_linear(values, q)

    return result


def calculate_basic_stats(values: list[float]) -> dict[str, float]:
    """Calculate min, max, avg, and count."""
    if not values:
        return {"min": 0.0, "max": 0.0, "avg": 0.0, "count": 0}

    return {
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
        "count": len(values),
    }

