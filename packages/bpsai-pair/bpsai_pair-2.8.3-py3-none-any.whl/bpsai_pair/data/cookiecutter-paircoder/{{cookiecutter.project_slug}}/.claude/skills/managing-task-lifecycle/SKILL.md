---
name: managing-task-lifecycle
description: Use when starting, pausing, completing, or transitioning task status in the development workflow.
---

# PairCoder Task Lifecycle

## Decision Tree: Which Command to Use?

```
Is Trello connected? (check: bpsai-pair trello status)
│
├── YES → Use `ttask` commands (primary)
│   ├── Start:    bpsai-pair ttask start TRELLO-XX
│   ├── Complete: bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"
│   └── Block:    bpsai-pair ttask block TRELLO-XX --reason "..."
│
└── NO → Use `task update` commands
    ├── Start:    bpsai-pair task update TASK-XXX --status in_progress
    ├── Complete: bpsai-pair task update TASK-XXX --status done
    └── Block:    bpsai-pair task update TASK-XXX --status blocked
```

**Rule of thumb:** If you see TRELLO-XX IDs, use `ttask`. If you only have TASK-XXX IDs, use `task update`.

## CRITICAL: Always Use CLI Commands

Task state changes MUST go through the CLI to trigger hooks (Trello sync, timers, state updates).

**Never** just edit task files or say "marking as done" - run the command.

## Starting a Task

**For Trello projects:**
```bash
bpsai-pair ttask start TRELLO-XX
```

**For non-Trello projects:**
```bash
bpsai-pair task update TASK-XXX --status in_progress
```

## During Work (Progress Updates)

```bash
bpsai-pair ttask comment TRELLO-XX "Completed API endpoints, starting tests"
```

This adds a comment to the Trello card without changing status.

## Completing a Task

### For Trello Projects (Recommended)

Use `ttask done` - it handles everything in one command:

```bash
bpsai-pair ttask done TRELLO-XX --summary "What was accomplished" --list "Deployed/Done"
```

This single command will:
- ✓ Move Trello card to "Deployed/Done" list
- ✓ Auto-check ALL acceptance criteria items
- ✓ Add completion summary to card
- ✓ Update local task file status
- ✓ Trigger all completion hooks (timer, metrics, state.md)

**You do NOT need to also run `task update --status done`** - `ttask done` handles it.

### For Non-Trello Projects

Use `task update`:

```bash
bpsai-pair task update TASK-XXX --status done
```

### Common Mistakes

| Mistake | Why It's Wrong | Correct Approach |
|---------|---------------|------------------|
| Using only `task update` on Trello projects | Doesn't check AC on Trello card | Use `ttask done` instead |
| Using both commands on Trello projects | Unnecessary duplication | Just use `ttask done` |
| Using `ttask` on non-Trello projects | Commands won't work | Use `task update` |

## Quick Reference

### For Trello-connected projects (preferred)

| Scenario | Command |
|----------|---------|
| Starting a task | `ttask start TRELLO-XX` |
| Progress updates | `ttask comment TRELLO-XX "message"` |
| Completing a task | `ttask done TRELLO-XX --summary "..." --list "Deployed/Done"` |
| Blocking a task | `ttask block TRELLO-XX --reason "..."` |

### For non-Trello projects

| Scenario | Command |
|----------|---------|
| Starting a task | `task update TASK-XXX --status in_progress` |
| Completing a task | `task update TASK-XXX --status done` |
| Blocking a task | `task update TASK-XXX --status blocked` |

## Task Status Values

| Status | Meaning | Trello List |
|--------|---------|-------------|
| `pending` | Not started | Backlog / Planned |
| `in_progress` | Currently working | In Progress |
| `blocked` | Waiting on something | Issues / Blocked |
| `review` | Ready for review | Review |
| `done` | Completed | Deployed / Done |

## Workflow Checklist

### When Starting a Task

**For Trello projects:**
1. Run: `bpsai-pair ttask start TRELLO-XX`
2. Verify Trello card moved
3. Read the task file for implementation plan
4. Begin work

**For non-Trello projects:**
1. Run: `bpsai-pair task update TASK-XXX --status in_progress`
2. Read the task file for implementation plan
3. Begin work

### When Completing a Task

**For Trello projects:**
1. Ensure tests pass: `pytest -v`
2. Find card ID: `bpsai-pair ttask list`
3. Complete: `bpsai-pair ttask done TRELLO-XX --summary "..." --list "Deployed/Done"`
4. Update state.md with what was done
5. Commit changes with task ID in message

**For non-Trello projects:**
1. Ensure tests pass: `pytest -v`
2. Complete: `bpsai-pair task update TASK-XXX --status done`
3. Update state.md with what was done
4. Commit changes with task ID in message

## Trello Sync Commands

```bash
# Check Trello connection status
bpsai-pair trello status

# Sync plan to Trello (creates/updates cards)
bpsai-pair plan sync-trello PLAN-ID

# Force refresh from Trello
bpsai-pair trello refresh
```
