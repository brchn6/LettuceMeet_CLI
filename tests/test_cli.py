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
        assert "Team sync" in captured.out
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


def test_delete_command_sends_mutation():
    """The delete command sends DeleteEventMutation."""
    with requests_mock.Mocker() as m:
        m.post(GRAPHQL_ENDPOINT, json={
            "data": {"deleteEvent": {"message": "Event Deleted Successfully"}}
        })
        exit_code = main(["--token", "test-token", "delete", "EVT1"])
        assert exit_code == 0
        req = m.request_history[0]
        assert "DeleteEventMutation" in req.text
