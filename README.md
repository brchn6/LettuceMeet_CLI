# LettuceMeet CLI

Terminal automation for [LettuceMeet](https://lettucemeet.com) -- create polls,
view responses, and find optimal meeting overlaps, all from the command line.
Designed for humans **and** AI agents (Pi, Claude Code, Codex, etc.).

## Quick Start

```bash
# Install
uv sync

# Save your session token (one-time, from browser)
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."

# Create a poll
uv run python main.py create --title "Standup" --dates 2026-07-20 2026-07-21
```

One command per task. See full reference below.

---

## Install as an AI Agent Skill

This project includes a skill file that teaches AI agents how to use the CLI
automatically. Agents discover it when you ask about scheduling or polls.

```bash
# Install for your agent (Pi, Claude Code, Codex, etc.)
bash scripts/install-skill.sh

# Or symlink to stay updated with git pulls
bash scripts/install-skill.sh --link

# Remove it later
bash scripts/install-skill.sh --uninstall
```

The skill lives at `.agents/skills/lettucemeet-cli/SKILL.md` and installs to
`~/.agents/skills/lettucemeet-cli/`.

---

## Token Setup (one-time, user does this)

The agent cannot access your browser. You extract the token once.

**Easiest -- DevTools Console:**

```javascript
copy(localStorage.getItem('akoko:session_token'))
```

Paste that on lettucemeet.com (logged in) > DevTools Console. Send the copied
token to the agent, who runs `login <token>`.

**Or bookmarklet** -- create a bookmark with this URL for one-click copying:

```
javascript:(function(){let t=localStorage.getItem('akoko:session_token');if(t){navigator.clipboard.writeText(t).then(()=>{alert('Token copied!')}).catch(()=>{prompt('Copy:',t)})}else{alert('Not found - on lettucemeet.com?')}})();
```

**Or manual** -- DevTools > Application > Local Storage > `https://lettucemeet.com` >
key `akoko:session_token`.

**Or env var** (no saved file):

```bash
export LETTUCEMEET_TOKEN="eyJhbGciOiJIUzI1NiIs..."
```

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

Output: `Event created! ID: KZaEn` -- share `https://lettucemeet.com/l/KZaEn`.

### View event and responses

```bash
uv run python main.py show KZaEn
```

### Submit availability

```bash
uv run python main.py respond KZaEn \
  --name "Alice" --email "alice@example.com" \
  --slots "2026-07-20 09:00 12:00" "2026-07-21 14:00 17:00"
```

### Find optimal meeting times

```bash
uv run python main.py overlap KZaEn
```

```
--- 2026-07-20 ---
    Time  Count  Available
09:00      2  Alice, Bob
10:00      2  Alice, Bob
11:00      1  Bob
```

### Save token

```bash
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."
```

---

## Project Structure

```
.agents/skills/lettucemeet-cli/   # Agent skill (installable)
src/lettucemeet_cli/              # Python package
tests/                            # 39 tests
docs/                             # Architecture, HAR archive
data/                             # Local session (gitignored)
scripts/install-skill.sh          # Skill installer
```

## How It Works

This uses LettuceMeet's **internal GraphQL API** (`api.lettucemeet.com/graphql`),
reverse-engineered from a browser HAR capture. No public API exists.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full breakdown.

## Development

```bash
uv run pytest          # 39 tests
uv run ruff check .    # Lint
uv run mypy src/       # Type check
```
