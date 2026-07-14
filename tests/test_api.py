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
            assert event.title == "Team sync"
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
