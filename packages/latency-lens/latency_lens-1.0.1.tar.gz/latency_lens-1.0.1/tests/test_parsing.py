"""Tests for CSV and JSON parsing."""

import tempfile
from pathlib import Path

import pytest

from latency_lens.io.csv_reader import parse_csv
from latency_lens.io.json_reader import parse_json
from latency_lens.io.normalize import TimingRow


def test_csv_parse_with_header():
    """Test CSV parsing with header."""
    content = "ts,dur,name,track\n1000.0,12.5,render,main\n1012.5,8.3,update,main"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)

    try:
        rows = parse_csv(path)
        assert len(rows) == 2
        assert rows[0].ts_ms == 1000.0
        assert rows[0].dur_ms == 12.5
        assert rows[0].name == "render"
        assert rows[0].track == "main"
    finally:
        path.unlink()


def test_csv_parse_headerless():
    """Test CSV parsing without header."""
    content = "1000.0,12.5\n1012.5,8.3\n1020.8,15.2"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)

    try:
        rows = parse_csv(path, has_header=False)
        assert len(rows) >= 2
        assert rows[0].ts_ms == 1000.0
    finally:
        path.unlink()


def test_csv_derive_durations():
    """Test deriving durations from timestamps."""
    content = "ts\n1000.0\n1012.5\n1020.8"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)

    try:
        rows = parse_csv(path)
        assert len(rows) >= 2
        assert rows[1].dur_ms > 0
    finally:
        path.unlink()


def test_json_parse_array():
    """Test JSON parsing with array format."""
    content = '[{"ts": 1000.0, "dur": 12.5, "name": "render"}, {"ts": 1012.5, "dur": 8.3}]'
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)

    try:
        rows = parse_json(path)
        assert len(rows) == 2
        assert rows[0].ts_ms == 1000.0
        assert rows[0].dur_ms == 12.5
        assert rows[0].name == "render"
    finally:
        path.unlink()


def test_json_parse_chrome_trace():
    """Test JSON parsing with Chrome trace format."""
    content = '{"traceEvents": [{"ph": "X", "ts": 1000000, "dur": 12500, "name": "render"}]}'
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)

    try:
        rows = parse_json(path)
        assert len(rows) == 1
        assert rows[0].name == "render"
    finally:
        path.unlink()

