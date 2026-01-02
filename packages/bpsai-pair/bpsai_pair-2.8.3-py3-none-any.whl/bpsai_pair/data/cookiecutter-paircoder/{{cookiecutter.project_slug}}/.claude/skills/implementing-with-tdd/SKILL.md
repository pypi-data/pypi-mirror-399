---
name: implementing-with-tdd
description: Use when implementing bug fixes, features, or any code changes where test-first development is appropriate.
---

# Test-Driven Development (TDD) Workflow

A disciplined approach: write tests first, implement to pass, then refactor.

## When This Skill Activates

This skill is invoked when:
- User asks to fix a bug
- User asks to implement a specific, well-defined feature
- User mentions TDD or test-driven development
- Task has clear acceptance criteria
- Keywords: fix, bug, implement, test, TDD, failing

## The TDD Cycle

```
┌─────────────────────────────────────────┐
│                                         │
│   RED → GREEN → REFACTOR → (repeat)     │
│                                         │
│   1. Write failing test                 │
│   2. Write minimum code to pass         │
│   3. Refactor for clarity               │
│                                         │
└─────────────────────────────────────────┘
```

## Phase 1: RED - Write Failing Test

### 1.1 Understand the Requirement
Before writing tests:
1. Read the task/bug description carefully
2. Identify the expected behavior
3. Find existing related tests:
   ```bash
   grep -r "test_.*relevant" tests/
   ```

### 1.2 Write the Test
```python
def test_feature_does_expected_thing():
    """Test that [feature] produces [expected result]."""
    # Arrange: Set up test data
    input_data = create_test_input()
    
    # Act: Call the function under test
    result = function_under_test(input_data)
    
    # Assert: Verify expected behavior
    assert result == expected_output
    assert result.property == expected_value
```

### 1.3 Run and Confirm Failure
```bash
# Run the specific test
pytest tests/test_module.py::test_feature_does_expected_thing -v

# Expected: FAILED (if test is correct)
```

**Important**: If the test passes immediately, either:
- The feature already exists (check first!)
- The test is not testing what you think

## Phase 2: GREEN - Make It Pass

### 2.1 Write Minimum Code
Implement the **simplest possible code** that makes the test pass:
- Don't optimize
- Don't handle edge cases yet
- Don't refactor
- Just make it work

### 2.2 Run Tests Again
```bash
# Run the test
pytest tests/test_module.py::test_feature_does_expected_thing -v

# Expected: PASSED
```

### 2.3 Run Full Test Suite
Ensure you didn't break anything:
```bash
pytest
```

## Phase 3: REFACTOR - Clean Up

### 3.1 Improve Code Quality
Now that tests pass, improve the code:
- Extract helper functions
- Improve variable names
- Remove duplication
- Add type hints
- Add docstrings

### 3.2 Refactoring Rules
- **Keep tests passing** at all times
- Make small changes, run tests after each
- Don't add new functionality during refactor

### 3.3 Final Test Run
```bash
# Full suite passes
pytest

# Linting passes
ruff check .
```

## Phase 4: Iterate

### 4.1 Add Edge Cases
Write additional tests for:
- Empty inputs
- Invalid inputs
- Boundary conditions
- Error conditions

### 4.2 Repeat the Cycle
For each edge case:
1. RED: Write failing test
2. GREEN: Implement handler
3. REFACTOR: Clean up

## Bug Fix Workflow

When fixing bugs, the TDD cycle is slightly modified:

### Step 1: Reproduce with Test
```python
def test_bug_is_fixed():
    """Regression test for issue #XXX."""
    # This test reproduces the bug
    result = buggy_function(problematic_input)
    assert result == correct_behavior  # Currently fails
```

### Step 2: Confirm Bug Exists
```bash
pytest tests/test_module.py::test_bug_is_fixed -v
# Should FAIL, confirming the bug
```

### Step 3: Fix the Bug
Implement the minimal fix to pass the test.

### Step 4: Verify Fix
```bash
# Specific test passes
pytest tests/test_module.py::test_bug_is_fixed -v

# No regressions
pytest
```

## Quick Reference

### Test File Location
```
src/module/feature.py → tests/test_feature.py
src/cli/commands.py → tests/test_cli_commands.py
```

### Test Naming Convention
```python
def test_<function>_<scenario>_<expected_result>():
    """Test that <function> <scenario> results in <expected>."""
```

### Common Assertions
```python
assert result == expected           # Equality
assert result is not None           # Not None
assert "substring" in result        # Contains
assert result.startswith("prefix")  # Starts with
assert len(result) == 5             # Length
assert isinstance(result, MyClass)  # Type
pytest.raises(ValueError)           # Exception
```

### Pytest Commands
```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_module.py

# Run specific test
pytest tests/test_module.py::test_function

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Coverage report
pytest --cov=src
```

## Task Integration

### When Starting a Task
1. Set task status: `status: in_progress`
2. Read acceptance criteria
3. Write test for first criterion
4. Begin TDD cycle

### When Completing a Task
1. All acceptance criteria have tests
2. All tests pass
3. Code is refactored
4. Update task: `status: done`
5. Commit: `[TASK-XXX] Description`

## Anti-Patterns to Avoid

❌ **Don't write tests after code**
- You lose the design benefits of TDD
- Tests may just verify what code does, not what it should do

❌ **Don't skip the RED phase**
- If test passes immediately, you haven't learned anything
- You might not be testing the right thing

❌ **Don't refactor while RED**
- Fix the test first
- Refactoring requires green tests as safety net

❌ **Don't write multiple tests at once**
- One test at a time
- Keeps focus and provides clear feedback

## Recording Your Work

### Before Starting
Mark the task as started:

**Via CLI:**
```bash
bpsai-pair task update TASK-XXX --status in_progress
```

**Via MCP (if available):**
```json
Tool: paircoder_task_start
Input: {"task_id": "TASK-XXX", "agent": "claude-code"}
```

### During Implementation
Track test counts as you work. When completing, include:
- Number of tests added
- Files modified

### After Completing
Record your work with test metrics:

**Via CLI:**
```bash
bpsai-pair task update TASK-XXX --status done
```

**Via MCP (if available):**
```json
Tool: paircoder_task_complete
Input: {
  "task_id": "TASK-XXX",
  "summary": "Fixed bug X with 5 new tests",
  "input_tokens": 10000,
  "output_tokens": 2000,
  "model": "claude-sonnet-4-5"
}
```

### Commit Format
```bash
git commit -m "[TASK-XXX] Fix: Description

- Added N tests
- Fixed edge case handling"
```
