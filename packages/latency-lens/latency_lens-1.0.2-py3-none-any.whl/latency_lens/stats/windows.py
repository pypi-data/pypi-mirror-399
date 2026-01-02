"""Worst window analysis."""

from dataclasses import dataclass
from typing import Optional

from latency_lens.io.normalize import TimingRow
from latency_lens.stats.percentiles import percentile_linear_sorted


@dataclass
class Window:
    """Represents a time window with statistics."""

    start_ms: float
    end_ms: float
    p99: float
    total_ms: float
    count: int

    @property
    def duration_ms(self) -> float:
        """Window duration."""
        return self.end_ms - self.start_ms


def find_worst_windows(rows: list[TimingRow], window_ms: float, top_n: int = 10) -> list[Window]:
    """Find worst windows by p99 or total time."""
    if not rows:
        return []
    rs = sorted(rows, key=lambda r: r.ts_ms)
    n = len(rs)
    out: list[Window] = []
    j = 0

    for i in range(n):
        start = rs[i].ts_ms
        end = start + window_ms
        if j < i:
            j = i
        while j < n and rs[j].ts_ms < end:
            j += 1

        window_rows = rs[i:j]
        if not window_rows:
            continue

        durs = [r.dur_ms for r in window_rows]
        durs.sort()
        p99 = percentile_linear_sorted(durs, 0.99)
        total = sum(durs)

        out.append(Window(start_ms=start, end_ms=end, p99=p99, total_ms=total, count=len(durs)))

    out.sort(key=lambda w: (w.p99, w.total_ms), reverse=True)
    return out[:top_n]

