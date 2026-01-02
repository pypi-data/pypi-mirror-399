# MCP Server Setup

This guide explains how to set up the PairCoder MCP (Model Context Protocol) server for enhanced IDE integration.

## Prerequisites

- Claude Desktop or compatible MCP client
- Python 3.10+ with `bpsai-pair` installed
- PairCoder-initialized project

## Quick Setup

### 1. Locate your MCP configuration

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add the PairCoder MCP server

```json
{
  "mcpServers": {
    "paircoder": {
      "command": "bpsai-pair",
      "args": ["mcp", "serve"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### 3. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server.

## Available MCP Tools

Once configured, Claude has access to these PairCoder tools:

| Tool | Description |
|------|-------------|
| `paircoder_status` | Get project status |
| `paircoder_task_list` | List tasks |
| `paircoder_task_update` | Update task status |
| `paircoder_plan_list` | List plans |
| `paircoder_flow_run` | Run a workflow |

## Troubleshooting

### Server not appearing

1. Check the path to `bpsai-pair` is correct
2. Ensure `cwd` points to a PairCoder project
3. Check Claude Desktop logs for errors

### Permission errors

Ensure the terminal/shell has access to your Python environment where `bpsai-pair` is installed.

## More Information

- [Full MCP Documentation](https://modelcontextprotocol.io/)
- [PairCoder User Guide](./USER_GUIDE.md)
