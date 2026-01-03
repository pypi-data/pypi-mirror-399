"""Tests for the agent invoker module."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

import pytest

from bpsai_pair.orchestration.invoker import (
    AgentDefinition,
    AgentInvoker,
    InvocationResult,
    invoke_agent,
)


class TestAgentDefinition:
    """Tests for AgentDefinition dataclass."""

    def test_from_file_valid(self, tmp_path):
        """Test loading a valid agent definition."""
        agent_file = tmp_path / "planner.md"
        agent_file.write_text("""---
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

        agent = AgentDefinition.from_file(agent_file)

        assert agent.name == "planner"
        assert agent.description == "Design and planning specialist"
        assert agent.model == "sonnet"
        assert agent.permission_mode == "plan"
        assert agent.tools == ["Read", "Grep", "Glob", "Bash"]
        assert agent.skills == "design-plan-implement"
        assert "senior software architect" in agent.system_prompt
        assert agent.source_file == agent_file

    def test_from_file_missing_frontmatter(self, tmp_path):
        """Test loading file without YAML frontmatter."""
        agent_file = tmp_path / "invalid.md"
        agent_file.write_text("""# No Frontmatter

Just plain markdown content.
""")

        with pytest.raises(ValueError, match="no YAML frontmatter"):
            AgentDefinition.from_file(agent_file)

    def test_from_file_missing_required_fields(self, tmp_path):
        """Test loading file with missing required fields."""
        agent_file = tmp_path / "incomplete.md"
        agent_file.write_text("""---
name: incomplete
---

# Missing required fields
""")

        with pytest.raises(ValueError, match="Missing required fields"):
            AgentDefinition.from_file(agent_file)

    def test_from_file_not_found(self, tmp_path):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            AgentDefinition.from_file(tmp_path / "nonexistent.md")

    def test_from_file_tools_as_list(self, tmp_path):
        """Test loading with tools specified as YAML list."""
        agent_file = tmp_path / "agent.md"
        agent_file.write_text("""---
name: test
description: Test agent
tools:
  - Read
  - Grep
model: sonnet
permissionMode: plan
---

# Test Agent
""")

        agent = AgentDefinition.from_file(agent_file)
        assert agent.tools == ["Read", "Grep"]

    def test_to_dict(self, tmp_path):
        """Test dictionary conversion."""
        agent = AgentDefinition(
            name="test",
            description="Test agent",
            model="sonnet",
            permission_mode="plan",
            tools=["Read", "Grep"],
            system_prompt="# Test",
            source_file=tmp_path / "test.md",
        )

        data = agent.to_dict()

        assert data["name"] == "test"
        assert data["model"] == "sonnet"
        assert data["permission_mode"] == "plan"
        assert data["tools"] == ["Read", "Grep"]


class TestInvocationResult:
    """Tests for InvocationResult dataclass."""

    def test_total_tokens(self):
        """Test total token calculation."""
        result = InvocationResult(
            success=True,
            output="test",
            agent_name="planner",
            input_tokens=100,
            output_tokens=50,
        )
        assert result.total_tokens == 150

    def test_to_dict(self):
        """Test dictionary conversion."""
        result = InvocationResult(
            success=True,
            output="test result",
            agent_name="planner",
            cost_usd=0.05,
            input_tokens=100,
            output_tokens=50,
            session_id="abc123",
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["output"] == "test result"
        assert data["agent_name"] == "planner"
        assert data["cost_usd"] == 0.05
        assert data["tokens"]["total"] == 150
        assert data["session_id"] == "abc123"

    def test_error_result(self):
        """Test error result."""
        result = InvocationResult(
            success=False,
            output="",
            agent_name="security",
            error="Command failed",
        )

        assert not result.success
        assert result.error == "Command failed"


class TestAgentInvoker:
    """Tests for AgentInvoker."""

    @pytest.fixture
    def agents_dir(self, tmp_path):
        """Create an agents directory with sample agents."""
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

You are a senior software architect.
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

You review operations for security issues.
""")

        return agents

    def test_load_agent(self, agents_dir, tmp_path):
        """Test loading an agent by name."""
        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        agent = invoker.load_agent("planner")

        assert agent.name == "planner"
        assert agent.model == "sonnet"
        assert agent.permission_mode == "plan"

    def test_load_agent_not_found(self, agents_dir, tmp_path):
        """Test loading non-existent agent."""
        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        with pytest.raises(FileNotFoundError, match="Agent 'nonexistent' not found"):
            invoker.load_agent("nonexistent")

    def test_load_agent_caching(self, agents_dir, tmp_path):
        """Test that agents are cached after first load."""
        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        agent1 = invoker.load_agent("planner")
        agent2 = invoker.load_agent("planner")

        assert agent1 is agent2  # Same object from cache

    def test_list_agents(self, agents_dir, tmp_path):
        """Test listing all available agents."""
        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        agents = invoker.list_agents()

        assert len(agents) == 2
        names = [a.name for a in agents]
        assert "planner" in names
        assert "security" in names

    def test_list_agents_empty_dir(self, tmp_path):
        """Test listing agents from empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        invoker = AgentInvoker(agents_dir=empty_dir)
        agents = invoker.list_agents()

        assert agents == []

    def test_list_agents_nonexistent_dir(self, tmp_path):
        """Test listing agents from non-existent directory."""
        invoker = AgentInvoker(
            agents_dir=tmp_path / "nonexistent",
            working_dir=tmp_path,
        )
        agents = invoker.list_agents()

        assert agents == []

    @patch("bpsai_pair.orchestration.invoker.HeadlessSession")
    def test_invoke_success(self, mock_session_class, agents_dir, tmp_path):
        """Test successful agent invocation."""
        # Setup mock
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.is_error = False
        mock_response.result = "Plan output here"
        mock_response.cost_usd = 0.05
        mock_response.input_tokens = 100
        mock_response.output_tokens = 50
        mock_response.session_id = "abc123"
        mock_response.duration_seconds = 1.5
        mock_session.invoke.return_value = mock_response
        mock_session_class.return_value = mock_session

        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = invoker.invoke("planner", "Design an auth system")

        assert result.success
        assert result.output == "Plan output here"
        assert result.agent_name == "planner"
        assert result.cost_usd == 0.05
        assert result.total_tokens == 150
        mock_session_class.assert_called_once()
        mock_session.invoke.assert_called_once()

    @patch("bpsai_pair.orchestration.invoker.HeadlessSession")
    def test_invoke_error(self, mock_session_class, agents_dir, tmp_path):
        """Test agent invocation error handling."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.is_error = True
        mock_response.error_message = "Command timed out"
        mock_response.duration_seconds = 300.0
        mock_session.invoke.return_value = mock_response
        mock_session_class.return_value = mock_session

        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = invoker.invoke("planner", "Task context")

        assert not result.success
        assert result.error == "Command timed out"
        assert result.agent_name == "planner"

    @patch("bpsai_pair.orchestration.invoker.HeadlessSession")
    def test_invoke_with_agent_definition(self, mock_session_class, agents_dir, tmp_path):
        """Test invoking with AgentDefinition object instead of name."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.is_error = False
        mock_response.result = "Output"
        mock_response.cost_usd = 0.01
        mock_response.input_tokens = 50
        mock_response.output_tokens = 25
        mock_response.session_id = None
        mock_response.duration_seconds = 0.5
        mock_session.invoke.return_value = mock_response
        mock_session_class.return_value = mock_session

        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )
        agent = invoker.load_agent("security")

        result = invoker.invoke(agent, "Review this command")

        assert result.success
        assert result.agent_name == "security"

    @patch("bpsai_pair.orchestration.invoker.HeadlessSession")
    def test_invoke_with_prompt_prefix(self, mock_session_class, agents_dir, tmp_path):
        """Test invoking with system prompt prefix."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.is_error = False
        mock_response.result = "Output"
        mock_response.cost_usd = 0.01
        mock_response.input_tokens = 50
        mock_response.output_tokens = 25
        mock_response.session_id = None
        mock_response.duration_seconds = 0.5
        mock_session.invoke.return_value = mock_response
        mock_session_class.return_value = mock_session

        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = invoker.invoke(
            "planner",
            "Context here",
            system_prompt_prefix="Extra instructions",
            system_prompt_suffix="Final notes",
        )

        assert result.success
        # Verify the prompt includes all parts
        call_args = mock_session.invoke.call_args
        prompt = call_args[0][0]
        assert "Extra instructions" in prompt
        assert "Final notes" in prompt
        assert "Context here" in prompt

    @patch("bpsai_pair.orchestration.invoker.HeadlessSession")
    def test_invoke_permission_mode(self, mock_session_class, agents_dir, tmp_path):
        """Test that permission mode is passed from agent definition."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.is_error = False
        mock_response.result = "Output"
        mock_response.cost_usd = 0.01
        mock_response.input_tokens = 50
        mock_response.output_tokens = 25
        mock_response.session_id = None
        mock_response.duration_seconds = 0.5
        mock_session.invoke.return_value = mock_response
        mock_session_class.return_value = mock_session

        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        invoker.invoke("planner", "Context")

        # Verify HeadlessSession was created with correct permission mode
        mock_session_class.assert_called_once()
        call_kwargs = mock_session_class.call_args[1]
        assert call_kwargs["permission_mode"] == "plan"

    @patch("bpsai_pair.orchestration.invoker.HeadlessSession")
    def test_invoke_with_handoff(self, mock_session_class, agents_dir, tmp_path):
        """Test invoking with handoff context."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.is_error = False
        mock_response.result = "Continued work"
        mock_response.cost_usd = 0.02
        mock_response.input_tokens = 100
        mock_response.output_tokens = 50
        mock_response.session_id = None
        mock_response.duration_seconds = 1.0
        mock_session.invoke.return_value = mock_response
        mock_session_class.return_value = mock_session

        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        result = invoker.invoke_with_handoff(
            "security",
            "Review these changes",
            handoff_from="planner",
            handoff_context="Previous planning work done...",
        )

        assert result.success
        call_args = mock_session.invoke.call_args
        prompt = call_args[0][0]
        assert "Handoff from planner" in prompt
        assert "Previous planning work done" in prompt


class TestInvokeAgentFunction:
    """Tests for the invoke_agent convenience function."""

    @patch("bpsai_pair.orchestration.invoker.AgentInvoker")
    def test_invoke_agent_convenience(self, mock_invoker_class, tmp_path):
        """Test the invoke_agent convenience function."""
        mock_invoker = MagicMock()
        mock_result = InvocationResult(
            success=True,
            output="Result",
            agent_name="planner",
        )
        mock_invoker.invoke.return_value = mock_result
        mock_invoker_class.return_value = mock_invoker

        result = invoke_agent(
            "planner",
            "Design something",
            working_dir=tmp_path,
            timeout=600,
        )

        assert result.success
        assert result.output == "Result"
        mock_invoker.invoke.assert_called_once_with("planner", "Design something")


class TestIntegrationWithRealFiles:
    """Integration tests using actual agent files."""

    def test_load_real_planner_agent(self):
        """Test loading the actual planner agent if it exists."""
        # This test uses the real .claude/agents directory
        project_root = Path(__file__).parent.parent.parent.parent
        agents_dir = project_root / ".claude" / "agents"

        if not (agents_dir / "planner.md").exists():
            pytest.skip("Planner agent file not found")

        invoker = AgentInvoker(agents_dir=agents_dir)
        agent = invoker.load_agent("planner")

        assert agent.name == "planner"
        assert agent.model in ["sonnet", "opus", "haiku"]
        assert agent.permission_mode in ["plan", "auto", "full"]
        assert len(agent.system_prompt) > 0

    def test_load_real_security_agent(self):
        """Test loading the actual security agent if it exists."""
        project_root = Path(__file__).parent.parent.parent.parent
        agents_dir = project_root / ".claude" / "agents"

        if not (agents_dir / "security.md").exists():
            pytest.skip("Security agent file not found")

        invoker = AgentInvoker(agents_dir=agents_dir)
        agent = invoker.load_agent("security")

        assert agent.name == "security"
        assert "security" in agent.description.lower() or "gatekeeper" in agent.description.lower()
