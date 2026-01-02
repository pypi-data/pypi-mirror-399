---
name: paircoder-task-lifecycle
version: 1
description: >
  Manage task lifecycle with optional Trello sync. Start tasks, update progress,
  and complete work while keeping state in sync.
when_to_use:
  - Starting or completing a task
  - Working on a task (local or Trello)
  - Reporting blockers
  - Checking what to work on next
roles:
  driver: { primary: true }
  navigator: { primary: false }
triggers:
  - work_on_task
  - trello_task
  - next_task
  - finish_task
requires:
  tools:
    - bpsai-pair CLI
  context:
    - Trello connection (bpsai-pair trello connect)
    - Active board (bpsai-pair trello use-board)
tags:
  - trello
  - tasks
  - workflow
---

# Trello Task Workflow

Work on tasks managed in Trello, keeping the board in sync with your progress.

## Preconditions

Before starting this flow:

- [ ] Connected to Trello: `bpsai-pair trello status`
- [ ] Board is configured: check for "Board: <name>" in status
- [ ] You know which task to work on (or will find one)

---

## Phase 1 - Find Your Task

### Step 1.1: List Available Tasks

```bash
# Show tasks in Sprint and In Progress
bpsai-pair ttask list

# Show only AI-ready tasks (if using Agent Task custom field)
bpsai-pair ttask list --agent

# Filter by status
bpsai-pair ttask list --status sprint
```

### Step 1.2: Choose a Task

Select a task that:
- Has no unchecked dependencies (not blocked)
- Matches your capabilities
- Is highest priority available

### Step 1.3: View Task Details

```bash
bpsai-pair ttask show TRELLO-123
```

Review:
- Description and requirements
- Checklists/acceptance criteria
- Any comments or context

---

## Phase 2 - Start Work

### Step 2.1: Claim the Task

```bash
bpsai-pair ttask start TRELLO-123 --summary "Starting implementation"
```

This will:
- Move card to "In Progress" list
- Add a comment with timestamp and agent ID
- Return the card URL for reference

### Step 2.2: Understand Requirements

From the task details:
1. Identify the goal
2. List acceptance criteria
3. Note any constraints or dependencies

### Step 2.3: Plan Your Approach

Before coding:
- Break into smaller steps if needed
- Identify files to modify
- Consider test approach

---

## Phase 3 - Implementation

### Step 3.1: Choose Implementation Flow

Based on the task type:

| Task Type | Recommended Flow |
|-----------|-----------------|
| Bug fix | `tdd-implement` |
| New feature | `tdd-implement` or `design-plan-implement` |
| Refactor | `tdd-implement` |

### Step 3.2: Make Progress

Work on the implementation, committing regularly.

### Step 3.3: Log Progress (Optional)

For long-running tasks:

```bash
bpsai-pair ttask comment TRELLO-123 "Completed authentication module"
```

---

## Phase 4 - Handle Blockers

### If You Get Blocked

```bash
bpsai-pair ttask block TRELLO-123 --reason "Waiting for API credentials"
```

This will:
- Move card to "Blocked" list
- Add comment explaining the blocker
- Make the impediment visible to team

### To Unblock Later

```bash
bpsai-pair ttask move TRELLO-123 --list "In Progress"
bpsai-pair ttask comment TRELLO-123 "Blocker resolved, resuming work"
```

---

## Phase 5 - Complete the Task

### Step 5.1: Verify Completion

Before marking done:
- [ ] All acceptance criteria met
- [ ] Tests pass: `pytest -v`
- [ ] No lint errors: `ruff check .`
- [ ] Code committed

### Step 5.2: Mark Complete

```bash
# Move to In Review (default)
bpsai-pair ttask done TRELLO-123 --summary "Implemented feature with tests"

# Or move directly to Done
bpsai-pair ttask done TRELLO-123 --summary "Complete" --list "Done"
```

### Step 5.3: Update Local State

```bash
bpsai-pair context-sync \
    --last "Completed TRELLO-123: <description>" \
    --next "<next task or action>"
```

---

## Quick Reference

### Common Commands

```bash
# Check connection
bpsai-pair trello status

# List tasks
bpsai-pair ttask list
bpsai-pair ttask list --status sprint

# Work on task
bpsai-pair ttask show TRELLO-123
bpsai-pair ttask start TRELLO-123
bpsai-pair ttask comment TRELLO-123 "message"
bpsai-pair ttask done TRELLO-123 -s "Summary"

# Handle issues
bpsai-pair ttask block TRELLO-123 -r "Reason"
bpsai-pair ttask move TRELLO-123 -l "Sprint"
```

### Card ID Formats

Accepted formats:
- `TRELLO-123` (recommended)
- `123` (short ID)
- Full Trello card ID

---

## Completion Checklist

- [ ] Task claimed with `ttask start`
- [ ] Requirements understood
- [ ] Implementation complete
- [ ] Tests pass
- [ ] Task marked done with `ttask done`
- [ ] Local state updated
