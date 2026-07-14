# LettuceMeet MCP

Unofficial CLI + MCP tools for [LettuceMeet](https://lettucemeet.com).

Create polls, read responses, find meeting overlaps -- all from the terminal.
Designed for AI agents that want to automate scheduling without a browser.

## Why

LettuceMeet has no public API. The official platform only works through a
web browser. This project reverse-engineers the internal GraphQL API so that
**AI agents can schedule meetings directly from the command line**.

Built by someone who believes every web app should be automatable from a
terminal. CLI-first, agent-friendly, zero bloat.

## How it works

A Python CLI (`argparse` + `requests`) talks to `api.lettucemeet.com/graphql`
using JWT auth. An MCP server wrapper exposes the same operations as callable
tools for any MCP-compatible agent (Pi, Claude Code, Codex, etc.).

```
User / Agent -> CLI / MCP -> GraphQL -> lettucemeet.com
```

## Quick setup

```bash
uv sync
uv run python main.py login "<token>"   # one-time: paste token from user
```

**Token** -- user runs this on lettucemeet.com (logged in) > DevTools Console:
```javascript
copy(localStorage.getItem('akoko:session_token'))
```

## Commands

| Command | Action |
|---|---|
| `login <token>` | Save session token |
| `create --title T --dates D1 D2 [--start-time 09:00] [--end-time 17:00] [--timezone TZ]` | Create poll |
| `show <id>` | View event + responses |
| `respond <id> --name N --email E --slots "DATE START END"` | Submit availability |
| `overlap <id>` | Compute best meeting times |
| `delete <id>` | Delete an event |

Token resolution: `--token` flag > `LETTUCEMEET_TOKEN` env var > `data/session.json`

## MCP server

```json
{
  "mcpServers": {
    "lettucemeet": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to", "python", "src/lettucemeet_cli/mcp_server.py"]
    }
  }
}
```

Tools: `create_poll`, `show_event`, `respond_to_poll`, `compute_overlap`, `delete_event`

## Agent skill

```bash
bash scripts/install-skill.sh --link
```

Agents auto-discover and can run CLI commands autonomously.

## Project

```
src/lettucemeet_cli/   # Python package (6 modules, 42 tests)
scripts/               # Skill installer
docs/                  # Architecture, MCP docs
```

```bash
uv run pytest          # 42 tests
```

## License

MIT
