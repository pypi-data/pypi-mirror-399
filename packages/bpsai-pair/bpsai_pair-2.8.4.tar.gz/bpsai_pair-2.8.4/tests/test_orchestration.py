"""Tests for the orchestration module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bpsai_pair.orchestration.headless import (
    HeadlessResponse,
    HeadlessSession,
    invoke_headless,
)
from bpsai_pair.orchestration.handoff import (
    HandoffManager,
    HandoffPackage,
)
from bpsai_pair.orchestration.codex import (
    CodexAdapter,
    Flow,
    FlowStep,
    parse_flow,
)
from bpsai_pair.orchestration.orchestrator import (
    Orchestrator,
    TaskCharacteristics,
    TaskType,
    TaskComplexity,
)


class TestHeadlessResponse:
    """Tests for HeadlessResponse."""

    def test_total_tokens(self):
        """Test total token calculation."""
        response = HeadlessResponse(input_tokens=100, output_tokens=50)
        assert response.total_tokens == 150

    def test_to_dict(self):
        """Test dictionary conversion."""
        response = HeadlessResponse(
            session_id="abc123",
            result="test result",
            cost_usd=0.05,
            input_tokens=100,
            output_tokens=50,
        )
        data = response.to_dict()
        assert data["session_id"] == "abc123"
        assert data["tokens"]["total"] == 150
        assert data["cost_usd"] == 0.05


class TestHeadlessSession:
    """Tests for HeadlessSession."""

    def test_init(self):
        """Test session initialization."""
        session = HeadlessSession(permission_mode="plan")
        assert session.permission_mode == "plan"
        assert session.session_id is None

    def test_resume_without_session_raises(self):
        """Test resume raises error without session."""
        session = HeadlessSession()
        with pytest.raises(ValueError, match="No session to resume"):
            session.resume("follow-up")

    def test_build_command(self):
        """Test command building."""
        session = HeadlessSession(permission_mode="plan")
        cmd = session._build_command("test prompt", resume=False)

        assert "claude" in cmd
        assert "-p" in cmd
        assert "test prompt" in cmd
        assert "--permission-mode" in cmd
        assert "plan" in cmd
        assert "--no-input" in cmd

    def test_build_command_with_resume(self):
        """Test command building with resume."""
        session = HeadlessSession()
        session.session_id = "test-session"
        cmd = session._build_command("follow-up", resume=True)

        assert "--resume" in cmd
        assert "test-session" in cmd

    def test_parse_json_response(self):
        """Test parsing JSON response."""
        session = HeadlessSession()
        stdout = json.dumps({
            "session_id": "abc123",
            "result": "test result",
            "cost_usd": 0.05,
            "tokens": {"input": 100, "output": 50},
        })

        response = session._parse_response(stdout, "", 0)

        assert response.session_id == "abc123"
        assert response.result == "test result"
        assert response.cost_usd == 0.05
        assert not response.is_error

    def test_parse_plain_text_response(self):
        """Test parsing plain text response."""
        session = HeadlessSession()
        stdout = "Plain text result"

        response = session._parse_response(stdout, "", 0)

        assert response.result == "Plain text result"
        assert not response.is_error

    def test_parse_error_response(self):
        """Test parsing error response."""
        session = HeadlessSession()

        response = session._parse_response("", "error occurred", 1)

        assert response.is_error
        assert "error occurred" in response.error_message


class TestHandoffPackage:
    """Tests for HandoffPackage."""

    def test_to_metadata(self):
        """Test metadata generation."""
        package = HandoffPackage(
            task_id="TASK-001",
            source_agent="claude",
            target_agent="codex",
            token_estimate=5000,
            files_included=["src/main.py"],
        )

        metadata = package.to_metadata()

        assert metadata["task_id"] == "TASK-001"
        assert metadata["source_agent"] == "claude"
        assert metadata["target_agent"] == "codex"
        assert metadata["version"] == "1.0"

    def test_generate_handoff_md(self):
        """Test HANDOFF.md generation."""
        package = HandoffPackage(
            task_id="TASK-001",
            source_agent="claude",
            target_agent="codex",
            task_description="Implement authentication",
            current_state="Basic auth done, need OAuth",
            instructions="Add OAuth support",
        )

        md = package.generate_handoff_md()

        assert "TASK-001" in md
        assert "claude" in md
        assert "codex" in md
        assert "Implement authentication" in md
        assert "OAuth" in md


class TestHandoffManager:
    """Tests for HandoffManager."""

    def test_init(self, tmp_path):
        """Test manager initialization."""
        manager = HandoffManager(project_root=tmp_path)
        assert manager.project_root == tmp_path

    def test_estimate_tokens(self, tmp_path):
        """Test token estimation."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("x" * 400)  # 400 chars = ~100 tokens

        manager = HandoffManager(project_root=tmp_path)
        tokens = manager._estimate_tokens([test_file])

        assert tokens == 100

    def test_extract_section(self):
        """Test section extraction from markdown."""
        manager = HandoffManager()
        content = """
## Description

This is the description.

## Other Section

Other content.
"""
        section = manager._extract_section(content, "Description")
        assert "This is the description" in section


class TestFlowParsing:
    """Tests for flow parsing."""

    def test_parse_simple_flow(self):
        """Test parsing a simple flow."""
        content = """# Flow: test-flow

## Description
A test flow for validation.

## Steps

### 1. First Step
- Do something
- Do something else
- Output: result.md

### 2. Second Step
- Another action
"""
        flow = parse_flow(content, "test-flow")

        assert flow.name == "test-flow"
        assert len(flow.steps) == 2
        assert flow.steps[0].name == "First Step"
        assert len(flow.steps[0].instructions) == 2
        assert "result.md" in flow.steps[0].outputs

    def test_parse_flow_with_triggers(self):
        """Test parsing flow with triggers."""
        content = """# Flow: design-flow

## Triggers: design, plan, approach

## Steps

### Design Phase
- Analyze requirements
"""
        flow = parse_flow(content)

        assert "design" in flow.triggers


class TestCodexAdapter:
    """Tests for CodexAdapter."""

    def test_init(self):
        """Test adapter initialization."""
        adapter = CodexAdapter(approval_mode="full-auto")
        assert adapter.approval_mode == "full-auto"

    def test_translate_step(self):
        """Test step translation to prompt."""
        adapter = CodexAdapter()
        step = FlowStep(
            name="Implement Feature",
            instructions=["Write the code", "Add tests"],
            outputs=["src/feature.py"],
        )
        context = {"task": "TASK-001", "focus": "Authentication"}

        prompt = adapter.translate_step(step, context)

        assert "Implement Feature" in prompt
        assert "TASK-001" in prompt
        assert "Write the code" in prompt

    def test_validate_flow_valid(self):
        """Test flow validation passes for valid flow."""
        adapter = CodexAdapter()
        flow = Flow(
            name="test",
            steps=[FlowStep(name="Step 1", instructions=["Do something"])],
        )

        issues = adapter.validate_flow(flow)
        assert len(issues) == 0

    def test_validate_flow_empty(self):
        """Test flow validation catches empty flow."""
        adapter = CodexAdapter()
        flow = Flow(name="")

        issues = adapter.validate_flow(flow)
        assert any("no name" in issue for issue in issues)
        assert any("no steps" in issue for issue in issues)

    def test_dry_run(self):
        """Test dry run mode."""
        adapter = CodexAdapter(dry_run=True)
        step = FlowStep(name="Test", instructions=["Action"])

        result = adapter.execute_step(step, {})

        assert result.success
        assert "Dry run" in result.output


class TestOrchestrator:
    """Tests for Orchestrator."""

    def test_init(self, tmp_path):
        """Test orchestrator initialization."""
        orchestrator = Orchestrator(project_root=tmp_path)
        assert orchestrator.project_root == tmp_path
        assert "claude-code" in orchestrator.agents

    def test_analyze_task_design(self, tmp_path):
        """Test task analysis for design task."""
        # Create a task file
        tasks_dir = tmp_path / ".paircoder" / "tasks" / "test"
        tasks_dir.mkdir(parents=True)
        task_file = tasks_dir / "TASK-001.task.md"
        task_file.write_text("""# Design Authentication System

## Description
Design a comprehensive authentication architecture.

## Complexity
This is a complex design task.
""")

        orchestrator = Orchestrator(project_root=tmp_path)
        task = orchestrator.analyze_task("TASK-001")

        assert task.task_id == "TASK-001"
        assert task.task_type == TaskType.DESIGN
        assert task.complexity == TaskComplexity.HIGH

    def test_select_agent_design_task(self, tmp_path):
        """Test agent selection for design task."""
        orchestrator = Orchestrator(project_root=tmp_path)
        task = TaskCharacteristics(
            task_id="TASK-001",
            task_type=TaskType.DESIGN,
            requires_reasoning=True,
        )

        decision = orchestrator.select_agent(task)

        # Claude should be preferred for design tasks
        assert decision.agent == "claude-code"
        assert decision.score > 0

    def test_select_agent_with_preference(self, tmp_path):
        """Test agent selection with user preference."""
        orchestrator = Orchestrator(project_root=tmp_path)
        task = TaskCharacteristics(task_id="TASK-001")

        decision = orchestrator.select_agent(task, constraints={"prefer": "codex-cli"})

        # Preference should boost score
        assert "User preferred" in decision.reasoning or decision.agent == "codex-cli"

    def test_assign_task(self, tmp_path):
        """Test task assignment."""
        tasks_dir = tmp_path / ".paircoder" / "tasks" / "test"
        tasks_dir.mkdir(parents=True)
        task_file = tasks_dir / "TASK-002.task.md"
        task_file.write_text("# Implement Feature\n\nImplementation task.")

        orchestrator = Orchestrator(project_root=tmp_path)
        assignment = orchestrator.assign_task("TASK-002")

        assert assignment.task_id == "TASK-002"
        assert assignment.agent in ["claude-code", "codex-cli"]
        assert assignment.status == "pending"

    def test_routing_decision_tree(self, tmp_path):
        """Test the routing decision tree from task spec."""
        orchestrator = Orchestrator(project_root=tmp_path)

        # Design task → Claude
        design_task = TaskCharacteristics(task_id="T1", task_type=TaskType.DESIGN)
        assert orchestrator.select_agent(design_task).agent == "claude-code"

        # Review task → Claude
        review_task = TaskCharacteristics(task_id="T2", task_type=TaskType.REVIEW)
        assert orchestrator.select_agent(review_task).agent == "claude-code"

        # Refactor task → Codex (if available)
        refactor_task = TaskCharacteristics(
            task_id="T3",
            task_type=TaskType.REFACTOR,
            requires_iteration=True,
        )
        decision = orchestrator.select_agent(refactor_task)
        # Either agent is acceptable for refactoring
        assert decision.agent in ["claude-code", "codex-cli"]
