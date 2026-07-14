"""Configuration and session storage management."""

import json
import os
from pathlib import Path
from typing import Optional


GRAPHQL_ENDPOINT = "https://api.lettucemeet.com/graphql"


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
