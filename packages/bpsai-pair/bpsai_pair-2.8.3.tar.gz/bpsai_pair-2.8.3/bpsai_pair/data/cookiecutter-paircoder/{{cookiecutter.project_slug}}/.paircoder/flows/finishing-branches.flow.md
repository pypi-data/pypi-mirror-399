---
name: finish-branch
version: 1
description: >
  Finalize a feature branch for merge. Final verification, cleanup,
  and preparation for integration.
when_to_use:
  - Work is complete and reviewed
  - Ready to merge to main
  - User says "done", "finished", "ready to merge"
roles:
  driver:
    primary: true
    description: Performs final verification and cleanup
triggers:
  - pre_merge
  - work_complete
  - user_says_done
requires:
  tools:
    - git
  context:
    - .paircoder/context/state.md
tags:
  - finish
  - merge
  - cleanup
---

# Finish Branch Flow

## Preconditions

Before starting this flow:

- [ ] All planned work is complete
- [ ] Code has been reviewed (self or peer)
- [ ] All tests pass
- [ ] You're on the feature branch

---

## Phase 1 — Final Verification

### Step 1.1: Confirm Branch

```bash
git branch --show-current
```

Ensure you're on the feature branch, not `main`.

### Step 1.2: Run All Tests

```bash
pytest -v
```

**Gate:** All tests must pass.

### Step 1.3: Run Linter/Type Checker

```bash
# If configured
ruff check .
mypy .
```

### Step 1.4: Check for Uncommitted Changes

```bash
git status
```

If there are uncommitted changes, either:
- Commit them with appropriate message
- Stash them: `git stash`
- Discard them: `git checkout -- .`

---

## Phase 2 — Sync with Main

### Step 2.1: Fetch Latest Main

```bash
git fetch origin main
```

### Step 2.2: Check for Conflicts

```bash
git log origin/main..HEAD --oneline  # Your commits
git log HEAD..origin/main --oneline  # Their commits
```

### Step 2.3: Rebase or Merge (if needed)

If main has moved:

```bash
# Option A: Rebase (cleaner history)
git rebase origin/main

# Option B: Merge (preserves history)
git merge origin/main
```

### Step 2.4: Re-run Tests After Sync

```bash
pytest -v
```

**Gate:** Tests still pass after sync.

---

## Phase 3 — Cleanup

### Step 3.1: Review Commit History

```bash
git log origin/main..HEAD --oneline
```

Consider squashing if there are many small commits:

```bash
git rebase -i origin/main
```

### Step 3.2: Check for Debug Artifacts

Search for and remove:
- `print()` debug statements
- `console.log()` statements
- `TODO` comments that should be addressed
- Commented-out code

### Step 3.3: Update Documentation (if needed)

- README changes?
- API documentation?
- Configuration examples?

---

## Phase 4 — Update State

### Step 4.1: Update Plan Status

If working from a plan, update `.paircoder/plans/<plan>.plan.yaml`:

```yaml
status: complete  # was: in_progress
```

### Step 4.2: Update State File

Update `.paircoder/context/state.md`:

```markdown
## Active Plan

**Plan:** `plan-YYYY-MM-<slug>`
**Status:** complete

## What Was Just Done

- Completed all tasks for <feature>
- Passed review
- Ready to merge

## What's Next

- Merge to main
- Deploy (if applicable)
- Start next plan
```

### Step 4.3: Final Commit

If any cleanup was done:

```bash
git add .
git commit -m "chore: finalize branch for merge"
```

---

## Phase 5 — Merge Preparation

### Step 5.1: Push Branch

```bash
git push origin <branch-name>
```

### Step 5.2: Create PR/MR (if using)

If your workflow uses Pull Requests:

1. Create PR on GitHub/GitLab/etc.
2. Fill in description with:
   - What changed
   - How to test
   - Related issues/tasks

### Step 5.3: Or Merge Directly (if permitted)

```bash
git checkout main
git merge <branch-name>
git push origin main
```

---

## Phase 6 — Post-Merge Cleanup

### Step 6.1: Delete Feature Branch (optional)

```bash
# Local
git branch -d <branch-name>

# Remote
git push origin --delete <branch-name>
```

### Step 6.2: Archive Plan (optional)

Move completed plan to archive or update status:

```yaml
status: archived
completed_at: 2025-01-15T12:00:00Z
```

---

## Completion Checklist

### Before Merge
- [ ] All tests pass
- [ ] Code reviewed
- [ ] No lint errors
- [ ] Synced with main
- [ ] No merge conflicts
- [ ] Documentation updated
- [ ] State updated

### After Merge
- [ ] Main branch tests pass
- [ ] Feature branch cleaned up
- [ ] Plan marked complete

---

## Quick Commands Reference

```bash
# Check status
git status
git branch --show-current

# Sync with main
git fetch origin main
git rebase origin/main

# Run tests
pytest -v

# Push and merge
git push origin <branch>
git checkout main
git merge <branch>
git push origin main

# Cleanup
git branch -d <branch>
git push origin --delete <branch>
```

---

## Troubleshooting

### Merge Conflicts

1. Identify conflicting files: `git status`
2. Open each file and resolve conflicts (look for `<<<<<<<`)
3. Mark resolved: `git add <file>`
4. Continue: `git rebase --continue` or `git commit`

### Tests Fail After Rebase

1. Don't panic
2. Identify which tests fail
3. Check if it's a conflict resolution error
4. Fix and amend: `git commit --amend`

### Accidentally Merged Wrong Branch

```bash
git revert -m 1 <merge-commit>
```
