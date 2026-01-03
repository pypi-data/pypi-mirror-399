---
description: Enter Driver role to work on a task with pre-flight checks, verification gates, and proper completion
allowed-tools: Bash(bpsai-pair:*), Bash(git:*), Bash(pytest:*), Bash(python:*)
argument-hint: <task-id>
---

# Driver Role - Task Execution Workflow

You are now in **Driver role**. Your job is to complete the task with bulletproof verification.

The task ID is: `$ARGUMENTS`

## Phase 1: Pre-Flight Checks

Before starting work, verify everything is ready:

```bash
# Check budget for this task
bpsai-pair budget check --task $ARGUMENTS

# Verify task exists and get details
bpsai-pair task show $ARGUMENTS

# Check for blockers (dependencies)
bpsai-pair task list --status blocked
```

**If budget check warns**: Inform user of token estimate, ask to proceed.
**If task not found**: Check if it's a Trello ID (TRELLO-XXX) vs local ID (T26.1).

## Phase 2: Start Task

```bash
# Create checkpoint before starting (safety net)
# Note: This may be automatic via hooks, but explicit is safer

# Start the task locally
bpsai-pair task update $ARGUMENTS --status in_progress

# If there's a linked Trello card, start it there too
bpsai-pair ttask start <TRELLO-ID> 2>/dev/null || true
```

Read the task file to understand requirements:
```bash
cat .paircoder/tasks/*/$ARGUMENTS.task.md 2>/dev/null || \
cat .paircoder/tasks/$ARGUMENTS.task.md 2>/dev/null || \
bpsai-pair task show $ARGUMENTS
```

## Phase 3: Work on Task

### Understand Acceptance Criteria

From the task file or Trello card, identify ALL acceptance criteria. These MUST be completed before the task can be marked done.

### Follow TDD Approach (when applicable)

1. **Red**: Write failing test for the requirement
2. **Green**: Write minimal code to pass
3. **Refactor**: Clean up while tests pass

```bash
# Run tests frequently
pytest tests/ -x --tb=short

# Or for specific test file
pytest tests/test_<module>.py -v
```

### Track Progress

As you complete each acceptance criterion:
```bash
# Check off items in Trello (if linked)
bpsai-pair trello check <TRELLO-ID> "<acceptance criterion text>"
```

## Phase 4: Pre-Completion Verification

**CRITICAL**: Before marking task complete, verify ALL gates pass.

### 4.1 Run Tests
```bash
# Full test suite must pass
pytest tests/ --tb=short

# Check coverage if required
pytest tests/ --cov=bpsai_pair --cov-report=term-missing
```

### 4.2 Verify Acceptance Criteria

```bash
# Check what's still unchecked on Trello
bpsai-pair ttask show <TRELLO-ID>
```

If ANY acceptance criteria are unchecked, complete them before proceeding.

### 4.3 Self-Review

Before completing, verify:
- [ ] All acceptance criteria addressed
- [ ] Tests pass
- [ ] No obvious bugs or TODOs left
- [ ] Code follows project conventions

## Phase 5: Complete Task (ENFORCEMENT GATE)

**This is where enforcement happens. Use `--strict` to ensure AC verification.**

```bash
# Complete the Trello card with strict AC verification
bpsai-pair ttask done <TRELLO-ID> --strict --summary "<brief summary of work done>"
```

**If `--strict` fails**: You have unchecked acceptance criteria. Go back and complete them.

**NEVER use `--force`** unless explicitly instructed by the user. Forced completions are logged.

After Trello completion succeeds:
```bash
# Update local task status
bpsai-pair task update $ARGUMENTS --status done
```

## Phase 6: Update State (NON-NEGOTIABLE)

**You MUST update state.md after completing any task.**

```bash
# Update state with what was done and what's next
bpsai-pair context-sync \
    --last "$ARGUMENTS: <brief description of what was accomplished>" \
    --next "<next task ID or 'Ready for next task'>"
```

Or manually edit `.paircoder/context/state.md`:
- Add entry under "What Was Just Done"
- Update "What's Next"
- Mark task as done in any task lists

## Phase 7: Report Completion

Provide completion summary to user:

```
✅ **Task Complete**: $ARGUMENTS

**Summary**: <what was accomplished>
**Time**: <actual time if tracked>
**Tests**: All passing
**Acceptance Criteria**: All verified ✓

**Files Changed**:
- path/to/file1.py
- path/to/file2.py

**Next Task**: <next task ID> or "Sprint complete!"
```

## Error Recovery

### If tests fail during completion:
1. Fix the failing tests
2. Re-run verification
3. Then complete

### If AC verification fails (`--strict` blocks):
1. Check which items are unchecked: `bpsai-pair ttask show <TRELLO-ID>`
2. Complete the missing work
3. Check off the items: `bpsai-pair trello check <TRELLO-ID> "<item>"`
4. Retry completion

### If you need to force completion (LAST RESORT):
```bash
# This logs a bypass - only use if user explicitly approves
bpsai-pair ttask done <TRELLO-ID> --force --summary "<summary>"
```

## Task ID Formats

This command accepts multiple ID formats:
- `T26.1` - Sprint task format (preferred)
- `TASK-150` - Legacy format
- `TRELLO-456` - Trello card ID (for ttask commands)

When working with both local and Trello:
- Use `T26.1` for `bpsai-pair task` commands
- Use `TRELLO-XXX` for `bpsai-pair ttask` commands

## Reminders

- **NEVER** mark a task complete without updating state.md
- **ALWAYS** use `--strict` for `ttask done` (enforcement gate)
- **ALWAYS** run tests before completing
- Checkpoints are created automatically on task start (if hooks enabled)
- Forced bypasses are logged to `.paircoder/history/bypass_log.jsonl`
