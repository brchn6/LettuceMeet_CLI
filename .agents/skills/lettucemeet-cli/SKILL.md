---
name: lettucemeet-cli
description: Use when the user wants to create a meeting poll, check availability, find optimal meeting times, or automate LettuceMeet scheduling via CLI
---

# LettuceMeet CLI

Terminal automation for [LettuceMeet](https://lettucemeet.com) -- create polls,
view responses, and find optimal meeting overlaps. Uses the website's internal
GraphQL API (no public API exists).

## Prerequisites

- Python 3.11+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- A LettuceMeet account (free at https://lettucemeet.com)

## Quick Install

```bash
# Clone the project
git clone <repo-url> lettucemeet-cli
cd lettucemeet-cli

# Install dependencies
uv sync

# Install the agent skill (for AI agent integration)
bash scripts/install-skill.sh

# Save your session token (one-time setup)
# Get it from browser DevTools > Console:
#   copy(localStorage.getItem('akoko:session_token'))
uv run python main.py login "<your-token>"
```

## Available Commands

Run all commands from the project root via `uv run`:

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

Output: `Event created! ID: KZaEn` -- share link `https://lettucemeet.com/l/KZaEn`.

### Show event with responses

```bash
uv run python main.py show J5R5a
```

Shows title, dates, hours, and every respondent's availability.

### Submit your availability (anonymous)

```bash
uv run python main.py respond KZaEn \
  --name "Alice" \
  --email "alice@example.com" \
  --slots "2026-07-20 09:00 12:00" "2026-07-21 14:00 17:00"
```

### Compute best meeting times

```bash
uv run python main.py overlap KZaEn
```

Prints a per-date, per-hour grid:

```
--- 2026-07-20 ---
    Time  Count  Available
09:00      2  Alice, Bob
10:00      2  Alice, Bob
11:00      1  Bob
```

### Delete an event

```bash
uv run python main.py delete KZaEn
```

### Save session token

```bash
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."
```

## Token Setup (user must do this once)

The agent cannot access your browser's localStorage remotely. You must extract
the token once and give it to the agent.

**Easiest way -- DevTools Console:**

```javascript
copy(localStorage.getItem('akoko:session_token'))
```

Paste that in DevTools Console on lettucemeet.com (logged in), then paste the
copied token to the agent.

**Alternative -- Bookmarklet:**

Create a bookmark with this URL for one-click token copying:

```
javascript:(function(){let t=localStorage.getItem('akoko:session_token');if(t){navigator.clipboard.writeText(t).then(()=>{alert('Token copied!')}).catch(()=>{prompt('Copy:',t)})}else{alert('Not found - on lettucemeet.com?')}})();
```

**Alternative -- Manual:**

DevTools > Application > Local Storage > `https://lettucemeet.com` >
key `akoko:session_token` > copy value.

**Token env var (no file needed):**

```bash
export LETTUCEMEET_TOKEN="eyJhbGciOiJIUzI1NiIs..."
```

## Architecture

```
User/Agent -> CLI (argparse) -> GraphQLClient (requests) -> api.lettucemeet.com/graphql
```

- **No public API** -- Reverse-engineered from a browser HAR capture
- **GraphQL endpoint**: `POST https://api.lettucemeet.com/graphql`
- **Auth**: JWT bearer token in `Authorization` header
- **Token chain**: `--token` flag > `LETTUCEMEET_TOKEN` env var > `data/session.json`

All queries and mutations (EventQuery, CreateEventMutation, etc.) are in
`src/lettucemeet_cli/api.py`. Full architecture at `docs/ARCHITECTURE.md`.

## Project Structure

```
src/lettucemeet_cli/     # Python package
  cli.py                 # CLI dispatch (argparse, 5 subcommands)
  client.py              # GraphQL HTTP client + JWT auth
  api.py                 # Typed API operations (get, create, respond)
  models.py              # Dataclasses: Event, PollResponse, Availability
  overlap.py             # Overlap grid computation
  config.py              # Token/session management
tests/                   # 39 tests (uv run pytest)
data/session.json        # Saved token (gitignored)
docs/                    # Architecture docs, HAR archive
.agents/skills/          # Agent skill for AI integration
scripts/install-skill.sh # Install skill to ~/.agents/skills/
```

## Installing the Skill for Your Agent

The skill file at `.agents/skills/lettucemeet-cli/SKILL.md` teaches AI agents
(Pi, Claude Code, Codex, etc.) how to use this CLI.

To install it for your agent:

```bash
# Option A: Use the install script
bash scripts/install-skill.sh

# Option B: Manual symlink
ln -sf "$(pwd)/.agents/skills/lettucemeet-cli" ~/.agents/skills/lettucemeet-cli

# Option C: Just copy
cp -r .agents/skills/lettucemeet-cli ~/.agents/skills/lettucemeet-cli
```

Once installed, agents will discover the skill automatically when you ask about
meeting scheduling, poll creation, or availability overlap.

## How the Agent Uses This

When you tell an agent "create a meeting poll for next week" or "find when
everyone is free", the agent:

1. Reads the `lettucemeet-cli` skill (auto-discovered)
2. Checks `data/session.json` for an existing token
3. If no token, asks you for one (via DevTools console one-liner)
4. Runs the appropriate CLI command via `uv run python main.py ...`
5. Returns the output to you

The skill file documents the exact commands, flags, and token flow so any
agent can use it without additional instruction.

## Development

```bash
uv run pytest          # 39 tests
uv run ruff check .    # Lint
uv run mypy src/       # Type check
```
