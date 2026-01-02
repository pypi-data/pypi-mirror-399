---
name: planning-with-trello
description: Use when planning features, organizing sprints, or syncing work with Trello boards.
---

# Trello-Aware Planning Skill

## Purpose
Create and manage development plans with automatic Trello synchronization following BPS AI Software project management guidelines.

## Triggers
- "plan feature", "create plan", "new project"
- "create tasks", "break down", "sprint planning"
- "sync to trello", "create board"

## BPS Trello Guidelines

### Board Structure (7 Lists Max)
1. **Intake / Backlog** - New ideas, bugs, tickets
2. **Planned / Ready** - Selected for upcoming work (1-2 weeks)
3. **In Progress** - Active development
4. **Review / Testing** - Under review or verification
5. **Deployed / Done** - Completed and live
6. **Issues / Tech Debt** - Bugs, regressions, improvements
7. **Notes / Ops Log** - Deployment notes, decisions

### Card Title Format
```
[Stack] Task Name
```
Examples:
- `[CLI] Implement MCP server core`
- `[Docs] Update README with v2.4 features`
- `[Flask] Add authentication middleware`

### Effort Estimation (Not Story Points)
Use throughput-based sizing:
- **S (Small)** - Few hours, single file changes (complexity 0-25)
- **M (Medium)** - Half day to full day (complexity 26-50)
- **L (Large)** - Multiple days, cross-cutting (complexity 51+)

### Labels by Stack
| Label | Color | Use For |
|-------|-------|---------|
| Frontend | 🟩 Green | React, UI, UX |
| Backend | 🟦 Blue | Flask, API, Python |
| Worker | 🟪 Purple | Background jobs, AI pipelines |
| Deployment | 🟥 Red | CI/CD, infrastructure |
| Bug / Issue | 🟧 Orange | Bugs, runtime issues |
| Security | 🟨 Yellow | Auth, compliance |
| Documentation | 🟫 Brown | Docs, guides |
| AI / ML | ⚫ Black | Models, LLM, MCP |

## Workflow

### Phase 1: Planning

1. **Understand Requirements**
   - What problem are we solving?
   - What's the scope?
   - What are the acceptance criteria?

2. **Break Down into Tasks**
   - Each task = one unit of work
   - Tasks should be completable in 1-2 days max
   - Identify dependencies

3. **Create Plan File**
   ```bash
   bpsai-pair plan new <slug> --type feature --title "Title"
   ```

4. **Add Tasks to Plan**
   For each task:
   - Assign effort (S/M/L based on complexity)
   - Identify stack for labeling
   - Note dependencies

### Phase 2: Trello Sync

1. **Sync Plan to Trello**

   **Option A: Direct to Planned/Ready** (Recommended for sprint planning)
   ```bash
   bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready" [--board <board-id>]
   ```

   **Option B: To Intake/Backlog then move** (Default behavior)
   ```bash
   bpsai-pair plan sync-trello <plan-id> [--board <board-id>]
   ```
   Then move each card:
   ```bash
   bpsai-pair ttask move TRELLO-XX --list "Planned/Ready"
   ```

   ⚠️ **IMPORTANT:** Sprint tasks should be in "Planned/Ready", not "Intake/Backlog".
   Cards in "Intake/Backlog" are just ideas, not selected for work.

2. **Verify Card Creation**
   - Cards should be in "Planned / Ready" list (not Intake/Backlog)
   - Title format: `[Stack] Task Name`
   - Description includes objective and acceptance criteria
   - Labels match stack
   - Effort field set

### Phase 3: Execution Tracking

When starting a task:
```bash
bpsai-pair task update <task-id> --status in_progress
# Or via MCP: paircoder_task_start
```
- Card moves to "In Progress"
- Timer starts automatically (if hooks enabled)

When completing a task:
```bash
bpsai-pair task update <task-id> --status done
# Or via MCP: paircoder_task_complete
```
- Card moves to "Deployed / Done"
- Metrics recorded
- Timer stopped

## Recording Your Work

### Before Planning Session
```bash
# Check current plans
bpsai-pair plan list

# Check what's already in progress
bpsai-pair task list --status in_progress
```

### After Creating Plan
```bash
# Verify plan created
bpsai-pair plan status <plan-id>

# Sync to Trello
bpsai-pair plan sync-trello <plan-id> --dry-run  # Preview first
bpsai-pair plan sync-trello <plan-id>            # Actually sync
```

### Via MCP (if available)
```json
Tool: paircoder_plan_status
Input: {"plan_id": "plan-2025-01-feature-xyz"}

Tool: paircoder_trello_sync_plan
Input: {"plan_id": "plan-2025-01-feature-xyz", "create_lists": true}
```

## Weekly Summary

At end of each week, create summary in "Notes / Ops Log":

```markdown
### Week {N} Summary ({date range})
✅ {X} Completed
⚙️ {Y} In Progress
🐞 {Z} Issues

**Highlights:**
- Completed feature X
- Fixed critical bug Y

**Blockers:**
- Waiting on API access for Z
```

## Best Practices

1. **Keep tasks small** - If > 2 days, break it down further
2. **Clear titles** - Anyone should understand from title alone
3. **Track throughput** - Count cards completed, not points estimated
4. **Update daily** - 5 min to move cards and add notes
5. **Weekly review** - 15 min to summarize and plan ahead
