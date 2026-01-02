---
name: trello-aware-planning
version: 1
description: >
  Plan features and create tasks in Trello. Break down work into
  manageable cards and organize sprints.
when_to_use:
  - Planning a new feature with Trello
  - Breaking down work into tasks
  - Organizing sprint backlog
  - Creating cards during design phase
roles:
  navigator: { primary: true }
  driver: { primary: false }
triggers:
  - plan_feature
  - create_tasks
  - organize_sprint
  - breakdown_work
requires:
  tools:
    - bpsai-pair CLI
  context:
    - Trello connection (bpsai-pair trello connect)
    - Active board (bpsai-pair trello use-board)
tags:
  - trello
  - planning
  - tasks
---

# Trello-Aware Planning

Plan features and create tasks in Trello, integrated with PairCoder's planning system.

## Preconditions

Before starting this flow:

- [ ] Connected to Trello: `bpsai-pair trello status`
- [ ] Board configured with appropriate lists
- [ ] Feature/work to plan is understood

---

## Phase 1 - Understand the Work

### Step 1.1: Gather Requirements

Before creating cards, clarify:

1. **What**: Describe the feature in 2-3 sentences
2. **Why**: What problem does it solve?
3. **Who**: Who benefits from this?
4. **Scope**: What's in/out of scope?

### Step 1.2: Review Existing Board

```bash
# Check current board state
bpsai-pair trello lists

# See what's already in backlog
bpsai-pair ttask list --status backlog

# Check for related cards
bpsai-pair ttask list --list "Sprint"
```

### Step 1.3: Identify Constraints

- Dependencies on other work
- Technical constraints
- Timeline expectations

---

## Phase 2 - Design the Approach

### Step 2.1: High-Level Design

Before task breakdown:

1. Identify major components
2. Define interfaces/contracts
3. Consider implementation options
4. Select recommended approach

### Step 2.2: Document Decision

If significant, create an ADR or design doc:

```
templates/adr.md -> docs/adr/XXXX-decision.md
```

---

## Phase 3 - Break Down into Tasks

### Step 3.1: Task Sizing Guidelines

| Size | Duration | Description |
|------|----------|-------------|
| Small | 15-30 min | Single function, simple change |
| Medium | 30-60 min | Module, multiple related changes |
| Large | 1-2 hours | Feature component |

**Avoid tasks larger than 2 hours** - break them down further.

### Step 3.2: Define Each Task

For each task, prepare:

```markdown
**Title**: [Action verb] [component] [outcome]
**Description**:
- What needs to be done
- Where in codebase
- Special considerations

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

**Priority**: P0 (must) / P1 (should) / P2 (could)
**Dependencies**: None / Other task
```

### Step 3.3: Order by Dependencies

1. Foundation tasks first (setup, interfaces)
2. Core implementation tasks
3. Integration tasks
4. Polish/documentation tasks

---

## Phase 4 - Create in Trello

### Option A: Manual Card Creation

For each task, create a Trello card with:
- Clear title (action-oriented)
- Description with requirements
- Checklist for acceptance criteria
- Priority label if using labels
- Dependencies in checklist if needed

### Option B: Use PairCoder CLI

Create a local plan first:

```bash
# Create plan
bpsai-pair plan new feature-name --type feature --title "Feature Title"

# Add tasks
bpsai-pair plan add-task feature-name --id TASK-001 --title "First task"
bpsai-pair plan add-task feature-name --id TASK-002 --title "Second task"
```

Then create corresponding Trello cards manually.

---

## Phase 5 - Organize the Sprint

### Step 5.1: Prioritize

Order tasks by:
1. **P0 - Must Have**: Required for feature to work
2. **P1 - Should Have**: Important but shippable without
3. **P2 - Nice to Have**: Future enhancement

### Step 5.2: Consider Capacity

```
Sprint Days × Hours/Day × Team Size = Available Hours
Available Hours × 0.7 = Realistic Capacity (70% efficiency)
```

### Step 5.3: Move to Sprint

```bash
# Move priority items to Sprint list
bpsai-pair ttask move TRELLO-123 --list "Sprint"
bpsai-pair ttask move TRELLO-124 --list "Sprint"
```

### Step 5.4: Verify Sprint

```bash
# Review sprint contents
bpsai-pair ttask list --status sprint
```

---

## Phase 6 - Document the Plan

### Step 6.1: Update Local State

```bash
bpsai-pair context-sync \
    --last "Planned feature: <name>, created X tasks" \
    --next "Start with TRELLO-XXX: <first task>"
```

### Step 6.2: Create Plan File (Optional)

For larger features:

```yaml
# .paircoder/plans/plan-YYYY-MM-feature.plan.yaml
id: plan-YYYY-MM-feature
title: "Feature Name"
type: feature
status: in_progress
trello_cards:
  - TRELLO-123
  - TRELLO-124
  - TRELLO-125
goals:
  - Goal 1
  - Goal 2
```

---

## Quick Reference

### Planning Commands

```bash
# View board
bpsai-pair trello lists
bpsai-pair ttask list --status backlog

# Move tasks
bpsai-pair ttask move TRELLO-123 --list "Sprint"

# PairCoder planning
bpsai-pair plan new feature-x --type feature
bpsai-pair plan add-task feature-x --id TASK-001 --title "Task 1"
```

### Task Template

```markdown
**Title**: Implement user validation

**Description**:
Add validation for user registration form fields.
Validate: email format, password strength, username uniqueness.

**Acceptance Criteria**:
- [ ] Email validation with proper regex
- [ ] Password requires 8+ chars, number, special char
- [ ] Username uniqueness check against database
- [ ] Error messages shown inline

**Priority**: P0
**Dependencies**: TRELLO-100 (user model)
```

---

## Completion Checklist

- [ ] Requirements gathered and understood
- [ ] High-level approach designed
- [ ] Work broken into 2-hour max tasks
- [ ] Each task has clear acceptance criteria
- [ ] Tasks ordered by dependency
- [ ] Sprint populated with priority items
- [ ] Local state updated
- [ ] Plan file created (if needed)

---

## Best Practices

### DO
- Keep tasks small and focused
- Include clear acceptance criteria
- Set realistic priorities
- Consider dependencies
- Document the plan

### DON'T
- Create vague tasks ("fix stuff")
- Skip acceptance criteria
- Overload the sprint
- Ignore dependencies
- Plan too far ahead
