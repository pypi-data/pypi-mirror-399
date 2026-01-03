# PairCoder v2.8.4 Feature Matrix

> Updated after Sprint 27 on 2025-12-31

## CLI Commands Summary

| Group | Commands | Count |
|-------|----------|-------|
| Core | init, feature, pack, context-sync, status, validate, ci | 7 |
| Presets | preset list/show/preview, init --preset | 4 |
| Planning | plan new/list/show/tasks/status/sync-trello/add-task/estimate | 8 |
| Tasks | task list/show/update/next/auto-next/archive/restore/list-archived/cleanup/changelog-preview | 11 |
| Skills | skill list/validate/export/install/suggest/gaps/generate | 7 |
| Flows | flow list/show/run/validate ⚠️ DEPRECATED | 4 |
| Orchestration | orchestrate task/analyze/handoff/auto-run/auto-session/workflow-status | 6 |
| Intent | intent detect/should-plan/suggest-flow | 3 |
| GitHub | github status/create/list/merge/link/auto-pr/archive-merged | 7 |
| Standup | standup generate/post | 2 |
| Metrics | metrics summary/task/breakdown/budget/export/velocity/burndown/accuracy/tokens | 9 |
| Timer | timer start/stop/status/show/summary | 5 |
| Benchmark | benchmark run/results/compare/list | 4 |
| Cache | cache stats/clear/invalidate | 3 |
| Budget | budget estimate/status/check | 3 |
| Session | session check/status | 2 |
| Compaction | compaction snapshot save/list, check/recover/cleanup | 5 |
| Security | security scan-secrets/pre-commit/install-hook/scan-deps | 4 |
| Upgrade | upgrade | 1 |
| Migrate | migrate, migrate status | 2 |
| Template | template check/list | 2 |
| Release | release plan/checklist/prep | 3 |
| Sprint | sprint list/complete | 2 |
| Trello | trello connect/status/disconnect/boards/use-board/lists/config/progress/webhook serve/webhook status | 10 |
| Trello Tasks | ttask list/show/start/done/block/comment/move | 7 |
| MCP | mcp serve/tools/test | 3 |
| **Total** | | **120+** |

## Features by Sprint

### Sprint 1-3: Foundation (v2.0)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| v2 directory structure | `bpsai-pair init` | ✅ Works | Creates .paircoder/ and .claude/ |
| LLM capability manifest | - | ✅ Exists | .paircoder/capabilities.yaml |
| Context files | - | ✅ Exists | project.md, workflow.md, state.md |
| ADR documentation | - | ✅ Exists | docs/architecture/ |
| Flow parser | `flow list/show/run` | ⚠️ Deprecated | Use skills instead |

### Sprint 4: Planning System (v2.0)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Plan YAML parser | - | ✅ Works | .plan.yaml format |
| Task YAML+MD parser | - | ✅ Works | .task.md format |
| Plan commands | `plan new/list/show/tasks/add-task` | ✅ Works | Full CRUD |
| Task commands | `task list/show/update/next` | ✅ Works | Status management |

### Sprint 5: Claude Code Alignment (v2.1)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Skills (SKILL.md) | - | ✅ Exists | 6+ skills in .claude/skills/ |
| Custom subagents | - | ✅ Exists | planner.md, reviewer.md |
| AGENTS.md | - | ✅ Exists | Universal entry point |
| CLAUDE.md | - | ✅ Exists | Claude Code pointer |

### Sprint 6: Multi-Agent Orchestration (v2.1)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Orchestrator service | `orchestrate task/analyze/handoff` | ✅ Works | Model routing |
| Complexity analysis | `orchestrate analyze` | ✅ Works | Routing recommendation |
| Handoff packages | `orchestrate handoff` | ✅ Works | Agent transitions |

### Sprint 7: Lifecycle & Analytics (v2.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Task archival | `task archive/restore/list-archived/cleanup` | ✅ Works | .gz compression |
| Changelog generation | `task changelog-preview` | ✅ Works | From archived tasks |
| Token tracking | `metrics summary/task/breakdown` | ✅ Works | JSONL storage |
| Cost estimation | `metrics budget` | ✅ Works | Model pricing |
| Metrics export | `metrics export` | ✅ Works | CSV format |
| Time tracking | `timer start/stop/status/show/summary` | ✅ Works | Toggl integration |
| Benchmarking | `benchmark run/results/compare/list` | ✅ Works | YAML suites |

### Sprint 8: Consolidation (v2.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Doc consolidation | - | ✅ Done | docs/ directory |
| Template cleanup | - | ✅ Done | Removed prompts/ |

### Sprint 9: Prompt Caching (v2.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Context cache | `cache stats/clear/invalidate` | ✅ Works | mtime-based |
| Lite pack | `pack --lite` | ✅ Works | For Codex 32KB limit |

### Sprint 10: Trello Integration (v2.3)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Trello connection | `trello connect/status/disconnect` | ✅ Works | API key + token |
| Board management | `trello boards/use-board/lists/config` | ✅ Works | Board selection |
| Task operations | `ttask list/show/start/done/block/comment/move` | ✅ Works | Card management |
| Trello skills | - | ✅ Exists | managing-task-lifecycle, planning-with-trello |

### Sprint 11: MCP Server (v2.4)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| MCP server | `mcp serve` | ✅ Works | stdio transport |
| MCP tools list | `mcp tools` | ✅ Works | 13 tools |
| MCP tool testing | `mcp test` | ✅ Works | Local testing |
| Plan-to-Trello sync | `plan sync-trello` | ✅ Works | Creates cards |
| Plan status | `plan status` | ✅ Works | Task breakdown |
| Auto-hooks | - | ✅ Works | In config.yaml |

### Sprint 12: Trello Webhooks (v2.4)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Trello webhooks | `trello webhook serve/status` | ✅ Works | Listen for card moves |
| Agent assignment | - | ✅ Works | Assign on Ready column |
| GitHub PR integration | `github create/list/merge/link` | ✅ Works | Task-linked PRs |

### Sprint 13: Full Autonomy (v2.5)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Preset system | `preset list/show/preview` | ✅ Works | 8 built-in presets |
| BPS preset | `init --preset bps` | ✅ Works | 7-list Trello workflow |
| Intent detection | `intent detect/should-plan/suggest-flow` | ✅ Works | Natural language intent |
| Autonomous workflow | `orchestrate auto-session/auto-run/workflow-status` | ✅ Works | State machine |
| Auto-task assignment | `task next --start`, `task auto-next` | ✅ Works | Pick and start next |
| Progress comments | `trello progress` | ✅ Works | 7 report types |
| Auto-PR creation | `github auto-pr` | ✅ Works | Detect TASK-xxx from branch |
| PR merge archive | `github archive-merged` | ✅ Works | Archive task on merge |
| Daily standup | `standup generate/post` | ✅ Works | markdown/slack/trello formats |
| Hook reliability | - | ✅ Works | Always fires on status change |

### Sprint 14: Trello Deep Integration (v2.5.1)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Custom fields sync | `trello config` | ✅ Works | Project, Stack, Status, Effort |
| BPS label colors | - | ✅ Works | Exact color hex matching |
| Card description templates | - | ✅ Works | BPS format templates |
| Effort field mapping | - | ✅ Works | complexity → S/M/L |
| Two-way sync | `ttask sync` | ✅ Works | Trello → local status |
| Card checklists | - | ✅ Works | From acceptance criteria |
| Due date sync | - | ✅ Works | Plan due dates |
| Activity log comments | `ttask comment` | ✅ Works | Progress tracking |
| Check/uncheck items | `trello check/uncheck` | ✅ Works | Partial text matching |

### Sprint 15: Security & Sandboxing (v2.5.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Security agent | `.claude/agents/security.md` | ✅ Done | SOC2-focused gatekeeper |
| Command allowlist | `security/allowlist.py` | ✅ Done | ALLOW/REVIEW/BLOCK decisions |
| Pre-execution review | `security/review.py` | ✅ Done | Command + code review hooks |
| Docker sandbox | `security/sandbox.py` | ✅ Done | Isolated container execution |
| Git checkpoint/rollback | `security/checkpoint.py` | ✅ Done | Auto-checkpoint + rollback |
| Secret detection | `security scan-secrets` | ✅ Done | Pre-commit scanning |
| Dependency vuln scan | `security scan-deps` | ✅ Done | CVE scanning |

### Sprint 22-24: CLI Architecture Refactor (EPIC-003) (v2.6-2.7)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Command extraction | `commands/` module | ✅ Done | 12 command modules |
| Sprint commands | `sprint list/complete` | ✅ Done | Sprint management |
| Release commands | `release plan/checklist/prep` | ✅ Done | Release engineering |
| Template commands | `template check/list` | ✅ Done | Template validation |
| Core module | `core/` directory | ✅ Done | ops, utils, config, hooks |
| Session management | `session check/status` | ✅ Done | Session detection + context |
| Compaction recovery | `compaction snapshot/check/recover` | ✅ Done | Context compaction handling |
| Upgrade command | `upgrade` | ✅ Done | Version migrations |
| Parser consolidation | `flows/parser.py` | ✅ Done | Unified v1+v2 flow parser |
| V1 deprecation | - | ✅ Done | Deprecation warnings |

### Sprint 25: Token Budget System (v2.8.0)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| tiktoken integration | - | ✅ Done | Token counting dependency |
| Token estimation | `tokens.py` | ✅ Done | count_tokens, estimate_task_tokens |
| Budget commands | `budget estimate/status/check` | ✅ Done | CLI for token estimation |
| Session budget | `session status` | ✅ Done | Progress bar in status |
| Pre-task hook | `check_token_budget` | ✅ Done | Warns before large tasks |

### Sprint 25.5-25.6: Skill System Enhancement (v2.8.1)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Skill export | `skill export` | ✅ Done | Cursor/Continue/Windsurf export |
| Skill install | `skill install` | ✅ Done | From URL/path |
| Skill suggestions | `skill suggest` | ✅ Done | AI-powered suggestions |
| Skill gaps | `skill gaps` | ✅ Done | Pattern detection |
| Skill generation | `skill generate` | ✅ Done | From gaps |
| Subagent detection | - | ✅ Done | Finds .claude/agents/*.md |
| Flow deprecation warnings | `flow *` | ⚠️ Deprecated | Warnings on all flow commands |

### Sprint 26: Dogfooding & Documentation (v2.8.2)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Cross-project dogfooding | - | ✅ Done | KMasty, PCTest repos |
| Trello workflow refinement | - | ✅ Done | BPS conventions doc |
| Slash commands | `/pc-plan`, `/start-task`, `/prep-release` | ✅ Done | Claude Code commands |

### Sprint 27: Release Engineering (v2.8.3-2.8.4)
| Feature | CLI Command | Status | Notes |
|---------|-------------|--------|-------|
| Template check fix | `template check` | ✅ Done | T27.1 - ProjectRootNotFoundError handling |
| Unicode handling | `ttask *` | ✅ Done | T27.3 - UTF-8 encoding throughout |
| Version bump | - | ✅ Done | v2.8.4 |

## MCP Tools (13 total)

| Tool | Description | Parameters |
|------|-------------|------------|
| paircoder_task_list | List tasks with filters | status, plan, sprint |
| paircoder_task_next | Get next recommended task | - |
| paircoder_task_start | Start a task | task_id, agent |
| paircoder_task_complete | Complete a task | task_id, summary |
| paircoder_context_read | Read project context files | file |
| paircoder_plan_status | Get plan status | plan_id |
| paircoder_plan_list | List available plans | - |
| paircoder_orchestrate_analyze | Analyze task complexity | task_id, context, prefer_agent |
| paircoder_orchestrate_handoff | Create handoff package | task_id, from_agent, to_agent, progress_summary |
| paircoder_metrics_record | Record token usage | task_id, agent, model, input_tokens, output_tokens |
| paircoder_metrics_summary | Get metrics summary | scope, scope_id |
| paircoder_trello_sync_plan | Sync plan to Trello | plan_id, board_id, create_lists, link_cards |
| paircoder_trello_update_card | Update Trello card | task_id, action, comment |

## Skills (6+ in .claude/skills/)

| Skill | Purpose | Triggers |
|-------|---------|----------|
| designing-and-implementing | Feature development workflow | "design", "plan", "feature" |
| implementing-with-tdd | Test-driven implementation | "fix", "bug", "test" |
| reviewing-code | Code review workflow | "review", "check", "PR" |
| finishing-branches | Branch completion workflow | "finish", "merge", "complete" |
| managing-task-lifecycle | Task lifecycle with Trello sync | "work on task", "start task", "TRELLO-", "plan feature" |
| planning-with-trello | Planning with Trello integration | "plan", "sprint", "trello" |
| creating-skills | Skill creation guide | "create skill", "new skill" |

## Hooks (11 built-in)

| Hook | Event | Description |
|------|-------|-------------|
| check_token_budget | on_task_start | Warn if task exceeds budget threshold |
| start_timer | on_task_start | Start time tracking |
| stop_timer | on_task_complete | Stop time tracking |
| record_metrics | on_task_complete | Record token usage |
| record_task_completion | on_task_complete | Record estimated vs actual hours |
| record_velocity | on_task_complete | Record complexity points for velocity |
| record_token_usage | on_task_complete | Record token estimate accuracy |
| log_trello_activity | on_task_start/complete/block | Log activity to Trello card |
| sync_trello | on_task_start/complete/block | Update Trello card |
| update_state | on_task_start/complete/block | Refresh state.md |
| check_unblocked | on_task_complete | Find unblocked tasks |

## Project Structure

```
my-project/
├── .paircoder/                    # PairCoder data
│   ├── config.yaml               # Project configuration
│   ├── capabilities.yaml         # LLM capability manifest
│   ├── context/                  # Project context files
│   │   ├── project.md           # Project overview
│   │   ├── workflow.md          # Workflow guidelines
│   │   └── state.md             # Current state
│   ├── plans/                    # Plan files (.plan.yaml)
│   ├── tasks/                    # Task files (.task.md)
│   └── history/                  # Archives, metrics
├── .claude/                       # Claude Code native
│   ├── skills/                   # Model-invoked skills
│   │   ├── designing-and-implementing/SKILL.md
│   │   ├── implementing-with-tdd/SKILL.md
│   │   ├── reviewing-code/SKILL.md
│   │   ├── finishing-branches/SKILL.md
│   │   ├── managing-task-lifecycle/SKILL.md
│   │   └── planning-with-trello/SKILL.md
│   ├── agents/                   # Custom subagents
│   │   ├── planner.md
│   │   ├── reviewer.md
│   │   └── security.md
│   └── commands/                 # Slash commands
│       ├── pc-plan.md
│       ├── start-task.md
│       └── prep-release.md
├── AGENTS.md                      # Universal AI entry point
├── CLAUDE.md                      # Claude Code pointer
└── docs/                          # Documentation
```

## CLI Architecture Diagram

```
                          ┌─────────────────────────────────────────────────────┐
                          │                  USER INTERFACE                     │
                          │    $ bpsai-pair <command>  |  MCP Server (stdio)    │
                          └───────────────────────────┬─────────────────────────┘
                                                      │
                          ┌───────────────────────────▼─────────────────────────┐
                          │                    cli.py                           │
                          │   Typer app • Sub-app registration • Help system    │
                          └───────────────────────────┬─────────────────────────┘
                                                      │
        ┌────────────────────────────────────────────────────────────────────────┐
        │                         COMMAND MODULES                                │
        └────────────────────────────────────────────────────────────────────────┘
        ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
        │commands/ │ │planning/ │ │ sprint/  │ │ release/ │ │  trello/ │
        │  core    │ │  plan    │ │  sprint  │ │ release  │ │  trello  │
        │  preset  │ │  task    │ │ complete │ │ template │ │  ttask   │
        │ session  │ │  intent  │ │          │ │   prep   │ │          │
        │  budget  │ │ standup  │ │          │ │          │ │          │
        │  skills  │ │          │ │          │ │          │ │          │
        └─────┬────┘ └─────┬────┘ └────┬─────┘ └────┬─────┘ └─────┬────┘
              │            │           │            │             │
        ┌────────────────────────────────────────────────────────────────────────┐
        │                         CORE INFRASTRUCTURE                            │
        │  ┌──────────────────────────────────────────────────────────────────┐  │
        │  │                          core/                                   │  │
        │  │  config.py    hooks.py    ops.py    presets.py    utils.py       │  │
        │  │  (settings)   (11 hooks)  (git/fs)  (templates)   (utilities)    │  │
        │  └──────────────────────────────────────────────────────────────────┘  │
        │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
        │  │ tokens.py   │ │ session.py  │ │ metrics.py  │ │compaction.py│       │
        │  │ (tiktoken)  │ │ (detection) │ │ (tracking)  │ │ (recovery)  │       │
        │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘       │
        └────────────────────────────────────────────────────────────────────────┘
                                          │
        ┌────────────────────────────────────────────────────────────────────────┐
        │                        DOMAIN MODULES                                  │
        │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐ │
        │  │  skills/  │ │orchestrate│ │  github/  │ │ security/ │ │  flows/  │ │
        │  │ validator │ │  routing  │ │    PR     │ │ sandbox   │ │  parser  │ │
        │  │  export   │ │  handoff  │ │  issues   │ │ allowlist │ │(deprec.) │ │
        │  │  install  │ │           │ │           │ │           │ │          │ │
        │  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └──────────┘ │
        └────────────────────────────────────────────────────────────────────────┘
                                          │
        ┌────────────────────────────────────────────────────────────────────────┐
        │                      EXTERNAL INTEGRATIONS                             │
        │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
        │  │  Trello API   │  │  GitHub API   │  │  Toggl API    │               │
        │  │ (cards/boards)│  │  (PRs/issues) │  │(time tracking)│               │
        │  └───────────────┘  └───────────────┘  └───────────────┘               │
        └────────────────────────────────────────────────────────────────────────┘
```

## CLI Module Structure (tools/cli/bpsai_pair/)

```
bpsai_pair/
├── __init__.py             # Package exports
├── __main__.py             # Entry point (4 lines)
├── cli.py                  # Sub-app registration (~200 lines)
├── tokens.py               # Token estimation (tiktoken)
├── session.py              # Session detection and management
├── compaction.py           # Context compaction recovery
├── metrics.py              # MetricsCollector, VelocityTracker, TokenFeedbackTracker
├── core/                   # Shared infrastructure
│   ├── __init__.py        # Module exports and re-exports
│   ├── config.py          # Configuration loading and management
│   ├── constants.py       # Application constants
│   ├── hooks.py           # Hook system (11 hooks including check_token_budget)
│   ├── ops.py             # Git and file operations (find_project_root)
│   ├── presets.py         # Preset system for project templates
│   └── utils.py           # Merged utilities (repo_root, project_files, etc.)
├── commands/               # Extracted from cli.py
│   ├── __init__.py        # Command exports
│   ├── core.py            # init, feature, pack, status, validate, ci
│   ├── preset.py          # preset list/show/preview
│   ├── config.py          # config validate/update/show
│   ├── orchestrate.py     # orchestrate task/analyze/handoff/etc
│   ├── metrics.py         # metrics summary/task/breakdown/etc
│   ├── timer.py           # timer start/stop/status/show/summary
│   ├── benchmark.py       # benchmark run/results/compare/list
│   ├── cache.py           # cache stats/clear/invalidate
│   ├── mcp.py             # mcp serve/tools/test
│   ├── flow.py            # flow list/show/run/validate (deprecated)
│   ├── security.py        # security scan-secrets/pre-commit/etc
│   ├── session.py         # session check/status, compaction commands
│   ├── budget.py          # budget estimate/status/check
│   └── upgrade.py         # upgrade command
├── skills/                 # Skill management
│   ├── validator.py       # SkillValidator class
│   ├── exporter.py        # Cross-platform export
│   ├── installer.py       # Skill installation
│   ├── suggestion.py      # AI-powered suggestions
│   ├── gap_detector.py    # Pattern detection
│   ├── generator.py       # Skill generation
│   └── cli_commands.py    # skill validate/list/export/install/suggest/gaps/generate
├── flows/                  # Flow definitions (deprecated)
│   ├── __init__.py        # V1/V2 exports
│   ├── models.py          # V1 Flow, Step models (backward compat)
│   └── parser.py          # Unified v1+v2 parser with deprecation
├── planning/               # Planning system
│   ├── commands.py        # plan/task/intent/standup CLI commands
│   ├── models.py          # Plan, Task, Sprint models
│   ├── parser.py          # YAML/MD file parsers
│   ├── state.py           # StateManager
│   ├── standup.py         # Standup generation logic
│   └── intent_detection.py # Intent classification logic
├── sprint/                 # Sprint management
│   └── commands.py        # sprint list/complete
├── release/                # Release engineering
│   ├── commands.py        # release plan/checklist/prep
│   └── template.py        # template check/list
├── trello/                 # Trello integration
│   ├── commands.py        # trello connect/status/etc
│   ├── task_commands.py   # ttask list/show/done/etc
│   └── activity.py        # TrelloActivityLogger
├── github/                 # GitHub integration
│   └── commands.py        # github status/create/merge/etc
├── migrate.py              # Migration commands
├── integrations/           # External integrations
│   └── time_tracking.py   # Toggl integration
└── security/               # Security module
    ├── allowlist.py       # Command allowlist
    ├── review.py          # Pre-execution review
    ├── sandbox.py         # Docker sandbox
    └── checkpoint.py      # Git checkpoint/rollback
```

## Configuration (config.yaml)

```yaml
version: "2.8"

project:
  name: "project-name"
  description: "Project description"
  primary_goal: "Main objective"
  coverage_target: 80

workflow:
  default_branch_type: "feature"
  main_branch: "main"
  context_dir: ".paircoder/context"
  plans_dir: ".paircoder/plans"
  tasks_dir: ".paircoder/tasks"

models:
  navigator: claude-opus-4-5
  driver: claude-sonnet-4-5
  reviewer: claude-sonnet-4-5

routing:
  by_complexity:
    trivial:   { max_score: 20,  model: claude-haiku-4-5 }
    simple:    { max_score: 40,  model: claude-haiku-4-5 }
    moderate:  { max_score: 60,  model: claude-sonnet-4-5 }
    complex:   { max_score: 80,  model: claude-opus-4-5 }
    epic:      { max_score: 100, model: claude-opus-4-5 }

metrics:
  enabled: true
  store_path: .paircoder/history/metrics.jsonl

token_budget:
  warning_threshold: 75   # Warn when task estimated above this %
  critical_threshold: 90  # Critical when above this %

hooks:
  enabled: true
  on_task_start:
    - check_token_budget
    - start_timer
    - sync_trello
    - update_state
  on_task_complete:
    - stop_timer
    - record_metrics
    - record_task_completion
    - record_velocity
    - sync_trello
    - update_state
    - check_unblocked
  on_task_block:
    - sync_trello
    - update_state
```

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| Core CLI | 50+ | ✅ Pass |
| Planning | 40+ | ✅ Pass |
| Orchestration | 30+ | ✅ Pass |
| Intent | 37 | ✅ Pass |
| Autonomous | 19 | ✅ Pass |
| Metrics | 20+ | ✅ Pass |
| Time Tracking | 15+ | ✅ Pass |
| Benchmarks | 15+ | ✅ Pass |
| Cache | 14 | ✅ Pass |
| Trello | 50+ | ✅ Pass |
| GitHub | 25+ | ✅ Pass |
| Standup | 10+ | ✅ Pass |
| Presets | 27 | ✅ Pass |
| MCP | 29 | ✅ Pass |
| **Security (Sprint 15)** | **129** | ✅ Pass |
| - Allowlist | 39 | ✅ Pass |
| - Review | 35 | ✅ Pass |
| - Sandbox | 35 | ✅ Pass |
| - Checkpoint | 20 | ✅ Pass |
| **Flows (Sprint 24)** | **33** | ✅ Pass |
| **Tokens (Sprint 25)** | **28** | ✅ Pass |
| **Budget Commands** | **15** | ✅ Pass |
| **Session/Budget** | **4** | ✅ Pass |
| **Hooks** | **6** | ✅ Pass |
| **Skills (Sprint 25.5-25.6)** | **45+** | ✅ Pass |
| - Validator | 15 | ✅ Pass |
| - Exporter | 12 | ✅ Pass |
| - Installer | 8 | ✅ Pass |
| - Suggestion | 10 | ✅ Pass |
| **Total** | **2050+** | ✅ Pass |
