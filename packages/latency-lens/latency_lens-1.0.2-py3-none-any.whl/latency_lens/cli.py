"""Command-line interface for latency-lens."""

import re
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from latency_lens.io.csv_reader import parse_csv
from latency_lens.io.json_reader import parse_json
from latency_lens.io.normalize import TimingRow
from latency_lens.report.html import generate_html_report
from latency_lens.stats.jitter import calculate_jitter_metrics
from latency_lens.stats.percentiles import calculate_basic_stats, calculate_percentiles
from latency_lens.stats.spikes import detect_spikes, spike_rate
from latency_lens.stats.windows import find_worst_windows

console = Console()


def parse_quantiles(spec: str) -> list[float]:
    """Parse and validate quantile specification."""
    qs = []
    for part in spec.split(","):
        if not part.strip():
            continue
        q = float(part.strip())
        if not (0.0 < q < 1.0):
            raise click.BadParameter(f"Quantile out of range (0,1): {q}")
        qs.append(q)
    return sorted(set(qs))


def load_data(path: Path, format: Optional[str] = None) -> list[TimingRow]:
    """Load timing data from file."""
    if format == "csv" or (format is None and path.suffix.lower() == ".csv"):
        return parse_csv(path)
    elif format == "json" or (format is None and path.suffix.lower() == ".json"):
        return parse_json(path)
    else:
        raise click.BadParameter(f"Unsupported format: {format or path.suffix}")


def filter_rows(rows: list[TimingRow], pattern: Optional[str]) -> list[TimingRow]:
    """Filter rows by name or track using regex."""
    if not pattern:
        return rows

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise click.BadParameter(f"Invalid regex pattern: {e}")

    filtered = []
    for row in rows:
        if (row.name and regex.search(row.name)) or (row.track and regex.search(row.track)):
            filtered.append(row)
    return filtered


def group_rows(rows: list[TimingRow], by: Optional[str]) -> dict[str, list[TimingRow]]:
    """Group rows by name or track."""
    if not by or by == "none":
        return {"all": rows}

    groups: dict[str, list[TimingRow]] = {}
    for row in rows:
        key = getattr(row, by, None) or "unknown"
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    return groups


def analyze_group(rows: list[TimingRow], quantiles: list[float], spike_threshold: float) -> dict:
    """Analyze a group of timing rows."""
    if not rows:
        return {}

    durations = [r.dur_ms for r in rows]
    basic = calculate_basic_stats(durations)
    percentiles_dict = calculate_percentiles(durations, quantiles)

    spikes = detect_spikes(rows, spike_threshold)
    spike_rate_pct = spike_rate(spikes, len(rows))

    p50 = percentiles_dict.get(0.5, 0.0)
    p99 = percentiles_dict.get(0.99, 0.0)
    jitter = calculate_jitter_metrics(durations, p50, p99, spike_rate_pct / 100.0)

    return {
        "basic": basic,
        "percentiles": percentiles_dict,
        "spikes": spikes,
        "spike_rate": spike_rate_pct,
        "jitter": jitter,
        "rows": rows,
    }


def print_summary_table(results: dict, group_name: str = "Overall") -> None:
    """Print summary statistics table."""
    basic = results["basic"]
    percentiles = results["percentiles"]

    table = Table(title=f"{group_name} Summary", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Count", f"{basic['count']:,}")
    table.add_row("Min", f"{basic['min']:.2f} ms")
    table.add_row("Max", f"{basic['max']:.2f} ms")
    table.add_row("Avg", f"{basic['avg']:.2f} ms")
    table.add_row("", "")
    table.add_row("p50", f"{percentiles.get(0.5, 0.0):.2f} ms")
    table.add_row("p90", f"{percentiles.get(0.9, 0.0):.2f} ms")
    table.add_row("p95", f"{percentiles.get(0.95, 0.0):.2f} ms")
    table.add_row("p99", f"{percentiles.get(0.99, 0.0):.2f} ms")

    console.print(table)
    console.print()


def print_jitter_table(results: dict) -> None:
    """Print jitter metrics table."""
    jitter = results["jitter"]

    table = Table(title="Jitter Metrics", show_header=True, header_style="bold yellow")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    table.add_row("Std Dev", f"{jitter['std_dev']:.2f} ms")
    table.add_row("MAD", f"{jitter['mad']:.2f} ms")
    table.add_row("Stability", f"{jitter['stability']:.1f}/100")

    console.print(table)
    console.print()


def print_spike_table(results: dict, top_n: int) -> None:
    """Print top spikes table."""
    spikes = results["spikes"][:top_n]
    spike_rate_pct = results["spike_rate"]

    if not spikes:
        console.print("[dim]No spikes detected above threshold.[/dim]\n")
        return

    table = Table(title=f"Top {top_n} Spikes (Rate: {spike_rate_pct:.2f}%)", show_header=True, header_style="bold red")
    table.add_column("Rank", justify="right", style="dim")
    table.add_column("Timestamp", justify="right")
    table.add_column("Duration", justify="right", style="red")
    table.add_column("Name", style="cyan")
    table.add_column("Track", style="dim")

    for i, spike in enumerate(spikes, 1):
        table.add_row(
            str(i),
            f"{spike.ts_ms:.2f} ms",
            f"{spike.dur_ms:.2f} ms",
            spike.name or "-",
            spike.track or "-",
        )

    console.print(table)
    console.print()


def print_windows_table(windows: list, window_ms: float) -> None:
    """Print worst windows table."""
    if not windows:
        console.print("[dim]No windows found.[/dim]\n")
        return

    table = Table(title=f"Worst Windows ({window_ms:.0f}ms)", show_header=True, header_style="bold magenta")
    table.add_column("Rank", justify="right", style="dim")
    table.add_column("Start", justify="right")
    table.add_column("End", justify="right")
    table.add_column("p99", justify="right", style="red")
    table.add_column("Total", justify="right")
    table.add_column("Count", justify="right")

    for i, window in enumerate(windows, 1):
        table.add_row(
            str(i),
            f"{window.start_ms:.2f} ms",
            f"{window.end_ms:.2f} ms",
            f"{window.p99:.2f} ms",
            f"{window.total_ms:.2f} ms",
            str(window.count),
        )

    console.print(table)
    console.print()


@click.group()
def cli() -> None:
    """Latency Lens - See p99 latency and jitter, not averages."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--format", type=click.Choice(["csv", "json", "auto"]), default="auto", help="Input format")
@click.option("--by", type=click.Choice(["name", "track", "none"]), default="none", help="Group by field")
@click.option("--filter", type=str, help="Filter by regex pattern on name/track")
@click.option("--spike-ms", type=float, default=16.6, help="Spike threshold in ms")
@click.option("--window-ms", type=float, default=1000.0, help="Rolling window size in ms")
@click.option("--top", type=int, default=10, help="Top N spikes/windows")
@click.option("--quantiles", type=str, default="0.5,0.9,0.95,0.99", help="Comma-separated quantiles")
@click.option("--csv", type=click.Path(path_type=Path), help="Export normalized CSV")
def analyze(
    path: Path,
    format: Optional[str],
    by: str,
    filter: Optional[str],
    spike_ms: float,
    window_ms: float,
    top: int,
    quantiles: str,
    csv: Optional[Path],
) -> None:
    """Analyze timing data and display results in terminal."""
    try:
        format_val = None if format == "auto" else format
        rows = load_data(path, format_val)
        rows = filter_rows(rows, filter)

        if not rows:
            console.print("[red]No data found after filtering.[/red]")
            sys.exit(1)

        quantile_list = parse_quantiles(quantiles)

        groups = group_rows(rows, by)
        all_results = {}

        for group_name, group_rows_list in groups.items():
            results = analyze_group(group_rows_list, quantile_list, spike_ms)
            all_results[group_name] = results

            if by != "none":
                console.print(f"\n[bold cyan]Group: {group_name}[/bold cyan]\n")

            print_summary_table(results, group_name)
            print_jitter_table(results)
            print_spike_table(results, top)

            windows = find_worst_windows(group_rows_list, window_ms, top)
            print_windows_table(windows, window_ms)

        if csv:
            export_csv(rows, csv)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--html", type=click.Path(path_type=Path), required=True, help="Output HTML file")
@click.option("--format", type=click.Choice(["csv", "json", "auto"]), default="auto", help="Input format")
@click.option("--by", type=click.Choice(["name", "track", "none"]), default="none", help="Group by field")
@click.option("--filter", type=str, help="Filter by regex pattern on name/track")
@click.option("--spike-ms", type=float, default=16.6, help="Spike threshold in ms")
@click.option("--window-ms", type=float, default=1000.0, help="Rolling window size in ms")
@click.option("--top", type=int, default=10, help="Top N spikes/windows")
@click.option("--quantiles", type=str, default="0.5,0.9,0.95,0.99", help="Comma-separated quantiles")
@click.option("--csv", type=click.Path(path_type=Path), help="Export normalized CSV")
def report(
    path: Path,
    html: Path,
    format: Optional[str],
    by: str,
    filter: Optional[str],
    spike_ms: float,
    window_ms: float,
    top: int,
    quantiles: str,
    csv: Optional[Path],
) -> None:
    """Generate HTML report from timing data."""
    try:
        format_val = None if format == "auto" else format
        rows = load_data(path, format_val)
        rows = filter_rows(rows, filter)

        if not rows:
            console.print("[red]No data found after filtering.[/red]")
            sys.exit(1)

        quantile_list = parse_quantiles(quantiles)

        groups = group_rows(rows, by)
        all_results = {}

        for group_name, group_rows_list in groups.items():
            results = analyze_group(group_rows_list, quantile_list, spike_ms)
            windows = find_worst_windows(group_rows_list, window_ms, top)
            results["windows"] = windows
            all_results[group_name] = results

        generate_html_report(all_results, html, spike_ms, window_ms)

        console.print(f"[green]HTML report generated: {html}[/green]")

        if csv:
            export_csv(rows, csv)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def export_csv(rows: list[TimingRow], path: Path) -> None:
    """Export normalized rows to CSV."""
    import csv

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ts_ms", "dur_ms", "name", "track"])
        for row in rows:
            writer.writerow([row.ts_ms, row.dur_ms, row.name or "", row.track or ""])

    console.print(f"[green]Exported normalized CSV: {path}[/green]")


def main() -> None:
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()

