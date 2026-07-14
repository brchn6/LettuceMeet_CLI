"""Shared test fixtures."""
import json
from pathlib import Path

import pytest


FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def event_j5r5a() -> dict:
    """Real event data for 'LIS1 proteomics analysis discussion'."""
    path = FIXTURE_DIR / "event_j5r5a.json"
    if path.exists():
        return json.loads(path.read_text())
    # Fallback inline data so tests work without the fixture file
    return {
        "id": "J5R5a",
        "title": "LIS1 proteomics analysis discussion",
        "description": "go over the LIS1 organoids proteomics experiment",
        "type": 0,
        "pollStartTime": "09:00:00.000Z",
        "pollEndTime": "17:00:00.000Z",
        "timeZone": "Asia/Jerusalem",
        "pollDates": [
            "2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25",
            "2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02",
        ],
        "start": None,
        "end": None,
        "isScheduled": False,
        "pollResponses": [
            {
                "id": "UG9sbFJlc3BvbnNlOjExMDg3NTYz",
                "user": {"__typename": "User", "name": "Alice", "email": "alice@example.com"},
                "availabilities": [
                    {"start": "2026-06-22T09:00:00.000Z", "end": "2026-06-22T17:00:00.000Z"},
                    {"start": "2026-06-25T09:00:00.000Z", "end": "2026-06-25T17:00:00.000Z"},
                    {"start": "2026-06-29T09:00:00.000Z", "end": "2026-06-29T17:00:00.000Z"},
                    {"start": "2026-06-30T09:00:00.000Z", "end": "2026-06-30T17:00:00.000Z"},
                    {"start": "2026-07-01T09:00:00.000Z", "end": "2026-07-01T17:00:00.000Z"},
                ],
                "event": {"id": "J5R5a"},
            },
        ],
    }


@pytest.fixture
def session_file(tmp_path, monkeypatch):
    """Set up a temporary session file and override session_path."""
    from lettucemeet_cli import config
    path = tmp_path / "session.json"
    monkeypatch.setattr(config, "session_path", lambda: path)
    return path
