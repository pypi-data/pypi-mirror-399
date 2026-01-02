Show the current or next task to work on.

If `$ARGUMENTS` is provided, show that specific task:
```bash
bpsai-pair task show $ARGUMENTS
```

Otherwise, find the next priority task:
```bash
bpsai-pair task next
```

Then read the task file from `.paircoder/tasks/` and summarize:
1. Task ID and title
2. Priority and complexity
3. Acceptance criteria
4. Implementation notes (if any)
