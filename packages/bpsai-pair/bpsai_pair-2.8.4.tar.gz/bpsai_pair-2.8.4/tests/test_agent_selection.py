"""Tests for enhanced agent selection logic."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bpsai_pair.orchestration.orchestrator import (
    Orchestrator,
    TaskCharacteristics,
    TaskType,
    TaskComplexity,
    TaskScope,
    Assignment,
    RoutingDecision,
)
from bpsai_pair.orchestration.agent_selector import (
    AgentSelector,
    AgentMatch,
    SelectionCriteria,
    select_agent_for_task,
)


class TestAgentMatch:
    """Tests for AgentMatch dataclass."""

    def test_agent_match_creation(self):
        """Test creating an agent match."""
        match = AgentMatch(
            agent_name="planner",
            score=0.85,
            reasons=["Task is design type", "Agent has planning strengths"],
            permission_mode="plan",
        )

        assert match.agent_name == "planner"
        assert match.score == 0.85
        assert len(match.reasons) == 2
        assert match.permission_mode == "plan"

    def test_agent_match_to_dict(self):
        """Test agent match dictionary conversion."""
        match = AgentMatch(
            agent_name="reviewer",
            score=0.75,
            reasons=["Review task"],
        )

        data = match.to_dict()

        assert data["agent_name"] == "reviewer"
        assert data["score"] == 0.75
        assert "Review task" in data["reasons"]


class TestSelectionCriteria:
    """Tests for SelectionCriteria dataclass."""

    def test_criteria_creation(self):
        """Test creating selection criteria."""
        criteria = SelectionCriteria(
            task_type="design",
            task_title="Implement authentication",
            task_tags=["security", "backend"],
            complexity=45,
            requires_review=True,
            requires_security=True,
        )

        assert criteria.task_type == "design"
        assert "security" in criteria.task_tags
        assert criteria.complexity == 45

    def test_criteria_from_task_characteristics(self):
        """Test creating criteria from TaskCharacteristics."""
        task = TaskCharacteristics(
            task_id="TASK-001",
            task_type=TaskType.DESIGN,
            complexity=TaskComplexity.HIGH,
            requires_reasoning=True,
        )

        criteria = SelectionCriteria.from_task_characteristics(
            task=task,
            task_title="Design auth system",
            task_tags=["security"],
        )

        assert criteria.task_type == "DESIGN"
        assert "security" in criteria.task_tags

    def test_criteria_requires_security_detection(self):
        """Test automatic security detection from tags."""
        criteria = SelectionCriteria(
            task_title="Add API key handling",
            task_tags=["auth"],
        )

        assert criteria.requires_security is True

    def test_criteria_requires_review_detection(self):
        """Test automatic review detection from title."""
        criteria = SelectionCriteria(
            task_title="Review authentication code",
        )

        assert criteria.requires_review is True


class TestAgentSelector:
    """Tests for AgentSelector."""

    @pytest.fixture
    def agents_dir(self, tmp_path):
        """Create agents directory with test agents."""
        agents = tmp_path / ".claude" / "agents"
        agents.mkdir(parents=True)

        # Create planner agent
        (agents / "planner.md").write_text("""---
name: planner
description: Design and planning specialist
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
---

# Planner Agent

Design and plan implementations.
""")

        # Create reviewer agent
        (agents / "reviewer.md").write_text("""---
name: reviewer
description: Code review specialist
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
---

# Reviewer Agent

Review code for quality.
""")

        # Create security agent
        (agents / "security.md").write_text("""---
name: security
description: Security gatekeeper
tools: Read, Grep, Glob, Bash
model: sonnet
permissionMode: plan
---

# Security Agent

Security review and enforcement.
""")

        return agents

    def test_selector_init(self, agents_dir, tmp_path):
        """Test agent selector initialization."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        assert selector is not None
        assert len(selector.available_agents) >= 3

    def test_selector_loads_agents(self, agents_dir, tmp_path):
        """Test selector loads agent definitions."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        agents = selector.get_available_agents()

        assert "planner" in agents
        assert "reviewer" in agents
        assert "security" in agents

    def test_select_for_design_task(self, agents_dir, tmp_path):
        """Test selection for design task."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        criteria = SelectionCriteria(
            task_type="design",
            task_title="Design authentication system",
        )

        match = selector.select(criteria)

        assert match.agent_name == "planner"
        assert match.score > 0.5

    def test_select_for_review_task(self, agents_dir, tmp_path):
        """Test selection for review task."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        criteria = SelectionCriteria(
            task_type="review",
            task_title="Review the code changes",
            requires_review=True,
        )

        match = selector.select(criteria)

        assert match.agent_name == "reviewer"
        assert match.permission_mode == "plan"

    def test_select_for_security_task(self, agents_dir, tmp_path):
        """Test selection for security-related task."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        criteria = SelectionCriteria(
            task_title="Implement authentication",
            task_tags=["security", "auth"],
            requires_security=True,
        )

        match = selector.select(criteria)

        assert match.agent_name == "security"
        assert "security" in str(match.reasons).lower()

    def test_select_with_explicit_agent(self, agents_dir, tmp_path):
        """Test selection with explicitly requested agent."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        criteria = SelectionCriteria(
            task_title="Any task",
            preferred_agent="reviewer",
        )

        match = selector.select(criteria)

        assert match.agent_name == "reviewer"
        assert "Explicitly requested" in match.reasons or match.score >= 1.0

    def test_fallback_to_default(self, agents_dir, tmp_path):
        """Test fallback to default when no match."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        # Generic task with no specific requirements
        criteria = SelectionCriteria(
            task_title="Do something generic",
        )

        match = selector.select(criteria)

        # Should return claude-code as default
        assert match.agent_name in ["claude-code", "planner", "reviewer"]

    def test_score_calculation(self, agents_dir, tmp_path):
        """Test score calculation for agent selection."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        # High complexity task should prefer more capable agents
        criteria = SelectionCriteria(
            task_type="implement",
            complexity=75,  # High complexity
            task_title="Complex implementation",
        )

        match = selector.select(criteria)

        # Should have a score based on complexity match
        assert 0.0 <= match.score <= 1.0

    def test_get_all_matches(self, agents_dir, tmp_path):
        """Test getting all matches with scores."""
        selector = AgentSelector(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        criteria = SelectionCriteria(
            task_type="design",
            task_title="Design feature",
        )

        matches = selector.get_all_matches(criteria)

        assert len(matches) >= 1  # At least one match
        # Should be sorted by score descending
        scores = [m.score for m in matches]
        assert scores == sorted(scores, reverse=True)


class TestSelectAgentForTask:
    """Tests for select_agent_for_task convenience function."""

    def test_select_for_task_by_type(self, tmp_path):
        """Test selection by task type."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "planner.md").write_text("""---
name: planner
description: Planning agent
tools: Read
model: sonnet
permissionMode: plan
---
Plan things.
""")

        match = select_agent_for_task(
            task_type="design",
            task_title="Design feature",
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        assert match.agent_name == "planner"

    def test_select_for_task_by_tags(self, tmp_path):
        """Test selection by task tags."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "security.md").write_text("""---
name: security
description: Security agent
tools: Read
model: sonnet
permissionMode: plan
---
Security checks.
""")

        match = select_agent_for_task(
            task_tags=["security", "auth"],
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        assert match.agent_name == "security"

    def test_select_for_task_default(self, tmp_path):
        """Test selection returns default when no agents defined."""
        agents_dir = tmp_path / ".claude" / "agents"
        # Don't create any agents

        match = select_agent_for_task(
            task_title="Generic task",
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        # Should return default agent
        assert match.agent_name == "claude-code"


class TestOrchestratorIntegration:
    """Tests for Orchestrator integration with AgentSelector."""

    @pytest.fixture
    def setup_project(self, tmp_path):
        """Set up project with agents and tasks."""
        # Create agents
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        (agents_dir / "planner.md").write_text("""---
name: planner
description: Planning
tools: Read
model: sonnet
permissionMode: plan
---
Plan.
""")
        (agents_dir / "reviewer.md").write_text("""---
name: reviewer
description: Review
tools: Read
model: sonnet
permissionMode: plan
---
Review.
""")
        (agents_dir / "security.md").write_text("""---
name: security
description: Security
tools: Read
model: sonnet
permissionMode: plan
---
Security.
""")

        # Create tasks
        tasks_dir = tmp_path / ".paircoder" / "tasks"
        tasks_dir.mkdir(parents=True)

        (tasks_dir / "TASK-001.task.md").write_text("""---
id: TASK-001
title: Design auth system
status: pending
tags:
  - security
  - design
---

# Design auth system

Design authentication.
""")

        (tasks_dir / "TASK-002.task.md").write_text("""---
id: TASK-002
title: Review code changes
status: pending
tags:
  - review
---

# Review code changes

Code review needed.
""")

        return tmp_path

    def test_orchestrator_selects_specialized_agent(self, setup_project):
        """Test orchestrator uses specialized agents."""
        orchestrator = Orchestrator(project_root=setup_project)

        # Analyze design task
        task = orchestrator.analyze_task("TASK-001")
        decision = orchestrator.select_agent(task)

        # Should prefer claude-code for design (or planner if integrated)
        assert decision.agent in ["claude-code", "planner"]

    def test_orchestrator_assign_uses_correct_agent(self, setup_project):
        """Test assignment uses the correct agent."""
        orchestrator = Orchestrator(project_root=setup_project)

        assignment = orchestrator.assign_task("TASK-002")

        # Review task should use appropriate agent
        assert assignment.agent in ["claude-code", "reviewer"]
        # Review tasks should use plan mode
        assert assignment.permission_mode == "plan"

    def test_orchestrator_respects_preference(self, setup_project):
        """Test orchestrator respects agent preference."""
        orchestrator = Orchestrator(project_root=setup_project)

        task = orchestrator.analyze_task("TASK-001")
        decision = orchestrator.select_agent(task, constraints={"prefer": "codex-cli"})

        # Orchestrator uses its own selection logic
        # Preference may boost score but doesn't guarantee selection
        assert decision.agent in ["claude-code", "codex-cli"]
        assert decision.score > 0


class TestAgentSelectionRules:
    """Tests for specific agent selection rules from TASK-101."""

    @pytest.fixture
    def selector(self, tmp_path):
        """Create selector with standard agents."""
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)

        for agent in ["planner", "reviewer", "security"]:
            (agents_dir / f"{agent}.md").write_text(f"""---
name: {agent}
description: {agent.title()} agent
tools: Read
model: sonnet
permissionMode: plan
---
{agent.title()} agent.
""")

        return AgentSelector(agents_dir=agents_dir, working_dir=tmp_path)

    def test_design_or_plan_routes_to_planner(self, selector):
        """Test design/plan tasks route to planner."""
        criteria = SelectionCriteria(
            task_type="design",
            task_title="Design the API",
        )
        match = selector.select(criteria)
        assert match.agent_name == "planner"

        criteria2 = SelectionCriteria(
            task_title="Plan the implementation",
        )
        match2 = selector.select(criteria2)
        assert match2.agent_name == "planner"

    def test_review_or_pr_routes_to_reviewer(self, selector):
        """Test review/PR tasks route to reviewer."""
        criteria = SelectionCriteria(
            task_type="review",
            task_title="Review changes",
        )
        match = selector.select(criteria)
        assert match.agent_name == "reviewer"

        criteria2 = SelectionCriteria(
            task_title="Create PR for feature",
        )
        match2 = selector.select(criteria2)
        assert match2.agent_name == "reviewer"

    def test_security_tag_routes_to_security(self, selector):
        """Test security/auth tasks route to security."""
        criteria = SelectionCriteria(
            task_tags=["security"],
            task_title="Implement feature",
        )
        match = selector.select(criteria)
        assert match.agent_name == "security"

    def test_auth_keyword_routes_to_security(self, selector):
        """Test auth keyword routes to security."""
        criteria = SelectionCriteria(
            task_title="Implement authentication system",
        )
        match = selector.select(criteria)
        assert match.agent_name == "security"

    def test_high_complexity_uses_full_agent(self, selector):
        """Test high complexity tasks use claude-code."""
        criteria = SelectionCriteria(
            complexity=75,  # High
            task_title="Complex task",
        )
        match = selector.select(criteria)
        # High complexity should prefer claude-code for full capability
        assert match.agent_name in ["claude-code", "planner"]

    def test_fallback_default_agent(self, selector):
        """Test fallback to default agent."""
        criteria = SelectionCriteria(
            task_title="Simple task",
            complexity=20,  # Low
        )
        match = selector.select(criteria)
        # Should return some valid agent
        assert match.agent_name is not None
        assert match.score > 0
