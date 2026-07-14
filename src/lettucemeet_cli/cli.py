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

    Each slot is a single string 'DATE START END', e.g. '2026-07-14 09:00 12:00'.
    Times are in 24h HH:MM format.
    """
    availabilities: list[Availability] = []
    for slot in slot_args:
        parts = slot.split()
        if len(parts) == 3:
            date_str, start_time, end_time = parts

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
