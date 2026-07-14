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


def test_load_token_returns_none_when_not_set(session_file, monkeypatch):
    monkeypatch.delenv("LETTUCEMEET_TOKEN", raising=False)
    assert config.load_token() is None


def test_save_token_writes_file(session_file):
    config.save_token("new-token")
    data = json.loads(session_file.read_text())
    assert data["session_token"] == "new-token"
