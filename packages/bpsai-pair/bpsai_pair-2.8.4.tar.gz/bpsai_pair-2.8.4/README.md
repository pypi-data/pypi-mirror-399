# bpsai-pair CLI Package

The PairCoder CLI tool for AI pair programming workflows.

See [main README](../../README.md) for full documentation.

## Development

```bash
# Install for development
pip install -e .

# Run tests
pytest -v

# Build
python -m build
```

## Package Structure

```
bpsai_pair/
├── cli.py              # Main CLI entry point
├── ops.py              # Core operations
├── config.py           # Configuration handling
├── planning/           # Plan and task management
├── tasks/              # Lifecycle, archival
├── metrics/            # Token tracking
├── integrations/       # Time tracking (Toggl)
├── benchmarks/         # Benchmark framework
├── orchestration/      # Multi-agent routing
├── mcp/                # MCP server for AI tool integration
├── hooks.py            # Auto-hooks for task state changes
├── trello/             # Trello integration
└── data/               # Cookiecutter template
```

## MCP Server

PairCoder provides an MCP (Model Context Protocol) server for AI tool integration:

```bash
# Start MCP server (stdio transport)
bpsai-pair mcp serve

# List available tools
bpsai-pair mcp tools

# Test a tool locally
bpsai-pair mcp test paircoder_task_list
```

Install with MCP support:
```bash
pip install 'bpsai-pair[mcp]'
```
