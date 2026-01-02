---
name: finishing-branches
description: Use when work is complete and ready for integration, merge, or PR creation.
---

# Finish Branch Workflow

A checklist-driven approach to completing work and preparing for merge.

## When This Skill Activates

This skill is invoked when:
- User says work is done and wants to merge
- User asks to finish or complete the current branch
- User wants to prepare for PR submission
- Keywords: finish, merge, complete, ship, wrap up, done, ready, PR

## Pre-Completion Checklist

### Step 1: Verify All Tests Pass

```bash
# Run full test suite
pytest

# Check for any skipped tests that should run
pytest --collect-only | grep "skip"

# Run with coverage to verify
pytest --cov=src --cov-report=term-missing
```

**Gate**: All tests must pass before proceeding.

### Step 2: Verify Linting

```bash
# Check for lint errors
ruff check .

# Check formatting
ruff format --check .

# If needed, auto-fix
ruff check --fix .
ruff format .
```

**Gate**: No lint errors allowed.

### Step 3: Verify Type Hints (if applicable)

```bash
# Run type checker
mypy src/

# Or for specific module
mypy src/module_being_changed/
```

### Step 4: Update Documentation

Check and update as needed:
- [ ] Docstrings on new/changed public functions
- [ ] README.md if public API changed
- [ ] CHANGELOG.md for user-facing changes
- [ ] Any relevant docs/ files

### Step 5: Review Changes

```bash
# See all changes from main
git diff main...HEAD

# See changed files
git diff main...HEAD --stat

# Look for debug statements to remove
git diff main...HEAD | grep -E "print\(|console\.log|debugger|TODO|FIXME"
```

### Step 6: Clean Up

Remove before committing:
- [ ] Debug print statements
- [ ] Commented-out code (unless intentional with explanation)
- [ ] Unused imports
- [ ] TODO comments that are now done

### Step 7: Update Task Status

If working on a PairCoder task:
```markdown
# In .paircoder/tasks/{plan}/TASK-XXX.task.md
status: done
```

Verify acceptance criteria are checked off:
```markdown
# Acceptance Criteria
- [x] Feature implemented
- [x] Tests written and passing
- [x] Documentation updated
```

## Commit & Push

### Commit Message Format
```
[TASK-XXX] Brief description of change

More detailed explanation if needed:
- What was changed
- Why it was changed
- Any notable decisions

Closes #issue-number (if applicable)
```

### Commit Commands
```bash
# Stage all changes
git add -A

# Or stage specific files
git add src/module.py tests/test_module.py

# Commit with message
git commit -m "[TASK-XXX] Implement feature description"

# Push to remote
git push origin feature/branch-name
```

## Create Pull Request

### PR Title Format
```
[TASK-XXX] Brief description
```

### PR Description Template
```markdown
## Summary
Brief description of what this PR does.

## Related Task
Closes TASK-XXX

## Changes
- Added X functionality
- Modified Y to support Z
- Fixed bug in W

## Testing
- [ ] Unit tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed (if applicable)

## Checklist
- [ ] Code follows project style guide
- [ ] Documentation updated
- [ ] No debug statements left
- [ ] Changelog updated (if user-facing)
```

## Post-Merge Cleanup

After PR is merged:

### Update Local Repository
```bash
# Switch to main
git checkout main

# Pull latest
git pull origin main

# Delete local feature branch
git branch -d feature/branch-name

# Delete remote branch (usually done by PR merge)
git push origin --delete feature/branch-name
```

### Archive Task (if using PairCoder)
```bash
# Archive completed task
bpsai-pair archive --task TASK-XXX
```

### Update State
Update `.paircoder/context/state.md`:
- Remove task from "In Progress"
- Note completion in recent activity

## Quick Finish Commands

```bash
# One-liner: test + lint + commit
pytest && ruff check . && git add -A && git commit -m "[TASK-XXX] Description"

# Check if ready to merge
git diff main...HEAD --stat && pytest && ruff check .
```

## Common Issues Before Merge

### Merge Conflicts
```bash
# Update from main
git fetch origin main
git rebase origin/main

# Resolve conflicts, then continue
git add <resolved-files>
git rebase --continue
```

### Failing CI
1. Check CI logs for specific failure
2. Reproduce locally: `pytest` or specific test
3. Fix issue and push update

### Forgotten Changes
```bash
# Add forgotten file to last commit
git add forgotten_file.py
git commit --amend --no-edit
git push --force-with-lease
```

## Definition of Done Checklist

Before marking complete, verify:

- [ ] All acceptance criteria met
- [ ] Tests pass locally
- [ ] Linting passes
- [ ] Type checking passes (if applicable)
- [ ] Documentation updated
- [ ] No debug code left
- [ ] Commit message follows format
- [ ] PR description complete
- [ ] Task status updated to `done`

## Recording Your Work

### Completing a Task
When ready to finish:

**Via CLI:**
```bash
# Mark task complete
bpsai-pair task update TASK-XXX --status done
```

**Via MCP (if available):**
```json
Tool: paircoder_task_complete
Input: {
  "task_id": "TASK-XXX",
  "summary": "Implemented feature X with tests",
  "input_tokens": 20000,
  "output_tokens": 5000,
  "agent": "claude-code"
}
```

### Recording Files Changed
Include in your completion summary:
- Files modified
- Tests added
- Key decisions made

### Syncing to Trello (if configured)
If the task is linked to Trello, it will auto-sync on completion if hooks are enabled.

Manual sync:
```bash
# Update card status
bpsai-pair ttask done TRELLO-XXX -s "Completed implementation"
```

### Archive After Merge
```bash
# Archive completed tasks (after PR merged)
bpsai-pair task archive --completed --plan <plan-id>
```
