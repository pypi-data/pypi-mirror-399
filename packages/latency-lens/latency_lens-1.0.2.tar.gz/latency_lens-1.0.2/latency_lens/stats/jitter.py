"""Jitter and stability metrics."""

import math
from typing import Optional


def standard_deviation(values: list[float]) -> float:
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


def median_absolute_deviation(values: list[float]) -> float:
    """Calculate Median Absolute Deviation (MAD)."""
    if not values:
        return 0.0

    sorted_vals = sorted(values)
    n = len(sorted_vals)
    median = sorted_vals[n // 2] if n % 2 == 1 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

    deviations = [abs(x - median) for x in values]
    deviations_sorted = sorted(deviations)
    n_dev = len(deviations_sorted)
    mad_median = (
        deviations_sorted[n_dev // 2]
        if n_dev % 2 == 1
        else (deviations_sorted[n_dev // 2 - 1] + deviations_sorted[n_dev // 2]) / 2.0
    )

    return mad_median


def stability_score(p50: float, p99: float, spike_rate: float) -> float:
    """Calculate stability score (0-100) based on p99/p50 ratio and spike rate."""
    if p50 == 0:
        return 0.0

    ratio = p99 / p50
    ratio_penalty = min(ratio / 10.0, 1.0)
    spike_penalty = min(spike_rate * 10.0, 1.0)

    score = 100.0 * (1.0 - (ratio_penalty * 0.6 + spike_penalty * 0.4))
    return max(0.0, min(100.0, score))


def calculate_jitter_metrics(values: list[float], p50: float, p99: float, spike_rate: float) -> dict[str, float]:
    """Calculate all jitter-related metrics."""
    return {
        "std_dev": standard_deviation(values),
        "mad": median_absolute_deviation(values),
        "stability": stability_score(p50, p99, spike_rate),
    }

