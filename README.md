# LettuceMeet CLI

Terminal automation for [LettuceMeet](https://lettucemeet.com) -- create polls,
view responses, and find optimal meeting overlaps, all from the command line.
Designed to be used directly by humans **and** by AI agents (Pi, Claude Code,
etc.) for autonomous scheduling.

## Quick Start (for the Agent to Work)

You do **one thing**: give the agent a fresh session token from your browser.
That is it. The agent handles the rest.

```bash
# Step 1: Install dependencies (one-time)
uv sync

# Step 2: Give the agent your token (after browser login)
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."
```

### Where to find the token

1. Open [lettucemeet.com](https://lettucemeet.com) and log in
2. Open DevTools (F12)
3. **Chrome:** Application tab > Local Storage > `https://lettucemeet.com` > key `akoko:session_token`
   **Firefox:** Storage tab > Local Storage > `https://lettucemeet.com` > key `akoko:session_token`
4. Copy the token value (long JWT string starting with `eyJ...`)
5. Run the `login` command above

That is the **only manual step**. Now the agent can create polls, fetch
responses, and compute overlaps on your behalf.

### If the token expires

The JWT token expires after some time. When commands start failing with auth
errors, just repeat the steps above and run `login` with a fresh token.

### Alternative: environment variable

If you prefer not to save the token to disk, set it as an env var:

```bash
export LETTUCEMEET_TOKEN="eyJhbGciOiJIUzI1NiIs..."
```

This takes priority over the saved file and lasts for the shell session.

---

## Usage

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

Output: `Event created! ID: KZaEn` -- share the link
`https://lettucemeet.com/l/KZaEn` with participants.

### View event details and responses

```bash
uv run python main.py show KZaEn
```

Shows title, description, dates, time range, and every respondent's name, email,
and availability slots.

### Submit availability

```bash
uv run python main.py respond KZaEn \
  --name "Alice" \
  --email "alice@example.com" \
  --slots "2026-07-20 09:00 12:00" "2026-07-21 14:00 17:00"
```

Each `--slots` argument is a quoted string with three parts: `DATE START END`.

### Find optimal meeting times

```bash
uv run python main.py overlap KZaEn
```

Prints a per-date, per-hour grid showing how many people are available at each
time slot and who they are.

```
--- 2026-07-20 ---
    Time  Count  Available
----------------------------------------
09:00      1  Alice
10:00      2  Alice, Bob
11:00      2  Alice, Bob
12:00      1  Bob
```

---

## Setup (one-time)

```bash
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

---

## How It Works

This is **not** using a public API. LettuceMeet does not issue API tokens.
Instead, the CLI uses the website's **internal GraphQL endpoint**
(`https://api.lettucemeet.com/graphql`), reverse-engineered from a browser
HAR capture.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full breakdown:
how the API was discovered, how the agent runs the CLI, the data flow, and
limitations.

---

## Project Structure

```
src/         Python package (lettucemeet_cli)
tests/       Test suite (39 tests)
docs/        Architecture docs and HAR archive
data/        Local session storage (gitignored, created by login)
```

## Development

```bash
uv run pytest          # Run all 39 tests
uv run ruff check .    # Lint
uv run mypy src/       # Type check
```
