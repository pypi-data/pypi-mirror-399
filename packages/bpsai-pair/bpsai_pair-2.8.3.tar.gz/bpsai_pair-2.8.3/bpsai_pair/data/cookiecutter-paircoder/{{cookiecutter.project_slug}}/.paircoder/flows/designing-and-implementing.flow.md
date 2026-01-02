---
name: design-plan-implement
version: 1
description: >
  Turn a feature request into a validated design, a concrete implementation plan,
  and a sequence of TDD-anchored tasks.
when_to_use:
  - Starting a new feature
  - Substantive refactoring
  - Work that will take more than 30 minutes
  - User describes something they want to build
roles:
  navigator:
    primary: true
    description: Leads design and planning phases
  driver:
    primary: true
    description: Leads implementation phase
  reviewer:
    description: Reviews completed work
triggers:
  - feature_request
  - large_refactor
  - user_describes_feature
requires:
  tools:
    - git
  context:
    - .paircoder/context/project.md
    - .paircoder/context/workflow.md
    - .paircoder/context/state.md
tags:
  - design
  - planning
  - implementation
  - feature
---

# Design → Plan → Implement Flow

## Preconditions

Before starting this flow:

- [ ] The request is substantial (not a trivial fix or typo)
- [ ] You understand the project context (read `project.md`)
- [ ] The repo is on a clean working tree or feature branch
- [ ] Tests can be run locally (if applicable)

**Do NOT use this flow for:**
- Trivial changes (typos, comment fixes, small tweaks)
- Documentation-only changes
- Simple bug fixes (use `tdd-implement` instead)

---

## Phase 1 — Clarify & Design (Navigator)

### Step 1.1: Understand the Request

1. Restate the goal in 1-3 sentences
2. Identify affected components/directories
3. List explicit non-goals (what we're NOT doing)

### Step 1.2: Explore Designs

1. Propose 2-3 alternative approaches
2. For each approach, list:
   - Pros
   - Cons
   - Estimated complexity (trivial/simple/moderate/complex/epic)
   - Risk factors

### Step 1.3: Select Design

1. Recommend one approach with justification
2. Confirm with the user before proceeding
3. Document the design decision

**Gate:** User approves design before proceeding to Phase 2.

---

## Phase 2 — Plan (Navigator)

### Step 2.1: Decompose into Tasks

Break the design into 5-20 tasks, each taking 2-20 minutes:

For each task, specify:
- **ID**: TASK-NNN
- **Title**: Brief description
- **Type**: feature | bugfix | refactor | test | docs
- **Priority**: P0 (must have) | P1 (should have) | P2 (nice to have)
- **Complexity**: 0-100 score
- **Files touched**: Expected files to modify
- **Verification**: How to confirm task is done

### Step 2.2: Create Plan File

Save the plan to `.paircoder/plans/plan-YYYY-MM-<slug>.plan.yaml`

```yaml
id: plan-YYYY-MM-<slug>
title: "<Feature name>"
type: feature
status: planned
flows:
  - design-plan-implement
goals:
  - <Goal 1>
  - <Goal 2>
tasks:
  - id: TASK-001
    title: "..."
    priority: P0
    complexity: 40
```

### Step 2.3: Create Task Files

For each task, create `.paircoder/tasks/<plan-slug>/TASK-NNN.task.md`:

```markdown
---
id: TASK-NNN
plan: plan-YYYY-MM-<slug>
title: "Task title"
type: feature
priority: P0
complexity: 40
status: pending
---

# Objective

What this task accomplishes.

# Implementation Plan

- Step 1
- Step 2

# Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

# Verification

How to verify this task is complete.
```

### Step 2.4: Update State

Update `.paircoder/context/state.md`:
- Set active plan
- List tasks with initial status
- Note "What's Next"

**Gate:** Plan and tasks created before proceeding to Phase 3.

---

## Phase 3 — Implement (Driver)

### Step 3.1: For Each Task

1. Update task status to `in_progress`
2. Run the `tdd-implement` subflow:
   - Write failing test (if applicable)
   - Write minimal code to pass
   - Refactor if needed
3. Verify the task meets acceptance criteria
4. Update task status to `done`
5. Commit with proper message: `feat(<scope>): <description>`

### Step 3.2: After All Tasks Complete

1. Run full test suite
2. Run linter/type checker (if configured)
3. Update plan status to `complete`

---

## Phase 4 — Review (Reviewer)

### Step 4.1: Self-Review or Request Review

Run the `review` flow:
- Check code quality
- Verify all acceptance criteria met
- Ensure tests pass
- Check for missing edge cases

### Step 4.2: Finish

Run the `finish-branch` flow:
- Final verification
- Update state
- Prepare for merge

---

## Completion Checklist

- [ ] Design documented and approved
- [ ] Plan created with all tasks
- [ ] All tasks completed and verified
- [ ] Tests pass
- [ ] Code reviewed
- [ ] State updated
- [ ] Ready to merge

---

## Subflows Referenced

- `tdd-implement` — For implementing each task
- `review` — For code review
- `finish-branch` — For completing the branch
