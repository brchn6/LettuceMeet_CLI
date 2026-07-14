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
        assert event.poll_responses[0].user_name == "BarCohen"

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
