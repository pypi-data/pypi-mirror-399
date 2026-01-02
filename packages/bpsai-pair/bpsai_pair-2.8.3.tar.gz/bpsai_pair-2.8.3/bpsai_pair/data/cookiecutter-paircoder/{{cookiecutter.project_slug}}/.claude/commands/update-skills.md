---
description: Analyze recent conversations and suggest skill improvements
allowed-tools: Bash(bpsai-pair skill:*)
---

Analyze the current conversation for:
1. Repeated workflows not captured in existing skills
2. Commands or patterns used frequently
3. Gaps where a skill would have helped

Then:
1. Run `bpsai-pair skill suggest` to get AI recommendations
2. Present suggestions to user with confidence scores
3. If user approves, create skill draft with `bpsai-pair skill suggest --create N`

Example workflow:
```bash
# Show skill suggestions based on session patterns
bpsai-pair skill suggest

# Create draft for suggestion #1
bpsai-pair skill suggest --create 1

# Validate the new skill
bpsai-pair skill validate
```
