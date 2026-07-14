# LettuceMeet CLI

Terminal automation for [LettuceMeet](https://lettucemeet.com) - create polls, view responses, and find optimal meeting overlaps, all from the command line.

## Setup

```bash
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

## Authentication

Get your session token from lettucemeet.com cookies and save it:

```bash
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."
```

Or set the `LETTUCEMEET_TOKEN` environment variable.

## Usage

### Create a poll

```bash
uv run python main.py create \
  --title "Team standup" \
  --dates 2026-07-20 2026-07-21 2026-07-22 \
  --start-time 09:00 \
  --end-time 17:00 \
  --timezone Asia/Jerusalem
```

### View event details and responses

```bash
uv run python main.py show J5R5a
```

### Submit availability

```bash
uv run python main.py respond J5R5a \
  --name "Alice" \
  --email "alice@example.com" \
  --slots "2026-07-20 09:00 12:00" "2026-07-21 14:00 17:00"
```

### Find optimal meeting times

```bash
uv run python main.py overlap J5R5a
```

## Project Structure

```
src/         Python package
tests/       Test suite
docs/        Documentation and HAR archive
data/        Local session storage (gitignored)
```

## Development

```bash
uv run pytest          # Run tests
uv run ruff check .    # Lint
uv run mypy src/       # Type check
```
