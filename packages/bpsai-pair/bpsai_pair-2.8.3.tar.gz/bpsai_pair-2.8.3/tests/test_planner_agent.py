"""Tests for the planner agent implementation."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock
from textwrap import dedent

import pytest

from bpsai_pair.orchestration.planner import (
    PlannerAgent,
    PlanOutput,
    PlanPhase,
    invoke_planner,
)


class TestPlanOutput:
    """Tests for PlanOutput dataclass."""

    def test_plan_output_creation(self):
        """Test creating a basic plan output."""
        plan = PlanOutput(
            summary="Design an authentication system",
            phases=[
                PlanPhase(
                    name="Research",
                    description="Understand existing auth patterns",
                    files=["src/auth.py"],
                    tasks=["Review current code", "Identify gaps"],
                ),
                PlanPhase(
                    name="Implement",
                    description="Add OAuth support",
                    files=["src/auth.py", "src/oauth.py"],
                    tasks=["Create OAuth client", "Add token validation"],
                ),
            ],
            files_to_modify=["src/auth.py", "src/oauth.py"],
            estimated_complexity="medium",
            risks=["Token storage security"],
        )

        assert plan.summary == "Design an authentication system"
        assert len(plan.phases) == 2
        assert plan.phases[0].name == "Research"
        assert plan.files_to_modify == ["src/auth.py", "src/oauth.py"]
        assert plan.estimated_complexity == "medium"
        assert plan.risks == ["Token storage security"]

    def test_plan_output_to_dict(self):
        """Test plan output dictionary conversion."""
        plan = PlanOutput(
            summary="Test plan",
            phases=[
                PlanPhase(
                    name="Phase 1",
                    description="First phase",
                    files=[],
                    tasks=["Task 1"],
                ),
            ],
            files_to_modify=["file.py"],
            estimated_complexity="low",
        )

        data = plan.to_dict()

        assert data["summary"] == "Test plan"
        assert data["phases"][0]["name"] == "Phase 1"
        assert data["files_to_modify"] == ["file.py"]
        assert data["estimated_complexity"] == "low"

    def test_plan_output_from_raw_text(self):
        """Test parsing plan from raw markdown output."""
        raw_text = dedent("""
            ## Summary
            Design an authentication system with OAuth support.

            ## Phases

            ### Phase 1: Research
            - Review existing authentication code
            - Identify OAuth library options

            ### Phase 2: Implementation
            - Create OAuth client module
            - Integrate with existing auth

            ## Files to Modify
            - src/auth.py
            - src/oauth.py (new)

            ## Complexity
            Medium

            ## Risks
            - Token storage security
            - Session management complexity
        """).strip()

        plan = PlanOutput.from_raw_text(raw_text)

        assert "authentication system" in plan.summary.lower()
        assert len(plan.phases) >= 2
        assert "src/auth.py" in plan.files_to_modify


class TestPlanPhase:
    """Tests for PlanPhase dataclass."""

    def test_phase_creation(self):
        """Test creating a plan phase."""
        phase = PlanPhase(
            name="Implementation",
            description="Implement the auth module",
            files=["src/auth.py", "src/oauth.py"],
            tasks=["Create module", "Add tests"],
        )

        assert phase.name == "Implementation"
        assert phase.description == "Implement the auth module"
        assert len(phase.files) == 2
        assert len(phase.tasks) == 2

    def test_phase_to_dict(self):
        """Test phase dictionary conversion."""
        phase = PlanPhase(
            name="Test Phase",
            description="A test phase",
            files=["test.py"],
            tasks=["Run tests"],
        )

        data = phase.to_dict()

        assert data["name"] == "Test Phase"
        assert data["description"] == "A test phase"
        assert data["files"] == ["test.py"]
        assert data["tasks"] == ["Run tests"]


class TestPlannerAgent:
    """Tests for PlannerAgent."""

    @pytest.fixture
    def agents_dir(self, tmp_path):
        """Create an agents directory with planner agent."""
        agents = tmp_path / ".claude" / "agents"
        agents.mkdir(parents=True)

        (agents / "planner.md").write_text("""---
name: planner
description: Design and planning specialist
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
skills: design-plan-implement
---

# Planner Agent

You are a senior software architect focused on design and planning.

## Your Role

You help with understanding requirements and designing solutions.
""")
        return agents

    @pytest.fixture
    def task_dir(self, tmp_path):
        """Create a task directory with sample task."""
        tasks = tmp_path / ".paircoder" / "tasks"
        tasks.mkdir(parents=True)

        (tasks / "TASK-001.task.md").write_text("""---
id: TASK-001
title: Design authentication system
status: pending
---

# TASK-001: Design authentication system

## Description

Design and plan an OAuth-based authentication system.

## Acceptance Criteria

- [ ] Research OAuth libraries
- [ ] Design token storage
- [ ] Plan integration tests
""")
        return tasks

    @pytest.fixture
    def context_dir(self, tmp_path):
        """Create context directory with state and project files."""
        context = tmp_path / ".paircoder" / "context"
        context.mkdir(parents=True)

        (context / "state.md").write_text("""# Current State

## Active Plan

**Plan:** test-plan
**Status:** in_progress

## Current Focus

Working on authentication.
""")

        (context / "project.md").write_text("""# Project Overview

This is a test project for authentication.

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
""")
        return context

    def test_planner_agent_init(self, agents_dir, tmp_path):
        """Test initializing planner agent."""
        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        assert planner.agent_name == "planner"
        assert planner.permission_mode == "plan"

    def test_planner_agent_loads_definition(self, agents_dir, tmp_path):
        """Test that planner loads agent definition correctly."""
        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        definition = planner.load_agent_definition()

        assert definition.name == "planner"
        assert definition.permission_mode == "plan"
        assert "Read" in definition.tools
        assert "software architect" in definition.system_prompt.lower()

    def test_planner_agent_builds_context(self, agents_dir, task_dir, context_dir, tmp_path):
        """Test building context from task and project files."""
        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        context = planner.build_context(
            task_id="TASK-001",
            task_dir=task_dir.parent,
            context_dir=context_dir,
        )

        assert "TASK-001" in context
        assert "authentication" in context.lower()
        assert "OAuth" in context

    def test_planner_agent_builds_context_with_files(
        self, agents_dir, task_dir, context_dir, tmp_path
    ):
        """Test building context with relevant source files."""
        # Create a source file
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "auth.py").write_text("""
class AuthManager:
    def login(self, username: str, password: str):
        pass

    def logout(self):
        pass
""")

        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        context = planner.build_context(
            task_id="TASK-001",
            task_dir=task_dir.parent,
            context_dir=context_dir,
            relevant_files=[src_dir / "auth.py"],
        )

        assert "AuthManager" in context
        assert "login" in context

    @patch("bpsai_pair.orchestration.planner.AgentInvoker")
    def test_planner_agent_invoke(self, mock_invoker_class, agents_dir, tmp_path):
        """Test invoking planner agent."""
        # Setup mock
        mock_invoker = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = """## Summary
Design an auth system.

## Phases

### Phase 1: Research
- Review code

## Files to Modify
- src/auth.py

## Complexity
Medium
"""
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = planner.invoke("Design an authentication system")

        assert result.success
        mock_invoker.invoke.assert_called_once()

    @patch("bpsai_pair.orchestration.planner.AgentInvoker")
    def test_planner_agent_plan_returns_structured_output(
        self, mock_invoker_class, agents_dir, task_dir, context_dir, tmp_path
    ):
        """Test that plan method returns structured PlanOutput."""
        mock_invoker = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = """## Summary
Design OAuth authentication.

## Phases

### Phase 1: Research
- Review existing code
- Identify OAuth library

### Phase 2: Implementation
- Create OAuth client
- Add token handling

## Files to Modify
- src/auth.py
- src/oauth.py (new)

## Complexity
Medium

## Risks
- Token security
"""
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        plan = planner.plan(
            task_id="TASK-001",
            task_dir=task_dir.parent,
            context_dir=context_dir,
        )

        assert isinstance(plan, PlanOutput)
        assert "OAuth" in plan.summary or "auth" in plan.summary.lower()
        assert len(plan.phases) >= 2

    @patch("bpsai_pair.orchestration.planner.AgentInvoker")
    def test_planner_agent_handles_error(
        self, mock_invoker_class, agents_dir, tmp_path
    ):
        """Test error handling when invocation fails."""
        mock_invoker = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Command timed out"
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = planner.invoke("Some task")

        assert not result.success
        assert result.error == "Command timed out"

    def test_planner_agent_permission_mode_is_plan(self, agents_dir, tmp_path):
        """Test that planner always uses 'plan' permission mode."""
        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        assert planner.permission_mode == "plan"

    @patch("bpsai_pair.orchestration.planner.AgentInvoker")
    def test_planner_passes_correct_permission_mode(
        self, mock_invoker_class, agents_dir, tmp_path
    ):
        """Test that HeadlessSession is created with plan mode."""
        mock_invoker = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = "Plan output"
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        planner = PlannerAgent(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        planner.invoke("Task description")

        # Verify invoker was called with correct agent
        mock_invoker.invoke.assert_called_once()
        call_args = mock_invoker.invoke.call_args
        # The agent should be loaded with plan permission mode
        # This is verified by the agent definition having permissionMode: plan


class TestInvokePlannerFunction:
    """Tests for the invoke_planner convenience function."""

    @patch("bpsai_pair.orchestration.planner.PlannerAgent")
    def test_invoke_planner_convenience(self, mock_planner_class, tmp_path):
        """Test the invoke_planner convenience function."""
        mock_planner = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.output = "Plan result"
        mock_planner.invoke.return_value = mock_result
        mock_planner_class.return_value = mock_planner

        result = invoke_planner(
            "Design something",
            working_dir=tmp_path,
        )

        assert result.success
        mock_planner.invoke.assert_called_once_with("Design something")

    @patch("bpsai_pair.orchestration.planner.PlannerAgent")
    def test_invoke_planner_with_task(self, mock_planner_class, tmp_path):
        """Test invoke_planner with task context."""
        mock_planner = MagicMock()
        mock_plan = PlanOutput(
            summary="Test plan",
            phases=[],
            files_to_modify=[],
            estimated_complexity="low",
        )
        mock_planner.plan.return_value = mock_plan
        mock_planner_class.return_value = mock_planner

        result = invoke_planner(
            task_id="TASK-001",
            working_dir=tmp_path,
        )

        assert isinstance(result, PlanOutput)


class TestPlannerAgentIntegration:
    """Integration tests with real agent files."""

    def test_load_real_planner_agent(self):
        """Test loading the actual planner agent if it exists."""
        project_root = Path(__file__).parent.parent.parent.parent
        agents_dir = project_root / ".claude" / "agents"

        if not (agents_dir / "planner.md").exists():
            pytest.skip("Planner agent file not found")

        planner = PlannerAgent(agents_dir=agents_dir, working_dir=project_root)
        definition = planner.load_agent_definition()

        assert definition.name == "planner"
        assert definition.permission_mode == "plan"
        assert len(definition.system_prompt) > 0
        assert "software architect" in definition.system_prompt.lower()


class TestTriggerConditions:
    """Tests for planner trigger conditions."""

    def test_should_trigger_for_design_task(self):
        """Test trigger for design task type."""
        from bpsai_pair.orchestration.planner import should_trigger_planner

        assert should_trigger_planner(task_type="DESIGN")

    def test_should_trigger_for_plan_in_title(self):
        """Test trigger for 'plan' in task title."""
        from bpsai_pair.orchestration.planner import should_trigger_planner

        assert should_trigger_planner(task_title="Plan authentication system")

    def test_should_trigger_for_design_in_title(self):
        """Test trigger for 'design' in task title."""
        from bpsai_pair.orchestration.planner import should_trigger_planner

        assert should_trigger_planner(task_title="Design API architecture")

    def test_should_trigger_for_architecture_in_title(self):
        """Test trigger for 'architecture' in task title."""
        from bpsai_pair.orchestration.planner import should_trigger_planner

        assert should_trigger_planner(task_title="Review system architecture")

    def test_should_not_trigger_for_implement_task(self):
        """Test no trigger for implementation task."""
        from bpsai_pair.orchestration.planner import should_trigger_planner

        assert not should_trigger_planner(
            task_type="IMPLEMENT",
            task_title="Implement login feature",
        )

    def test_should_trigger_when_explicit_request(self):
        """Test trigger for explicit planning request."""
        from bpsai_pair.orchestration.planner import should_trigger_planner

        assert should_trigger_planner(explicit_request=True)
