---
name: tdd-implement
version: 1
description: >
  Test-Driven Development implementation flow. Write failing tests first,
  then minimal code to pass, then refactor.
when_to_use:
  - Implementing a planned task
  - Fixing a bug
  - Adding a new function or feature
  - Any code change that should have tests
roles:
  driver: { primary: true }
  navigator: { primary: false }
triggers:
  - bugfix
  - implement_task
  - code_change
tags:
  - implementation
  - tdd
  - testing
---

# TDD Implementation Flow

## Preconditions

Before starting this flow:

- [ ] You have a clear task/goal
- [ ] Tests can be run locally
- [ ] You understand the acceptance criteria

---

## The TDD Cycle

```
RED -> GREEN -> REFACTOR -> (repeat)
```

---

## Phase 1 - Red (Write Failing Test)

### Step 1.1: Identify What to Test

Based on the task, identify:
- The function/method/behavior to implement
- Expected inputs and outputs
- Edge cases and error conditions

### Step 1.2: Write the Test

```python
def test_<what_it_does>():
    # Arrange
    <setup test data>

    # Act
    result = <call the function>

    # Assert
    assert result == <expected>
```

### Step 1.3: Run and Confirm Failure

```bash
pytest tests/test_<module>.py::<test_name> -v
```

**Gate:** Test fails with expected error before proceeding.

---

## Phase 2 - Green (Make Test Pass)

### Step 2.1: Write Minimal Code

Write the **simplest possible code** that makes the test pass:
- Don't optimize yet
- Don't handle cases not covered by tests
- Don't add features "while you're in there"

### Step 2.2: Run Test

```bash
pytest tests/test_<module>.py::<test_name> -v
```

**Gate:** Test passes before proceeding to refactor.

---

## Phase 3 - Refactor (Improve Code)

### Step 3.1: Review the Code

Now that tests pass, consider:
- Is the code readable?
- Are there duplicate patterns to extract?
- Are variable/function names clear?

### Step 3.2: Refactor Safely

Make improvements while keeping tests green.

### Step 3.3: Verify Tests Still Pass

```bash
pytest tests/ -v
```

**Gate:** All tests still pass after refactoring.

---

## Phase 4 - Completion

### Step 4.1: Run Full Test Suite

```bash
pytest -v
```

### Step 4.2: Update State

Update `.paircoder/context/state.md`:
- Mark task as `done`
- Note what was implemented

### Step 4.3: Commit

```bash
git add .
git commit -m "<type>(<scope>): <description>"
```

---

## Completion Checklist

- [ ] Failing test written first
- [ ] Minimal code makes test pass
- [ ] Code refactored for clarity
- [ ] Full test suite passes
- [ ] State updated
- [ ] Changes committed
