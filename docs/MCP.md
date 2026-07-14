# Unofficial LettuceMeet MCP

Exposes LettuceMeet poll management as **MCP tools** that AI agents can call
directly -- no manual CLI commands needed.

## Tools

| Tool | What it does |
|---|---|
| `create_poll` | Create a new poll event with dates and times |
| `show_event` | Get event details with all poll responses |
| `respond_to_poll` | Submit availability to an event |
| `compute_overlap` | Calculate best meeting times from responses |
| `delete_event` | Delete an event |

## Setup

### 1. Install the project

```bash
git clone <repo-url> lettucemeet-cli
cd lettucemeet-cli
uv sync
```

### 2. Save your token

```bash
uv run python main.py login "eyJhbGciOiJIUzI1NiIs..."
```

### 3. Add the MCP server to your agent

**For Pi** -- add to `~/.pi/agent/settings.json`:

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

**For Claude Code** -- add to `~/.claude/claude.json` or project `.claude/settings.json`:

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

**For any MCP-compatible agent** -- run as a subprocess:

```bash
uv run --directory /path/to/lettucemeet-cli python src/lettucemeet_cli/mcp_server.py
```

The server communicates over **stdio** (JSON-RPC 2.0).

### 4. Done

Your agent can now call these tools directly:

> "create a poll for team standup next week"
> "show me the responses for event KZaEn"
> "find the best meeting time for everyone"
