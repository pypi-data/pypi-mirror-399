# {{ cookiecutter.project_name }} - PairCoder Guide

This project uses **PairCoder v2** for AI-augmented pair programming.

## Quick Start

```bash
# Check status
bpsai-pair status

# List available flows
bpsai-pair flow list

# Create a plan
bpsai-pair plan new my-feature --type feature --title "My Feature"

# Work on a task
bpsai-pair task next
bpsai-pair task update TASK-001 --status in_progress
```

## Key Files

| File | Purpose |
|------|---------|
| `.paircoder/capabilities.yaml` | What AI agents can do |
| `.paircoder/context/state.md` | Current status |
| `.paircoder/context/project.md` | Project overview |
| `.paircoder/config.yaml` | Configuration |

## Commands Reference

### Planning

```bash
bpsai-pair plan new <slug> --type feature
bpsai-pair plan list
bpsai-pair plan show <id>
bpsai-pair plan add-task <id> --id TASK-XXX --title "..."
```

### Tasks

**Which command to use?**

```
Is Trello connected? (bpsai-pair trello status)
├── YES → Use ttask commands
│   ├── Start:    ttask start TRELLO-XX
│   ├── Complete: ttask done TRELLO-XX --summary "..." --list "Deployed/Done"
│   └── Block:    ttask block TRELLO-XX --reason "..."
│
└── NO → Use task update commands
    ├── Start:    task update TASK-XXX --status in_progress
    ├── Complete: task update TASK-XXX --status done
    └── Block:    task update TASK-XXX --status blocked
```

**For non-Trello projects:**

```bash
bpsai-pair task list
bpsai-pair task show <id>
bpsai-pair task update <id> --status done
bpsai-pair task next
```

**For Trello projects:** See [Trello Integration](#trello-integration) section.

### Flows

```bash
bpsai-pair flow list
bpsai-pair flow show <name>
bpsai-pair flow run <name>
```

### Slash Commands

Quick commands available in Claude Code:

| Command | Purpose |
|---------|---------|
| `/status` | Show project status, current sprint, active tasks |
| `/pc-plan` | Show current plan details and progress |
| `/task [ID]` | Show current or specific task details |

**Usage**: Type `/status` in Claude Code chat.

**Create custom commands**: Add markdown files to `.claude/commands/`:

```markdown
# .claude/commands/my-command.md
Run these steps:
1. First step
2. Second step
```

Then use `/my-command` in Claude Code.

### Context

```bash
bpsai-pair context-sync --last "..." --next "..."
bpsai-pair pack
```

## Working with AI

1. AI agents read `AGENTS.md` or `CLAUDE.md` at repo root
2. They check `.paircoder/capabilities.yaml` to understand what they can do
3. They read `.paircoder/context/state.md` for current status
4. They follow flows when appropriate

## Trello Integration

PairCoder integrates with Trello for task management. Follow these steps to connect your project to a Trello board.

### Step 1: Get Trello API Credentials

1. Go to [trello.com/power-ups/admin](https://trello.com/power-ups/admin)
2. Click **"New"** to create a new Power-Up (or use an existing one)
3. Copy the **API Key**
4. Click **"Generate Token"** link next to the API Key
5. Authorize the app and copy the **Token**

### Step 2: Set Environment Variables

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export TRELLO_API_KEY=your_api_key_here
export TRELLO_TOKEN=your_token_here

# Or set temporarily for current session
export TRELLO_API_KEY=abc123...
export TRELLO_TOKEN=xyz789...
```

### Step 3: Connect to Trello

```bash
# Verify credentials are working
bpsai-pair trello connect

# List your boards
bpsai-pair trello boards
```

### Step 4: Set Active Board

Find your board ID from the Trello URL: `https://trello.com/b/<BOARD_ID>/board-name`

```bash
# Set the active board
bpsai-pair trello use-board <board-id>

# Verify connection
bpsai-pair trello status

# View board lists
bpsai-pair trello lists
```

### Step 5: Configure Board in config.yaml

The board ID is automatically saved to `.paircoder/config.yaml`:

```yaml
trello:
  board_id: "your_board_id"
  sync_on_task_update: true
  list_mappings:
    backlog: "Intake/Backlog"
    ready: "Planned/Ready"
    in_progress: "In Progress"
    review: "In Review"
    done: "Deployed/Done"
```

### Working with Trello Tasks

```bash
# List tasks from board
bpsai-pair ttask list

# List AI-ready tasks (assigned, in backlog)
bpsai-pair ttask list --agent

# Start working on a task
bpsai-pair ttask start TRELLO-123

# Complete a task (checks acceptance criteria)
bpsai-pair ttask done TRELLO-123 --summary "Implemented feature X"

# Add a comment to a card
bpsai-pair ttask comment TRELLO-123 "Progress update: 50% complete"
```

### Syncing Plans to Trello

```bash
# Create a plan and sync to Trello
bpsai-pair plan new my-feature --type feature --title "My Feature"
bpsai-pair plan sync-trello my-feature

# Sync directly to Planned/Ready list
bpsai-pair plan sync-trello my-feature --target-list "Planned/Ready"
```

### Troubleshooting

**"Invalid credentials" error:**
- Verify TRELLO_API_KEY and TRELLO_TOKEN are set correctly
- Regenerate the token if expired

**"Board not found" error:**
- Check the board ID in your Trello URL
- Ensure you have access to the board

**Cards not moving:**
- Verify list names in config match your board exactly
- Check `bpsai-pair trello lists` for correct list names

## More Information

- [MCP Setup Guide](./MCP_SETUP.md) - Claude Desktop integration
- [Feature Matrix](./FEATURE_MATRIX.md) - All PairCoder capabilities
- [Full Documentation](https://github.com/bps-ai/paircoder)
