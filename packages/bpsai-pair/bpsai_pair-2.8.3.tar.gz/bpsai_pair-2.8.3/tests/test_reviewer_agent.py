"""Tests for the reviewer agent implementation."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from textwrap import dedent

import pytest

from bpsai_pair.orchestration.reviewer import (
    ReviewerAgent,
    ReviewOutput,
    ReviewItem,
    ReviewSeverity,
    ReviewVerdict,
    invoke_reviewer,
    should_trigger_reviewer,
)


class TestReviewSeverity:
    """Tests for ReviewSeverity enum."""

    def test_severity_ordering(self):
        """Test severity ordering for comparison."""
        assert ReviewSeverity.INFO < ReviewSeverity.WARNING
        assert ReviewSeverity.WARNING < ReviewSeverity.BLOCKER

    def test_severity_from_string(self):
        """Test creating severity from string."""
        assert ReviewSeverity.from_string("info") == ReviewSeverity.INFO
        assert ReviewSeverity.from_string("warning") == ReviewSeverity.WARNING
        assert ReviewSeverity.from_string("blocker") == ReviewSeverity.BLOCKER
        assert ReviewSeverity.from_string("error") == ReviewSeverity.BLOCKER
        assert ReviewSeverity.from_string("must fix") == ReviewSeverity.BLOCKER
        assert ReviewSeverity.from_string("should fix") == ReviewSeverity.WARNING
        assert ReviewSeverity.from_string("consider") == ReviewSeverity.INFO
        assert ReviewSeverity.from_string("unknown") == ReviewSeverity.INFO  # default


class TestReviewItem:
    """Tests for ReviewItem dataclass."""

    def test_review_item_creation(self):
        """Test creating a review item."""
        item = ReviewItem(
            severity=ReviewSeverity.WARNING,
            file_path="src/auth.py",
            line_number=42,
            message="Missing error handling",
            suggestion="Add try/except block",
            category="error_handling",
        )

        assert item.severity == ReviewSeverity.WARNING
        assert item.file_path == "src/auth.py"
        assert item.line_number == 42
        assert item.message == "Missing error handling"
        assert item.suggestion == "Add try/except block"
        assert item.category == "error_handling"

    def test_review_item_to_dict(self):
        """Test review item dictionary conversion."""
        item = ReviewItem(
            severity=ReviewSeverity.BLOCKER,
            file_path="test.py",
            line_number=10,
            message="Bug found",
        )

        data = item.to_dict()

        assert data["severity"] == "blocker"
        assert data["file_path"] == "test.py"
        assert data["line_number"] == 10
        assert data["message"] == "Bug found"

    def test_review_item_without_line(self):
        """Test review item without line number."""
        item = ReviewItem(
            severity=ReviewSeverity.INFO,
            file_path="module.py",
            message="General suggestion",
        )

        assert item.line_number is None
        assert item.file_path == "module.py"


class TestReviewOutput:
    """Tests for ReviewOutput dataclass."""

    def test_review_output_creation(self):
        """Test creating a review output."""
        output = ReviewOutput(
            verdict=ReviewVerdict.APPROVE_WITH_COMMENTS,
            summary="Generally good with minor issues",
            items=[
                ReviewItem(
                    severity=ReviewSeverity.WARNING,
                    file_path="auth.py",
                    line_number=42,
                    message="Missing validation",
                ),
                ReviewItem(
                    severity=ReviewSeverity.INFO,
                    file_path="auth.py",
                    line_number=50,
                    message="Consider caching",
                ),
            ],
            positive_notes=["Good test coverage", "Clear naming"],
        )

        assert output.verdict == ReviewVerdict.APPROVE_WITH_COMMENTS
        assert len(output.items) == 2
        assert len(output.positive_notes) == 2

    def test_review_output_to_dict(self):
        """Test review output dictionary conversion."""
        output = ReviewOutput(
            verdict=ReviewVerdict.REQUEST_CHANGES,
            summary="Critical issues found",
            items=[
                ReviewItem(
                    severity=ReviewSeverity.BLOCKER,
                    file_path="api.py",
                    line_number=100,
                    message="SQL injection vulnerability",
                ),
            ],
        )

        data = output.to_dict()

        assert data["verdict"] == "request_changes"
        assert data["summary"] == "Critical issues found"
        assert len(data["items"]) == 1
        assert data["items"][0]["severity"] == "blocker"

    def test_review_output_counts(self):
        """Test review item counts by severity."""
        output = ReviewOutput(
            verdict=ReviewVerdict.APPROVE_WITH_COMMENTS,
            summary="Test",
            items=[
                ReviewItem(severity=ReviewSeverity.BLOCKER, file_path="a.py", message="1"),
                ReviewItem(severity=ReviewSeverity.BLOCKER, file_path="b.py", message="2"),
                ReviewItem(severity=ReviewSeverity.WARNING, file_path="c.py", message="3"),
                ReviewItem(severity=ReviewSeverity.INFO, file_path="d.py", message="4"),
            ],
        )

        assert output.blocker_count == 2
        assert output.warning_count == 1
        assert output.info_count == 1
        assert output.has_blockers is True

    def test_review_output_from_raw_text(self):
        """Test parsing review from raw markdown output."""
        raw_text = dedent("""
            ## Review Summary

            Generally good code with some issues to address.

            ## 🔴 Must Fix (Blocking)

            **[src/auth.py:42]** SQL injection vulnerability

            The current code uses string formatting for queries.

            Suggestion: Use parameterized queries instead.

            ## 🟡 Should Fix (Non-blocking)

            **[src/auth.py:67]** Missing input validation

            Suggestion: Add validation for email format.

            ## 🟢 Consider (Optional)

            **[src/auth.py:89]** Could use dataclass here

            ## 👍 Positive Notes

            - Good test coverage
            - Clear variable names

            ## Verdict

            **Status**: Request changes

            **Summary**:
            - 1 must-fix issues
            - 1 should-fix issues
            - 1 suggestions
        """).strip()

        output = ReviewOutput.from_raw_text(raw_text)

        assert output.verdict == ReviewVerdict.REQUEST_CHANGES
        assert len(output.items) >= 3
        assert any(item.severity == ReviewSeverity.BLOCKER for item in output.items)
        assert any(item.severity == ReviewSeverity.WARNING for item in output.items)
        assert any(item.severity == ReviewSeverity.INFO for item in output.items)
        assert len(output.positive_notes) >= 2


class TestReviewVerdict:
    """Tests for ReviewVerdict enum."""

    def test_verdict_values(self):
        """Test verdict enum values."""
        assert ReviewVerdict.APPROVE.value == "approve"
        assert ReviewVerdict.APPROVE_WITH_COMMENTS.value == "approve_with_comments"
        assert ReviewVerdict.REQUEST_CHANGES.value == "request_changes"

    def test_verdict_from_string(self):
        """Test creating verdict from string."""
        assert ReviewVerdict.from_string("approve") == ReviewVerdict.APPROVE
        assert ReviewVerdict.from_string("Approve with comments") == ReviewVerdict.APPROVE_WITH_COMMENTS
        assert ReviewVerdict.from_string("Request changes") == ReviewVerdict.REQUEST_CHANGES
        assert ReviewVerdict.from_string("approved") == ReviewVerdict.APPROVE
        assert ReviewVerdict.from_string("changes requested") == ReviewVerdict.REQUEST_CHANGES


class TestReviewerAgent:
    """Tests for ReviewerAgent."""

    @pytest.fixture
    def agents_dir(self, tmp_path):
        """Create an agents directory with reviewer agent."""
        agents = tmp_path / ".claude" / "agents"
        agents.mkdir(parents=True)

        (agents / "reviewer.md").write_text("""---
name: reviewer
description: Code review specialist
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
skills: code-review
---

# Reviewer Agent

You are a senior code reviewer focused on quality and correctness.

## Your Role

You help with reviewing code changes for correctness.
""")
        return agents

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a fake git repository structure."""
        repo = tmp_path
        git_dir = repo / ".git"
        git_dir.mkdir()

        # Create some source files
        src = repo / "src"
        src.mkdir()
        (src / "auth.py").write_text("""
class AuthManager:
    def login(self, username: str, password: str):
        # TODO: Add validation
        return True
""")
        (src / "api.py").write_text("""
def handle_request(data):
    query = f"SELECT * FROM users WHERE id = {data['id']}"
    return query
""")
        return repo

    def test_reviewer_agent_init(self, agents_dir, tmp_path):
        """Test initializing reviewer agent."""
        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        assert reviewer.agent_name == "reviewer"
        assert reviewer.permission_mode == "plan"

    def test_reviewer_agent_loads_definition(self, agents_dir, tmp_path):
        """Test that reviewer loads agent definition correctly."""
        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        definition = reviewer.load_agent_definition()

        assert definition.name == "reviewer"
        assert definition.permission_mode == "plan"
        assert "Read" in definition.tools
        assert "code reviewer" in definition.system_prompt.lower()

    def test_reviewer_agent_builds_context_from_diff(self, agents_dir, git_repo):
        """Test building context from git diff."""
        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=git_repo,
        )

        # Simulate a diff string
        diff = """
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,5 +1,8 @@
 class AuthManager:
-    def login(self, username: str, password: str):
+    def login(self, username: str, password: str) -> bool:
+        if not username or not password:
+            raise ValueError("Invalid credentials")
         return True
"""

        context = reviewer.build_context(
            diff=diff,
            changed_files=["src/auth.py"],
        )

        assert "diff --git" in context
        assert "src/auth.py" in context
        assert "AuthManager" in context

    def test_reviewer_agent_builds_context_with_files(self, agents_dir, git_repo):
        """Test building context with changed file contents."""
        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=git_repo,
        )

        context = reviewer.build_context(
            diff="",
            changed_files=["src/auth.py", "src/api.py"],
            include_file_contents=True,
        )

        assert "AuthManager" in context
        assert "handle_request" in context

    @patch("bpsai_pair.orchestration.reviewer.AgentInvoker")
    def test_reviewer_agent_invoke(self, mock_invoker_class, agents_dir, tmp_path):
        """Test invoking reviewer agent."""
        # Setup mock
        mock_invoker = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = """## Review Summary
Good code with minor issues.

## Verdict
**Status**: Approve
"""
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = reviewer.invoke("Review this code")

        assert result.success
        mock_invoker.invoke.assert_called_once()

    @patch("bpsai_pair.orchestration.reviewer.AgentInvoker")
    def test_reviewer_agent_review_returns_structured_output(
        self, mock_invoker_class, agents_dir, git_repo
    ):
        """Test that review method returns structured ReviewOutput."""
        mock_invoker = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = """## Review Summary

Code looks good overall with a few suggestions.

## 🟡 Should Fix (Non-blocking)

**[src/auth.py:5]** Missing error handling

Suggestion: Add try/except.

## 👍 Positive Notes

- Clear structure

## Verdict

**Status**: Approve with comments
"""
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=git_repo,
        )

        output = reviewer.review(
            diff="some diff",
            changed_files=["src/auth.py"],
        )

        assert isinstance(output, ReviewOutput)
        assert output.verdict == ReviewVerdict.APPROVE_WITH_COMMENTS

    @patch("bpsai_pair.orchestration.reviewer.AgentInvoker")
    def test_reviewer_agent_handles_error(
        self, mock_invoker_class, agents_dir, tmp_path
    ):
        """Test error handling when invocation fails."""
        mock_invoker = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Command timed out"
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = reviewer.invoke("Review task")

        assert not result.success
        assert result.error == "Command timed out"

    def test_reviewer_agent_permission_mode_is_plan(self, agents_dir, tmp_path):
        """Test that reviewer always uses 'plan' permission mode."""
        reviewer = ReviewerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        assert reviewer.permission_mode == "plan"


class TestInvokeReviewerFunction:
    """Tests for the invoke_reviewer convenience function."""

    @patch("bpsai_pair.orchestration.reviewer.ReviewerAgent")
    def test_invoke_reviewer_convenience(self, mock_reviewer_class, tmp_path):
        """Test the invoke_reviewer convenience function."""
        mock_reviewer = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = "Review result"
        mock_reviewer.invoke.return_value = mock_result
        mock_reviewer_class.return_value = mock_reviewer

        result = invoke_reviewer(
            "Review this code",
            working_dir=tmp_path,
        )

        assert result.success
        mock_reviewer.invoke.assert_called_once_with("Review this code")

    @patch("bpsai_pair.orchestration.reviewer.ReviewerAgent")
    def test_invoke_reviewer_with_diff(self, mock_reviewer_class, tmp_path):
        """Test invoke_reviewer with diff context."""
        mock_reviewer = MagicMock()
        mock_output = ReviewOutput(
            verdict=ReviewVerdict.APPROVE,
            summary="Looks good",
            items=[],
        )
        mock_reviewer.review.return_value = mock_output
        mock_reviewer_class.return_value = mock_reviewer

        result = invoke_reviewer(
            diff="some diff content",
            changed_files=["file.py"],
            working_dir=tmp_path,
        )

        assert isinstance(result, ReviewOutput)


class TestReviewerAgentIntegration:
    """Integration tests with real agent files."""

    def test_load_real_reviewer_agent(self):
        """Test loading the actual reviewer agent if it exists."""
        project_root = Path(__file__).parent.parent.parent.parent
        agents_dir = project_root / ".claude" / "agents"

        if not (agents_dir / "reviewer.md").exists():
            pytest.skip("Reviewer agent file not found")

        reviewer = ReviewerAgent(agents_dir=agents_dir, working_dir=project_root)
        definition = reviewer.load_agent_definition()

        assert definition.name == "reviewer"
        assert definition.permission_mode == "plan"
        assert len(definition.system_prompt) > 0
        assert "code reviewer" in definition.system_prompt.lower()


class TestTriggerConditions:
    """Tests for reviewer trigger conditions."""

    def test_should_trigger_for_review_task(self):
        """Test trigger for review task type."""
        assert should_trigger_reviewer(task_type="REVIEW")

    def test_should_trigger_for_review_in_title(self):
        """Test trigger for 'review' in task title."""
        assert should_trigger_reviewer(task_title="Review authentication changes")

    def test_should_trigger_for_code_review_in_title(self):
        """Test trigger for 'code review' in task title."""
        assert should_trigger_reviewer(task_title="Code review PR #123")

    def test_should_trigger_pre_pr(self):
        """Test trigger for pre-PR review."""
        assert should_trigger_reviewer(pre_pr=True)

    def test_should_not_trigger_for_implement_task(self):
        """Test no trigger for implementation task."""
        assert not should_trigger_reviewer(
            task_type="IMPLEMENT",
            task_title="Implement login feature",
        )

    def test_should_trigger_when_explicit_request(self):
        """Test trigger for explicit review request."""
        assert should_trigger_reviewer(explicit_request=True)


class TestGitDiffExtraction:
    """Tests for git diff context extraction."""

    def test_extract_changed_files_from_diff(self):
        """Test extracting changed files from diff."""
        from bpsai_pair.orchestration.reviewer import extract_changed_files

        diff = """
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -1,5 +1,8 @@
 class AuthManager:
     pass

diff --git a/src/api.py b/src/api.py
index 111111..222222 100644
--- a/src/api.py
+++ b/src/api.py
@@ -1,2 +1,3 @@
 def api():
     pass
"""

        files = extract_changed_files(diff)

        assert "src/auth.py" in files
        assert "src/api.py" in files
        assert len(files) == 2

    def test_extract_line_references(self):
        """Test extracting line references from diff."""
        from bpsai_pair.orchestration.reviewer import extract_line_changes

        diff = """
@@ -10,5 +10,8 @@ class AuthManager:
-    old_code()
+    new_code()
+    more_code()
"""

        additions, deletions = extract_line_changes(diff)

        assert len(additions) > 0
        assert len(deletions) > 0
