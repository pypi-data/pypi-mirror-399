"""JSON input reader for timing data."""

import json
from pathlib import Path
from typing import Any, Optional

try:
    import orjson
    JSON_LOAD = orjson.loads
except ImportError:
    JSON_LOAD = json.loads

from latency_lens.io.normalize import TimingRow, derive_durations_from_timestamps, dur_to_ms, ts_to_ms


def parse_chrome_trace_event(event: dict[str, Any]) -> Optional[TimingRow]:
    """Parse a Chrome trace format event."""
    if event.get("ph") != "X":
        return None
    ts = event.get("ts")
    dur = event.get("dur")
    if ts is None or dur is None:
        return None
    ts_ms = float(ts) / 1000.0
    dur_ms = float(dur) / 1000.0
    name = event.get("name")
    track = event.get("tid") or event.get("cat")
    return TimingRow(ts_ms=ts_ms, dur_ms=dur_ms, name=name, track=str(track) if track else None)


def parse_json(path: Path) -> list[TimingRow]:
    """Parse JSON file into normalized timing rows."""
    with open(path, "rb") as f:
        content = f.read()

    try:
        data = JSON_LOAD(content)
    except Exception:
        # Fallback to standard json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

    rows: list[TimingRow] = []

    # Check if it's a Chrome trace format
    if isinstance(data, dict) and "traceEvents" in data:
        events = data["traceEvents"]
        for event in events:
            if isinstance(event, dict):
                row = parse_chrome_trace_event(event)
                if row:
                    rows.append(row)
    elif isinstance(data, list):
        # Array of objects
        for item in data:
            if not isinstance(item, dict):
                continue

            ts = item.get("ts") or item.get("timestamp") or item.get("time")
            if ts is None:
                continue

            ts_ms = ts_to_ms(float(ts))

            dur = item.get("dur") or item.get("duration") or item.get("delta")
            dur_ms = 0.0
            if dur is not None:
                dur_ms = dur_to_ms(float(dur))

            name = item.get("name") or item.get("event") or item.get("span")
            track = item.get("track") or item.get("thread") or item.get("tid") or item.get("category")

            rows.append(TimingRow(ts_ms=ts_ms, dur_ms=dur_ms, name=name, track=str(track) if track else None))

    # Derive durations if missing
    if all(row.dur_ms == 0.0 for row in rows):
        rows = derive_durations_from_timestamps(rows)

    return rows

