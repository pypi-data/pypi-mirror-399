#!/usr/bin/env python3
"""
Shared pytest fixtures for claude-dashboard tests.

Provides common fixtures for creating temporary log directories,
log files, and sample event data.
"""

import json
import pytest
from pathlib import Path


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary log directory."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True)
    return log_dir


@pytest.fixture
def temp_log_file(temp_log_dir):
    """Create a temporary log file."""
    return temp_log_dir / "test.jsonl"


@pytest.fixture
def sample_events():
    """Sample events for testing."""
    return [
        {
            "timestamp": "2024-01-15T10:30:00+00:00",
            "event_type": "PreToolUse",
            "tool": {"tool_name": "Bash"},
        },
        {
            "timestamp": "2024-01-15T10:30:01+00:00",
            "event_type": "PostToolUse",
            "tool": {"tool_name": "Read"},
        },
    ]


@pytest.fixture
def sample_pre_tool_event():
    """Sample PreToolUse event data."""
    return {
        "event_id": "abc123",
        "timestamp": "2024-01-15T10:30:00+00:00",
        "event_type": "PreToolUse",
        "session_id": "test-session-123",
        "tool_use_id": "tool-456",
        "cwd": "/home/user/project",
        "tool": {"tool_name": "Bash", "command": "ls -la"},
        "hook_processing_ms": 1.5,
    }


@pytest.fixture
def sample_post_tool_event():
    """Sample PostToolUse event data."""
    return {
        "event_id": "def456",
        "timestamp": "2024-01-15T10:30:01+00:00",
        "event_type": "PostToolUse",
        "session_id": "test-session-123",
        "tool_use_id": "tool-456",
        "cwd": "/home/user/project",
        "tool": {"tool_name": "Read", "file_path": "/path/to/file.py"},
        "response": {"success": True},
        "hook_processing_ms": 1.2,
    }


@pytest.fixture
def sample_events_jsonl(temp_log_file):
    """Create a log file with sample events."""
    events = [
        {
            "event_id": "abc123",
            "timestamp": "2024-01-15T10:30:00+00:00",
            "event_type": "PreToolUse",
            "session_id": "sess-1",
            "tool_use_id": "tool-1",
            "cwd": "/home/user",
            "tool": {"tool_name": "Bash", "command": "ls"},
            "hook_processing_ms": 1.5,
        },
        {
            "event_id": "def456",
            "timestamp": "2024-01-15T10:30:01+00:00",
            "event_type": "PostToolUse",
            "session_id": "sess-1",
            "tool_use_id": "tool-1",
            "cwd": "/home/user",
            "tool": {"tool_name": "Bash", "command": "ls"},
            "response": {"success": True},
            "hook_processing_ms": 1.2,
        },
        {
            "event_id": "ghi789",
            "timestamp": "2024-01-15T10:30:02+00:00",
            "event_type": "PreToolUse",
            "session_id": "sess-1",
            "tool_use_id": "tool-2",
            "cwd": "/home/user",
            "tool": {"tool_name": "Read", "file_path": "/test.py"},
            "hook_processing_ms": 0.8,
        },
    ]
    with open(temp_log_file, "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")
    return temp_log_file


@pytest.fixture
def multiple_log_files(temp_log_dir):
    """Create multiple log files with different events."""
    files = {}

    # First file with Bash events
    file1 = temp_log_dir / "session1.jsonl"
    with open(file1, "w") as f:
        f.write(
            json.dumps(
                {
                    "event_id": "file1-event1",
                    "timestamp": "2024-01-15T10:30:00+00:00",
                    "event_type": "PreToolUse",
                    "tool": {"tool_name": "Bash", "command": "ls"},
                }
            )
            + "\n"
        )
        f.write(
            json.dumps(
                {
                    "event_id": "file1-event2",
                    "timestamp": "2024-01-15T10:30:01+00:00",
                    "event_type": "PostToolUse",
                    "tool": {"tool_name": "Bash", "command": "ls"},
                    "response": {"success": True},
                }
            )
            + "\n"
        )
    files["file1"] = file1

    # Second file with Read events
    file2 = temp_log_dir / "session2.jsonl"
    with open(file2, "w") as f:
        f.write(
            json.dumps(
                {
                    "event_id": "file2-event1",
                    "timestamp": "2024-01-15T10:31:00+00:00",
                    "event_type": "PreToolUse",
                    "tool": {"tool_name": "Read", "file_path": "/test.py"},
                }
            )
            + "\n"
        )
    files["file2"] = file2

    # Non-jsonl file that should be ignored
    other_file = temp_log_dir / "other.txt"
    other_file.write_text("ignored\n")
    files["other"] = other_file

    return files
