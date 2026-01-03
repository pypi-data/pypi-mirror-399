---
description: Enter Release Engineer role to prepare a release with documentation verification and security checks
allowed-tools: Bash(bpsai-pair:*), Bash(git:*), Bash(pytest:*), Bash(pip:*), Bash(grep:*), Bash(diff:*), Bash(rm:*), Bash(cd:*), Bash(ls:*)
argument-hint: <version>
---

# Release Engineer Role - Release Preparation Workflow

You are now in **Release Engineer role**. Your job is to prepare a bulletproof release.

The version is: `$ARGUMENTS` (e.g., `v1.0.0` or `1.0.0`)

## Phase 1: Pre-Release Validation

### 1.1 Verify All Sprint Tasks Complete

```bash
# Check for incomplete tasks
bpsai-pair task list --status in_progress
bpsai-pair task list --status blocked

# Check current state
bpsai-pair status
```

**BLOCKER**: If any tasks are in_progress or blocked, they must be completed or moved to next sprint before release.

### 1.2 Run Full Test Suite

```bash
# All tests must pass
pytest tests/ -v --tb=short

# Check coverage meets target
pytest tests/ --cov --cov-report=term-missing
```

**BLOCKER**: Release cannot proceed if tests fail.

### 1.3 Security Scans

```bash
# Scan for accidentally committed secrets
bpsai-pair security scan-secrets

# Scan dependencies for known vulnerabilities
bpsai-pair security scan-deps
```

**BLOCKER**: Release cannot proceed if secrets are detected.
**WARNING**: Dependency vulnerabilities should be reviewed but may not block.

## Phase 2: Version Bump

Locate and update version in project files:

```bash
# Common version file locations - check which exist:
ls pyproject.toml setup.py setup.cfg package.json 2>/dev/null

# Search for current version
grep -r "version" pyproject.toml setup.py setup.cfg 2>/dev/null | head -5
grep "__version__" src/*/__init__.py */__init__.py 2>/dev/null
```

Update version in the appropriate files (without 'v' prefix).

## Phase 3: Documentation Verification

### 3.1 Required Documentation Check

```bash
# Check CHANGELOG has entry for this version
grep -A 20 "## \[$ARGUMENTS\]" CHANGELOG.md || grep -A 20 "## $ARGUMENTS" CHANGELOG.md

# Check README is current
head -100 README.md
```

### 3.2 Documentation Freshness

Check when key docs were last modified:

```bash
# Check modification dates
git log -1 --format="%ci" -- README.md
git log -1 --format="%ci" -- CHANGELOG.md
git log -1 --format="%ci" -- docs/ 2>/dev/null || echo "No docs directory"
```

**WARNING** if any required doc is older than 7 days - may need update.

### 3.3 CHANGELOG Entry

If CHANGELOG doesn't have an entry for this version, create one:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Feature 1
- Feature 2

### Changed
- Change 1

### Fixed
- Fix 1

### Removed
- (if applicable)
```

## Phase 4: Build Verification

```bash
# Clean any old builds
rm -rf dist/ build/ *.egg-info

# Build the package (Python projects)
pip install build && python -m build

# Or for Node.js projects:
# npm run build

# Verify build artifacts exist
ls -la dist/
```

## Phase 5: Create Release Checklist

Track manually:

- [ ] All sprint tasks complete
- [ ] Tests passing (100%)
- [ ] Coverage meets target
- [ ] No secrets in codebase
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] README current
- [ ] Package builds successfully

## Phase 6: Git Operations

```bash
# Stage all changes
git add -A

# Commit with release message
git commit -m "Release $ARGUMENTS"

# Create annotated tag
git tag -a "$ARGUMENTS" -m "Release $ARGUMENTS"

# Show what will be pushed
git log --oneline -5
git tag -l | tail -5
```

**DO NOT push yet** - let user review and confirm.

## Phase 7: Report Summary

Provide release summary to user:

```
📦 **Release Prepared**: $ARGUMENTS

**Pre-Release Checks**:
- ✅ All tasks complete
- ✅ Tests: XXX passed
- ✅ Coverage: XX%
- ✅ Security: Clean

**Documentation**:
- ✅ CHANGELOG: Updated
- ✅ README: Current

**Build**:
- ✅ Package built
- ✅ Build artifacts verified

**Ready to Release**:
```bash
git push origin main
git push origin $ARGUMENTS
```

Then publish (if applicable):
```bash
# PyPI
twine upload dist/*

# npm
npm publish
```
```

## Error Handling

### If tests fail:
1. Do not proceed with release
2. Fix failing tests
3. Re-run from Phase 1

### If secrets detected:
1. Do not proceed with release
2. Remove secrets from history (git filter-branch or BFG)
3. Rotate any exposed credentials
4. Re-run security scan

### If documentation is stale:
1. This is a WARNING, not a blocker
2. User can choose to update or proceed
3. Log the decision

## Reminders

- Version format: `X.Y.Z` in files, `vX.Y.Z` for git tags
- CHANGELOG follows Keep a Changelog format
- Always verify build artifacts before pushing
- Security scans are BLOCKERS, not warnings
- User must explicitly approve the push
