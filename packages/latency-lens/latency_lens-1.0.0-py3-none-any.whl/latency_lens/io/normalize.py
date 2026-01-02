"""Normalize timing data into a consistent internal format."""

from dataclasses import dataclass
from typing import Optional


def ts_to_ms(value: float) -> float:
    """
    Best-effort timestamp normalization to milliseconds.

    Handles:
    - relative seconds (0..1e6) -> ms
    - epoch seconds (~1e9..1e11) -> ms
    - epoch milliseconds (~1e11..1e14) -> already ms
    - microseconds (~1e14..1e17) -> ms
    - nanoseconds (>=1e17) -> ms
    """
    v = float(value)
    av = abs(v)

    if av < 1e6:
        return v * 1000.0
    if 1e9 <= av < 1e11:
        return v * 1000.0
    if 1e11 <= av < 1e14:
        return v
    if av >= 1e17:
        return v / 1_000_000.0  # ns -> ms
    if av >= 1e14:
        return v / 1000.0  # us -> ms
    return v


def dur_to_ms(value: float) -> float:
    """
    Duration normalization to milliseconds.

    Common cases:
    - 0.016 -> seconds (16ms)
    - 16.6  -> milliseconds
    - 1000000 -> microseconds
    """
    v = float(value)
    av = abs(v)

    if av <= 60.0:
        return v * 1000.0  # seconds -> ms (common in traces)
    if av >= 1e6:
        return v / 1000.0  # us -> ms
    return v  # assume ms


@dataclass
class TimingRow:
    """Normalized timing data row."""

    ts_ms: float
    dur_ms: float
    name: Optional[str] = None
    track: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate and ensure non-negative values."""
        if self.ts_ms < 0:
            raise ValueError(f"Timestamp must be non-negative, got {self.ts_ms}")
        if self.dur_ms < 0:
            raise ValueError(f"Duration must be non-negative, got {self.dur_ms}")


def derive_durations_from_timestamps(rows: list[TimingRow]) -> list[TimingRow]:
    """Derive durations from successive timestamps if durations are missing."""
    if not rows:
        return rows

    sorted_rows = sorted(rows, key=lambda r: r.ts_ms)
    result = []

    for i, row in enumerate(sorted_rows):
        if row.dur_ms == 0.0:
            if i > 0:
                dur = row.ts_ms - sorted_rows[i - 1].ts_ms
                result.append(TimingRow(ts_ms=row.ts_ms, dur_ms=max(0.0, dur), name=row.name, track=row.track))
            else:
                result.append(TimingRow(ts_ms=row.ts_ms, dur_ms=0.0, name=row.name, track=row.track))
        else:
            result.append(row)

    return result

