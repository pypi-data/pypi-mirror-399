# PairCoder Feature Matrix

Quick reference for PairCoder capabilities in this project.

## Core Features

| Feature | Status | Description |
|---------|--------|-------------|
| Planning | Active | Create and manage development plans |
| Tasks | Active | Track tasks with priorities and complexity |
| Flows | Active | Structured workflows for common operations |
| Context | Active | Project context for AI agents |
| CLI | Active | Command-line interface for all operations |

## Workflows (Flows)

| Flow | Purpose | Trigger Phrases |
|------|---------|-----------------|
| `design-plan-implement` | New feature development | "build a", "create a", "add a" |
| `tdd-implement` | Test-driven bug fixes | "fix", "bug", "broken" |
| `review` | Code review | "review", "check my" |
| `finish-branch` | Complete and merge | "done", "finished", "merge" |

## Integrations

| Integration | Status | Configuration |
|-------------|--------|---------------|
| Trello | Optional | `.paircoder/config.yaml` |
| MCP Server | Optional | See [MCP_SETUP.md](./MCP_SETUP.md) |
| GitHub Actions | Template | `.github/workflows/` |

## AI Agent Support

| Agent Type | Configuration |
|------------|---------------|
| Claude Code | `CLAUDE.md`, `.claude/skills/` |
| Generic Agents | `AGENTS.md` |
| Custom Agents | `.claude/agents/` |

## Slash Commands

| Command | Description |
|---------|-------------|
| `/status` | Show project status |
| `/pc-plan` | Show current plan |
| `/task [ID]` | Show task details |

## Skills (Claude Code)

| Skill | Purpose |
|-------|---------|
| `design-plan-implement` | New feature workflow |
| `tdd-implement` | Test-driven development |
| `code-review` | Code review workflow |
| `finish-branch` | Branch completion |
| `paircoder-task-lifecycle` | Task lifecycle with Trello sync |
| `trello-aware-planning` | Trello-integrated planning |

## CLI Commands

```bash
# Status
bpsai-pair status

# Planning
bpsai-pair plan new <slug> --type feature
bpsai-pair plan list
bpsai-pair plan show <id>

# Tasks
bpsai-pair task list
bpsai-pair task show <id>
bpsai-pair task update <id> --status done
bpsai-pair task next

# Flows
bpsai-pair flow list
bpsai-pair flow run <name>

# Context
bpsai-pair pack
bpsai-pair context-sync
```

## Directory Structure

```
.paircoder/
├── docs/           # PairCoder documentation (this directory)
├── context/        # Project context for AI
├── config.yaml     # Configuration
├── capabilities.yaml # AI capability manifest
├── flows/          # Workflow definitions
├── plans/          # Plan files
└── tasks/          # Task files

.claude/            # Claude Code specific
├── commands/       # Slash commands
├── skills/         # Model-invoked skills
├── agents/         # Custom subagents
└── settings.json   # Hook configuration
```

## More Information

- [User Guide](./USER_GUIDE.md)
- [MCP Setup](./MCP_SETUP.md)
- [Full Documentation](https://github.com/bps-ai/paircoder)
