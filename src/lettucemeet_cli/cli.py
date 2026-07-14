"""CLI entry point with argparse-based subcommand dispatch."""

import argparse
import sys
from typing import Optional


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

    # overlap
    p_overlap = sub.add_parser("overlap", help="Calculate optimal meeting times from poll responses")
    p_overlap.add_argument("event_id", help="Event ID")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "login":
        from lettucemeet_cli.config import save_token
        save_token(args.token_arg)
        print("Token saved.")
        return 0

    print(f"Command '{args.command}' not yet implemented.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
