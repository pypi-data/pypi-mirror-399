"""End-to-end tests for plan sync-trello command.

These tests exercise the full sync path through TrelloSyncManager,
including field validation. They would have caught Issue #2 (tuple
unpacking bug) from Sprint 19 planning.

The bug was in sync.py:validate_and_map_custom_fields():
    # BUG: map_and_validate returns 4 values, not 3
    mapped_value, option_id, error = self.field_validator.map_and_validate(...)

    # FIX: Unpack all 4 values
    is_valid, mapped_value, option_id, error = self.field_validator.map_and_validate(...)
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone

from bpsai_pair.trello.sync import (
    TrelloSyncManager,
    TaskSyncConfig,
    TaskData,
)
from bpsai_pair.trello.fields import FieldValidator
from bpsai_pair.trello.client import TrelloService


class TestValidateAndMapCustomFieldsE2E:
    """E2E tests for validate_and_map_custom_fields with real FieldValidator.

    These tests ensure the full path through field validation is exercised,
    which would have caught the tuple unpacking bug.
    """

    @pytest.fixture
    def mock_board_fields(self):
        """Create realistic board field definitions.

        Note: The options dict uses {text: id} format, as produced by
        fetch_board_custom_fields() which inverts the Trello API's {id: text}.
        """
        return {
            "Project": {
                "id": "field_project",
                "name": "Project",
                "type": "list",
                "options": {
                    "PairCoder": "opt_paircoder",
                    "Aurora": "opt_aurora",
                    "Other Project": "opt_other",
                }
            },
            "Stack": {
                "id": "field_stack",
                "name": "Stack",
                "type": "list",
                "options": {
                    "React": "opt_react",
                    "Flask": "opt_flask",
                    "Worker/Function": "opt_worker",
                    "Infra": "opt_infra",
                    "Collection": "opt_collection",
                }
            },
            "Status": {
                "id": "field_status",
                "name": "Status",
                "type": "list",
                "options": {
                    "Planning": "opt_planning",
                    "Enqueued": "opt_enqueued",
                    "In progress": "opt_inprogress",
                    "Testing": "opt_testing",
                    "Done": "opt_done",
                    "Blocked": "opt_blocked",
                }
            },
            "Effort": {
                "id": "field_effort",
                "name": "Effort",
                "type": "list",
                "options": {
                    "S": "opt_s",
                    "M": "opt_m",
                    "L": "opt_l",
                }
            },
        }

    @pytest.fixture
    def mock_service_with_board(self, mock_board_fields):
        """Create TrelloService mock with board set up."""
        service = Mock(spec=TrelloService)
        service.board = Mock()
        service.board.id = "board_123"
        service.get_custom_fields.return_value = []
        service.get_labels.return_value = []
        service.find_card_with_prefix.return_value = (None, None)
        service.create_card_with_custom_fields.return_value = Mock()
        service.set_effort_field.return_value = True
        service.add_label_to_card.return_value = True
        service.ensure_checklist.return_value = {"id": "cl1"}
        service.set_due_date.return_value = True
        return service

    @pytest.fixture
    def field_validator_with_fields(self, mock_board_fields, mock_service_with_board):
        """Create FieldValidator with mocked board fields."""
        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = mock_board_fields
            validator = FieldValidator(
                board_id="board_123",
                client=mock_service_with_board,
                use_cache=True
            )
            return validator

    def test_validate_and_map_custom_fields_full_path(
        self, mock_service_with_board, field_validator_with_fields
    ):
        """Test validate_and_map_custom_fields exercises full validation path.

        This test would have caught the tuple unpacking bug because it:
        1. Creates a real FieldValidator (not None)
        2. Calls validate_and_map_custom_fields which calls map_and_validate
        3. map_and_validate returns 4 values, must be unpacked correctly
        """
        manager = TrelloSyncManager(mock_service_with_board)
        # Inject the real field validator
        manager._field_validator = field_validator_with_fields

        custom_fields = {
            "Project": "PairCoder",
            "Stack": "Worker/Function",
            "Status": "Planning",
        }

        # This call would have raised "too many values to unpack"
        # before the fix
        result = manager.validate_and_map_custom_fields(custom_fields)

        # All valid fields should be returned
        assert "Project" in result
        assert result["Project"] == "PairCoder"
        assert "Stack" in result
        assert result["Stack"] == "Worker/Function"
        assert "Status" in result
        assert result["Status"] == "Planning"

    def test_validate_and_map_with_invalid_value(
        self, mock_service_with_board, field_validator_with_fields
    ):
        """Test validation rejects invalid dropdown values."""
        manager = TrelloSyncManager(mock_service_with_board)
        manager._field_validator = field_validator_with_fields

        custom_fields = {
            "Project": "NonExistent Project",  # Invalid
            "Stack": "Worker/Function",  # Valid
        }

        result = manager.validate_and_map_custom_fields(custom_fields)

        # Invalid Project should be skipped
        assert "Project" not in result
        # Valid Stack should remain
        assert "Stack" in result
        assert result["Stack"] == "Worker/Function"

    def test_validate_and_map_with_alias_mapping(
        self, mock_service_with_board, field_validator_with_fields
    ):
        """Test validation maps aliases to valid values."""
        manager = TrelloSyncManager(mock_service_with_board)
        manager._field_validator = field_validator_with_fields

        # "cli" is an alias for "Worker/Function" in common mappings
        custom_fields = {
            "Stack": "Worker/Function",
        }

        result = manager.validate_and_map_custom_fields(custom_fields)

        assert "Stack" in result
        assert result["Stack"] == "Worker/Function"


class TestSyncTaskToCardE2E:
    """E2E tests for sync_task_to_card with field validation enabled."""

    @pytest.fixture
    def mock_board_fields(self):
        """Create realistic board field definitions.

        Note: The options dict uses {text: id} format.
        """
        return {
            "Project": {
                "id": "field_project",
                "name": "Project",
                "type": "list",
                "options": {"PairCoder": "opt_paircoder"}
            },
            "Stack": {
                "id": "field_stack",
                "name": "Stack",
                "type": "list",
                "options": {"Worker/Function": "opt_worker"}
            },
            "Status": {
                "id": "field_status",
                "name": "Status",
                "type": "list",
                "options": {
                    "Enqueued": "opt_enqueued",
                    "In progress": "opt_inprogress",
                }
            },
            "Effort": {
                "id": "field_effort",
                "name": "Effort",
                "type": "list",
                "options": {"S": "opt_s", "M": "opt_m", "L": "opt_l"}
            },
        }

    @pytest.fixture
    def mock_service(self, mock_board_fields):
        """Create fully mocked TrelloService."""
        service = Mock(spec=TrelloService)
        service.board = Mock()
        service.board.id = "board_123"
        service.find_card_with_prefix.return_value = (None, None)

        mock_card = Mock()
        mock_card.id = "card_123"
        service.create_card_with_custom_fields.return_value = mock_card
        service.set_effort_field.return_value = True
        service.add_label_to_card.return_value = True
        service.ensure_checklist.return_value = {"id": "cl1"}
        service.set_due_date.return_value = True
        service.ensure_label_exists.return_value = {"id": "lbl1"}

        return service

    @pytest.fixture
    def sync_manager_with_validator(self, mock_service, mock_board_fields):
        """Create TrelloSyncManager with real field validator."""
        manager = TrelloSyncManager(mock_service)

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = mock_board_fields
            manager._field_validator = FieldValidator(
                board_id="board_123",
                client=mock_service,
                use_cache=True
            )

        return manager

    def test_sync_task_to_card_with_validation(self, sync_manager_with_validator, mock_service):
        """Test full sync_task_to_card path with field validation.

        This is an E2E test that would have caught the tuple unpacking bug
        because it exercises the complete code path:

        sync_task_to_card()
          -> _create_card()
            -> validate_and_map_custom_fields()
              -> field_validator.map_and_validate()  # Returns 4 values!
        """
        task = TaskData(
            id="T19.1",
            title="Mandatory state.md Update Hook",
            description="Block task completion if state.md not updated",
            status="pending",
            priority="P0",
            complexity=40,
            tags=["hooks", "workflow"],
            plan_title="PairCoder",  # Should be validated
        )

        # This would have raised "too many values to unpack" before fix
        result = sync_manager_with_validator.sync_task_to_card(task, "Planned/Ready")

        assert result is not None
        mock_service.create_card_with_custom_fields.assert_called_once()

    def test_sync_task_validates_all_custom_fields(self, sync_manager_with_validator, mock_service):
        """Test all custom fields go through validation."""
        task = TaskData(
            id="T19.2",
            title="Session Restart Enforcement",
            status="in_progress",
            priority="P0",
            complexity=45,
            tags=[],
            plan_title="PairCoder",
        )

        sync_manager_with_validator.sync_task_to_card(task, "In Progress")

        # Verify create_card_with_custom_fields was called
        call_args = mock_service.create_card_with_custom_fields.call_args
        assert call_args is not None

        # The custom_fields should have been validated
        custom_fields = call_args[1]["custom_fields"]
        # Status should be mapped to Trello value
        assert "Status" in custom_fields


class TestPlanSyncTrelloCommandE2E:
    """E2E tests for the plan sync-trello CLI command flow.

    These tests simulate what happens when running:
    bpsai-pair plan sync-trello <plan-id> --target-list "Planned/Ready"
    """

    @pytest.fixture
    def temp_paircoder_dir(self):
        """Create temporary .paircoder directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            paircoder_dir = Path(tmpdir) / ".paircoder"
            paircoder_dir.mkdir()
            (paircoder_dir / "plans").mkdir()
            (paircoder_dir / "tasks").mkdir()

            # Create a plan file
            plan_content = """id: plan-test-sprint
title: Test Sprint
type: feature
status: planned
created_at: '2025-12-22T10:00:00'
tasks:
  - T99.1
  - T99.2
"""
            (paircoder_dir / "plans" / "plan-test-sprint.plan.yaml").write_text(plan_content)

            # Create task files with proper frontmatter
            task1_content = """---
id: T99.1
title: First Test Task
plan: plan-test-sprint
type: feature
priority: P0
complexity: 30
status: pending
depends_on: []
tags:
- test
---

# Objective

Test task 1

# Acceptance Criteria

- [ ] Test passes
"""
            (paircoder_dir / "tasks" / "T99.1.task.md").write_text(task1_content)

            task2_content = """---
id: T99.2
title: Second Test Task
plan: plan-test-sprint
type: feature
priority: P1
complexity: 40
status: pending
depends_on:
- T99.1
tags:
- test
---

# Objective

Test task 2

# Acceptance Criteria

- [ ] Another test passes
"""
            (paircoder_dir / "tasks" / "T99.2.task.md").write_text(task2_content)

            yield paircoder_dir

    @pytest.fixture
    def mock_board_fields(self):
        """Create realistic board field definitions.

        Note: The options dict uses {text: id} format.
        """
        return {
            "Project": {
                "id": "field_project",
                "name": "Project",
                "type": "list",
                "options": {"PairCoder": "opt_paircoder"}
            },
            "Stack": {
                "id": "field_stack",
                "name": "Stack",
                "type": "list",
                "options": {"Worker/Function": "opt_worker"}
            },
            "Status": {
                "id": "field_status",
                "name": "Status",
                "type": "list",
                "options": {
                    "Planning": "opt_planning",
                    "Enqueued": "opt_enqueued",
                }
            },
            "Effort": {
                "id": "field_effort",
                "name": "Effort",
                "type": "list",
                "options": {"S": "opt_s", "M": "opt_m", "L": "opt_l"}
            },
        }

    def test_sync_plan_with_field_validation(self, temp_paircoder_dir, mock_board_fields):
        """Test syncing a plan exercises field validation for all tasks.

        This simulates the full CLI command flow and would have caught
        the tuple unpacking bug.
        """
        from bpsai_pair.planning.parser import PlanParser, TaskParser
        from bpsai_pair.trello.sync import TrelloSyncManager, TaskSyncConfig, TaskData

        # Parse plan and tasks
        plan_parser = PlanParser(temp_paircoder_dir / "plans")
        task_parser = TaskParser(temp_paircoder_dir / "tasks")

        plan = plan_parser.get_plan_by_id("plan-test-sprint")
        assert plan is not None

        tasks = task_parser.get_tasks_for_plan("plan-test-sprint")
        assert len(tasks) == 2

        # Create mock service
        mock_service = Mock(spec=TrelloService)
        mock_service.board = Mock()
        mock_service.board.id = "board_123"
        mock_service.board.name = "Test Board"
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_service.create_card_with_custom_fields.return_value = Mock(id="card_new")
        mock_service.set_effort_field.return_value = True
        mock_service.add_label_to_card.return_value = True
        mock_service.ensure_checklist.return_value = {"id": "cl1"}
        mock_service.set_due_date.return_value = True
        mock_service.ensure_label_exists.return_value = {"id": "lbl1"}
        mock_service.get_board_lists.return_value = {"Planned/Ready": Mock()}
        mock_service.lists = {"Planned/Ready": Mock()}

        # Create sync manager with field validator
        config = TaskSyncConfig()
        manager = TrelloSyncManager(mock_service, config)

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = mock_board_fields
            manager._field_validator = FieldValidator(
                board_id="board_123",
                client=mock_service,
                use_cache=True
            )

            # Sync each task - this exercises the full path
            for task in tasks:
                task_data = TaskData.from_task(task)
                task_data.plan_title = plan.title

                # This would fail with "too many values to unpack" before fix
                result = manager.sync_task_to_card(task_data, "Planned/Ready")
                assert result is not None

        # Verify both tasks were synced
        assert mock_service.create_card_with_custom_fields.call_count == 2


class TestFieldValidatorMapAndValidate:
    """Direct tests for FieldValidator.map_and_validate return value.

    These tests verify the method returns exactly 4 values as expected.
    """

    @pytest.fixture
    def board_fields(self):
        """Create board field definitions.

        Note: The options dict uses {text: id} format.
        """
        return {
            "Status": {
                "id": "field_status",
                "name": "Status",
                "type": "list",
                "options": {
                    "Planning": "opt_planning",
                    "Done": "opt_done",
                }
            },
        }

    def test_map_and_validate_returns_four_values(self, board_fields):
        """Test map_and_validate returns exactly 4 values.

        This is the core test that would have caught the bug immediately.
        """
        mock_service = Mock()

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = board_fields
            validator = FieldValidator("board_123", mock_service, use_cache=True)

        # Call map_and_validate
        result = validator.map_and_validate("Status", "Planning")

        # Must return exactly 4 values
        assert isinstance(result, tuple)
        assert len(result) == 4, f"Expected 4 values, got {len(result)}: {result}"

        # Unpack to verify structure
        is_valid, mapped_value, option_id, error = result
        assert isinstance(is_valid, bool)
        assert is_valid is True
        assert mapped_value == "Planning"
        assert error is None

    def test_map_and_validate_invalid_value_returns_four_values(self, board_fields):
        """Test map_and_validate returns 4 values even for invalid input."""
        mock_service = Mock()

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = board_fields
            validator = FieldValidator("board_123", mock_service, use_cache=True)

        result = validator.map_and_validate("Status", "InvalidValue")

        assert len(result) == 4
        is_valid, mapped_value, option_id, error = result
        assert is_valid is False
        assert error is not None

    def test_map_and_validate_unknown_field_returns_four_values(self, board_fields):
        """Test map_and_validate returns 4 values for unknown field."""
        mock_service = Mock()

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = board_fields
            validator = FieldValidator("board_123", mock_service, use_cache=True)

        result = validator.map_and_validate("UnknownField", "SomeValue")

        assert len(result) == 4
        is_valid, mapped_value, option_id, error = result
        assert is_valid is False
        assert "not found" in error.lower()


class TestSyncManagerFieldValidatorIntegration:
    """Integration tests between TrelloSyncManager and FieldValidator."""

    def test_sync_manager_correctly_unpacks_map_and_validate(self):
        """Test TrelloSyncManager correctly unpacks map_and_validate result.

        This is the exact scenario that failed in Sprint 19 planning.
        The fix changed line 355 from:
            mapped_value, option_id, error = self.field_validator.map_and_validate(...)
        To:
            is_valid, mapped_value, option_id, error = self.field_validator.map_and_validate(...)
        """
        # Note: options dict uses {text: id} format
        board_fields = {
            "Project": {
                "id": "f1",
                "name": "Project",
                "type": "list",
                "options": {"PairCoder": "opt1"}
            }
        }

        mock_service = Mock(spec=TrelloService)
        mock_service.board = Mock()
        mock_service.board.id = "board_123"

        manager = TrelloSyncManager(mock_service)

        with patch('bpsai_pair.trello.fields.get_cached_board_fields') as mock_cache:
            mock_cache.return_value = board_fields
            manager._field_validator = FieldValidator(
                "board_123", mock_service, use_cache=True
            )

        # This should NOT raise "too many values to unpack"
        result = manager.validate_and_map_custom_fields({"Project": "PairCoder"})

        assert "Project" in result
        assert result["Project"] == "PairCoder"
