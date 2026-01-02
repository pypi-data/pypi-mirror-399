"""Tests for the enhanced agent handoff protocol."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from bpsai_pair.orchestration.handoff import (
    HandoffManager,
    HandoffPackage,
    EnhancedHandoffPackage,
    HandoffChain,
    HandoffSerializer,
    prepare_handoff,
    receive_handoff,
)


class TestEnhancedHandoffPackage:
    """Tests for EnhancedHandoffPackage dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating enhanced package with all fields."""
        package = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            task_description="Review the authentication implementation",
            acceptance_criteria=["AC1: Tests pass", "AC2: No security issues"],
            files_touched=["src/auth.py", "tests/test_auth.py"],
            current_state="Implementation complete",
            work_completed="Added OAuth2 support",
            remaining_work="Code review needed",
            token_budget=10000,
            handoff_id="handoff-001",
            previous_handoff_id=None,
            chain_depth=0,
        )

        assert package.task_id == "TASK-001"
        assert package.source_agent == "planner"
        assert package.target_agent == "reviewer"
        assert len(package.acceptance_criteria) == 2
        assert len(package.files_touched) == 2
        assert package.token_budget == 10000
        assert package.chain_depth == 0

    def test_creation_with_minimal_fields(self):
        """Test creating enhanced package with minimal required fields."""
        package = EnhancedHandoffPackage(
            task_id="TASK-002",
            source_agent="claude",
            target_agent="codex",
        )

        assert package.task_id == "TASK-002"
        assert package.acceptance_criteria == []
        assert package.files_touched == []
        assert package.chain_depth == 0
        assert package.handoff_id is not None  # Auto-generated

    def test_to_dict(self):
        """Test conversion to dictionary."""
        package = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            task_description="Review changes",
            acceptance_criteria=["AC1"],
            files_touched=["file.py"],
            current_state="Done",
            work_completed="Implementation",
            remaining_work="Review",
            token_budget=5000,
            handoff_id="h-001",
            chain_depth=1,
        )

        data = package.to_dict()

        assert data["task_id"] == "TASK-001"
        assert data["source_agent"] == "planner"
        assert data["target_agent"] == "reviewer"
        assert data["task_description"] == "Review changes"
        assert data["acceptance_criteria"] == ["AC1"]
        assert data["files_touched"] == ["file.py"]
        assert data["token_budget"] == 5000
        assert data["chain_depth"] == 1

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "task_id": "TASK-003",
            "source_agent": "security",
            "target_agent": "reviewer",
            "task_description": "Security review",
            "acceptance_criteria": ["No vulnerabilities"],
            "files_touched": ["auth.py"],
            "current_state": "Reviewed",
            "work_completed": "Security scan",
            "remaining_work": "Fix issues",
            "token_budget": 8000,
            "handoff_id": "h-003",
            "previous_handoff_id": "h-002",
            "chain_depth": 2,
        }

        package = EnhancedHandoffPackage.from_dict(data)

        assert package.task_id == "TASK-003"
        assert package.source_agent == "security"
        assert package.previous_handoff_id == "h-002"
        assert package.chain_depth == 2

    def test_generate_context_markdown(self):
        """Test generating markdown context for receiving agent."""
        package = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            task_description="Review the implementation",
            acceptance_criteria=["AC1: All tests pass"],
            files_touched=["src/main.py"],
            current_state="Ready for review",
            work_completed="Implemented feature X",
            remaining_work="Code review",
            handoff_id="h-001",
            chain_depth=0,
        )

        md = package.generate_context_markdown()

        assert "TASK-001" in md
        assert "planner" in md
        assert "reviewer" in md
        assert "Review the implementation" in md
        assert "AC1: All tests pass" in md
        assert "src/main.py" in md
        assert "Ready for review" in md
        assert "Implemented feature X" in md
        assert "h-001" in md


class TestHandoffChain:
    """Tests for HandoffChain tracking."""

    def test_create_chain(self):
        """Test creating a new handoff chain."""
        chain = HandoffChain(task_id="TASK-001")

        assert chain.task_id == "TASK-001"
        assert len(chain.handoffs) == 0
        assert chain.current_depth == 0

    def test_add_handoff_to_chain(self):
        """Test adding handoffs to chain."""
        chain = HandoffChain(task_id="TASK-001")

        package1 = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
        )
        chain.add(package1)

        assert len(chain.handoffs) == 1
        assert chain.current_depth == 1

        package2 = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="reviewer",
            target_agent="security",
            handoff_id="h-002",
            previous_handoff_id="h-001",
        )
        chain.add(package2)

        assert len(chain.handoffs) == 2
        assert chain.current_depth == 2

    def test_get_chain_history(self):
        """Test getting chain history."""
        chain = HandoffChain(task_id="TASK-001")

        chain.add(EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
        ))
        chain.add(EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="reviewer",
            target_agent="security",
            handoff_id="h-002",
            previous_handoff_id="h-001",
        ))

        history = chain.get_history()

        assert len(history) == 2
        assert history[0]["source_agent"] == "planner"
        assert history[1]["source_agent"] == "reviewer"

    def test_to_dict_and_from_dict(self):
        """Test chain serialization."""
        chain = HandoffChain(task_id="TASK-001")
        chain.add(EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
        ))

        data = chain.to_dict()
        restored = HandoffChain.from_dict(data)

        assert restored.task_id == "TASK-001"
        assert len(restored.handoffs) == 1


class TestHandoffSerializer:
    """Tests for HandoffSerializer."""

    def test_save_handoff(self, tmp_path):
        """Test saving handoff to file."""
        serializer = HandoffSerializer(handoffs_dir=tmp_path)

        package = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
            task_description="Review changes",
        )

        path = serializer.save(package)

        assert path.exists()
        assert "h-001" in path.name
        assert path.suffix == ".json"

        # Verify content
        with open(path) as f:
            data = json.load(f)
        assert data["task_id"] == "TASK-001"

    def test_load_handoff(self, tmp_path):
        """Test loading handoff from file."""
        serializer = HandoffSerializer(handoffs_dir=tmp_path)

        # Save first
        package = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
        )
        serializer.save(package)

        # Load
        loaded = serializer.load("h-001")

        assert loaded.task_id == "TASK-001"
        assert loaded.source_agent == "planner"
        assert loaded.handoff_id == "h-001"

    def test_list_handoffs(self, tmp_path):
        """Test listing all handoffs."""
        serializer = HandoffSerializer(handoffs_dir=tmp_path)

        # Save multiple
        for i in range(3):
            package = EnhancedHandoffPackage(
                task_id=f"TASK-00{i}",
                source_agent="agent",
                target_agent="target",
                handoff_id=f"h-00{i}",
            )
            serializer.save(package)

        handoffs = serializer.list_all()

        assert len(handoffs) == 3

    def test_load_chain(self, tmp_path):
        """Test loading handoff chain."""
        serializer = HandoffSerializer(handoffs_dir=tmp_path)

        # Save chain
        chain = HandoffChain(task_id="TASK-001")
        chain.add(EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
        ))
        serializer.save_chain(chain)

        # Load chain
        loaded = serializer.load_chain("TASK-001")

        assert loaded.task_id == "TASK-001"
        assert len(loaded.handoffs) == 1


class TestPrepareHandoff:
    """Tests for prepare_handoff function."""

    def test_prepare_handoff_basic(self, tmp_path):
        """Test basic handoff preparation."""
        package = prepare_handoff(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            task_description="Review the code",
            working_dir=tmp_path,
        )

        assert package.task_id == "TASK-001"
        assert package.source_agent == "planner"
        assert package.target_agent == "reviewer"
        assert package.handoff_id is not None

    def test_prepare_handoff_with_files(self, tmp_path):
        """Test handoff preparation with file content."""
        # Create test files
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("def main(): pass")

        package = prepare_handoff(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            files_touched=["src/main.py"],
            working_dir=tmp_path,
        )

        assert "src/main.py" in package.files_touched

    def test_prepare_handoff_with_chain(self, tmp_path):
        """Test handoff preparation continuing a chain."""
        # Create first handoff
        package1 = prepare_handoff(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            working_dir=tmp_path,
        )

        # Create second handoff in chain
        package2 = prepare_handoff(
            task_id="TASK-001",
            source_agent="reviewer",
            target_agent="security",
            previous_handoff_id=package1.handoff_id,
            working_dir=tmp_path,
        )

        assert package2.previous_handoff_id == package1.handoff_id
        assert package2.chain_depth == 1

    def test_prepare_handoff_estimates_tokens(self, tmp_path):
        """Test token budget estimation."""
        # Create a file with known size
        (tmp_path / "test.py").write_text("x" * 4000)  # ~1000 tokens

        package = prepare_handoff(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            files_touched=["test.py"],
            working_dir=tmp_path,
            include_file_contents=True,
        )

        assert package.token_budget > 0


class TestReceiveHandoff:
    """Tests for receive_handoff function."""

    def test_receive_handoff_basic(self, tmp_path):
        """Test basic handoff reception."""
        serializer = HandoffSerializer(handoffs_dir=tmp_path / "handoffs")

        # Create and save handoff
        package = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
            task_description="Review the code",
            work_completed="Implemented feature",
        )
        serializer.save(package)

        # Receive
        received = receive_handoff(
            handoff_id="h-001",
            handoffs_dir=tmp_path / "handoffs",
        )

        assert received.task_id == "TASK-001"
        assert received.work_completed == "Implemented feature"

    def test_receive_handoff_with_context(self, tmp_path):
        """Test receiving handoff with context generation."""
        serializer = HandoffSerializer(handoffs_dir=tmp_path / "handoffs")

        package = EnhancedHandoffPackage(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            handoff_id="h-001",
            task_description="Review changes",
            acceptance_criteria=["Tests pass", "No bugs"],
            work_completed="Implementation done",
        )
        serializer.save(package)

        received, context = receive_handoff(
            handoff_id="h-001",
            handoffs_dir=tmp_path / "handoffs",
            generate_context=True,
        )

        assert "Review changes" in context
        assert "Tests pass" in context
        assert "Implementation done" in context

    def test_receive_handoff_not_found(self, tmp_path):
        """Test receiving non-existent handoff raises error."""
        with pytest.raises(FileNotFoundError):
            receive_handoff(
                handoff_id="nonexistent",
                handoffs_dir=tmp_path / "handoffs",
            )


class TestHandoffIntegration:
    """Integration tests for handoff protocol."""

    def test_full_handoff_workflow(self, tmp_path):
        """Test complete handoff workflow."""
        handoffs_dir = tmp_path / ".paircoder" / "handoffs"

        # Step 1: Planner prepares handoff
        package1 = prepare_handoff(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="reviewer",
            task_description="Implement auth feature",
            acceptance_criteria=["Login works", "Tests pass"],
            work_completed="Basic implementation done",
            remaining_work="Review and testing",
            working_dir=tmp_path,
            save=True,
            handoffs_dir=handoffs_dir,
        )

        # Step 2: Reviewer receives handoff
        received1, context1 = receive_handoff(
            handoff_id=package1.handoff_id,
            handoffs_dir=handoffs_dir,
            generate_context=True,
        )

        assert received1.task_id == "TASK-001"
        assert "Implement auth feature" in context1

        # Step 3: Reviewer prepares handoff to security
        package2 = prepare_handoff(
            task_id="TASK-001",
            source_agent="reviewer",
            target_agent="security",
            task_description="Security review of auth",
            previous_handoff_id=package1.handoff_id,
            work_completed="Code review complete",
            remaining_work="Security scan",
            working_dir=tmp_path,
            save=True,
            handoffs_dir=handoffs_dir,
        )

        assert package2.chain_depth == 1
        assert package2.previous_handoff_id == package1.handoff_id

        # Step 4: Load chain to verify
        serializer = HandoffSerializer(handoffs_dir=handoffs_dir)
        chain = serializer.load_chain("TASK-001")

        assert len(chain.handoffs) == 2
        history = chain.get_history()
        assert history[0]["source_agent"] == "planner"
        assert history[1]["source_agent"] == "reviewer"

    def test_handoff_with_invoker(self, tmp_path):
        """Test handoff integration with AgentInvoker."""
        from bpsai_pair.orchestration.invoker import AgentInvoker

        # Create agents directory with test agent
        agents_dir = tmp_path / ".claude" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "test.md").write_text("""---
name: test
description: Test agent
tools: Read
model: sonnet
permissionMode: plan
---

# Test Agent

You are a test agent.
""")

        # Prepare handoff
        package = prepare_handoff(
            task_id="TASK-001",
            source_agent="planner",
            target_agent="test",
            task_description="Test task",
            work_completed="Planning complete",
            working_dir=tmp_path,
        )

        # Create invoker
        invoker = AgentInvoker(
            agents_dir=agents_dir,
            working_dir=tmp_path,
        )

        # Generate handoff context
        handoff_context = package.generate_context_markdown()

        # Verify context can be used with invoke_with_handoff
        assert "TASK-001" in handoff_context
        assert "Planning complete" in handoff_context
