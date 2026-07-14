# MCP Server

Exposes LettuceMeet as callable MCP tools for AI agents.

## Tools

| Tool | What |
|---|---|
| `create_poll` | Create a poll |
| `show_event` | View event + responses |
| `respond_to_poll` | Submit availability |
| `compute_overlap` | Find best times |
| `delete_event` | Delete an event |

## Setup

Add to your agent's MCP config:

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

The server communicates over stdio (JSON-RPC 2.0).
