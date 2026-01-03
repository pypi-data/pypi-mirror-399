# PairCoder v2.8.4 User Guide

> Complete documentation for the AI-augmented pair programming framework

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Core Concepts](#core-concepts)
5. [Project Structure](#project-structure)
6. [Presets](#presets)
7. [Planning System](#planning-system)
8. [Skills](#skills)
9. [Skill Export & Cross-Platform](#skill-export--cross-platform)
10. [Slash Commands](#slash-commands)
11. [Orchestration](#orchestration)
12. [Autonomous Workflow](#autonomous-workflow)
13. [Intent Detection](#intent-detection)
14. [GitHub Integration](#github-integration)
15. [Metrics & Analytics](#metrics--analytics)
16. [Time Tracking](#time-tracking)
17. [Benchmarking](#benchmarking)
18. [Caching](#caching)
19. [Trello Integration](#trello-integration)
20. [Standup Summaries](#standup-summaries)
21. [MCP Server](#mcp-server)
22. [Auto-Hooks](#auto-hooks)
23. [CLI Reference](#cli-reference)
24. [Configuration Reference](#configuration-reference)
25. [Claude Code Integration](#claude-code-integration)
26. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is PairCoder?

PairCoder is a repo-native toolkit for pairing with AI coding agents (Claude, GPT, Codex, Gemini). It provides:

- **Structured context** — Project memory in `.paircoder/` that AI agents can read and update
- **Planning workflows** — Plans, sprints, and tasks with YAML+Markdown format
- **Skills** — Reusable workflow templates in `.claude/skills/` with cross-platform export
- **Multi-agent orchestration** — Route tasks to the right AI based on complexity
- **Analytics** — Token tracking, cost estimation, time tracking
- **Integrations** — Trello for visual task boards, MCP for Claude Desktop

### Philosophy

PairCoder treats AI as a **pair programming partner**:
- The AI navigates (plans, designs, reviews)
- You drive (approve, implement, test)
- Context is shared via standardized files

### v2 vs v1

| Aspect | v1 | v2 |
|--------|----|----|
| Structure | Scattered files | `.paircoder/` directory |
| Planning | None | Full planning system |
| Skills | None | Claude Code native skills |
| Orchestration | Manual | Automatic routing |
| Analytics | None | Token/cost/time tracking |

---

## Installation

### Basic Install

```bash
pip install bpsai-pair
bpsai-pair --version  # Should show 2.8.4
```

### With MCP Support

```bash
pip install 'bpsai-pair[mcp]'
```

### Development Install

```bash
git clone https://github.com/yourusername/paircoder.git
cd paircoder/tools/cli
pip install -e .
pytest -v  # 2050+ tests
```

### Verify Installation

```bash
bpsai-pair --help
bpsai-pair status
```

---

## Getting Started

### Initialize a New Project

```bash
bpsai-pair init my-project
cd my-project
```

### Initialize an Existing Project

```bash
cd your-project
bpsai-pair init .
```

### Your First Workflow

1. **Create a plan**
   ```bash
   bpsai-pair plan new my-feature --type feature --title "My Feature"
   ```

2. **Add tasks**
   ```bash
   bpsai-pair plan add-task plan-2025-12-my-feature \
     --id TASK-001 --title "Implement core logic"
   ```

3. **Check status**
   ```bash
   bpsai-pair plan status
   ```

4. **Work on tasks**
   ```bash
   bpsai-pair task next
   bpsai-pair task update TASK-001 --status in_progress
   # ... do the work ...
   bpsai-pair task update TASK-001 --status done
   ```

5. **Archive completed work**
   ```bash
   bpsai-pair task archive --completed
   ```

---

## Core Concepts

### Context Loop

The context loop is how PairCoder maintains project understanding:

1. **Read** — AI reads `project.md`, `workflow.md`, `state.md`
2. **Work** — AI performs tasks, writes code
3. **Update** — AI updates `state.md` with progress
4. **Persist** — Changes are committed to repo

### Plans & Tasks

**Plans** are high-level goals:
```yaml
# .paircoder/plans/plan-2025-12-feature.plan.yaml
id: plan-2025-12-feature
title: Add new feature
type: feature
status: in_progress
goals:
  - Implement core functionality
  - Add tests
  - Update documentation
sprints:
  - id: sprint-1
    title: Core Implementation
    task_ids: [TASK-001, TASK-002]
```

**Tasks** are specific work items:
```yaml
# .paircoder/tasks/feature/TASK-001.task.md
---
id: TASK-001
plan: plan-2025-12-feature
title: Implement core logic
status: pending
priority: P0
complexity: 50
sprint: sprint-1
---

# Objective
Implement the core business logic for the feature.

# Implementation Plan
- Create service class
- Add database models
- Write unit tests

# Verification
- [ ] Tests pass
- [ ] Code reviewed
```

### Skills

Skills are Claude Code native workflows in `.claude/skills/`:
```markdown
# .claude/skills/tdd-implement/SKILL.md
---
name: implementing-with-tdd
description: Guides test-driven development workflow for bug fixes and feature implementation.
---

# TDD Implementation

## When to Use
Use this skill when fixing bugs or implementing features with tests.

## Steps
1. Understand the requirement
2. Write failing test
3. Implement solution
4. Verify tests pass
```

---

## Project Structure

### .paircoder/ Directory

```
.paircoder/
├── config.yaml           # Project configuration
├── capabilities.yaml     # LLM capability manifest
├── context/
│   ├── project.md       # Project overview, goals, constraints
│   ├── workflow.md      # How work is done here
│   └── state.md         # Current state, active tasks
├── plans/               # Plan files (.plan.yaml)
├── tasks/               # Task files (.task.md)
│   └── <plan-slug>/     # Tasks grouped by plan
└── history/             # Archives, metrics
    ├── archives/        # Archived task files
    ├── metrics.jsonl    # Token/cost tracking
    └── manifest.json    # Archive manifest
```

### .claude/ Directory

```
.claude/
├── skills/              # Claude Code skills
│   ├── design-plan-implement/SKILL.md
│   ├── tdd-implement/SKILL.md
│   ├── code-review/SKILL.md
│   ├── finish-branch/SKILL.md
│   ├── managing-task-lifecycle/SKILL.md
│   └── planning-with-trello/SKILL.md
├── agents/              # Custom subagents
│   ├── planner.md      # Planning specialist
│   └── reviewer.md     # Code review specialist
└── settings.json        # Claude Code settings
```

### Root Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Universal AI entry point - works with any agent |
| `CLAUDE.md` | Claude Code specific pointer |

---

## Presets

Presets provide pre-configured project setups for common use cases.

### Available Presets

| Preset | Description |
|--------|-------------|
| `python-cli` | Python CLI application with Click/Typer |
| `python-api` | Python REST API with Flask/FastAPI |
| `react` | React/Next.js frontend application |
| `fullstack` | Full-stack (Python backend + React frontend) |
| `library` | Python library/package for distribution |
| `minimal` | Minimal configuration with essential defaults |
| `autonomous` | Full autonomy with Trello integration |
| `bps` | BPS AI Software preset with 7-list Trello workflow |

### Using Presets

```bash
# List available presets
bpsai-pair preset list

# Show preset details
bpsai-pair preset show bps

# Preview generated config
bpsai-pair preset preview bps

# Initialize project with preset
bpsai-pair init my-project --preset bps
```

### BPS Preset

The `bps` preset configures a full BPS AI Software workflow:

**Trello 7-List Structure:**
- Intake / Backlog
- Planned / Ready
- In Progress
- Review / Testing
- Deployed / Done
- Issues / Tech Debt
- Notes / Ops Log

**Label Colors:**
- Backend (green), Frontend (yellow), Database (orange)
- DevOps (purple), Testing (blue), Documentation (sky)
- Architecture (pink), Security (red)

**Automation:**
- Task start → moves card to "In Progress"
- Task complete → moves card to "Deployed / Done"
- Task blocked → moves card to "Issues / Tech Debt"

---

## Planning System

### Creating Plans

```bash
# Create a feature plan
bpsai-pair plan new my-feature --type feature --title "My Feature"

# Create a bugfix plan
bpsai-pair plan new fix-issue-123 --type bugfix --title "Fix login bug"

# With goals
bpsai-pair plan new my-feature \
  --goal "Implement core logic" \
  --goal "Add comprehensive tests"
```

### Managing Plans

```bash
# List all plans
bpsai-pair plan list

# Show plan details
bpsai-pair plan show plan-2025-12-my-feature

# Show plan with tasks
bpsai-pair plan tasks plan-2025-12-my-feature

# Show plan status with progress
bpsai-pair plan status plan-2025-12-my-feature
# or for active plan:
bpsai-pair plan status
```

### Adding Tasks

```bash
bpsai-pair plan add-task plan-2025-12-my-feature \
  --id TASK-001 \
  --title "Implement core logic" \
  --type feature \
  --priority P0 \
  --complexity 50 \
  --sprint sprint-1
```

### Task Lifecycle

```
pending → in_progress → done
                     ↘ blocked → pending (when unblocked)
                     ↘ cancelled
```

```bash
# Get next recommended task
bpsai-pair task next

# Start working
bpsai-pair task update TASK-001 --status in_progress

# Mark complete
bpsai-pair task update TASK-001 --status done

# Mark blocked
bpsai-pair task update TASK-001 --status blocked
```

### Archiving Tasks

```bash
# Archive specific task
bpsai-pair task archive TASK-001

# Archive all completed
bpsai-pair task archive --completed

# Archive by sprint
bpsai-pair task archive --sprint sprint-1

# Restore from archive
bpsai-pair task restore TASK-001

# List archived
bpsai-pair task list-archived

# Preview changelog
bpsai-pair task changelog-preview --sprint sprint-1 --version v1.0.0

# Clean old archives (90 days default)
bpsai-pair task cleanup --retention 90
```

---

## Skills

Skills are the primary way to define reusable workflows in PairCoder. They follow the cross-platform Agent Skills specification.

### Available Skills

| Skill | Triggers | Purpose |
|-------|----------|---------|
| `designing-and-implementing` | "design", "plan", "feature" | Feature development |
| `implementing-with-tdd` | "fix", "bug", "test" | Test-driven implementation |
| `reviewing-code` | "review", "check", "PR" | Code review workflow |
| `finishing-branches` | "finish", "merge", "complete" | Branch completion |
| `managing-task-lifecycle` | "work on task", "start task", "TRELLO-" | Task execution (includes Trello) |
| `planning-with-trello` | "plan feature", "create tasks" | Planning with Trello |

### Skill Commands

```bash
# List all skills
bpsai-pair skill list

# Validate skill format
bpsai-pair skill validate

# Validate specific skill
bpsai-pair skill validate designing-and-implementing

# Get AI-powered skill suggestions
bpsai-pair skill suggest

# Detect gaps in skill coverage
bpsai-pair skill gaps

# Generate skill from detected gap
bpsai-pair skill generate gap-name

# Install skill from URL or path
bpsai-pair skill install https://example.com/skill.tar.gz
bpsai-pair skill install ./my-skill/
```

---

## Skill Export & Cross-Platform

PairCoder skills can be exported to other AI coding tools for cross-platform compatibility.

### Supported Platforms

| Platform | Export Format | Location |
|----------|---------------|----------|
| Cursor | Markdown rules | `.cursor/rules/*.md` |
| Continue.dev | Context file | `.continue/context/*.md` |
| Windsurf | Rules file | `.windsurfrules` |

### Export Commands

```bash
# Export single skill to Cursor
bpsai-pair skill export my-skill --format cursor

# Export all skills to Continue.dev
bpsai-pair skill export --all --format continue

# Export to Windsurf
bpsai-pair skill export my-skill --format windsurf

# Dry run (preview without writing)
bpsai-pair skill export my-skill --format cursor --dry-run
```

### Portability Tips

For maximum portability:
- Avoid platform-specific commands in skill content
- Use generic instructions (what to do, not tool-specific how)
- Keep skills focused on workflow, not tool invocations

See [Cross-Platform Skills Guide](../CROSS_PLATFORM_SKILLS.md) for detailed documentation.

---

## Slash Commands

Slash commands provide quick access to common operations in Claude Code.

### Available Commands

| Command | Purpose |
|---------|---------|
| `/status` | Show project status, current sprint, active tasks |
| `/pc-plan` | Show current plan details and progress |
| `/task [ID]` | Show current or specific task details |
| `/start-task <ID>` | Start working on a task with pre-flight checks |
| `/prep-release <version>` | Prepare a release with documentation verification |

### Usage

Type the command in Claude Code chat:

```
/status
```

Claude Code will execute the command and display the results.

### Creating Custom Commands

Place markdown files in `.claude/commands/` to create custom slash commands:

```markdown
# .claude/commands/my-command.md
Description of what this command does.

Steps:
1. First step
2. Second step
```

Then use `/my-command` in Claude Code.

### Command File Structure

```
.claude/
└── commands/
    ├── status.md      # /status command
    ├── pc-plan.md     # /pc-plan command
    ├── task.md        # /task command
    ├── start-task.md  # /start-task command
    ├── prep-release.md # /prep-release command
    └── custom.md      # /custom command (your own)
```

### Best Practices

1. **Keep commands focused** - Each command should do one thing well
2. **Use CLI commands** - Reference `bpsai-pair` commands for consistency
3. **Document steps** - Write clear step-by-step instructions
4. **Test commands** - Verify commands work as expected before sharing

---

## Orchestration

### Model Routing

PairCoder routes tasks to appropriate models based on complexity:

```yaml
# In config.yaml
routing:
  by_complexity:
    trivial:   { max_score: 20,  model: claude-haiku-4-5 }
    simple:    { max_score: 40,  model: claude-haiku-4-5 }
    moderate:  { max_score: 60,  model: claude-sonnet-4-5 }
    complex:   { max_score: 80,  model: claude-opus-4-5 }
    epic:      { max_score: 100, model: claude-opus-4-5 }
```

### Orchestration Commands

```bash
# Route a task to best agent
bpsai-pair orchestrate task TASK-001

# Analyze without executing
bpsai-pair orchestrate analyze TASK-001

# Create handoff package for another agent
bpsai-pair orchestrate handoff TASK-001 \
  --from claude-code --to codex \
  --progress "Completed step 1 and 2"
```

---

## Autonomous Workflow

PairCoder provides an autonomous workflow framework for hands-off task execution.

### Auto-Session

```bash
# Run autonomous session (executes tasks until complete)
bpsai-pair orchestrate auto-session

# Run single task workflow
bpsai-pair orchestrate auto-run --task TASK-001

# Check workflow status
bpsai-pair orchestrate workflow-status
```

### Auto-Task Assignment

```bash
# Get next recommended task
bpsai-pair task next

# Auto-start next task
bpsai-pair task next --start

# Full auto-assignment with Trello
bpsai-pair task auto-next
```

### Workflow States

The autonomous workflow uses a state machine:

```
IDLE → SELECTING_TASK → PREPARING → EXECUTING → REVIEWING → COMPLETING → IDLE
                                                         ↘ BLOCKED
```

---

## Intent Detection

PairCoder can detect work intent from natural language to suggest appropriate workflows.

### Commands

```bash
# Detect intent from text
bpsai-pair intent detect "fix the login bug"
# Output: bugfix

bpsai-pair intent detect "add user authentication"
# Output: feature

# Check if planning is needed
bpsai-pair intent should-plan "refactor the database layer"
# Output: true (complex task needs planning)

# Suggest appropriate flow
bpsai-pair intent suggest-flow "review the PR for security issues"
# Output: code-review
```

### Intent Types

| Intent | Triggers | Suggested Skill |
|--------|----------|-----------------|
| `feature` | "add", "create", "implement" | designing-and-implementing |
| `bugfix` | "fix", "bug", "broken", "error" | implementing-with-tdd |
| `refactor` | "refactor", "clean up", "improve" | designing-and-implementing |
| `review` | "review", "check", "look at" | reviewing-code |
| `documentation` | "document", "docs", "README" | - |

---

## GitHub Integration

PairCoder integrates with GitHub for automated PR workflows.

### Commands

```bash
# Check GitHub connection
bpsai-pair github status

# Create PR for a task
bpsai-pair github create --task TASK-001

# Auto-create PR from branch name (detects TASK-xxx)
bpsai-pair github auto-pr
bpsai-pair github auto-pr --no-draft  # Create as ready PR

# List pull requests
bpsai-pair github list

# Merge PR and update task
bpsai-pair github merge 123

# Link task to existing PR
bpsai-pair github link TASK-001 --pr 123

# Archive task when its PR merges
bpsai-pair github archive-merged 123

# Scan and archive all merged PRs
bpsai-pair github archive-merged --all
```

### Branch Naming

Auto-PR detects task IDs from branch names:

- `feature/TASK-001-add-auth` → TASK-001
- `TASK-001/add-auth` → TASK-001
- `TASK-001-add-auth` → TASK-001

### Workflow

1. Create feature branch: `git checkout -b feature/TASK-001-add-auth`
2. Make changes and commit
3. Push branch: `git push -u origin feature/TASK-001-add-auth`
4. Auto-create PR: `bpsai-pair github auto-pr`
5. When PR merges: `bpsai-pair github archive-merged --all`

---

## Metrics & Analytics

### Token Tracking

```bash
# Session/daily summary
bpsai-pair metrics summary

# Task-specific metrics
bpsai-pair metrics task TASK-001

# Breakdown by dimension
bpsai-pair metrics breakdown --by agent
bpsai-pair metrics breakdown --by model
bpsai-pair metrics breakdown --by task
```

### Budget Management

```bash
# Check budget status
bpsai-pair metrics budget

# Estimate task cost
bpsai-pair budget estimate TASK-001

# Check if task fits current budget
bpsai-pair budget check --task TASK-001

# Export metrics
bpsai-pair metrics export --format csv --output metrics.csv
```

### Metrics Storage

Metrics are stored in `.paircoder/history/metrics.jsonl`:
```json
{"timestamp": "2025-12-16T10:00:00", "agent": "claude-code", "model": "claude-sonnet-4-5", "input_tokens": 1500, "output_tokens": 800, "cost_usd": 0.0115}
```

---

## Time Tracking

### Built-in Timer

```bash
# Start timer for a task
bpsai-pair timer start TASK-001

# Check current timer
bpsai-pair timer status

# Stop timer
bpsai-pair timer stop

# View time entries for a task
bpsai-pair timer show TASK-001

# Summary across tasks
bpsai-pair timer summary --plan plan-2025-12-feature
```

### Toggl Integration

Configure in `config.yaml`:
```yaml
time_tracking:
  provider: toggl
  api_token: ${TOGGL_API_TOKEN}
  workspace_id: 12345
```

---

## Benchmarking

### Running Benchmarks

```bash
# Run default benchmark suite
bpsai-pair benchmark run --suite default

# View latest results
bpsai-pair benchmark results --latest

# Compare two agents
bpsai-pair benchmark compare claude-code codex

# List available benchmarks
bpsai-pair benchmark list
```

### Benchmark Suite Format

```yaml
# .paircoder/benchmarks/default.yaml
name: default
description: Standard benchmark suite
benchmarks:
  - id: simple-function
    description: Write a simple function
    prompt: "Write a function that adds two numbers"
    validation:
      - type: exists
        path: solution.py
      - type: contains
        path: solution.py
        pattern: "def add"
```

---

## Caching

### Context Cache

PairCoder caches context files for efficiency:

```bash
# View cache statistics
bpsai-pair cache stats

# Clear entire cache
bpsai-pair cache clear

# Invalidate specific file
bpsai-pair cache invalidate .paircoder/context/state.md
```

### Lite Pack for Codex

```bash
# Create minimal pack for 32KB context limit
bpsai-pair pack --lite
```

---

## Trello Integration

### Setup

1. Get API key from https://trello.com/app-key
2. Generate token from the API key page
3. Connect PairCoder:

```bash
bpsai-pair trello connect
# Enter API key and token when prompted
```

### Board Management

```bash
# Check connection
bpsai-pair trello status

# List boards
bpsai-pair trello boards

# Set active board
bpsai-pair trello use-board <board-id>

# View board lists
bpsai-pair trello lists

# View/modify config
bpsai-pair trello config --show
```

### Working with Trello Tasks

```bash
# List tasks from board
bpsai-pair ttask list

# Show task details
bpsai-pair ttask show <card-id>

# Start working (moves to In Progress)
bpsai-pair ttask start <card-id>

# Complete task (moves to Done)
bpsai-pair ttask done <card-id> --summary "Implemented feature X"

# Mark blocked
bpsai-pair ttask block <card-id> --reason "Waiting for API"

# Add comment
bpsai-pair ttask comment <card-id> --message "50% complete"

# Move to different list
bpsai-pair ttask move <card-id> --list "In Review"
```

### Plan-to-Trello Sync

```bash
# Preview sync
bpsai-pair plan sync-trello plan-2025-12-feature --dry-run

# Sync tasks to Trello
bpsai-pair plan sync-trello plan-2025-12-feature --board <board-id>
```

### Progress Comments

Report progress directly on Trello cards:

```bash
# Post a progress update
bpsai-pair trello progress TASK-001 "Completed database schema"

# Report task started
bpsai-pair trello progress TASK-001 --started

# Report blocked with reason
bpsai-pair trello progress TASK-001 --blocked "Waiting for API docs"

# Report step completed
bpsai-pair trello progress TASK-001 --step "Database migration complete"

# Report task completion
bpsai-pair trello progress TASK-001 --completed "Feature fully implemented"

# Request review
bpsai-pair trello progress TASK-001 --review
```

### Webhook Server

Listen for Trello card movements:

```bash
# Start webhook server
bpsai-pair trello webhook serve --port 8080

# Check webhook status
bpsai-pair trello webhook status
```

The webhook server:
- Receives Trello card movement events
- Auto-assigns agents when cards move to "Ready" column
- Updates local task status to match card position

---

## Standup Summaries

Generate daily standup summaries from task data.

### Commands

```bash
# Generate markdown summary
bpsai-pair standup generate

# Generate in different formats
bpsai-pair standup generate --format markdown  # default
bpsai-pair standup generate --format slack     # Slack-formatted
bpsai-pair standup generate --format trello    # Trello comment format

# Custom lookback period (hours)
bpsai-pair standup generate --since 48  # Last 48 hours

# Filter by plan
bpsai-pair standup generate --plan plan-2025-12-feature

# Output to file
bpsai-pair standup generate -o standup.md

# Post summary to Trello Notes list
bpsai-pair standup post
```

### Output Format

The markdown format includes:

```markdown
# Daily Standup - 2025-12-16

## Completed Yesterday
- [TASK-001] Implement login API
- [TASK-002] Add form validation

## In Progress
- [TASK-003] User dashboard (50% complete)

## Blocked
- [TASK-004] Payment integration - Waiting for Stripe keys

## Ready to Start
- [TASK-005] Email notifications
- [TASK-006] User preferences
```

---

## MCP Server

### What is MCP?

MCP (Model Context Protocol) allows AI agents to call PairCoder tools directly. Claude Desktop and other MCP-compatible clients can use PairCoder autonomously.

### Installation

```bash
pip install 'bpsai-pair[mcp]'
```

### Starting the Server

```bash
# Start server (stdio transport)
bpsai-pair mcp serve

# List available tools
bpsai-pair mcp tools

# Test a tool locally
bpsai-pair mcp test paircoder_task_list
```

### Available Tools (13)

| Tool | Description | Parameters |
|------|-------------|------------|
| `paircoder_task_list` | List tasks with filters | status, plan, sprint |
| `paircoder_task_next` | Get next recommended task | - |
| `paircoder_task_start` | Start a task | task_id, agent |
| `paircoder_task_complete` | Complete a task | task_id, summary |
| `paircoder_context_read` | Read context files | file (state/project/workflow/config/capabilities) |
| `paircoder_plan_status` | Get plan progress | plan_id |
| `paircoder_plan_list` | List available plans | - |
| `paircoder_orchestrate_analyze` | Analyze task complexity | task_id, context, prefer_agent |
| `paircoder_orchestrate_handoff` | Create handoff package | task_id, from_agent, to_agent, progress_summary |
| `paircoder_metrics_record` | Record token usage | task_id, agent, model, input_tokens, output_tokens |
| `paircoder_metrics_summary` | Get metrics summary | scope, scope_id |
| `paircoder_trello_sync_plan` | Sync plan to Trello | plan_id, board_id, create_lists, link_cards |
| `paircoder_trello_update_card` | Update Trello card | task_id, action, comment |

### Claude Desktop Setup

See [MCP Setup Guide](MCP_SETUP.md) for detailed configuration.

---

## Auto-Hooks

### Configuration

Configure hooks in `.paircoder/config.yaml`:

```yaml
hooks:
  enabled: true
  on_task_start:
    - check_token_budget  # Warn if task exceeds budget
    - start_timer         # Start time tracking
    - sync_trello         # Update Trello card
    - update_state        # Refresh state.md
  on_task_complete:
    - stop_timer          # Stop time tracking
    - record_metrics      # Record token usage
    - sync_trello         # Update Trello card
    - update_state        # Refresh state.md
    - check_unblocked     # Find newly unblocked tasks
  on_task_block:
    - sync_trello         # Update Trello card
    - update_state        # Refresh state.md
```

### Available Hooks

| Hook | Description |
|------|-------------|
| `check_token_budget` | Warn if task exceeds budget threshold |
| `start_timer` | Start time tracking for task |
| `stop_timer` | Stop time tracking, calculate duration |
| `record_metrics` | Record token usage from context.extra |
| `sync_trello` | Update Trello card status |
| `update_state` | Reload and refresh state.md |
| `check_unblocked` | Find tasks unblocked by completion |

### Disabling Hooks

```yaml
hooks:
  enabled: false
```

---

## CLI Reference

### All Commands (120+ total)

| Group | Commands | Count |
|-------|----------|-------|
| Core | init, feature, pack, context-sync, status, validate, ci | 7 |
| Presets | preset list/show/preview, init --preset | 4 |
| Planning | plan new/list/show/tasks/status/sync-trello/add-task/estimate | 8 |
| Tasks | task list/show/update/next/auto-next/archive/restore/list-archived/cleanup/changelog-preview | 11 |
| Skills | skill list/validate/export/install/suggest/gaps/generate | 7 |
| Flows | flow list/show/run/validate (deprecated) | 4 |
| Orchestration | orchestrate task/analyze/handoff/auto-run/auto-session/workflow-status | 6 |
| Intent | intent detect/should-plan/suggest-flow | 3 |
| GitHub | github status/create/list/merge/link/auto-pr/archive-merged | 7 |
| Standup | standup generate/post | 2 |
| Metrics | metrics summary/task/breakdown/budget/export/velocity/burndown/accuracy/tokens | 9 |
| Budget | budget estimate/status/check | 3 |
| Timer | timer start/stop/status/show/summary | 5 |
| Benchmark | benchmark run/results/compare/list | 4 |
| Cache | cache stats/clear/invalidate | 3 |
| Session | session check/status | 2 |
| Compaction | compaction snapshot save/list, check/recover/cleanup | 5 |
| Security | security scan-secrets/pre-commit/install-hook/scan-deps | 4 |
| Migrate | migrate, migrate status | 2 |
| Upgrade | upgrade | 1 |
| Trello | trello connect/status/disconnect/boards/use-board/lists/config/progress/webhook serve/webhook status | 10 |
| Trello Tasks | ttask list/show/start/done/block/comment/move | 7 |
| MCP | mcp serve/tools/test | 3 |

See [README.md](../README.md) for complete command details.

---

## Configuration Reference

### Full config.yaml Schema

```yaml
version: "2.8"

project:
  name: "my-project"
  description: "Project description"
  primary_goal: "Main objective"
  coverage_target: 80

workflow:
  default_branch_type: "feature"
  main_branch: "main"
  context_dir: ".paircoder/context"
  plans_dir: ".paircoder/plans"
  tasks_dir: ".paircoder/tasks"

pack:
  default_name: "agent_pack.tgz"
  excludes:
    - ".git"
    - ".venv"
    - "__pycache__"
    - "node_modules"

models:
  navigator: claude-opus-4-5
  driver: claude-sonnet-4-5
  reviewer: claude-sonnet-4-5
  providers:
    anthropic:
      models: [claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5]
    openai:
      models: [gpt-5.1-codex-max, gpt-5.1-codex]

routing:
  by_complexity:
    trivial:   { max_score: 20,  model: claude-haiku-4-5 }
    simple:    { max_score: 40,  model: claude-haiku-4-5 }
    moderate:  { max_score: 60,  model: claude-sonnet-4-5 }
    complex:   { max_score: 80,  model: claude-opus-4-5 }
    epic:      { max_score: 100, model: claude-opus-4-5 }
  overrides:
    security: claude-opus-4-5
    architecture: claude-opus-4-5

metrics:
  enabled: true
  store_path: .paircoder/history/metrics.jsonl

token_budget:
  warning_threshold: 75
  critical_threshold: 90

hooks:
  enabled: true
  on_task_start: [check_token_budget, start_timer, sync_trello, update_state]
  on_task_complete: [stop_timer, record_metrics, sync_trello, update_state, check_unblocked]
  on_task_block: [sync_trello, update_state]

trello:
  board_id: null  # Set with `trello use-board`
  lists:
    backlog: "Backlog"
    in_progress: "In Progress"
    review: "In Review"
    done: "Done"
```

---

## Claude Code Integration

PairCoder is designed to complement Claude Code's built-in features. For detailed documentation on how they work together, see [Claude Code Integration Guide](../../docs/CLAUDE_CODE_INTEGRATION.md).

### Key Points

- **Built-in commands**: Use `/compact`, `/context`, `/plan` alongside PairCoder
- **Skills**: PairCoder skills in `.claude/skills/` are auto-loaded by Claude Code
- **Context management**: Claude Code handles conversation; PairCoder handles project state
- **Compaction recovery**: Use `bpsai-pair compaction recover` after `/compact`

### Quick Reference

| Need | Use |
|------|-----|
| Session planning | Claude Code `/plan` |
| Sprint planning | `bpsai-pair plan` |
| Check token usage | `/context` |
| Check project state | `/status` or `bpsai-pair status` |
| Start a task | `/start-task T19.1` |

---

## Troubleshooting

### Common Issues

**Command not found**
```bash
# If bpsai-pair not on PATH:
python -m bpsai_pair.cli --help
```

**No .paircoder directory**
```bash
# Initialize the project
bpsai-pair init .
```

**Task not found**
```bash
# List all tasks to find ID
bpsai-pair task list
```

**MCP server won't start**
```bash
# Verify MCP extra installed
pip show mcp

# Test locally
bpsai-pair mcp test paircoder_task_list
```

**Trello not connected**
```bash
# Check status
bpsai-pair trello status

# Reconnect
bpsai-pair trello connect
```

### Debug Commands

```bash
# Validate repo structure
bpsai-pair validate

# Show current state
bpsai-pair status

# List all plans
bpsai-pair plan list

# Show cache state
bpsai-pair cache stats
```

### Getting Help

- GitHub Issues: https://github.com/BPSAI/paircoder/issues
- Documentation: This guide and README.md
- MCP Setup: docs/MCP_SETUP.md

---

*PairCoder v2.8.4 - MIT License*
