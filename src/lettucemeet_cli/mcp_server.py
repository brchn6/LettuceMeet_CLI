#!/usr/bin/env python3
"""MCP (Model Context Protocol) server for LettuceMeet.

An unofficial MCP tool that exposes LettuceMeet poll management as callable
tools for AI agents. Communicates via JSON-RPC 2.0 over stdio.

Protocol: https://modelcontextprotocol.io
"""

from __future__ import annotations

import json
import sys
import traceback
from typing import Any

# Import the CLI internals
from lettucemeet_cli.client import GraphQLClient, LettuceMeetError
from lettucemeet_cli.api import get_event, create_event, create_poll_response
from lettucemeet_cli.models import (
    CreateEventInput,
    CreatePollResponseInput,
    Availability,
)
from lettucemeet_cli.overlap import compute_overlap_grid, format_overlap_grid
from lettucemeet_cli.config import load_token


# --- MCP Protocol helpers ---

def jsonrpc_error(id: Any, code: int, message: str, data: Any = None) -> dict:
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": id, "error": err}


def jsonrpc_result(id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": id, "result": result}


def jsonrpc_notification(method: str, params: dict | None = None) -> dict:
    msg: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    return msg


# --- Tool definitions ---

TOOLS = [
    {
        "name": "create_poll",
        "description": "Create a new LettuceMeet poll event",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Poll title"},
                "description": {"type": "string", "description": "Poll description"},
                "dates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Poll dates in YYYY-MM-DD format",
                },
                "start_time": {
                    "type": "string",
                    "description": "Poll start time HH:MM (default 09:00)",
                    "default": "09:00",
                },
                "end_time": {
                    "type": "string",
                    "description": "Poll end time HH:MM (default 17:00)",
                    "default": "17:00",
                },
                "timezone": {
                    "type": "string",
                    "description": "Timezone (default Asia/Jerusalem)",
                    "default": "Asia/Jerusalem",
                },
            },
            "required": ["title", "dates"],
        },
    },
    {
        "name": "show_event",
        "description": "Get event details and all poll responses",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID (e.g. J5R5a)"},
            },
            "required": ["event_id"],
        },
    },
    {
        "name": "respond_to_poll",
        "description": "Submit availability to an event poll (as anonymous user)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID"},
                "name": {"type": "string", "description": "Your name"},
                "email": {"type": "string", "description": "Your email"},
                "slots": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Availability slots as 'DATE START END' e.g. '2026-07-20 09:00 12:00'",
                },
            },
            "required": ["event_id", "name", "email", "slots"],
        },
    },
    {
        "name": "compute_overlap",
        "description": "Calculate optimal meeting times from poll responses",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID"},
            },
            "required": ["event_id"],
        },
    },
]

# --- Tool implementations ---


def _create_client(token: str | None = None) -> GraphQLClient:
    t = token or load_token()
    if not t:
        raise LettuceMeetError(
            "No token available. Use login tool first or set LETTUCEMEET_TOKEN env var."
        )
    return GraphQLClient(token=t)


def tool_create_poll(args: dict) -> str:
    client = _create_client(args.get("_token"))
    inp = CreateEventInput(
        title=args["title"],
        description=args.get("description", ""),
        poll_dates=list(args["dates"]),
        poll_start_time=args.get("start_time", "09:00"),
        poll_end_time=args.get("end_time", "17:00"),
        timezone=args.get("timezone", "Asia/Jerusalem"),
    )
    result = create_event(client, inp)
    event_id = result["id"]
    return (
        f"Event created!\n"
        f"ID:    {event_id}\n"
        f"Title: {result.get('title', '')}\n"
        f"Link:  https://lettucemeet.com/l/{event_id}"
    )


def tool_show_event(args: dict) -> str:
    client = _create_client(args.get("_token"))
    event = get_event(client, args["event_id"])
    lines = [
        f"Event: {event.title}",
        f"ID:    {event.id}",
        f"Desc:  {event.description}",
        f"Dates: {', '.join(event.poll_dates)}",
        f"Hours: {event.poll_start_time[:5]} - {event.poll_end_time[:5]}",
        f"TZ:    {event.timezone}",
        f"",
        f"Responses ({len(event.poll_responses)}):",
    ]
    for r in event.poll_responses:
        lines.append(f"  - {r.user_name} ({r.user_email})")
        for a in r.availabilities:
            lines.append(
                f"      {a.start.strftime('%Y-%m-%d %H:%M')} - {a.end.strftime('%H:%M')}"
            )
    return "\n".join(lines)


def tool_respond_to_poll(args: dict) -> str:
    client = _create_client(args.get("_token"))
    availabilities: list[Availability] = []
    for slot_str in args["slots"]:
        parts = slot_str.split()
        if len(parts) == 3:
            date_str, start_time, end_time = parts
            from datetime import datetime, timezone
            start_dt = datetime.fromisoformat(f"{date_str}T{start_time}:00+00:00")
            end_dt = datetime.fromisoformat(f"{date_str}T{end_time}:00+00:00")
            availabilities.append(Availability(start=start_dt, end=end_dt))
    inp = CreatePollResponseInput(
        event_id=args["event_id"],
        name=args["name"],
        email=args["email"],
        availabilities=availabilities,
        timezone=args.get("timezone", "UTC"),
    )
    result = create_poll_response(client, inp)
    return f"Response submitted! ID: {result['id']}"


def tool_compute_overlap(args: dict) -> str:
    client = _create_client(args.get("_token"))
    event = get_event(client, args["event_id"])
    grid = compute_overlap_grid(event)
    return format_overlap_grid(grid)


TOOL_DISPATCH = {
    "create_poll": tool_create_poll,
    "show_event": tool_show_event,
    "respond_to_poll": tool_respond_to_poll,
    "compute_overlap": tool_compute_overlap,
}

# --- MCP Server ---


def handle_request(request: dict) -> dict | None:
    req_id = request.get("id")
    method = request.get("method", "")
    params = request.get("params", {}) or {}

    if method == "initialize":
        return jsonrpc_result(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "lettucemeet-mcp",
                "version": "0.1.0",
            },
        })

    elif method == "notifications/initialized":
        return None  # No response needed

    elif method == "tools/list":
        return jsonrpc_result(req_id, {"tools": TOOLS})

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name not in TOOL_DISPATCH:
            return jsonrpc_error(
                req_id, -32601, f"Unknown tool: {tool_name}"
            )

        try:
            result = TOOL_DISPATCH[tool_name](arguments)
            return jsonrpc_result(req_id, {
                "content": [{"type": "text", "text": result}],
            })
        except LettuceMeetError as e:
            return jsonrpc_error(req_id, -32000, str(e))
        except Exception as e:
            return jsonrpc_error(
                req_id, -32603, f"Internal error: {e}",
                data={"traceback": traceback.format_exc()},
            )

    else:
        return jsonrpc_error(req_id, -32601, f"Method not found: {method}")


def main() -> None:
    """Run the MCP server over stdio."""
    # Send startup notification
    sys.stderr.write("LettuceMeet MCP server starting...\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"Invalid JSON: {e}\n")
            sys.stderr.flush()
            continue

        try:
            response = handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling request: {e}\n")
            traceback.print_exc(file=sys.stderr)
            sys.stderr.flush()
            if request.get("id") is not None:
                err_resp = jsonrpc_error(
                    request["id"], -32603, f"Unhandled error: {e}"
                )
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    main()
