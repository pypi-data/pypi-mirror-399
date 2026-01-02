---
name: designing-and-implementing
description: Use when receiving feature requests, architectural discussions, or multi-step implementation needs that require design before coding.
---

# Design → Plan → Implement

A structured workflow for developing new features with proper design consideration before coding.

## When This Skill Activates

This skill is invoked when:
- User describes a substantial feature to build
- User asks about approach or design ("how should we...")
- Work will involve multiple files or components
- Estimated implementation time > 30 minutes
- Keywords: design, plan, approach, architecture, strategy, feature

## Phase 1: Clarify & Design

### 1.1 Understand the Request
1. Restate the goal in 1-3 sentences
2. Identify affected components/files
3. List any unstated assumptions
4. Ask clarifying questions if requirements are ambiguous

### 1.2 Research Context
Before proposing solutions:
```bash
# Find relevant code
grep -r "relevant_pattern" src/
# Check existing implementations
ls -la src/relevant_module/
# Review tests for expected behavior
cat tests/test_relevant.py
```

### 1.3 Propose Solutions
Present 2-3 approaches with:
- **Approach name**: Brief description
- **Pros**: Benefits of this approach
- **Cons**: Drawbacks or risks
- **Complexity**: Low/Medium/High
- **Recommendation**: Which approach and why

### 1.4 Get Confirmation
Before proceeding to planning, confirm:
> "I recommend [Approach X] because [reasons]. Should I create a detailed plan?"

## Phase 2: Create Plan

### 2.1 Break Into Tasks
Create tasks with:
- Clear, actionable titles
- Specific acceptance criteria
- Complexity estimates (10-100 scale)
- Priority (P0 = must have, P1 = should have, P2 = nice to have)
- Dependencies on other tasks

### 2.2 Task Format
```markdown
## TASK-XXX: [Title]
**Priority**: P0 | **Complexity**: 30 | **Sprint**: sprint-N

### Objective
What this task accomplishes

### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests pass

### Dependencies
- Requires TASK-YYY (if any)

### Implementation Notes
Any relevant context or approach hints
```

### 2.3 Sequence Tasks
Order tasks to:
1. Minimize blocked work
2. Enable incremental testing
3. Group related changes

## Phase 3: Implement

### 3.1 Start Each Task
1. Update task status: `status: in_progress`
2. Create feature branch if needed: `git checkout -b feature/task-xxx`
3. Read task acceptance criteria

### 3.2 Write Tests First (TDD)
When possible:
1. Write failing test that defines success
2. Run test to confirm it fails
3. Implement minimum code to pass
4. Refactor for clarity

### 3.3 Implementation Checklist
- [ ] Code follows project conventions
- [ ] Type hints on public functions
- [ ] Docstrings on public interfaces
- [ ] No hardcoded values (use config)
- [ ] Error handling for edge cases

### 3.4 Complete Each Task
1. Run tests: `pytest`
2. Run linting: `ruff check .`
3. Update task: `status: done`
4. Commit: `git commit -m "[TASK-XXX] Description"`

## Phase 4: Verify

### 4.1 Integration Check
```bash
# Run full test suite
pytest

# Check for type errors
mypy src/

# Verify documentation builds
mkdocs build
```

### 4.2 Documentation
- Update README if public API changed
- Add docstrings for new public functions
- Update CHANGELOG if user-facing changes

### 4.3 Final Review
Before marking feature complete:
- [ ] All tasks marked done
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed (or self-review checklist)

## Quick Reference

### Phase Summary
| Phase | Focus | Output |
|-------|-------|--------|
| Clarify | Understand requirements | Confirmed approach |
| Plan | Break into tasks | Task list with criteria |
| Implement | Write code + tests | Working code |
| Verify | Ensure quality | Ready for review |

### Key Files
- Check state: `.paircoder/context/state.md`
- Project context: `.paircoder/context/project.md`
- Task files: `.paircoder/tasks/{plan-slug}/`

### Status Transitions
```
pending → in_progress → done
                ↓
             blocked (with notes)
```

## Recording Your Work

### Before Starting a Task
If this is a tracked task, mark it as started:

**Via CLI:**
```bash
bpsai-pair task update TASK-XXX --status in_progress
```

**Via MCP (if available):**
```json
Tool: paircoder_task_start
Input: {"task_id": "TASK-XXX", "agent": "claude-code"}
```

### During Planning
After creating tasks from the design phase:

```bash
# Create plan file
bpsai-pair plan new my-feature --type feature --goal "Implement feature X"

# Add tasks to plan
bpsai-pair plan add-task <plan-id> --id TASK-001 --title "Task title"

# Sync to Trello (if configured)
bpsai-pair plan sync-trello <plan-id> --board <board-id>
```

### After Completing
Record your work when the feature is done:

**Via CLI:**
```bash
bpsai-pair task update TASK-XXX --status done
```

**Via MCP (if available):**
```json
Tool: paircoder_task_complete
Input: {
  "task_id": "TASK-XXX",
  "summary": "Implemented feature with X approach",
  "input_tokens": 15000,
  "output_tokens": 3000
}
```

### If Blocked
```bash
bpsai-pair task update TASK-XXX --status blocked
# Update task file with blocking reason
```
