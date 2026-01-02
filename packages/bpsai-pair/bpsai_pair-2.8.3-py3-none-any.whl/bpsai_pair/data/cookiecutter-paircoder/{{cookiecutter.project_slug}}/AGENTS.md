# AGENTS.md

## Project Overview

<!-- CUSTOMIZE: Replace with your project description -->
PairCoder CLI - A structured development workflow tool for human-AI pair programming.

## Quick Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check . && ruff format --check .

# Build documentation
mkdocs build
```

## Code Conventions

- Python 3.9+ with type hints on all public functions
- Docstrings in Google format for modules, classes, and public functions
- Tests in `tests/` mirroring `src/` structure
- Use `pathlib.Path` for file operations, not `os.path`
- Prefer dataclasses over plain dicts for structured data

## Testing Requirements

- All tests must pass before commits: `pytest`
- New code requires corresponding tests
- Minimum 80% coverage for new modules
- Integration tests for CLI commands

---

## PairCoder Structured Development

This project uses **PairCoder v2** for structured development workflows. Before starting any work, understand the current state and follow the appropriate workflow.

### Step 1: Check Current State

**Read `.paircoder/context/state.md`** to understand:
- Active plan and current sprint
- In-progress and pending tasks  
- Any blockers or dependencies

Example state check:
```markdown
## Current Focus
- Plan: plan-2025-01-paircoder-v2-upgrade
- Sprint: sprint-5
- Next task: TASK-020 (P0)
```

### Step 2: Understand the Project

Read these context files:
- `.paircoder/context/project.md` - Project overview, constraints, architecture
- `.paircoder/context/workflow.md` - Branch conventions, commit format, DoD

### Step 3: Select a Workflow

Workflows in `.paircoder/flows/` define how to approach different types of work:

| Workflow | Use When |
|----------|----------|
| `design-plan-implement.flow.md` | New features requiring design |
| `tdd-implement.flow.md` | Bug fixes or well-defined tasks |
| `code-review.flow.md` | Reviewing code changes |
| `finish-branch.flow.md` | Completing and merging work |

### Step 4: Work on Tasks

Tasks are in `.paircoder/tasks/{plan-slug}/`:

```markdown
# TASK-XXX.task.md structure
---
id: TASK-XXX
status: pending | in_progress | done | blocked
priority: P0 | P1 | P2
---

# Objective
What needs to be done

# Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

**Task Status Updates:**
- Set `status: in_progress` when starting
- Set `status: done` when complete
- Set `status: blocked` with blocker notes if stuck

### Step 5: Follow Definition of Done

Before marking a task complete:
- [ ] All acceptance criteria met
- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check .`)
- [ ] Documentation updated if needed
- [ ] Task file updated with `status: done`

---

## Workflow Quick Reference

### For New Features (design-plan-implement)

1. **Clarify**: Restate the goal, identify affected components
2. **Design**: Propose 2-3 approaches with trade-offs
3. **Plan**: Break into tasks with acceptance criteria
4. **Implement**: Write code following TDD where possible
5. **Verify**: Run tests, update documentation

### For Bug Fixes (tdd-implement)

1. **Reproduce**: Write a failing test
2. **Fix**: Implement minimal fix
3. **Verify**: All tests pass
4. **Refactor**: Clean up if needed

### For Code Review (code-review)

1. **Context**: Understand the PR's purpose
2. **Review**: Check correctness, style, tests
3. **Feedback**: Provide actionable comments
4. **Approve**: When criteria met

---

## Important Files Reference

```
.paircoder/
├── config.yaml              # PairCoder configuration
├── capabilities.yaml        # LLM capability manifest
├── context/
│   ├── project.md          # ← READ THIS: Project overview
│   ├── workflow.md         # ← READ THIS: Development workflow
│   └── state.md            # ← READ THIS: Current state
├── flows/                   # Workflow definitions
├── plans/                   # Plan YAML files
└── tasks/                   # Task files by plan
```

---

## CLI Commands (if bpsai-pair installed)

```bash
# View current status
bpsai-pair status

# List available flows
bpsai-pair flow list

# Get next priority task
bpsai-pair task next

# View specific task
bpsai-pair task show TASK-XXX

# Pack context for handoff
bpsai-pair pack --output context.tgz
```

---

## PR Guidelines

- **Title format**: `[TASK-XXX] Brief description`
- **Description**: Include task ID, what changed, how to test
- **Tests**: All tests must pass
- **Review**: Request review when ready

---

## Security Considerations

- Never commit secrets or API keys
- Use environment variables for configuration
- Sanitize user inputs in CLI commands
- Review dependencies for vulnerabilities
