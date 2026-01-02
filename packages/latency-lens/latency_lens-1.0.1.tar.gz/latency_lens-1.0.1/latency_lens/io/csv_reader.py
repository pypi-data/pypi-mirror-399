"""CSV input reader for timing data."""

import csv
from pathlib import Path
from typing import Iterator, Optional

from latency_lens.io.normalize import TimingRow, derive_durations_from_timestamps, dur_to_ms, ts_to_ms


def parse_csv(path: Path, has_header: Optional[bool] = None) -> list[TimingRow]:
    """Parse CSV file into normalized timing rows."""
    rows: list[TimingRow] = []

    with open(path, "r", encoding="utf-8") as f:
        # Sniff for delimiter and header
        sample = f.read(1024)
        f.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter

        reader = csv.reader(f, delimiter=delimiter)
        header = None

        # Try to detect header
        if has_header is None:
            try:
                first_row = next(reader)
                f.seek(0)
                reader = csv.reader(f, delimiter=delimiter)
                if sniffer.has_header(sample):
                    header = first_row
                    has_header = True
                else:
                    has_header = False
                    f.seek(0)
                    reader = csv.reader(f, delimiter=delimiter)
            except StopIteration:
                has_header = False

        if has_header:
            header = next(reader, None)
            if header:
                header = [col.strip().lower() for col in header]

        # Find column indices
        ts_col = None
        dur_col = None
        name_col = None
        track_col = None

        if header:
            for i, col in enumerate(header):
                if col in ("ts", "timestamp", "time"):
                    ts_col = i
                elif col in ("dur", "duration", "delta"):
                    dur_col = i
                elif col in ("name", "event", "span"):
                    name_col = i
                elif col in ("track", "thread", "category", "tid"):
                    track_col = i
        else:
            # Assume first column is ts, second is dur if present
            ts_col = 0
            first_row_peek = next(reader, [])
            if len(first_row_peek) > 1:
                dur_col = 1
            f.seek(0)
            reader = csv.reader(f, delimiter=delimiter)
            if has_header:
                next(reader)  # Skip header

        # Parse rows
        for line_num, row in enumerate(reader, start=1):
            if not row or all(not cell.strip() for cell in row):
                continue

            try:
                ts_val = None
                dur_val = 0.0
                name_val = None
                track_val = None

                if ts_col is not None and ts_col < len(row):
                    ts_val = ts_to_ms(float(row[ts_col].strip()))

                if dur_col is not None and dur_col < len(row):
                    dur_val = dur_to_ms(float(row[dur_col].strip()))

                if name_col is not None and name_col < len(row):
                    name_val = row[name_col].strip() or None

                if track_col is not None and track_col < len(row):
                    track_val = row[track_col].strip() or None

                if ts_val is not None:
                    rows.append(TimingRow(ts_ms=ts_val, dur_ms=dur_val, name=name_val, track=track_val))

            except (ValueError, IndexError) as e:
                # Skip malformed rows but continue
                continue

    # Derive durations if missing
    if all(row.dur_ms == 0.0 for row in rows):
        rows = derive_durations_from_timestamps(rows)

    return rows

