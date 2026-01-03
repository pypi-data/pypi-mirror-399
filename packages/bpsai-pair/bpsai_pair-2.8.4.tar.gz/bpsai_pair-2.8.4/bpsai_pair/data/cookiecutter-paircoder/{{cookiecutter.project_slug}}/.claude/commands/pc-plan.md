---
description: Enter Navigator role to create a comprehensive plan with budget validation and Trello sync
allowed-tools: Bash(bpsai-pair:*), Bash(cat:*)
argument-hint: [description] or [backlog-file.md]
---

# Navigator Role - Planning Workflow

You are now in **Navigator role**. Your job is to create a bulletproof plan with proper validation.

## Pre-Flight Checks

First, verify we're ready to plan:

```bash
# Check current budget status
bpsai-pair budget status

# Verify Trello connection
bpsai-pair trello status
```

If budget is above 80% daily usage, warn the user before proceeding.

## Input Processing

The argument `$ARGUMENTS` can be:
1. A backlog file path (e.g., `backlog-sprint-26.md`)
2. A feature description (e.g., `"Add webhook support for notifications"`)

**If backlog file**: Read `.paircoder/context/$ARGUMENTS` or `.paircoder/docs/$ARGUMENTS`
**If description**: Use the description directly to design the plan

## Planning Workflow

### Step 1: Context Gathering

Read the planning skill and agent definition:
```bash
cat .claude/skills/planning-with-trello/SKILL.md
cat .claude/agents/planner.md
```

Read current project state:
```bash
bpsai-pair status
cat .paircoder/context/state.md
```

### Step 2: Design the Plan

Based on the input, determine:
- **Plan slug**: kebab-case identifier (e.g., `webhook-support`)
- **Plan type**: `feature` | `bugfix` | `refactor` | `chore` (NOT `maintenance`)
- **Plan title**: Human-readable title
- **Task breakdown**: 3-8 tasks with complexity estimates

### Step 3: Budget Estimation

Before creating tasks, estimate the total token budget:

```bash
# After designing tasks mentally, check if plan fits budget
bpsai-pair budget check --estimated-tokens <total_estimate>
```

If budget check fails, either:
- Reduce scope
- Split into multiple plans
- Warn user and get explicit approval

### Step 4: Create Plan and Tasks

```bash
# Create the plan
bpsai-pair plan new <slug> --type <type> --title "<title>"

# Add tasks with proper complexity and priority
bpsai-pair plan add-task <slug> \
    --id "T<sprint>.<seq>" \
    --title "<task title>" \
    --complexity <0-100> \
    --priority <P0|P1|P2|P3>

# Repeat for each task...
```

**Task ID Format**: Use `T<sprint>.<sequence>` format (e.g., T26.1, T26.2)

**Complexity Guidelines**:
- 0-20: Trivial (< 1 hour)
- 21-40: Simple (1-2 hours)  
- 41-60: Moderate (2-4 hours)
- 61-80: Complex (4-8 hours)
- 81-100: Epic (8+ hours, consider splitting)

### Step 5: Sync to Trello

```bash
# Sync plan to Trello with proper custom fields
bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready"

# Verify sync succeeded
bpsai-pair trello status
```

### Step 6: Update State

```bash
# Update state.md with new plan
bpsai-pair context-sync \
    --last "Created plan: <plan-id>" \
    --next "Ready to start: <first-task-id>"
```

### Step 7: Report Summary

Provide a summary to the user:

```
**Plan Created**: <plan-id>
**Type**: <type>
**Tasks**: <count> tasks, <total-complexity> complexity points

| ID | Title | Priority | Complexity | Estimate |
|----|-------|----------|------------|----------|
| T26.1 | ... | P0 | 35 | ~2h |
| T26.2 | ... | P1 | 55 | ~4h |

**Token Budget**: ~<estimate>K tokens (<percent>% of daily limit)
**Trello**: <count> cards created in "Planned/Ready"

Ready to start? Use `/start-task T26.1`
```

## Error Handling

- If Trello sync fails, the plan still exists locally - report partial success
- If budget check fails, DO NOT proceed without user acknowledgment
- If plan creation fails, check for duplicate slugs or invalid types

## Reminders

- Plan type must be: `feature`, `bugfix`, `refactor`, or `chore` (NOT `maintenance`)
- Always update state.md after planning
- Custom fields: Project=PairCoder, Stack=Worker/Function (for CLI work)
