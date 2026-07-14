# LettuceMeet MCP (unofficial)

**MCP tools for LettuceMeet** -- create polls, view responses, find optimal
meeting times. Works as a CLI, an installable AI agent skill, and an MCP server.

[LettuceMeet](https://lettucemeet.com) is a meeting scheduler (like
When2Meet/Doodle). This project provides an unofficial API client using the
website's internal GraphQL endpoint.

---

## Quick Start

```bash
# Install
uv sync

# Save your session token (one-time, from browser)
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."

# Create a poll
uv run python main.py create --title "Standup" --dates 2026-07-20 2026-07-21
```

---

## Four Ways to Use

### 1. CLI (direct terminal)

```bash
uv run python main.py show KZaEn
uv run python main.py overlap KZaEn
uv run python main.py respond KZaEn --name "Alice" --email "a@b.com" --slots "2026-07-20 09:00 12:00"
```

### 2. MCP Server (agent calls tools directly)

Add to any MCP-compatible agent (Pi, Claude Code, Codex, etc.):

```json
{
  "mcpServers": {
    "lettucemeet": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/lettucemeet-cli", "python", "src/lettucemeet_cli/mcp_server.py"]
    }
  }
}
```

The server exposes 4 tools: `create_poll`, `show_event`, `respond_to_poll`, `compute_overlap`.
See [`docs/MCP.md`](docs/MCP.md) for details.

### 3. Agent Skill (agent reads docs and runs CLI)

Install so any agent auto-discovers it:

```bash
bash scripts/install-skill.sh          # copy
bash scripts/install-skill.sh --link   # symlink (stays updated)
bash scripts/install-skill.sh --uninstall
```

Agents read the skill at `~/.agents/skills/lettucemeet-cli/SKILL.md` and run CLI
commands automatically.

### 4. Python library (import in your code)

```python
from lettucemeet_cli.client import GraphQLClient
from lettucemeet_cli.api import get_event

client = GraphQLClient(token="eyJ...")
event = get_event(client, "KZaEn")
print(event.title)
```

---

## Token Setup (one-time, user does this)

The agent cannot access your browser. Extract the token once and hand it over.

**Easiest -- DevTools Console** on lettucemeet.com (logged in):

```javascript
copy(localStorage.getItem('akoko:session_token'))
```

Paste that, then paste the copied token here:

```bash
uv run python main.py login "<paste-token>"
```

**Bookmarklet** -- create a bookmark with this URL for one-click copying:

```
javascript:(function(){let t=localStorage.getItem('akoko:session_token');if(t){navigator.clipboard.writeText(t).then(()=>{alert('Token copied!')}).catch(()=>{prompt('Copy:',t)})}else{alert('Not found - on lettucemeet.com?')}})();
```

**Env var** (no saved file):
```bash
export LETTUCEMEET_TOKEN="eyJhbGciOiJIUzI1NiIs..."
```

---

## All CLI Commands

| Command | What it does |
|---|---|
| `login <token>` | Save session token |
| `create --title --dates --start-time --end-time --timezone` | Create a poll |
| `show <event-id>` | View event + all responses |
| `respond <event-id> --name --email --slots` | Submit availability |
| `overlap <event-id>` | Compute best meeting times |

### Examples

```bash
# Create
uv run python main.py create \
  --title "Team standup" \
  --dates 2026-07-20 2026-07-21 2026-07-22 \
  --start-time 09:00 --end-time 17:00 \
  --timezone Asia/Jerusalem

# Show
uv run python main.py show KZaEn

# Respond
uv run python main.py respond KZaEn \
  --name "Alice" --email "alice@example.com" \
  --slots "2026-07-20 09:00 12:00" "2026-07-21 14:00 17:00"

# Overlap
uv run python main.py overlap KZaEn
# Output:
# --- 2026-07-20 ---
#     Time  Count  Available
# 09:00      2  Alice, Bob
# 10:00      2  Alice, Bob
```

---

## How It Works

- Uses **`POST https://api.lettucemeet.com/graphql`** with JWT bearer auth
- Reverse-engineered from a browser HAR capture (no public API)
- Token chain: `--token` flag > `LETTUCEMEET_TOKEN` env var > `data/session.json`
- Full architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- MCP protocol: [`docs/MCP.md`](docs/MCP.md)

## Project Structure

```
src/lettucemeet_cli/              # Python package
  cli.py                          # CLI entry point
  mcp_server.py                   # MCP server (JSON-RPC over stdio)
  client.py                       # GraphQL HTTP client
  api.py                          # API operations
  models.py                       # Data models
  overlap.py                      # Overlap computation
  config.py                       # Token/session management
tests/                            # 39 tests
.agents/skills/lettucemeet-cli/   # Agent skill (installable)
scripts/install-skill.sh          # Skill installer
docs/                             # Architecture, MCP, HAR archive
data/session.json                 # Saved token (gitignored)
```

## Development

```bash
uv run pytest          # 39 tests
uv run ruff check .    # Lint
uv run mypy src/       # Type check
```
