---
name: reviewing-code
description: Use when reviewing code changes, checking PRs, or evaluating code quality.
---

# Code Review Workflow

A systematic approach to reviewing code for correctness, quality, and maintainability.

## When This Skill Activates

This skill is invoked when:
- User asks to review code or a PR
- User asks to check recent changes
- User wants feedback on implementation
- Keywords: review, check, PR, pull request, evaluate, feedback, look at

## Review Philosophy

Good code review is:
- **Constructive**: Focus on improvement, not criticism
- **Specific**: Point to exact lines and suggest fixes
- **Educational**: Explain *why* something should change
- **Prioritized**: Distinguish must-fix from nice-to-have

## Phase 1: Understand Context

### 1.1 Gather Information
```bash
# See what changed
git diff main...HEAD --stat

# View the actual changes
git diff main...HEAD

# Check commit history
git log main..HEAD --oneline
```

### 1.2 Understand the Purpose
Before reviewing code:
1. Read PR description or task file
2. Understand what problem this solves
3. Check acceptance criteria if available

### 1.3 Review Scope
Identify:
- Which files changed
- What type of change (feature, bugfix, refactor)
- Impact on existing functionality

## Phase 2: Review Checklist

### 2.1 Correctness
- [ ] Does the code do what it's supposed to?
- [ ] Are edge cases handled?
- [ ] Are error conditions handled gracefully?
- [ ] Are there off-by-one errors?
- [ ] Are null/None cases handled?

### 2.2 Tests
- [ ] Are there tests for new functionality?
- [ ] Do tests cover edge cases?
- [ ] Do tests actually verify behavior (not just execute code)?
- [ ] Are test names descriptive?

```bash
# Run tests to verify they pass
pytest

# Check coverage for changed files
pytest --cov=src --cov-report=term-missing
```

### 2.3 Code Quality
- [ ] Is the code readable and self-documenting?
- [ ] Are variable/function names meaningful?
- [ ] Is there unnecessary complexity?
- [ ] Is there code duplication?
- [ ] Are functions focused (single responsibility)?

### 2.4 Style & Conventions
- [ ] Does code follow project style guide?
- [ ] Are type hints present on public functions?
- [ ] Are docstrings present where needed?
- [ ] Does linting pass?

```bash
# Check linting
ruff check .

# Check formatting
ruff format --check .
```

### 2.5 Security
- [ ] No hardcoded secrets or credentials
- [ ] User inputs are validated/sanitized
- [ ] No SQL injection vulnerabilities
- [ ] No path traversal vulnerabilities
- [ ] Dependencies don't have known vulnerabilities

### 2.6 Performance
- [ ] No obvious O(n²) when O(n) is possible
- [ ] No unnecessary database queries in loops
- [ ] Large data operations are efficient
- [ ] Caching used where appropriate

### 2.7 Documentation
- [ ] Public APIs are documented
- [ ] Complex logic has explanatory comments
- [ ] README updated if needed
- [ ] CHANGELOG updated for user-facing changes

## Phase 3: Provide Feedback

### 3.1 Feedback Format
Structure feedback by severity:

#### 🔴 Must Fix (Blocking)
Issues that must be resolved before merge:
- Bugs or incorrect behavior
- Security vulnerabilities
- Missing tests for critical paths
- Breaking changes without migration

#### 🟡 Should Fix (Non-blocking)
Issues that should be addressed:
- Code quality concerns
- Minor edge cases
- Documentation gaps
- Style inconsistencies

#### 🟢 Consider (Suggestions)
Optional improvements:
- Alternative approaches
- Performance optimizations
- Future-proofing suggestions

### 3.2 Feedback Template
```markdown
## Code Review: [PR/Change Description]

### Summary
Brief overview of what was reviewed and overall assessment.

### 🔴 Must Fix
1. **[File:Line]** - Description of issue
   - Why it's a problem
   - Suggested fix

### 🟡 Should Fix
1. **[File:Line]** - Description
   - Suggestion

### 🟢 Consider
1. **[File:Line]** - Suggestion for improvement

### Positive Notes
- What was done well
- Good patterns observed

### Verdict
- [ ] Approve
- [ ] Approve with comments
- [ ] Request changes
```

### 3.3 Be Constructive
Instead of:
> "This code is bad"

Say:
> "Consider extracting this logic into a helper function for better testability. For example: `def validate_input(data): ...`"

## Quick Review Commands

```bash
# View changes in specific file
git diff main...HEAD -- path/to/file.py

# Find TODOs in changed files
git diff main...HEAD --name-only | xargs grep -n "TODO\|FIXME"

# Check for debug statements
git diff main...HEAD | grep -n "print(\|console.log\|debugger"

# View file history
git log -p --follow -- path/to/file.py
```

## Common Issues to Watch For

### Python Specific
- Using `==` instead of `is` for None comparison
- Mutable default arguments (`def f(x=[])`)
- Not closing file handles (use `with` statement)
- Catching bare exceptions (`except:`)
- Not using context managers

### General
- Magic numbers (use named constants)
- Long functions (> 50 lines usually needs splitting)
- Deep nesting (> 3 levels)
- Comments that describe "what" not "why"
- Dead code or unused imports

## Self-Review Checklist

When reviewing your own code before submitting:
1. Re-read the diff as if you're seeing it for the first time
2. Run all tests
3. Run linting
4. Check for debug statements
5. Verify documentation
6. Confirm task acceptance criteria are met

## Recording Your Work

### Tracking Review Time
While code review isn't a tracked task, you can log time spent:

**Via CLI:**
```bash
# Check current project metrics
bpsai-pair status
```

**Via MCP (if available):**
```json
Tool: paircoder_metrics_record
Input: {
  "task_id": "review",
  "agent": "claude-code",
  "model": "claude-sonnet-4-5",
  "input_tokens": 5000,
  "output_tokens": 1000,
  "action_type": "review"
}
```

### Recording Review Comments
When providing feedback on a PR:
1. Use the feedback template format above
2. Note files reviewed and issues found
3. Track time if significant

### After Review Complete
```bash
# Update project state if needed
bpsai-pair context-sync --last "Reviewed PR #XXX - 3 issues found"
```
