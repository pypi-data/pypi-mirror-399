---
name: review
version: 1
description: >
  Code review flow. Systematically check code quality, correctness,
  and completeness before merging.
when_to_use:
  - Before merging a feature branch
  - When asked to review code
  - Self-review before requesting human review
  - After completing a set of tasks
roles:
  reviewer:
    primary: true
    description: Reviews code for quality and correctness
triggers:
  - review_request
  - pre_merge
  - user_asks_review
requires:
  tools:
    - git
  context:
    - .paircoder/context/state.md
tags:
  - review
  - quality
  - verification
---

# Code Review Flow

## Preconditions

Before starting this flow:

- [ ] Code is committed (or staged)
- [ ] You can see the diff (`git diff` or `git diff --staged`)
- [ ] You understand the goal of the changes

---

## Phase 1 — Understand the Context

### Step 1.1: Review the Goal

Check `.paircoder/context/state.md` or the plan:
- What was this change supposed to accomplish?
- What are the acceptance criteria?

### Step 1.2: Get the Diff

```bash
# For uncommitted changes
git diff

# For staged changes
git diff --staged

# For branch vs main
git diff main..HEAD
```

### Step 1.3: List Changed Files

```bash
git diff --name-only main..HEAD
```

---

## Phase 2 — Correctness Check

### Step 2.1: Logic Review

For each changed file, verify:

- [ ] Does the code do what it's supposed to do?
- [ ] Are there off-by-one errors?
- [ ] Are edge cases handled?
- [ ] Are error conditions handled gracefully?

### Step 2.2: Test Review

- [ ] Are there tests for the new code?
- [ ] Do the tests cover the important cases?
- [ ] Are the tests actually testing the right thing?

### Step 2.3: Run Tests

```bash
pytest -v
```

**Gate:** All tests must pass.

---

## Phase 3 — Quality Check

### Step 3.1: Code Style

- [ ] Consistent formatting
- [ ] Meaningful variable/function names
- [ ] No commented-out code
- [ ] No debug prints/logs left in

### Step 3.2: Code Structure

- [ ] Functions are focused (single responsibility)
- [ ] No excessive nesting
- [ ] No code duplication
- [ ] Appropriate use of abstractions

### Step 3.3: Documentation

- [ ] Complex logic has comments explaining why
- [ ] Public functions have docstrings
- [ ] README updated if needed

### Step 3.4: Run Linter (if configured)

```bash
ruff check <files>
# or
flake8 <files>
```

---

## Phase 4 — Security & Safety Check

### Step 4.1: Security Review

- [ ] No hardcoded secrets or credentials
- [ ] Input validation for user data
- [ ] No SQL injection vulnerabilities
- [ ] No path traversal vulnerabilities

### Step 4.2: Safety Review

- [ ] No destructive operations without confirmation
- [ ] Proper error handling (no silent failures)
- [ ] Resources properly cleaned up (files, connections)

---

## Phase 5 — Completeness Check

### Step 5.1: Acceptance Criteria

Review each acceptance criterion from the task/plan:
- [ ] All criteria met
- [ ] Nothing missing from the implementation

### Step 5.2: Integration Check

- [ ] Changes work with existing code
- [ ] No breaking changes to public APIs
- [ ] Dependencies updated if needed

### Step 5.3: State Check

- [ ] `.paircoder/context/state.md` updated
- [ ] Task marked as complete

---

## Phase 6 — Generate Review Report

### Step 6.1: Summarize Findings

Create a review summary:

```markdown
## Review Summary

**Branch:** <branch-name>
**Reviewed:** <date>

### Changes Overview
<Brief description of what changed>

### Findings

#### ✅ Passed
- <What looks good>

#### ⚠️ Suggestions
- <Improvement suggestions>

#### ❌ Issues
- <Problems that must be fixed>

### Verdict
[ ] Approved
[ ] Approved with suggestions
[ ] Changes requested
```

### Step 6.2: Communicate Results

If reviewing for someone else:
- Share the review summary
- Be constructive and specific
- Suggest fixes, don't just criticize

---

## Review Checklist (Quick Reference)

### Must Pass
- [ ] Tests pass
- [ ] No security issues
- [ ] Acceptance criteria met
- [ ] No breaking changes

### Should Check
- [ ] Code is readable
- [ ] No obvious bugs
- [ ] Edge cases handled
- [ ] Error handling appropriate

### Nice to Have
- [ ] Code is elegant
- [ ] Good test coverage
- [ ] Documentation complete
- [ ] Performance considered

---

## Common Issues to Watch For

| Issue | Signs |
|-------|-------|
| **Off-by-one** | Loops, array indices, ranges |
| **Null/None** | Missing null checks |
| **Race conditions** | Shared state, async code |
| **Resource leaks** | Files, connections not closed |
| **Error swallowing** | Empty except blocks |
| **Magic numbers** | Unexplained numeric literals |
| **Dead code** | Unreachable or unused code |

---

## Completion

After review is complete:

1. If approved: Proceed to `finish-branch` flow
2. If changes needed: Return to implementation, then re-review
3. Update state with review outcome
