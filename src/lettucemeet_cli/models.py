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
            "title": self.title,
            "description": self.description,
            "pollType": self.poll_type,
            "maxScheduledDurationMins": self.max_scheduled_duration_mins,
            "pollStartTime": self.poll_start_time + ":00Z",
            "pollEndTime": self.poll_end_time + ":00Z",
            "pollDates": self.poll_dates,
            "timeZone": self.timezone,
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
