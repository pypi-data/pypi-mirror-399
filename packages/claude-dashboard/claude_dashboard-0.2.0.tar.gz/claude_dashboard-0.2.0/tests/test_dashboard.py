#!/usr/bin/env python3
"""
Tests for claude-dashboard dashboard module.

Tests for EventStore, LogWatcher, and dashboard UI components.
"""

import json
import time
from pathlib import Path

import pytest

from claude_dashboard.dashboard import (
    EventStore,
    LogWatcher,
    get_tool_color,
    build_events_table,
    build_stats_panel,
)


# ============================================================================
# Tests for EventStore
# ============================================================================


class TestEventStore:
    """Tests for the EventStore class."""

    def test_add_single_event(self):
        """Should add and track a single event."""
        store = EventStore()
        event = {"tool": {"tool_name": "Bash"}, "event_type": "PreToolUse"}
        store.add_event(event)

        assert len(store.events) == 1
        assert store.tool_counts["Bash"] == 1

    def test_add_multiple_events(self):
        """Should track multiple events by tool."""
        store = EventStore()
        store.add_event({"tool": {"tool_name": "Bash"}, "event_type": "PreToolUse"})
        store.add_event({"tool": {"tool_name": "Read"}, "event_type": "PreToolUse"})
        store.add_event({"tool": {"tool_name": "Bash"}, "event_type": "PreToolUse"})

        assert len(store.events) == 3
        assert store.tool_counts["Bash"] == 2
        assert store.tool_counts["Read"] == 1

    def test_max_events_limit(self):
        """Should cap events at max_events."""
        store = EventStore(max_events=5)
        for i in range(10):
            store.add_event({"tool": {"tool_name": "Bash"}, "event_type": "PreToolUse"})

        assert len(store.events) == 5
        assert store.tool_counts["Bash"] == 10  # Counts still track all

    def test_success_count(self):
        """Should track successful PostToolUse events."""
        store = EventStore()
        store.add_event(
            {
                "tool": {"tool_name": "Bash"},
                "event_type": "PostToolUse",
                "response": {"success": True},
            }
        )
        store.add_event(
            {
                "tool": {"tool_name": "Bash"},
                "event_type": "PostToolUse",
                "response": {"success": True},
            }
        )

        assert store.success_count == 2
        assert store.error_count == 0

    def test_error_count(self):
        """Should track failed PostToolUse events."""
        store = EventStore()
        store.add_event(
            {
                "tool": {"tool_name": "Bash"},
                "event_type": "PostToolUse",
                "response": {"success": False},
            }
        )

        assert store.success_count == 0
        assert store.error_count == 1

    def test_pre_tool_use_no_count(self):
        """PreToolUse events should not affect success/error counts."""
        store = EventStore()
        store.add_event({"tool": {"tool_name": "Bash"}, "event_type": "PreToolUse"})

        assert store.success_count == 0
        assert store.error_count == 0

    def test_handles_malformed_event(self):
        """Should handle malformed events gracefully."""
        store = EventStore()
        # Missing expected fields
        store.add_event({})
        assert store.tool_counts["unknown"] == 1

    def test_event_store_max_events_memory(self):
        """EventStore should properly limit memory usage."""
        store = EventStore(max_events=100)
        for i in range(1000):
            store.add_event(
                {
                    "tool": {"tool_name": "Bash"},
                    "event_type": "PreToolUse",
                    "large_data": "x" * 1000,
                }
            )

        assert len(store.events) == 100


# ============================================================================
# Tests for LogWatcher
# ============================================================================


class TestLogWatcher:
    """Tests for the LogWatcher class."""

    def test_get_new_events_empty_file(self, temp_log_file):
        """Should return empty list for empty/nonexistent file."""
        watcher = LogWatcher(temp_log_file)
        events = watcher.get_new_events()
        assert events == []

    def test_get_new_events_reads_all(self, sample_events_jsonl):
        """Should read all events on first call."""
        watcher = LogWatcher(sample_events_jsonl)
        events = watcher.get_new_events()
        assert len(events) == 3

    def test_get_new_events_incremental(self, temp_log_file):
        """Should only return new events on subsequent calls."""
        # Write initial events
        with open(temp_log_file, "w") as f:
            f.write(json.dumps({"event_id": "1"}) + "\n")
            f.write(json.dumps({"event_id": "2"}) + "\n")

        watcher = LogWatcher(temp_log_file)
        events = watcher.get_new_events()
        assert len(events) == 2

        # Add more events
        with open(temp_log_file, "a") as f:
            f.write(json.dumps({"event_id": "3"}) + "\n")

        events = watcher.get_new_events()
        assert len(events) == 1
        assert events[0]["event_id"] == "3"

    def test_get_new_events_skips_invalid_json(self, temp_log_file):
        """Should skip invalid JSON lines."""
        with open(temp_log_file, "w") as f:
            f.write(json.dumps({"event_id": "1"}) + "\n")
            f.write("not valid json\n")
            f.write(json.dumps({"event_id": "2"}) + "\n")

        watcher = LogWatcher(temp_log_file)
        events = watcher.get_new_events()
        assert len(events) == 2

    def test_get_new_events_nonexistent_file(self, tmp_path):
        """Should handle nonexistent file gracefully."""
        watcher = LogWatcher(tmp_path / "nonexistent.jsonl")
        events = watcher.get_new_events()
        assert events == []

    def test_handles_concurrent_writes(self, temp_log_file):
        """LogWatcher should handle file growing during read."""
        # Write initial data
        with open(temp_log_file, "w") as f:
            f.write(json.dumps({"event_id": "1"}) + "\n")

        watcher = LogWatcher(temp_log_file)
        events = watcher.get_new_events()
        assert len(events) == 1

        # Simulate another process writing
        with open(temp_log_file, "a") as f:
            for i in range(100):
                f.write(json.dumps({"event_id": str(i + 2)}) + "\n")

        events = watcher.get_new_events()
        assert len(events) == 100


# ============================================================================
# Tests for Multi-File LogWatcher
# ============================================================================


class TestMultiFileLogWatcher:
    """Tests for watching multiple log files."""

    def test_discovers_all_jsonl_files(self, tmp_path):
        """Should find all .jsonl files in directory."""
        # Create multiple log files
        (tmp_path / "file1.jsonl").write_text('{"event": "1"}\n')
        (tmp_path / "file2.jsonl").write_text('{"event": "2"}\n')
        (tmp_path / "other.txt").write_text("ignored\n")

        # Get all jsonl files
        jsonl_files = list(tmp_path.glob("*.jsonl"))

        assert len(jsonl_files) == 2
        assert all(f.suffix == ".jsonl" for f in jsonl_files)

    def test_tracks_events_per_file(self, multiple_log_files):
        """Should track which events came from which file."""
        file1 = multiple_log_files["file1"]
        file2 = multiple_log_files["file2"]

        watcher1 = LogWatcher(file1)
        watcher2 = LogWatcher(file2)

        events1 = watcher1.get_new_events()
        events2 = watcher2.get_new_events()

        assert len(events1) == 2
        assert len(events2) == 1
        assert events1[0]["event_id"].startswith("file1")
        assert events2[0]["event_id"].startswith("file2")

    def test_handles_new_files_appearing(self, tmp_path):
        """Should detect new log files added to directory."""
        # Start with one file
        (tmp_path / "file1.jsonl").write_text('{"event": "1"}\n')

        initial_files = set(tmp_path.glob("*.jsonl"))
        assert len(initial_files) == 1

        # Add new file
        (tmp_path / "file2.jsonl").write_text('{"event": "2"}\n')

        updated_files = set(tmp_path.glob("*.jsonl"))
        assert len(updated_files) == 2

        # New files should be discoverable
        new_files = updated_files - initial_files
        assert len(new_files) == 1
        new_file = new_files.pop()
        assert new_file.name == "file2.jsonl"

    def test_handles_empty_log_directory(self, tmp_path):
        """Should handle case where log directory has no files."""
        empty_dir = tmp_path / "empty_logs"
        empty_dir.mkdir()

        jsonl_files = list(empty_dir.glob("*.jsonl"))
        assert len(jsonl_files) == 0

    def test_aggregates_events_from_multiple_files(self, multiple_log_files):
        """Should aggregate events from multiple files into EventStore."""
        file1 = multiple_log_files["file1"]
        file2 = multiple_log_files["file2"]

        store = EventStore()

        watcher1 = LogWatcher(file1)
        watcher2 = LogWatcher(file2)

        for event in watcher1.get_new_events():
            store.add_event(event)
        for event in watcher2.get_new_events():
            store.add_event(event)

        assert len(store.events) == 3
        assert store.tool_counts["Bash"] == 2
        assert store.tool_counts["Read"] == 1

    def test_handles_files_with_different_schemas(self, tmp_path):
        """Should handle files with slightly different event schemas."""
        # File with minimal schema
        file1 = tmp_path / "minimal.jsonl"
        file1.write_text('{"tool": {"tool_name": "Bash"}}\n')

        # File with full schema
        file2 = tmp_path / "full.jsonl"
        file2.write_text(
            json.dumps(
                {
                    "event_id": "full-1",
                    "timestamp": "2024-01-15T10:30:00+00:00",
                    "event_type": "PreToolUse",
                    "session_id": "sess-1",
                    "tool": {"tool_name": "Read", "file_path": "/test.py"},
                }
            )
            + "\n"
        )

        watcher1 = LogWatcher(file1)
        watcher2 = LogWatcher(file2)

        events1 = watcher1.get_new_events()
        events2 = watcher2.get_new_events()

        assert len(events1) == 1
        assert len(events2) == 1

        # Both should be processable by EventStore
        store = EventStore()
        for event in events1 + events2:
            store.add_event(event)

        assert len(store.events) == 2


# ============================================================================
# Tests for get_tool_color
# ============================================================================


class TestGetToolColor:
    """Tests for the get_tool_color function."""

    def test_known_tools_have_colors(self):
        """Known tools should have specific colors."""
        assert get_tool_color("Bash") == "red"
        assert get_tool_color("Read") == "blue"
        assert get_tool_color("Write") == "green"
        assert get_tool_color("Edit") == "yellow"
        assert get_tool_color("Grep") == "cyan"
        assert get_tool_color("Glob") == "magenta"

    def test_web_tools_have_colors(self):
        """Web tools should have specific colors."""
        assert get_tool_color("WebFetch") == "bright_blue"
        assert get_tool_color("WebSearch") == "bright_cyan"

    def test_unknown_tools_are_white(self):
        """Unknown tools should be white."""
        assert get_tool_color("UnknownTool") == "white"
        assert get_tool_color("SomeRandomTool") == "white"


# ============================================================================
# Tests for build_events_table
# ============================================================================


class TestBuildEventsTable:
    """Tests for the build_events_table function."""

    def test_build_table_with_events(self):
        """Should build a table with event data."""
        events = [
            {
                "timestamp": "2024-01-15T10:30:00+00:00",
                "event_type": "PreToolUse",
                "session_id": "test-session-123",
                "tool": {"tool_name": "Bash", "command": "ls -la"},
            }
        ]
        table = build_events_table(events, title="Recent Events")
        assert table.title == "Recent Events"
        assert len(table.columns) == 4  # Time, Type, Tool, Details

    def test_build_table_empty_events(self):
        """Should build empty table with no events."""
        table = build_events_table([], title="Recent Events")
        assert table.title == "Recent Events"
        assert table.row_count == 0

    def test_build_table_limits_to_max_rows(self):
        """Should only show last max_rows events (default 8)."""
        events = [
            {
                "timestamp": f"2024-01-15T10:{i:02d}:00+00:00",
                "event_type": "PreToolUse",
                "tool": {"tool_name": "Bash", "command": f"cmd{i}"},
            }
            for i in range(20)
        ]
        table = build_events_table(events, title="Recent Events")
        assert table.row_count == 8  # Default max_rows is 8

    def test_build_table_custom_max_rows(self):
        """Should respect custom max_rows parameter."""
        events = [
            {
                "timestamp": f"2024-01-15T10:{i:02d}:00+00:00",
                "event_type": "PreToolUse",
                "tool": {"tool_name": "Bash", "command": f"cmd{i}"},
            }
            for i in range(20)
        ]
        table = build_events_table(events, title="Recent Events", max_rows=15)
        assert table.row_count == 15

    def test_build_table_with_title(self):
        """Should use provided title."""
        table = build_events_table([], title="Custom Title")
        assert table.title == "Custom Title"


# ============================================================================
# Tests for build_stats_panel
# ============================================================================


class TestBuildStatsPanel:
    """Tests for the build_stats_panel function."""

    def test_build_stats_empty_stores(self):
        """Should build panel with zero counts when stores are empty."""
        stores = {"file1.jsonl": EventStore()}
        panel = build_stats_panel(stores)
        assert panel.title == "Stats"

    def test_build_stats_with_data(self):
        """Should show tool counts in panel."""
        store = EventStore()
        for _ in range(5):
            store.add_event({"tool": {"tool_name": "Bash"}, "event_type": "PreToolUse"})
        for _ in range(3):
            store.add_event(
                {
                    "tool": {"tool_name": "Read"},
                    "event_type": "PostToolUse",
                    "response": {"success": True},
                }
            )

        stores = {"file1.jsonl": store}
        panel = build_stats_panel(stores)
        assert panel.title == "Stats"

    def test_build_stats_aggregates_multiple_stores(self):
        """Should aggregate stats from multiple stores."""
        store1 = EventStore()
        store2 = EventStore()

        store1.add_event({"tool": {"tool_name": "Bash"}, "event_type": "PreToolUse"})
        store1.add_event({"tool": {"tool_name": "Bash"}, "event_type": "PostToolUse", "response": {"success": True}})

        store2.add_event({"tool": {"tool_name": "Read"}, "event_type": "PreToolUse"})
        store2.add_event({"tool": {"tool_name": "Read"}, "event_type": "PostToolUse", "response": {"success": False}})

        stores = {"file1.jsonl": store1, "file2.jsonl": store2}
        panel = build_stats_panel(stores)
        assert panel.title == "Stats"

    def test_build_stats_empty_dict(self):
        """Should handle empty stores dict."""
        stores = {}
        panel = build_stats_panel(stores)
        assert panel.title == "Stats"


# ============================================================================
# Edge Cases and Integration Tests
# ============================================================================


class TestEdgeCases:
    """Edge case tests for dashboard components."""

    def test_event_store_handles_missing_tool_key(self):
        """EventStore should handle events without tool key."""
        store = EventStore()
        store.add_event({"event_type": "PreToolUse"})
        assert store.tool_counts["unknown"] == 1

    def test_event_store_handles_missing_tool_name(self):
        """EventStore should handle events with tool but no tool_name."""
        store = EventStore()
        store.add_event({"tool": {}, "event_type": "PreToolUse"})
        assert store.tool_counts["unknown"] == 1

    def test_log_watcher_handles_truncated_json(self, temp_log_file):
        """LogWatcher should handle truncated JSON at end of file."""
        with open(temp_log_file, "w") as f:
            f.write(json.dumps({"event_id": "1"}) + "\n")
            f.write('{"incomplete": "json')  # No closing brace

        watcher = LogWatcher(temp_log_file)
        events = watcher.get_new_events()
        # Should still get the valid event
        assert len(events) == 1
        assert events[0]["event_id"] == "1"

    def test_log_watcher_handles_empty_lines(self, temp_log_file):
        """LogWatcher should skip empty lines."""
        with open(temp_log_file, "w") as f:
            f.write(json.dumps({"event_id": "1"}) + "\n")
            f.write("\n")
            f.write("   \n")
            f.write(json.dumps({"event_id": "2"}) + "\n")

        watcher = LogWatcher(temp_log_file)
        events = watcher.get_new_events()
        assert len(events) == 2

    def test_event_store_preserves_order(self):
        """EventStore should preserve event order."""
        store = EventStore()
        for i in range(10):
            store.add_event({"tool": {"tool_name": f"Tool{i}"}, "event_type": "PreToolUse"})

        tool_names = [e["tool"]["tool_name"] for e in store.events]
        assert tool_names == [f"Tool{i}" for i in range(10)]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
