"""Overlap calculation logic for finding optimal meeting times."""

from __future__ import annotations

from typing import Any

from lettucemeet_cli.models import Event


def compute_overlap_grid(event: Event) -> list[dict[str, Any]]:
    """Compute availability overlap grid for an event.

    Returns a list per date, each containing per-hour breakdown of
    how many respondents are available and who they are.
    """
    start_hour, end_hour = event.poll_window_hours()
    total_hours = end_hour - start_hour
    result: list[dict[str, Any]] = []

    for date_str in event.poll_dates:
        hours = []
        for hour_offset in range(total_hours):
            hour = start_hour + hour_offset
            available_names: list[str] = []

            for response in event.poll_responses:
                for avail in response.availabilities:
                    # Check if this availability covers this hour on this date
                    avail_date = avail.start.strftime("%Y-%m-%d")
                    if avail_date != date_str:
                        continue
                    # Check if the hour falls within the availability window
                    slot_start = avail.start.hour
                    slot_end = avail.end.hour
                    if slot_start <= hour < slot_end:
                        available_names.append(response.user_name)
                        break  # count person once per hour

            hours.append({
                "hour": hour,
                "count": len(available_names),
                "available": available_names,
            })

        result.append({"date": date_str, "hours": hours})

    return result


def format_overlap_grid(grid: list[dict[str, Any]]) -> str:
    """Format the overlap grid as a human-readable string."""
    lines: list[str] = []
    for day in grid:
        lines.append(f"\n--- {day['date']} ---")
        lines.append(f"{'Time':>8}  {'Count':>5}  {'Available'}")
        lines.append("-" * 40)
        for h in day["hours"]:
            names = ", ".join(h["available"]) if h["available"] else "-"
            lines.append(f"{h['hour']:02d}:00  {h['count']:5d}  {names}")
    return "\n".join(lines)
