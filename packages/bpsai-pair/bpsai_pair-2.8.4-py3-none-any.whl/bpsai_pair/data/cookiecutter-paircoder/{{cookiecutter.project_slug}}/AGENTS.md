> **This is a pointer file.** Full context is in `.paircoder/`

## Quick Start for AI Agents

1. **Read capabilities**: `.paircoder/capabilities.yaml`
2. **Understand project**: `.paircoder/context/project.md`
3. **Check current state**: `.paircoder/context/state.md`
4. **Follow workflows**: `.paircoder/context/workflow.md`
5. **Use skills**: `.claude/skills/` for structured workflows

## What You Can Do

See `.paircoder/capabilities.yaml` for the full list. Key capabilities:

- **Create plans** for features, bugs, refactors
- **Use skills** for structured workflows (design, implement, review)
- **Update state** to track progress
- **Pack context** for handoff
- **Export skills** to other platforms

## Skills

Skills in `.claude/skills/` provide structured workflows:

| Skill | Purpose |
|-------|---------|
| `designing-and-implementing` | Feature development |
| `implementing-with-tdd` | Test-driven development |
| `reviewing-code` | Code review |
| `finishing-branches` | Branch completion |
| `managing-task-lifecycle` | Task workflow with Trello |
| `planning-with-trello` | Sprint planning |



## Current Status

Check `.paircoder/context/state.md` for:
- Active plan and sprint
- Task statuses
- What was just done
- What's next
- Any blockers

## Project Structure


## How to Help

1. Read the context files listed above
2. Check if a skill applies to the user's request
3. Suggest or follow the appropriate skill
4. Update `state.md` after completing work

## CLI Commands

```bash
bpsai-pair status              # Show current status
bpsai-pair plan show <id>      # Show plan details
bpsai-pair skill list          # List available skills
bpsai-pair task next           # Get next recommended task
bpsai-pair budget status       # Check token budget
```

## Skill Commands

```bash
bpsai-pair skill list              # List all skills
bpsai-pair skill validate          # Validate skill format
bpsai-pair skill export --format cursor  # Export to Cursor
bpsai-pair skill suggest           # Get AI suggestions
bpsai-pair skill gaps              # Detect skill gaps
```
