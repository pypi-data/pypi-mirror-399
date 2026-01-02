"""Spike detection and analysis."""

from dataclasses import dataclass
from typing import Optional

from latency_lens.io.normalize import TimingRow


@dataclass
class Spike:
    """Represents a detected latency spike."""

    ts_ms: float
    dur_ms: float
    name: Optional[str]
    track: Optional[str]

    def __lt__(self, other: "Spike") -> bool:
        """Sort by duration descending."""
        return self.dur_ms > other.dur_ms


def detect_spikes(rows: list[TimingRow], threshold_ms: float) -> list[Spike]:
    """Detect all spikes above the threshold."""
    spikes = []
    for row in rows:
        if row.dur_ms > threshold_ms:
            spikes.append(Spike(ts_ms=row.ts_ms, dur_ms=row.dur_ms, name=row.name, track=row.track))

    return sorted(spikes)


def spike_rate(spikes: list[Spike], total_count: int) -> float:
    """Calculate spike rate as percentage of total events."""
    if total_count == 0:
        return 0.0
    return (len(spikes) / total_count) * 100.0

