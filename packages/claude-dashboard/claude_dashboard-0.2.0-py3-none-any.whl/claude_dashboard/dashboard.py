#!/usr/bin/env python3
"""
Claude Code Observability Dashboard - Real-time CLI dashboard using Rich.

This dashboard monitors multiple JSONL log files in the .claude/logs/ directory
and displays events from each file in separate sections.
"""

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from claude_dashboard import __version__

# Default configuration
DEFAULT_LOGS_DIR = ".claude/logs"
REFRESH_RATE = 1.0
MAX_EVENTS_PER_FILE = 100


class EventStore:
    """Store events for a single log file."""

    def __init__(self, max_events: int = MAX_EVENTS_PER_FILE):
        self.events: List[Dict[str, Any]] = []
        self.tool_counts: Dict[str, int] = defaultdict(int)
        self.max_events = max_events
        self.success_count = 0
        self.error_count = 0

    def add_event(self, event: Dict[str, Any]) -> None:
        """Add an event to the store."""
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)

        # Track tool usage
        tool = event.get("tool", {})
        tool_name = tool.get("tool_name", "unknown") if isinstance(tool, dict) else "unknown"
        self.tool_counts[tool_name] += 1

        # Track success/error counts
        if event.get("event_type") == "PostToolUse":
            response = event.get("response", {})
            if isinstance(response, dict) and response.get("success", True):
                self.success_count += 1
            else:
                self.error_count += 1


class LogWatcher:
    """Watch a single log file for new events."""

    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.position = 0

    def get_new_events(self) -> List[Dict[str, Any]]:
        """Read new events from the log file since last read."""
        events = []
        if not self.log_path.exists():
            return events

        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                f.seek(self.position)
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
                self.position = f.tell()
        except (IOError, OSError):
            pass

        return events


class MultiFileLogWatcher:
    """Watch multiple log files in a directory."""

    def __init__(self, logs_dir: Path):
        self.logs_dir = logs_dir
        self.watchers: Dict[str, LogWatcher] = {}
        self.stores: Dict[str, EventStore] = {}

    def discover_log_files(self) -> List[Path]:
        """Find all .jsonl files in the logs directory."""
        if not self.logs_dir.exists():
            return []
        return sorted(self.logs_dir.glob("*.jsonl"))

    def update(self) -> None:
        """Check for new log files and read new events from all files."""
        # Discover any new log files
        for log_file in self.discover_log_files():
            file_name = log_file.name
            if file_name not in self.watchers:
                self.watchers[file_name] = LogWatcher(log_file)
                self.stores[file_name] = EventStore()

        # Read new events from all watched files
        for file_name, watcher in self.watchers.items():
            new_events = watcher.get_new_events()
            for event in new_events:
                self.stores[file_name].add_event(event)

    def get_file_names(self) -> List[str]:
        """Get list of watched file names."""
        return list(self.stores.keys())

    def get_store(self, file_name: str) -> Optional[EventStore]:
        """Get the event store for a specific file."""
        return self.stores.get(file_name)


def get_tool_color(tool_name: str) -> str:
    """Get the color for a tool name."""
    colors = {
        "Bash": "red",
        "Read": "blue",
        "Write": "green",
        "Edit": "yellow",
        "Grep": "cyan",
        "Glob": "magenta",
        "WebFetch": "bright_blue",
        "WebSearch": "bright_cyan",
    }
    return colors.get(tool_name, "white")


def build_events_table(events: List[Dict[str, Any]], title: str, max_rows: int = 8) -> Table:
    """Build a table of recent events."""
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        expand=True,
        title_style="bold white",
    )
    table.add_column("Time", width=10)
    table.add_column("Type", width=12)
    table.add_column("Tool", width=12)
    table.add_column("Details", ratio=1, overflow="ellipsis")

    for event in reversed(events[-max_rows:]):
        # Parse timestamp
        ts = event.get("timestamp", "")
        if "T" in ts:
            ts = ts.split("T")[-1][:8]
        else:
            ts = ts[:8] if ts else "-"

        # Get event type
        event_type = event.get("event_type", event.get("event", ""))
        if isinstance(event_type, str):
            event_type = event_type.replace("ToolUse", "")

        # Get tool info
        tool = event.get("tool", {})
        if isinstance(tool, dict):
            tool_name = tool.get("tool_name", "unknown")
            details = (
                tool.get("file_path")
                or str(tool.get("command", ""))[:50]
                or tool.get("pattern")
                or "-"
            )
        else:
            tool_name = str(tool) if tool else "-"
            details = event.get("message", "-")

        # Add row with colored tool name
        table.add_row(
            ts,
            str(event_type)[:12],
            f"[{get_tool_color(tool_name)}]{tool_name}[/]",
            str(details)[:60],
        )

    return table


def build_stats_panel(stores: Dict[str, EventStore]) -> Panel:
    """Build a statistics panel aggregating data from all stores."""
    total_events = 0
    total_success = 0
    total_error = 0
    combined_tool_counts: Dict[str, int] = defaultdict(int)

    for store in stores.values():
        total_events += sum(store.tool_counts.values())
        total_success += store.success_count
        total_error += store.error_count
        for tool, count in store.tool_counts.items():
            combined_tool_counts[tool] += count

    lines = [
        f"[bold]Total Events:[/bold] {total_events}",
        f"[green]OK:[/green] {total_success}  [red]Fail:[/red] {total_error}",
        "",
        "[bold]Top Tools:[/bold]",
    ]

    for tool, count in sorted(combined_tool_counts.items(), key=lambda x: -x[1])[:6]:
        lines.append(f"  [{get_tool_color(tool)}]{tool:12}[/] {count}x")

    return Panel("\n".join(lines), title="Stats", border_style="blue")


def build_file_section(file_name: str, store: EventStore) -> Panel:
    """Build a panel for a single log file's events."""
    title = file_name.replace(".jsonl", "")
    table = build_events_table(store.events, title=f"Recent Events ({len(store.events)} total)")
    return Panel(table, title=f"[bold]{title}[/bold]", border_style="cyan")


def build_dashboard(multi_watcher: MultiFileLogWatcher) -> Layout:
    """Build the complete dashboard layout."""
    layout = Layout()

    # Header
    header = Panel(
        Text("Claude Code Observability Dashboard", style="bold white on blue", justify="center"),
        style="blue",
    )

    file_names = multi_watcher.get_file_names()

    if not file_names:
        # No log files found
        no_logs_panel = Panel(
            Text(
                f"No log files found in {multi_watcher.logs_dir}\n\n"
                "Waiting for log files to appear...",
                style="dim",
                justify="center",
            ),
            title="Waiting for Logs",
            border_style="yellow",
        )
        layout.split_column(
            Layout(header, name="header", size=3),
            Layout(no_logs_panel, name="main"),
        )
        return layout

    # Build sections for each log file
    file_sections = []
    for file_name in sorted(file_names):
        store = multi_watcher.get_store(file_name)
        if store:
            section = build_file_section(file_name, store)
            file_sections.append(Layout(section, name=file_name))

    # Build stats panel
    stats = build_stats_panel(multi_watcher.stores)

    # Create layout
    if len(file_sections) == 1:
        # Single file: simple layout
        layout.split_column(
            Layout(header, name="header", size=3),
            Layout(name="main"),
        )
        layout["main"].split_row(
            file_sections[0],
            Layout(stats, name="stats", size=25),
        )
    else:
        # Multiple files: stack them vertically
        layout.split_column(
            Layout(header, name="header", size=3),
            Layout(name="content"),
        )

        # Split content into files area and stats
        layout["content"].split_row(
            Layout(name="files", ratio=4),
            Layout(stats, name="stats", size=25),
        )

        # Stack file sections vertically
        layout["files"].split_column(*file_sections)

    return layout


def run_dashboard(logs_dir: Optional[Path] = None) -> None:
    """Run the dashboard with live updates."""
    console = Console()

    # Determine logs directory
    if logs_dir is None:
        logs_dir = Path.cwd() / DEFAULT_LOGS_DIR

    multi_watcher = MultiFileLogWatcher(logs_dir)

    # Initial update to discover files
    multi_watcher.update()

    console.print(f"[dim]Watching: {logs_dir}[/dim]")
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")

    try:
        with Live(build_dashboard(multi_watcher), console=console, refresh_per_second=1) as live:
            while True:
                multi_watcher.update()
                live.update(build_dashboard(multi_watcher))
                time.sleep(REFRESH_RATE)
    except KeyboardInterrupt:
        console.print("\n[dim]Dashboard stopped.[/dim]")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="claude-dash",
        description="Real-time CLI dashboard for Claude Code tool events",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--logs-dir",
        type=Path,
        default=None,
        help=f"Directory containing JSONL log files (default: ./{DEFAULT_LOGS_DIR})",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Watch a single log file instead of a directory",
    )

    args = parser.parse_args()

    if args.log_file:
        # Single file mode - use parent directory
        logs_dir = args.log_file.parent
    else:
        logs_dir = args.logs_dir

    run_dashboard(logs_dir)


if __name__ == "__main__":
    main()
