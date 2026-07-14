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
