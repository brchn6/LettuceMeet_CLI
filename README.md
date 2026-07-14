# LettuceMeet MCP

Unofficial MCP tools for [LettuceMeet](https://lettucemeet.com) -- create polls, view responses, find meeting overlaps via CLI or MCP server.

Uses the website's internal GraphQL API (`api.lettucemeet.com/graphql`). No public API exists.

## MCP Server (for agents)

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

**Tools:** `create_poll`, `show_event`, `respond_to_poll`, `compute_overlap`

## Quick Setup

```bash
uv sync
uv run python main.py login "<token>"   # one-time: paste token from user
```

Token source (user extracts from browser):
```javascript
copy(localStorage.getItem('akoko:session_token'))
```
Paste in DevTools Console on lettucemeet.com (logged in).

## CLI Commands

| Command | What |
|---|---|
| `login <token>` | Save session token |
| `create --title T --dates D1 D2 [--start-time 09:00] [--end-time 17:00] [--timezone Asia/Jerusalem]` | Create poll |
| `show <id>` | View event + responses |
| `respond <id> --name N --email E --slots "DATE START END"` | Submit availability |
| `overlap <id>` | Compute best times |
| `delete <id>` | Delete an event |

Token resolution: `--token` flag > `LETTUCEMEET_TOKEN` env var > `data/session.json`

## Install as Agent Skill

```bash
bash scripts/install-skill.sh --link
```

## Tests

```bash
uv run pytest
```

## Structure

```
src/lettucemeet_cli/   # Python package
tests/                 # 39 tests
scripts/               # Skill installer
docs/                  # Architecture, MCP docs
data/session.json      # Saved token (gitignored)
```
