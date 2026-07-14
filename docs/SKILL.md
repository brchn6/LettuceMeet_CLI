---
name: lettucemeet-cli
description: Use when the user wants to create a meeting poll, check availability, find optimal meeting times, or automate LettuceMeet scheduling via CLI
---

# LettuceMeet CLI

Terminal automation for [LettuceMeet](https://lettucemeet.com) -- create polls,
view responses, and find optimal meeting overlaps. Uses the website's internal
GraphQL API (no public API exists).

## Setup (one-time)

The project lives at `/home/labs/pilpel/barc/dev/LettuceMeet_CLI/`.
Dependencies are already installed.

### Token: the only manual step

The agent needs a JWT session token from the user's browser localStorage.
The user provides it once and the agent saves it.

**Tell the user to do this:**

```
1. Open lettucemeet.com and log in
2. Open DevTools (F12) > Console tab
3. Paste: copy(localStorage.getItem('akoko:session_token'))
4. Send the token to the agent
```

**Agent saves it:**

```bash
cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI
uv run python main.py login "<token>"
```

The token is stored in `data/session.json` and picked up automatically.
Alternatively, the user can set `LETTUCEMEET_TOKEN` env var.

## Available Commands

Run everything via `uv run` in the project root:

```bash
cd /home/labs/pilpel/barc/dev/LettuceMeet_CLI
```

### Create a poll

```bash
uv run python main.py create \
  --title "Team standup" \
  --description "Weekly sync" \
  --dates 2026-07-20 2026-07-21 2026-07-22 \
  --start-time 09:00 \
  --end-time 17:00 \
  --timezone Asia/Jerusalem
```

Output: `Event created! ID: KZaEn` -- share `https://lettucemeet.com/l/KZaEn`.

### Show event + responses

```bash
uv run python main.py show J5R5a
```

Shows title, dates, hours, and every respondent's availability.

### Submit availability (anonymous)

```bash
uv run python main.py respond KZaEn \
  --name "Alice" \
  --email "alice@example.com" \
  --slots "2026-07-20 09:00 12:00" "2026-07-21 14:00 17:00"
```

### Compute overlap grid

```bash
uv run python main.py overlap KZaEn
```

Prints per-date, per-hour availability counts.

```
--- 2026-07-20 ---
    Time  Count  Available
09:00      2  Alice, Bob
10:00      2  Alice, Bob
11:00      1  Bob
```

### Login / save token

```bash
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."
```

## How It Works

- Uses `POST https://api.lettucemeet.com/graphql` with JWT bearer auth
- GraphQL operations were reverse-engineered from a HAR capture
- All queries/mutations are in `src/lettucemeet_cli/api.py`
- Token resolution chain: `--token` flag > env var > `data/session.json`
- Full architecture docs at `docs/ARCHITECTURE.md`

## Project Layout

```
src/lettucemeet_cli/     # Python package
  cli.py                 # CLI entry point, arg parsing, dispatch
  client.py              # GraphQL HTTP client + auth
  api.py                 # Typed API functions (create, get, respond)
  models.py              # Dataclasses: Event, PollResponse, Availability
  overlap.py             # Overlap grid computation
  config.py              # Token loading, session path, endpoint
tests/                   # 39 tests (use pytest)
data/session.json        # Saved token (gitignored)
docs/                    # Architecture docs, HAR archive
main.py                  # Entry: uv run python main.py
```

## Common Mistakes

- **Token expired**: Commands fail with auth errors. Ask user for a fresh token.
- **Wrong dates format**: Use YYYY-MM-DD (e.g., 2026-07-20).
- **Wrong time format**: Use HH:MM in 24h (e.g., 09:00, 14:00).
- **Slots format**: Each slot is a quoted string "DATE START END".
- **No token**: Commands that need auth (create, show, respond, overlap) fail
  without one. `--token` flag overrides everything.
