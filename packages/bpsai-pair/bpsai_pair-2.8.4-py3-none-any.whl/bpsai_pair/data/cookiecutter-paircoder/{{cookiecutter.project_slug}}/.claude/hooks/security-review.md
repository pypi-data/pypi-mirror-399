---
name: security-review
description: Pre-execution security review for commands and code changes
trigger: before bash, before git commit, before PR creation
---

# Security Review Hook

This hook provides pre-execution security review to prevent dangerous operations and catch security vulnerabilities before they are executed or committed.

## What It Does

### Command Review (`pre_execute`)

Before executing bash commands, the hook:

1. **Checks against allowlist** - Safe commands (git status, pytest, ls) proceed automatically
2. **Blocks dangerous commands** - rm -rf /, curl | bash, sudo rm are blocked
3. **Flags review-required commands** - git push, pip install require confirmation

### Code Change Review (`review_diff`, `review_code`)

Before commits and PRs, the hook scans for:

1. **Hardcoded Secrets**
   - API keys, passwords, tokens
   - AWS credentials (AKIA patterns)
   - Private keys (PEM format)
   - JWT tokens
   - Database connection strings
   - Slack webhooks

2. **Injection Vulnerabilities**
   - SQL injection (f-strings in queries)
   - Command injection (os.system, subprocess with shell=True)
   - Path traversal (../)

## Usage

### Python API

```python
from bpsai_pair.security import SecurityReviewHook, CodeChangeReviewer

# Command review
hook = SecurityReviewHook()
result = hook.pre_execute("git push origin main")

if result.is_blocked:
    print(f"Blocked: {result.reason}")
    print(f"Fixes: {result.suggested_fixes}")
elif result.has_warnings:
    print(f"Warnings: {result.warnings}")
else:
    # Safe to proceed
    execute_command()

# Code review
reviewer = CodeChangeReviewer()
result = reviewer.review_diff(git_diff_output)

if result.is_blocked:
    print(f"Security issues found: {result.reason}")
```

### With Audit Logging

```python
hook = SecurityReviewHook(enable_logging=True)
hook.pre_execute("rm -rf /")

# Check audit log
for entry in hook.audit_log:
    print(f"{entry['timestamp']}: {entry['command']} - {'allowed' if entry['allowed'] else 'blocked'}")
```

### Custom Allowlist

```python
from bpsai_pair.security import AllowlistManager, SecurityReviewHook

allowlist = AllowlistManager(config_path=Path(".paircoder/security/allowlist.yaml"))
hook = SecurityReviewHook(allowlist=allowlist)
```

## Result Types

### ReviewResult

```python
@dataclass
class ReviewResult:
    allowed: bool           # Can the operation proceed?
    reason: str             # Why blocked (if blocked)
    warnings: list[str]     # Warnings (if allowed with concerns)
    suggested_fixes: list[str]  # How to fix the issue
```

### Factory Methods

- `ReviewResult.allow()` - Create allowed result
- `ReviewResult.block(reason, suggested_fixes)` - Create blocked result
- `ReviewResult.warn(warnings)` - Create allowed result with warnings

### Properties

- `result.is_blocked` - True if operation should not proceed
- `result.has_warnings` - True if there are warnings to show

## Command Classifications

### Always Allowed (no prompt)
- `git status`, `git diff`, `git log`, `git branch`
- `pytest`, `python -m pytest`
- `bpsai-pair *`
- `ls`, `cat`, `head`, `tail`, `grep`, `find`

### Requires Review (user confirmation)
- `git push`, `git commit`, `git merge`
- `pip install`, `npm install`
- `docker run`, `docker build`
- `curl`, `wget` (without pipe to shell)

### Always Blocked (rejected)
- `rm -rf /`, `rm -rf ~`
- `sudo rm *`
- `curl | bash`, `wget | sh`
- `docker --privileged`
- `chmod 777`

## Secret Detection Patterns

The hook detects these secret patterns:

| Type | Pattern | Example |
|------|---------|---------|
| API Key | `api_key = "..."` | `api_key = "sk-1234"` |
| AWS Key | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| GitHub Token | `ghp_[A-Za-z0-9]{36}` | `ghp_xxxx...` |
| JWT | `eyJ...` | Bearer token |
| Private Key | `-----BEGIN...KEY-----` | RSA/SSH keys |
| DB URL | `protocol://user:pass@host` | Connection strings |

## Integration with Claude Code

This hook integrates with Claude Code's permission system via the security agent defined in `.claude/agents/security.md`.

The recommended integration points are:

1. **Pre-bash hook**: Review commands before execution
2. **Pre-commit hook**: Scan staged changes for secrets
3. **Pre-PR hook**: Full security review before PR creation

## Configuration

Configure via `.paircoder/security/allowlist.yaml`:

```yaml
commands:
  always_allowed:
    - git status
    - pytest
  require_review:
    - git push
  always_blocked:
    - rm -rf /
  patterns:
    blocked:
      - 'curl.*\|.*sh'
    review:
      - 'rm -rf'
```

## SOC2 Compliance

This hook supports SOC2 compliance controls:

| Control | Description | Implementation |
|---------|-------------|----------------|
| CC6.1 | Access Control | Block unauthorized commands |
| CC6.6 | External Threats | Block dangerous downloads |
| CC7.1 | Change Management | Review before commits |
| CC7.2 | Change Detection | Scan all code changes |
| CC8.1 | Infrastructure Protection | Block destructive ops |
