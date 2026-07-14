# LettuceMeet CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool that interacts with the LettuceMeet GraphQL API to create polls, view events with responses, and compute optimal meeting overlaps -- all from the terminal.

**Architecture:** Python package under `src/lettucemeet_cli/` with a CLI entry point using `argparse`. A `GraphQLClient` class handles HTTP + auth. Separate modules for API operations, data models, and overlap analysis. Session token stored locally in `data/session.json`.

**Tech Stack:** Python 3.11+, `requests` (HTTP client), stdlib `argparse` (CLI), stdlib `datetime` (time handling), stdlib `json` (config/session).

---

## File Structure

### New files to create:

```
src/
  lettucemeet_cli/
    __init__.py          # Package marker, version
    __main__.py          # Entry: python -m lettucemeet_cli
    cli.py               # Argument parser, subcommand dispatch
    client.py            # GraphQLClient (HTTP, auth, session management)
    api.py               # Typed API functions (create_event, get_event, etc.)
    models.py            # Dataclasses: Event, PollResponse, Availability, User, CreateEventInput
    overlap.py           # Overlap calculation logic
    config.py            # Config loading (session file path, env vars)

data/
  session.json           # Local session storage (gitignored)

tests/
  test_client.py         # Client unit tests (mocked HTTP)
  test_api.py            # API function tests
  test_models.py         # Model construction/validation tests
  test_overlap.py        # Overlap calculation tests
  test_cli.py            # CLI parsing tests
  conftest.py            # Shared fixtures
  fixtures/
    event_j5r5a.json     # Snapshot of real event data from HAR

docs/
  plans/
    2026-07-14-lettucemeet-cli.md    # This plan
```

### Modified files:
- `pyproject.toml` - Add `requests`, update description, add console_scripts entry point
- `README.md` - Replace placeholder with actual docs
- `main.py` - Simple wrapper that calls `cli.main()`
- `.memory/progress.md` - Update as work progresses

---

## Task Breakdown

### Task 1: Project scaffold + dependencies

**Files:**
- Modify: `pyproject.toml`
- Create: `src/lettucemeet_cli/__init__.py`
- Create: `src/lettucemeet_cli/__main__.py`
- Create: `src/lettucemeet_cli/cli.py`
- Create: `src/lettucemeet_cli/config.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Update pyproject.toml with description and dependencies**

Replace the placeholder description and add `requests` as a dependency.

```toml
[project]
name = "LettuceMeet_CLI"
version = "0.1.0"
description = "Terminal CLI for LettuceMeet - create polls, view responses, find meeting overlaps"
readme = "README.md"
requires-python = ">=3.11"
dependencies = ["requests"]

[project.scripts]
lettucemeet = "lettucemeet_cli.cli:main"

[dependency-groups]
dev = [
  "pytest",
  "ruff",
  "mypy",
  "requests-mock",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.11"
strict = true
```

- [ ] **Step 2: Sync dependencies**

Run: `uv sync`
Expected: `requests` is installed, dev deps installed.

- [ ] **Step 3: Create `src/lettucemeet_cli/__init__.py`**

```python
"""LettuceMeet CLI - terminal automation for LettuceMeet meeting polls."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Create `src/lettucemeet_cli/config.py`**

Manages session file paths and configuration loading.

```python
"""Configuration and session storage management."""

import json
import os
from pathlib import Path
from typing import Optional


def _project_root() -> Path:
    """Find the project root (directory containing pyproject.toml)."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return cwd


def session_path() -> Path:
    """Path to the local session file (gitignored data/ directory)."""
    return _project_root() / "data" / "session.json"


def load_token() -> Optional[str]:
    """Load the session token from the session file or env var.

    Priority: env var LETTUCEMEET_TOKEN > data/session.json > None.
    """
    token = os.environ.get("LETTUCEMEET_TOKEN")
    if token:
        return token

    path = session_path()
    if path.exists():
        try:
            data = json.loads(path.read_text())
            return data.get("session_token")
        except (json.JSONDecodeError, KeyError):
            return None

    return None


def save_token(token: str) -> None:
    """Save a session token to the session file."""
    path = session_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"session_token": token}, indent=2))
```

- [ ] **Step 5: Create `src/lettucemeet_cli/cli.py`**

Minimal CLI scaffold with subcommands stubbed out.

```python
"""CLI entry point with argparse-based subcommand dispatch."""

import argparse
import sys
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lettucemeet",
        description="Terminal CLI for LettuceMeet - create polls, view responses, find meeting overlaps.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # login
    p_login = sub.add_parser("login", help="Save a session token for authenticated requests")
    p_login.add_argument("token", help="JWT session token from lettucemeet.com cookies")

    # create
    p_create = sub.add_parser("create", help="Create a new poll event")
    p_create.add_argument("--title", required=True, help="Poll title")
    p_create.add_argument("--description", default="", help="Poll description")
    p_create.add_argument("--dates", required=True, nargs="+", help="Poll dates (YYYY-MM-DD)")
    p_create.add_argument("--start-time", default="09:00", help="Poll start time (HH:MM, default 09:00)")
    p_create.add_argument("--end-time", default="17:00", help="Poll end time (HH:MM, default 17:00)")
    p_create.add_argument("--timezone", default="Asia/Jerusalem", help="Timezone (default Asia/Jerusalem)")
    p_create.add_argument("--duration-mins", default="0", help="Max scheduled duration in minutes")

    # show
    p_show = sub.add_parser("show", help="Show event details and poll responses")
    p_show.add_argument("event_id", help="Event ID (e.g. J5R5a)")

    # respond
    p_respond = sub.add_parser("respond", help="Submit availability to an event poll")
    p_respond.add_argument("event_id", help="Event ID")
    p_respond.add_argument("--name", required=True, help="Your name")
    p_respond.add_argument("--email", required=True, help="Your email")
    p_respond.add_argument("--slots", required=True, nargs="+",
                           help="Availability slots: 'DATE START END' e.g. '2026-07-14 09:00 12:00'")

    # overlap
    p_overlap = sub.add_parser("overlap", help="Calculate optimal meeting times from poll responses")
    p_overlap.add_argument("event_id", help="Event ID")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "login":
        from lettucemeet_cli.config import save_token
        save_token(args.token)
        print("Token saved.")
        return 0

    print(f"Command '{args.command}' not yet implemented.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Create `src/lettucemeet_cli/__main__.py`**

```python
"""Allow `python -m lettucemeet_cli`."""
from lettucemeet_cli.cli import main
import sys

sys.exit(main())
```

- [ ] **Step 7: Create `tests/conftest.py`**

```python
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
```

- [ ] **Step 8: Run tests to verify scaffold**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/ -v`
Expected: no tests collected (empty) but no import errors.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: scaffold project with CLI skeleton and config module"
```

---

### Task 2: Add base URL constant and session config tests

**Files:**
- Create: `tests/test_config.py`
- Modify: `src/lettucemeet_cli/config.py`

- [ ] **Step 1: Write tests for config module**

```python
"""Tests for config module."""
import json
import os
from lettucemeet_cli import config


def test_session_path_returns_pathlib_path():
    path = config.session_path()
    assert str(path).endswith("data/session.json")


def test_load_token_from_env_var(monkeypatch):
    monkeypatch.setenv("LETTUCEMEET_TOKEN", "env-token-123")
    assert config.load_token() == "env-token-123"


def test_load_token_from_file(session_file):
    session_file.write_text(json.dumps({"session_token": "file-token-456"}))
    assert config.load_token() == "file-token-456"


def test_env_var_takes_priority_over_file(session_file, monkeypatch):
    monkeypatch.setenv("LETTUCEMEET_TOKEN", "env-token-789")
    session_file.write_text(json.dumps({"session_token": "file-token-000"}))
    assert config.load_token() == "env-token-789"


def test_load_token_returns_none_when_not_set(monkeypatch):
    monkeypatch.delenv("LETTUCEMEET_TOKEN", raising=False)
    assert config.load_token() is None


def test_save_token_writes_file(session_file):
    config.save_token("new-token")
    data = json.loads(session_file.read_text())
    assert data["session_token"] == "new-token"
```

- [ ] **Step 2: Add GRAPHQL_ENDPOINT to config.py**

```python
# --- Add at top after imports ---
GRAPHQL_ENDPOINT = "https://api.lettucemeet.com/graphql"
```

- [ ] **Step 3: Run config tests**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/test_config.py -v`
Expected: 6 tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add config module with session token and endpoint"
```

---

### Task 3: Data models

**Files:**
- Create: `src/lettucemeet_cli/models.py`
- Create: `tests/test_models.py`
- Create: `tests/fixtures/event_j5r5a.json`

- [ ] **Step 1: Write tests for models**

```python
"""Tests for data models."""
from datetime import datetime, timezone, timedelta
from lettucemeet_cli.models import (
    Availability,
    PollResponse,
    UserInfo,
    Event,
    CreateEventInput,
    CreatePollResponseInput,
)


class TestAvailability:
    def test_from_iso_strings(self):
        a = Availability.from_iso_strings(
            "2026-06-22T09:00:00.000Z", "2026-06-22T17:00:00.000Z"
        )
        assert a.start.year == 2026
        assert a.start.month == 6
        assert a.start.day == 22
        assert a.start.hour == 9
        assert a.start.tzinfo is not None

    def test_to_iso_string(self):
        a = Availability(
            start=datetime(2026, 6, 22, 9, 0, tzinfo=timezone.utc),
            end=datetime(2026, 6, 22, 17, 0, tzinfo=timezone.utc),
        )
        assert a.to_iso_strings() == ("2026-06-22T09:00:00.000Z", "2026-06-22T17:00:00.000Z")


class TestPollResponse:
    def test_from_api_data_user(self):
        data = {
            "id": "UG9sbFJlc3BvbnNlOjE=",
            "user": {"__typename": "User", "name": "Alice", "email": "alice@example.com"},
            "availabilities": [
                {"start": "2026-06-22T09:00:00.000Z", "end": "2026-06-22T12:00:00.000Z"}
            ],
        }
        r = PollResponse.from_api_data(data)
        assert r.user_name == "Alice"
        assert r.user_email == "alice@example.com"
        assert len(r.availabilities) == 1
        assert r.availabilities[0].start.hour == 9

    def test_from_api_data_anonymous(self):
        data = {
            "id": "UG9sbFJlc3BvbnNlOjI=",
            "user": {"__typename": "AnonymousUser", "name": "Bob", "email": "bob@example.com"},
            "availabilities": [],
        }
        r = PollResponse.from_api_data(data)
        assert r.user_name == "Bob"
        assert r.user_email == "bob@example.com"


class TestEvent:
    def test_from_api_data(self, event_j5r5a):
        event = Event.from_api_data(event_j5r5a)
        assert event.id == "J5R5a"
        assert event.title == "LIS1 proteomics analysis discussion"
        assert event.poll_start_time == "09:00:00.000Z"
        assert event.poll_end_time == "17:00:00.000Z"
        assert len(event.poll_dates) == 8
        assert len(event.poll_responses) >= 1
        assert event.poll_responses[0].user_name == "Alice"

    def test_poll_window_hours(self, event_j5r5a):
        event = Event.from_api_data(event_j5r5a)
        start_h, end_h = event.poll_window_hours()
        assert start_h == 9
        assert end_h == 17


class TestCreateEventInput:
    def test_to_api_variables(self):
        inp = CreateEventInput(
            title="Test Event",
            description="A test",
            poll_dates=["2026-07-14"],
            poll_start_time="09:00",
            poll_end_time="17:00",
            timezone="Asia/Jerusalem",
            poll_type=0,
        )
        vars = inp.to_api_variables()
        assert vars["title"] == "Test Event"
        assert vars["pollDates"] == ["2026-07-14"]
        assert vars["pollStartTime"] == "09:00:00Z"
        assert vars["pollEndTime"] == "17:00:00Z"
        assert vars["timeZone"] == "Asia/Jerusalem"
```

- [ ] **Step 2: Write the models module**

```python
"""Data models for LettuceMeet API entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Availability:
    """A time slot during which a respondent is available."""
    start: datetime
    end: datetime

    @classmethod
    def from_iso_strings(cls, start_str: str, end_str: str) -> "Availability":
        def _parse(s: str) -> datetime:
            s = s.replace("Z", "+00:00")
            return datetime.fromisoformat(s)
        return cls(start=_parse(start_str), end=_parse(end_str))

    def to_iso_strings(self) -> tuple[str, str]:
        def _fmt(dt: datetime) -> str:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S.") + "000Z"
        return (_fmt(self.start), _fmt(self.end))


@dataclass
class UserInfo:
    """User or anonymous respondent info embedded in a poll response."""
    name: str
    email: str
    is_anonymous: bool = True


@dataclass
class PollResponse:
    """A single respondent's availability submission."""
    id: str
    user_name: str
    user_email: str
    availabilities: list[Availability] = field(default_factory=list)

    @classmethod
    def from_api_data(cls, data: dict) -> "PollResponse":
        user = data.get("user", {})
        name = user.get("name", "Unknown")
        email = user.get("email", "")
        availabilities = [
            Availability.from_iso_strings(a["start"], a["end"])
            for a in data.get("availabilities", [])
        ]
        return cls(
            id=data["id"],
            user_name=name,
            user_email=email,
            availabilities=availabilities,
        )


@dataclass
class Event:
    """A LettuceMeet event (poll)."""
    id: str
    title: str
    description: str
    poll_start_time: str
    poll_end_time: str
    timezone: str
    poll_dates: list[str]
    is_scheduled: bool
    start: Optional[str]
    end: Optional[str]
    poll_responses: list[PollResponse] = field(default_factory=list)

    @classmethod
    def from_api_data(cls, data: dict) -> "Event":
        responses = [
            PollResponse.from_api_data(r)
            for r in data.get("pollResponses", [])
        ]
        return cls(
            id=data["id"],
            title=data.get("title", ""),
            description=data.get("description", ""),
            poll_start_time=data.get("pollStartTime", "09:00:00.000Z"),
            poll_end_time=data.get("pollEndTime", "17:00:00.000Z"),
            timezone=data.get("timeZone", "UTC"),
            poll_dates=data.get("pollDates", []),
            is_scheduled=data.get("isScheduled", False),
            start=data.get("start"),
            end=data.get("end"),
            poll_responses=responses,
        )

    def poll_window_hours(self) -> tuple[int, int]:
        """Extract start/end hours from pollStartTime/pollEndTime strings."""
        start_h = int(self.poll_start_time.split(":")[0])
        end_h = int(self.poll_end_time.split(":")[0])
        return start_h, end_h


@dataclass
class CreateEventInput:
    """Input for creating a new poll event."""
    title: str
    description: str
    poll_dates: list[str]
    poll_start_time: str
    poll_end_time: str
    timezone: str
    poll_type: int = 0
    max_scheduled_duration_mins: str = "0"

    def to_api_variables(self) -> dict:
        return {
            "input": {
                "title": self.title,
                "description": self.description,
                "pollType": self.poll_type,
                "maxScheduledDurationMins": self.max_scheduled_duration_mins,
                "pollStartTime": self.poll_start_time + ":00Z",
                "pollEndTime": self.poll_end_time + ":00Z",
                "pollDates": self.poll_dates,
                "timeZone": self.timezone,
            }
        }


@dataclass
class CreatePollResponseInput:
    """Input for submitting availability to an event."""
    event_id: str
    name: str
    email: str
    availabilities: list[Availability]
    timezone: str = "UTC"

    def to_api_variables(self) -> dict:
        return {
            "input": {
                "eventId": self.event_id,
                "name": self.name,
                "email": self.email,
                "timeZone": self.timezone,
                "availabilities": [
                    {"start": a.start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                     "end": a.end.strftime("%Y-%m-%dT%H:%M:%S.000Z")}
                    for a in self.availabilities
                ],
            }
        }
```

- [ ] **Step 3: Create fixture file from HAR data**

Create `tests/fixtures/event_j5r5a.json` with the actual event data from the HAR file (entry 28 response data).

- [ ] **Step 4: Run model tests**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/test_models.py -v`
Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add data models for Event, PollResponse, Availability, inputs"
```

---

### Task 4: GraphQL client

**Files:**
- Create: `src/lettucemeet_cli/client.py`
- Create: `tests/test_client.py`

- [ ] **Step 1: Write tests for GraphQLClient**

```python
"""Tests for GraphQL client."""
import json
import pytest
import requests_mock
from lettucemeet_cli.client import GraphQLClient, LettuceMeetError
from lettucemeet_cli.config import GRAPHQL_ENDPOINT


@pytest.fixture
def client():
    return GraphQLClient(token="test-token-123")


class TestGraphQLClient:
    def test_init_with_token(self):
        c = GraphQLClient("my-token")
        assert c.token == "my-token"

    def test_init_no_token(self):
        c = GraphQLClient()
        assert c.token is None
        assert not c.authenticated

    def test_authenticated_true_with_token(self, client):
        assert client.authenticated

    def test_headers_with_token(self, client):
        headers = client._headers()
        assert headers["Authorization"] == "Bearer test-token-123"
        assert headers["Content-Type"] == "application/json"

    def test_headers_without_token(self):
        c = GraphQLClient()
        headers = c._headers()
        assert "Authorization" not in headers

    def test_execute_success(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"data": {"event": {"id": "ABC"}}})
            result = client.execute("query { event(id: \"ABC\") { id } }")
            assert result == {"event": {"id": "ABC"}}

    def test_execute_returns_errors(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"errors": [{"message": "Not found"}]})
            with pytest.raises(LettuceMeetError, match="Not found"):
                client.execute("query { event(id: \"X\") { id } }")

    def test_execute_http_error(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, status_code=401, json={"message": "Unauthorized"})
            with pytest.raises(LettuceMeetError, match="401"):
                client.execute("query { event(id: \"X\") { id } }")

    def test_execute_sends_operation_name(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"data": {"ok": True}})
            client.execute(
                "query EventQuery($id: ID!) { event(id: $id) { id } }",
                variables={"id": "J5R5a"},
                operation_name="EventQuery",
            )
            req = m.request_history[0]
            body = json.loads(req.text)
            assert body["operationName"] == "EventQuery"
            assert body["variables"] == {"id": "J5R5a"}
```

- [ ] **Step 2: Write the client module**

```python
"""GraphQL API client for LettuceMeet."""

from __future__ import annotations

from typing import Any, Optional

import requests

from lettucemeet_cli.config import GRAPHQL_ENDPOINT, load_token


class LettuceMeetError(Exception):
    """Raised when the LettuceMeet API returns an error."""


class GraphQLClient:
    """Low-level GraphQL client for the LettuceMeet API."""

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token or load_token()
        self._session = requests.Session()

    @property
    def authenticated(self) -> bool:
        return self.token is not None

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def execute(
        self,
        query: str,
        variables: Optional[dict] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation and return the data dict."""
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        resp = self._session.post(
            GRAPHQL_ENDPOINT,
            headers=self._headers(),
            json=payload,
        )

        if resp.status_code != 200:
            raise LettuceMeetError(
                f"HTTP {resp.status_code}: {resp.text[:200]}"
            )

        body = resp.json()

        if "errors" in body:
            msgs = [e.get("message", "Unknown error") for e in body["errors"]]
            raise LettuceMeetError("; ".join(msgs))

        return body.get("data", {})
```

- [ ] **Step 3: Run client tests**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/test_client.py -v`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add GraphQL client with auth and error handling"
```

---

### Task 5: API operations layer

**Files:**
- Create: `src/lettucemeet_cli/api.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write tests for API operations**

```python
"""Tests for high-level API operations."""
import pytest
import requests_mock
from lettucemeet_cli.api import (
    get_event,
    create_event,
    create_poll_response,
)
from lettucemeet_cli.client import GraphQLClient
from lettucemeet_cli.models import CreateEventInput, CreatePollResponseInput, Availability
from lettucemeet_cli.config import GRAPHQL_ENDPOINT


@pytest.fixture
def client():
    return GraphQLClient(token="test-token")


class TestGetEvent:
    def test_returns_event_model(self, client, event_j5r5a):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"data": {"event": event_j5r5a}})
            event = get_event(client, "J5R5a")
            assert event.id == "J5R5a"
            assert event.title == "LIS1 proteomics analysis discussion"
            assert len(event.poll_responses) >= 1

    def test_sends_correct_query(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"data": {"event": {"id": "X"}}})
            get_event(client, "X")
            req = m.request_history[0]
            assert "query EventQuery" in req.text
            assert "pollResponses" in req.text


class TestCreateEvent:
    def test_returns_event_with_id(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={
                "data": {"createEvent": {"event": {"id": "NEW123", "title": "Test"}}}
            })
            inp = CreateEventInput(
                title="Test", description="",
                poll_dates=["2026-07-14"],
                poll_start_time="09:00", poll_end_time="17:00",
                timezone="Asia/Jerusalem",
            )
            result = create_event(client, inp)
            assert result["id"] == "NEW123"

    def test_sends_mutation(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={"data": {"createEvent": {"event": {"id": "X"}}}})
            inp = CreateEventInput(
                title="T", description="",
                poll_dates=["2026-07-14"],
                poll_start_time="09:00", poll_end_time="17:00",
                timezone="UTC",
            )
            create_event(client, inp)
            req = m.request_history[0]
            assert "mutation CreateEventMutation" in req.text


class TestCreatePollResponse:
    def test_returns_response(self, client):
        with requests_mock.Mocker() as m:
            m.post(GRAPHQL_ENDPOINT, json={
                "data": {"createPollResponse": {"pollResponse": {"id": "RESP1"}}}
            })
            inp = CreatePollResponseInput(
                event_id="EVT1", name="Alice", email="a@b.com",
                availabilities=[],
            )
            result = create_poll_response(client, inp)
            assert result["id"] == "RESP1"
```

- [ ] **Step 2: Write the API module**

```python
"""High-level typed API operations for LettuceMeet."""

from __future__ import annotations

from typing import Any

from lettucemeet_cli.client import GraphQLClient
from lettucemeet_cli.models import (
    CreateEventInput,
    CreatePollResponseInput,
    Event,
)

# ---- Queries ----

_EVENT_QUERY = """
query EventQuery($id: ID!) {
  event(id: $id) {
    id
    title
    description
    type
    pollStartTime
    pollEndTime
    maxScheduledDurationMins
    timeZone
    pollDates
    start
    end
    isScheduled
    createdAt
    updatedAt
    user { id }
    googleEvents { title start end }
    pollResponses {
      id
      user {
        __typename
        ... on AnonymousUser { name email }
        ... on User { id name email }
      }
      availabilities { start end }
      event { id }
    }
  }
}
"""


def get_event(client: GraphQLClient, event_id: str) -> Event:
    """Fetch an event with all poll responses."""
    data = client.execute(
        _EVENT_QUERY,
        variables={"id": event_id},
        operation_name="EventQuery",
    )
    return Event.from_api_data(data["event"])


# ---- Mutations ----

_CREATE_EVENT_MUTATION = """
mutation CreateEventMutation($input: CreateEventInput!) {
  createEvent(input: $input) {
    event {
      id
      title
      type
      description
      pollStartTime
      pollEndTime
      maxScheduledDurationMins
      timeZone
      pollDates
      isScheduled
      createdAt
      updatedAt
      user {
        events { id }
        eventsRespondedTo { id }
        id
      }
    }
  }
}
"""


def create_event(client: GraphQLClient, inp: CreateEventInput) -> dict[str, Any]:
    """Create a new poll event. Returns the created event dict."""
    data = client.execute(
        _CREATE_EVENT_MUTATION,
        variables=inp.to_api_variables(),
        operation_name="CreateEventMutation",
    )
    return data["createEvent"]["event"]


_CREATE_POLL_RESPONSE_MUTATION = """
mutation CreatePollResponseMutation($input: CreatePollResponseInput!) {
  createPollResponse(input: $input) {
    pollResponse {
      id
      user {
        __typename
        ... on AnonymousUser { name email }
        ... on User { id name email }
      }
      availabilities { start end }
      event { id }
    }
  }
}
"""


def create_poll_response(
    client: GraphQLClient, inp: CreatePollResponseInput
) -> dict[str, Any]:
    """Submit availability to an event poll. Returns the created poll response dict."""
    data = client.execute(
        _CREATE_POLL_RESPONSE_MUTATION,
        variables=inp.to_api_variables(),
        operation_name="CreatePollResponseMutation",
    )
    return data["createPollResponse"]["pollResponse"]
```

- [ ] **Step 3: Run API tests**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/test_api.py -v`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add API operations for event query, create, and poll response"
```

---

### Task 6: Overlap calculation

**Files:**
- Create: `src/lettucemeet_cli/overlap.py`
- Create: `tests/test_overlap.py`

- [ ] **Step 1: Write tests for overlap logic**

```python
"""Tests for overlap calculation."""
from datetime import datetime, timezone, timedelta
from lettucemeet_cli.models import Event, Availability, PollResponse
from lettucemeet_cli.overlap import compute_overlap_grid, format_overlap_grid


def _avail(start_day: int, start_hour: int, end_hour: int) -> Availability:
    """Helper: create an availability on June 22, 2026."""
    return Availability(
        start=datetime(2026, 6, start_day, start_hour, 0, tzinfo=timezone.utc),
        end=datetime(2026, 6, start_day, end_hour, 0, tzinfo=timezone.utc),
    )


class TestComputeOverlapGrid:
    def test_single_person_available_all_day(self):
        """One respondent available 9-17 on one date -> all hours count 1."""
        event = Event(
            id="E1", title="Test", description="",
            poll_start_time="09:00:00.000Z", poll_end_time="17:00:00.000Z",
            timezone="UTC", poll_dates=["2026-06-22"],
            is_scheduled=False, start=None, end=None,
            poll_responses=[
                PollResponse(
                    id="R1", user_name="Alice", user_email="a@b.com",
                    availabilities=[_avail(22, 9, 17)],
                ),
            ],
        )
        grid = compute_overlap_grid(event)
        # 1 day x 8 hours (9-17)
        assert len(grid) == 1  # one date
        assert grid[0]["date"] == "2026-06-22"
        assert len(grid[0]["hours"]) == 8
        # Alice available all hours -> count=1, names=["Alice"]
        for h in grid[0]["hours"]:
            assert h["count"] == 1
            assert h["available"] == ["Alice"]

    def test_two_people_partial_overlap(self):
        """Two people with different schedules on same date."""
        event = Event(
            id="E1", title="Test", description="",
            poll_start_time="09:00:00.000Z", poll_end_time="17:00:00.000Z",
            timezone="UTC", poll_dates=["2026-06-22"],
            is_scheduled=False, start=None, end=None,
            poll_responses=[
                PollResponse(
                    id="R1", user_name="Alice", user_email="a@b.com",
                    availabilities=[_avail(22, 9, 13)],  # 9-13
                ),
                PollResponse(
                    id="R2", user_name="Bob", user_email="b@b.com",
                    availabilities=[_avail(22, 12, 17)],  # 12-17
                ),
            ],
        )
        grid = compute_overlap_grid(event)
        hours = grid[0]["hours"]
        # 9:  Alice only
        assert hours[0]["count"] == 1
        assert hours[0]["available"] == ["Alice"]
        # 10: Alice only
        assert hours[1]["count"] == 1
        # 11: Alice only
        assert hours[2]["count"] == 1
        # 12: both
        assert hours[3]["count"] == 2
        assert set(hours[3]["available"]) == {"Alice", "Bob"}
        # 13: Bob only
        assert hours[4]["count"] == 1
        assert hours[4]["available"] == ["Bob"]
        # 14-16: Bob only
        for i in range(5, 8):
            assert hours[i]["count"] == 1

    def test_no_responses(self):
        """Event with no responses -> all hours count=0."""
        event = Event(
            id="E1", title="Test", description="",
            poll_start_time="09:00:00.000Z", poll_end_time="17:00:00.000Z",
            timezone="UTC", poll_dates=["2026-06-22"],
            is_scheduled=False, start=None, end=None,
            poll_responses=[],
        )
        grid = compute_overlap_grid(event)
        for h in grid[0]["hours"]:
            assert h["count"] == 0
            assert h["available"] == []

    def test_multiple_dates(self):
        """Two dates, person available only on first."""
        event = Event(
            id="E1", title="Test", description="",
            poll_start_time="09:00:00.000Z", poll_end_time="17:00:00.000Z",
            timezone="UTC",
            poll_dates=["2026-06-22", "2026-06-23"],
            is_scheduled=False, start=None, end=None,
            poll_responses=[
                PollResponse(
                    id="R1", user_name="Alice", user_email="a@b.com",
                    availabilities=[_avail(22, 9, 17)],
                ),
            ],
        )
        grid = compute_overlap_grid(event)
        assert len(grid) == 2
        assert grid[0]["date"] == "2026-06-22"
        assert grid[1]["date"] == "2026-06-23"
        # First date: all hours count=1
        assert grid[0]["hours"][0]["count"] == 1
        # Second date: all hours count=0 (no one available)
        assert grid[1]["hours"][0]["count"] == 0


class TestFormatOverlapGrid:
    def test_basic_format(self):
        grid = [
            {
                "date": "2026-06-22",
                "hours": [
                    {"hour": 9, "count": 2, "available": ["Alice", "Bob"]},
                    {"hour": 10, "count": 1, "available": ["Alice"]},
                    {"hour": 11, "count": 0, "available": []},
                ],
            },
        ]
        output = format_overlap_grid(grid)
        assert "2026-06-22" in output
        assert "09:00" in output
        assert "2" in output
        assert "Alice, Bob" in output
        assert "0" in output
```

- [ ] **Step 2: Write the overlap module**

```python
"""Overlap calculation logic for finding optimal meeting times."""

from __future__ import annotations

from typing import Any

from lettucemeet_cli.models import Event


def compute_overlap_grid(event: Event) -> list[dict[str, Any]]:
    """Compute availability overlap grid for an event.

    Returns a list per date, each containing per-hour breakdown of
    how many respondents are available and who they are.
    """
    start_hour, end_hour = event.poll_window_hours()
    total_hours = end_hour - start_hour
    result: list[dict[str, Any]] = []

    for date_str in event.poll_dates:
        hours = []
        for hour_offset in range(total_hours):
            hour = start_hour + hour_offset
            available_names: list[str] = []

            for response in event.poll_responses:
                for avail in response.availabilities:
                    # Check if this availability covers this hour on this date
                    avail_date = avail.start.strftime("%Y-%m-%d")
                    if avail_date != date_str:
                        continue
                    # Check if the hour falls within the availability window
                    slot_start = avail.start.hour
                    slot_end = avail.end.hour
                    if slot_start <= hour < slot_end:
                        available_names.append(response.user_name)
                        break  # count person once per hour

            hours.append({
                "hour": hour,
                "count": len(available_names),
                "available": available_names,
            })

        result.append({"date": date_str, "hours": hours})

    return result


def format_overlap_grid(grid: list[dict[str, Any]]) -> str:
    """Format the overlap grid as a human-readable string."""
    lines: list[str] = []
    for day in grid:
        lines.append(f"\n--- {day['date']} ---")
        lines.append(f"{'Time':>8}  {'Count':>5}  {'Available'}")
        lines.append("-" * 40)
        for h in day["hours"]:
            names = ", ".join(h["available"]) if h["available"] else "-"
            lines.append(f"{h['hour']:02d}:00  {h['count']:5d}  {names}")
    return "\n".join(lines)
```

- [ ] **Step 3: Run overlap tests**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/test_overlap.py -v`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add overlap calculation and grid formatting"
```

---

### Task 7: Wire CLI commands to API

**Files:**
- Modify: `src/lettucemeet_cli/cli.py`

- [ ] **Step 1: Write CLI integration tests**

Create `tests/test_cli.py`:

```python
"""Tests for CLI command dispatch and output."""
import json
import pytest
import requests_mock
from lettucemeet_cli.cli import main, build_parser
from lettucemeet_cli.config import GRAPHQL_ENDPOINT


def test_parser_builds():
    """Parser can be constructed without error."""
    parser = build_parser()
    assert parser is not None


def test_create_command_sends_mutation(event_j5r5a):
    """The create command sends a CreateEventMutation."""
    with requests_mock.Mocker() as m:
        m.post(GRAPHQL_ENDPOINT, json={
            "data": {"createEvent": {"event": {"id": "NEW1", "title": "My Poll"}}}
        })
        exit_code = main([
            "--token", "test-token",
            "create",
            "--title", "My Poll",
            "--dates", "2026-07-14",
            "--start-time", "09:00",
            "--end-time", "17:00",
            "--timezone", "Asia/Jerusalem",
        ])
        assert exit_code == 0
        req = m.request_history[0]
        body = json.loads(req.text)
        assert "CreateEventMutation" in body["query"]


def test_show_command_fetches_event(event_j5r5a):
    """The show command fetches and prints event details."""
    with requests_mock.Mocker() as m:
        m.post(GRAPHQL_ENDPOINT, json={"data": {"event": event_j5r5a}})
        exit_code = main(["--token", "test-token", "show", "J5R5a"])
        assert exit_code == 0
        req = m.request_history[0]
        assert "EventQuery" in req.text


def test_show_command_prints_event_info(event_j5r5a, capsys):
    """The show command prints event title and response count."""
    with requests_mock.Mocker() as m:
        m.post(GRAPHQL_ENDPOINT, json={"data": {"event": event_j5r5a}})
        main(["--token", "test-token", "show", "J5R5a"])
        captured = capsys.readouterr()
        assert "LIS1 proteomics" in captured.out
        assert "Alice" in captured.out


def test_respond_command_sends_mutation():
    """The respond command sends CreatePollResponseMutation."""
    with requests_mock.Mocker() as m:
        m.post(GRAPHQL_ENDPOINT, json={
            "data": {"createPollResponse": {"pollResponse": {"id": "RESP1"}}}
        })
        exit_code = main([
            "--token", "test-token",
            "respond", "EVT1",
            "--name", "Alice",
            "--email", "a@b.com",
            "--slots", "2026-07-14 09:00 12:00",
        ])
        assert exit_code == 0
        req = m.request_history[0]
        assert "CreatePollResponseMutation" in req.text


def test_overlap_command_computes_and_displays(event_j5r5a, capsys):
    """The overlap command fetches event and displays overlap grid."""
    with requests_mock.Mocker() as m:
        m.post(GRAPHQL_ENDPOINT, json={"data": {"event": event_j5r5a}})
        exit_code = main(["--token", "test-token", "overlap", "J5R5a"])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "2026-06-22" in captured.out
        assert "09:00" in captured.out
        assert "Alice" in captured.out


def test_login_saves_token(tmp_path, monkeypatch, capsys):
    """The login command saves token to session file."""
    from lettucemeet_cli import config
    session_path = tmp_path / "session.json"
    monkeypatch.setattr(config, "session_path", lambda: session_path)
    exit_code = main(["login", "mytoken123"])
    assert exit_code == 0
    data = json.loads(session_path.read_text())
    assert data["session_token"] == "mytoken123"
    captured = capsys.readouterr()
    assert "saved" in captured.out.lower()
```

- [ ] **Step 2: Add --token global option and implement all commands in cli.py**

Replace the existing `cli.py` with the full implementation:

```python
"""CLI entry point with argparse-based subcommand dispatch."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from lettucemeet_cli.api import get_event, create_event, create_poll_response
from lettucemeet_cli.client import GraphQLClient, LettuceMeetError
from lettucemeet_cli.config import save_token
from lettucemeet_cli.models import (
    CreateEventInput,
    CreatePollResponseInput,
    Availability,
)
from lettucemeet_cli.overlap import compute_overlap_grid, format_overlap_grid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lettucemeet",
        description="Terminal CLI for LettuceMeet - create polls, view responses, find meeting overlaps.",
    )
    parser.add_argument("--token", help="LettuceMeet API token (overrides config/env)")

    sub = parser.add_subparsers(dest="command", required=True)

    # login
    p_login = sub.add_parser("login", help="Save a session token for authenticated requests")
    p_login.add_argument("token_arg", metavar="TOKEN", help="JWT session token from lettucemeet.com cookies")

    # create
    p_create = sub.add_parser("create", help="Create a new poll event")
    p_create.add_argument("--title", required=True, help="Poll title")
    p_create.add_argument("--description", default="", help="Poll description")
    p_create.add_argument("--dates", required=True, nargs="+", help="Poll dates (YYYY-MM-DD)")
    p_create.add_argument("--start-time", default="09:00", help="Poll start time (HH:MM, default 09:00)")
    p_create.add_argument("--end-time", default="17:00", help="Poll end time (HH:MM, default 17:00)")
    p_create.add_argument("--timezone", default="Asia/Jerusalem", help="Timezone (default Asia/Jerusalem)")
    p_create.add_argument("--duration-mins", default="0", help="Max scheduled duration in minutes")

    # show
    p_show = sub.add_parser("show", help="Show event details and poll responses")
    p_show.add_argument("event_id", help="Event ID (e.g. J5R5a)")

    # respond
    p_respond = sub.add_parser("respond", help="Submit availability to an event poll")
    p_respond.add_argument("event_id", help="Event ID")
    p_respond.add_argument("--name", required=True, help="Your name")
    p_respond.add_argument("--email", required=True, help="Your email")
    p_respond.add_argument("--slots", required=True, nargs="+",
                           help="Availability slots: 'DATE START END' e.g. '2026-07-14 09:00 12:00'")
    p_respond.add_argument("--timezone", default="UTC", help="Your timezone (default UTC)")

    # overlap
    p_overlap = sub.add_parser("overlap", help="Calculate optimal meeting times from poll responses")
    p_overlap.add_argument("event_id", help="Event ID")

    return parser


def _parse_slots(slot_args: list[str]) -> list[Availability]:
    """Parse --slots arguments into Availability objects.

    Each slot is 'DATE START END', e.g. '2026-07-14 09:00 12:00'.
    Times are in 24h HH:MM format.
    """
    availabilities: list[Availability] = []
    for i in range(0, len(slot_args), 3):
        date_str = slot_args[i]
        start_time = slot_args[i + 1]
        end_time = slot_args[i + 2]

        from datetime import datetime, timezone
        start_dt = datetime.fromisoformat(f"{date_str}T{start_time}:00+00:00")
        end_dt = datetime.fromisoformat(f"{date_str}T{end_time}:00+00:00")
        availabilities.append(Availability(start=start_dt, end=end_dt))

    return availabilities


def _show_event(event_id: str, client: GraphQLClient) -> None:
    """Fetch and display an event's details and poll responses."""
    event = get_event(client, event_id)
    print(f"Event: {event.title}")
    print(f"ID:    {event.id}")
    print(f"Desc:  {event.description}")
    print(f"Dates: {', '.join(event.poll_dates)}")
    print(f"Hours: {event.poll_start_time[:5]} - {event.poll_end_time[:5]}")
    print(f"TZ:    {event.timezone}")
    print(f"Scheduled: {event.is_scheduled}")
    if event.start:
        print(f"Time:  {event.start} - {event.end}")
    print(f"\nResponses ({len(event.poll_responses)}):")
    for r in event.poll_responses:
        print(f"  - {r.user_name} ({r.user_email})")
        for a in r.availabilities:
            print(f"      {a.start.strftime('%Y-%m-%d %H:%M')} - {a.end.strftime('%H:%M')}")
    print()


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Login command uses the positional token_arg, not the --token option
    if args.command == "login":
        save_token(args.token_arg)
        print("Token saved.")
        return 0

    # All other commands need a GraphQL client
    client = GraphQLClient(token=args.token)

    try:
        if args.command == "create":
            inp = CreateEventInput(
                title=args.title,
                description=args.description,
                poll_dates=list(args.dates),
                poll_start_time=args.start_time,
                poll_end_time=args.end_time,
                timezone=args.timezone,
                max_scheduled_duration_mins=args.duration_mins,
            )
            result = create_event(client, inp)
            print(f"Event created! ID: {result['id']}")
            print(f"Title: {result.get('title', '')}")

        elif args.command == "show":
            _show_event(args.event_id, client)

        elif args.command == "respond":
            availabilities = _parse_slots(args.slots)
            inp = CreatePollResponseInput(
                event_id=args.event_id,
                name=args.name,
                email=args.email,
                availabilities=availabilities,
                timezone=args.timezone,
            )
            result = create_poll_response(client, inp)
            print(f"Response submitted! ID: {result['id']}")

        elif args.command == "overlap":
            event = get_event(client, args.event_id)
            grid = compute_overlap_grid(event)
            print(format_overlap_grid(grid))

    except LettuceMeetError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Run all tests**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: wire CLI commands to API operations with --token option"
```

---

### Task 8: Update main.py wrapper and README

**Files:**
- Modify: `main.py`
- Modify: `README.md`

- [ ] **Step 1: Replace main.py**

```python
#!/usr/bin/env python3
"""LettuceMeet CLI - terminal automation for LettuceMeet meeting polls.

Usage:
    uv run python main.py --help
    uv run python main.py login <token>
    uv run python main.py create --title "My Poll" --dates 2026-07-14
    uv run python main.py show J5R5a
    uv run python main.py respond J5R5a --name Alice --email a@b.com --slots "2026-07-14 09:00 12:00"
    uv run python main.py overlap J5R5a
"""

import sys
from lettucemeet_cli.cli import main

sys.exit(main())
```

- [ ] **Step 2: Replace README.md**

```markdown
# LettuceMeet CLI

Terminal automation for [LettuceMeet](https://lettucemeet.com) - create polls, view responses, and find optimal meeting overlaps, all from the command line.

## Setup

```bash
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

## Authentication

Get your session token from lettucemeet.com cookies and save it:

```bash
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."
```

Or set the `LETTUCEMEET_TOKEN` environment variable.

## Usage

### Create a poll

```bash
uv run python main.py create \
  --title "Team standup" \
  --dates 2026-07-20 2026-07-21 2026-07-22 \
  --start-time 09:00 \
  --end-time 17:00 \
  --timezone Asia/Jerusalem
```

### View event details and responses

```bash
uv run python main.py show J5R5a
```

### Submit availability

```bash
uv run python main.py respond J5R5a \
  --name "Alice" \
  --email "alice@example.com" \
  --slots "2026-07-20 09:00 12:00" "2026-07-21 14:00 17:00"
```

### Find optimal meeting times

```bash
uv run python main.py overlap J5R5a
```

## Project Structure

```
src/         Python package
tests/       Test suite
docs/        Documentation and HAR archive
data/        Local session storage (gitignored)
```

## Development

```bash
uv run pytest          # Run tests
uv run ruff check .    # Lint
uv run mypy src/       # Type check
```
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "docs: update main.py wrapper and README with usage examples"
```

---

### Task 9: End-to-end verification with real API

- [ ] **Step 1: Run the full test suite**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run pytest tests/ -v`
Expected: All tests green.

- [ ] **Step 2: Verify CLI help works**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run python main.py --help`
Expected: Shows usage with all subcommands.

- [ ] **Step 3: Verify no import errors or type issues**

Run: `cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI && uv run python -c "from lettucemeet_cli.cli import main; print('OK')"`
Expected: Prints "OK".

- [ ] **Step 4: Update progress.md**

Append completion summary to `.memory/progress.md`.

- [ ] **Step 5: Final commit (if needed)**

```bash
git add -A
git commit -m "chore: finalize LettuceMeet CLI implementation"
```
