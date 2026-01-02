"""Tests for Trello sync functionality."""
import pytest
from unittest.mock import Mock, MagicMock, patch
from bpsai_pair.trello.client import (
    TrelloService,
    CustomFieldDefinition,
    EffortMapping,
)
from bpsai_pair.trello.sync import (
    TrelloSyncManager,
    TaskSyncConfig,
    TaskData,
    BPS_LABELS,
    STACK_KEYWORDS,
    TASK_STATUS_TO_TRELLO_STATUS,
    TRELLO_STATUS_TO_TASK_STATUS,
    create_sync_manager,
)


class TestEffortMapping:
    """Tests for EffortMapping class."""

    def test_small_effort(self):
        """Test complexity 0-25 maps to S."""
        mapping = EffortMapping()
        assert mapping.get_effort(0) == "S"
        assert mapping.get_effort(10) == "S"
        assert mapping.get_effort(25) == "S"

    def test_medium_effort(self):
        """Test complexity 26-50 maps to M."""
        mapping = EffortMapping()
        assert mapping.get_effort(26) == "M"
        assert mapping.get_effort(35) == "M"
        assert mapping.get_effort(50) == "M"

    def test_large_effort(self):
        """Test complexity 51-100 maps to L."""
        mapping = EffortMapping()
        assert mapping.get_effort(51) == "L"
        assert mapping.get_effort(75) == "L"
        assert mapping.get_effort(100) == "L"

    def test_boundary_values(self):
        """Test exact boundary values."""
        mapping = EffortMapping()
        # Exact boundaries
        assert mapping.get_effort(25) == "S"  # Upper bound of S
        assert mapping.get_effort(26) == "M"  # Lower bound of M
        assert mapping.get_effort(50) == "M"  # Upper bound of M
        assert mapping.get_effort(51) == "L"  # Lower bound of L

    def test_negative_values(self):
        """Test negative complexity values default to S."""
        mapping = EffortMapping()
        assert mapping.get_effort(-1) == "S"
        assert mapping.get_effort(-100) == "S"

    def test_over_100_values(self):
        """Test values over 100 map to L."""
        mapping = EffortMapping()
        assert mapping.get_effort(101) == "L"
        assert mapping.get_effort(200) == "L"
        assert mapping.get_effort(1000) == "L"

    def test_custom_ranges(self):
        """Test custom effort mapping ranges."""
        mapping = EffortMapping(
            small=(0, 10),
            medium=(11, 30),
            large=(31, 100)
        )
        assert mapping.get_effort(10) == "S"
        assert mapping.get_effort(11) == "M"
        assert mapping.get_effort(30) == "M"
        assert mapping.get_effort(31) == "L"


class TestTaskSyncConfig:
    """Tests for TaskSyncConfig class."""

    def test_default_values(self):
        """Test default configuration values."""
        config = TaskSyncConfig()
        assert config.project_field == "Project"
        assert config.stack_field == "Stack"
        assert config.effort_field == "Effort"
        assert config.default_list == "Intake/Backlog"
        assert config.create_missing_labels is True
        assert config.preserve_manual_edits is True
        assert config.use_butler_workflow is True
        assert config.status_mapping == TASK_STATUS_TO_TRELLO_STATUS

    def test_from_config_empty(self):
        """Test loading from empty config uses defaults."""
        config = TaskSyncConfig.from_config({})
        assert config.project_field == "Project"
        assert config.effort_field == "Effort"
        assert config.effort_mapping.get_effort(25) == "S"

    def test_from_config_with_effort_mapping(self):
        """Test loading custom effort mapping from config."""
        yaml_config = {
            "sync": {
                "effort_mapping": {
                    "S": [0, 15],
                    "M": [16, 40],
                    "L": [41, 100],
                }
            }
        }
        config = TaskSyncConfig.from_config(yaml_config)
        assert config.effort_mapping.get_effort(15) == "S"
        assert config.effort_mapping.get_effort(16) == "M"
        assert config.effort_mapping.get_effort(40) == "M"
        assert config.effort_mapping.get_effort(41) == "L"

    def test_from_config_with_custom_fields(self):
        """Test loading custom field names from config."""
        yaml_config = {
            "sync": {
                "custom_fields": {
                    "project": "CustomProject",
                    "effort": "Size",
                }
            }
        }
        config = TaskSyncConfig.from_config(yaml_config)
        assert config.project_field == "CustomProject"
        assert config.effort_field == "Size"
        # Non-specified fields use defaults
        assert config.stack_field == "Stack"

    def test_from_config_full(self):
        """Test loading full configuration."""
        yaml_config = {
            "sync": {
                "custom_fields": {
                    "project": "MyProject",
                    "stack": "Technology",
                    "status": "State",
                    "effort": "Size",
                },
                "effort_mapping": {
                    "S": [0, 20],
                    "M": [21, 60],
                    "L": [61, 100],
                },
                "default_list": "Todo",
                "create_missing_labels": False,
                "preserve_manual_edits": False,
            }
        }
        config = TaskSyncConfig.from_config(yaml_config)
        assert config.project_field == "MyProject"
        assert config.stack_field == "Technology"
        assert config.effort_field == "Size"
        assert config.default_list == "Todo"
        assert config.create_missing_labels is False
        assert config.preserve_manual_edits is False
        assert config.effort_mapping.get_effort(20) == "S"
        assert config.effort_mapping.get_effort(21) == "M"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = TaskSyncConfig(
            project_field="Project",
            effort_field="Effort",
            effort_mapping=EffortMapping(small=(0, 25), medium=(26, 50), large=(51, 100)),
        )
        result = config.to_dict()
        assert "sync" in result
        assert result["sync"]["custom_fields"]["project"] == "Project"
        assert result["sync"]["effort_mapping"]["S"] == [0, 25]
        assert result["sync"]["effort_mapping"]["M"] == [26, 50]
        assert result["sync"]["effort_mapping"]["L"] == [51, 100]
        assert "status_mapping" in result["sync"]
        assert "use_butler_workflow" in result["sync"]

    def test_get_trello_status_mapped(self):
        """Test get_trello_status returns mapped value."""
        config = TaskSyncConfig()
        assert config.get_trello_status("pending") == "Planning"
        assert config.get_trello_status("in_progress") == "In progress"
        assert config.get_trello_status("done") == "Done"
        assert config.get_trello_status("blocked") == "Blocked"
        assert config.get_trello_status("review") == "Testing"

    def test_get_trello_status_unmapped(self):
        """Test get_trello_status falls back to title case for unknown status."""
        config = TaskSyncConfig()
        assert config.get_trello_status("unknown_status") == "Unknown Status"
        assert config.get_trello_status("custom") == "Custom"

    def test_get_trello_status_custom_mapping(self):
        """Test get_trello_status with custom mapping."""
        config = TaskSyncConfig(
            status_mapping={
                "pending": "New",
                "in_progress": "Working",
                "done": "Complete",
            }
        )
        assert config.get_trello_status("pending") == "New"
        assert config.get_trello_status("in_progress") == "Working"
        assert config.get_trello_status("done") == "Complete"

    def test_from_config_with_status_mapping(self):
        """Test loading custom status mapping from config."""
        yaml_config = {
            "sync": {
                "status_mapping": {
                    "pending": "New",
                    "in_progress": "Working",
                    "done": "Finished",
                }
            }
        }
        config = TaskSyncConfig.from_config(yaml_config)
        assert config.get_trello_status("pending") == "New"
        assert config.get_trello_status("in_progress") == "Working"
        assert config.get_trello_status("done") == "Finished"

    def test_from_config_with_butler_workflow(self):
        """Test loading butler workflow setting from config."""
        yaml_config = {
            "sync": {
                "use_butler_workflow": False,
            }
        }
        config = TaskSyncConfig.from_config(yaml_config)
        assert config.use_butler_workflow is False

    def test_from_config_default_list_intake(self):
        """Test default list is Intake/Backlog for Butler workflow."""
        config = TaskSyncConfig.from_config({})
        assert config.default_list == "Intake/Backlog"


class TestCustomFieldDefinition:
    """Tests for CustomFieldDefinition dataclass."""

    def test_text_field(self):
        """Test text field definition."""
        field = CustomFieldDefinition(
            id="abc123",
            name="Project",
            field_type="text",
            options={}
        )
        assert field.id == "abc123"
        assert field.name == "Project"
        assert field.field_type == "text"
        assert field.options == {}

    def test_list_field_with_options(self):
        """Test list field with options."""
        field = CustomFieldDefinition(
            id="def456",
            name="Effort",
            field_type="list",
            options={"opt1": "S", "opt2": "M", "opt3": "L"}
        )
        assert field.field_type == "list"
        assert field.options["opt1"] == "S"


class TestTaskData:
    """Tests for TaskData class."""

    def test_from_task(self):
        """Test creating TaskData from Task object."""
        mock_task = Mock()
        mock_task.id = "TASK-001"
        mock_task.title = "Implement feature"
        mock_task.status = "pending"
        mock_task.body = "Description\n\n- [ ] First item\n- [x] Done item"
        mock_task.priority = "P0"
        mock_task.complexity = 35
        mock_task.tags = ["backend", "api"]
        mock_task.plan = "sprint-14"

        task_data = TaskData.from_task(mock_task)

        assert task_data.id == "TASK-001"
        assert task_data.title == "Implement feature"
        assert task_data.status == "pending"
        assert task_data.priority == "P0"
        assert task_data.complexity == 35
        assert task_data.tags == ["backend", "api"]
        assert task_data.plan_title == "sprint-14"
        assert "First item" in task_data.acceptance_criteria
        assert "Done item" in task_data.acceptance_criteria

    def test_from_task_minimal(self):
        """Test creating TaskData from minimal Task object."""
        mock_task = Mock()
        mock_task.id = "TASK-002"
        mock_task.title = "Simple task"
        mock_task.status = "done"
        mock_task.body = None
        # Simulate missing attributes
        del mock_task.priority
        del mock_task.complexity
        del mock_task.tags
        del mock_task.plan

        task_data = TaskData.from_task(mock_task)

        assert task_data.id == "TASK-002"
        assert task_data.priority == "P1"  # default
        assert task_data.complexity == 50  # default
        assert task_data.tags == []
        assert task_data.acceptance_criteria == []


class TestTrelloSyncManager:
    """Tests for TrelloSyncManager class."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock TrelloService."""
        service = Mock(spec=TrelloService)
        service.get_custom_fields.return_value = []
        service.get_labels.return_value = []
        return service

    @pytest.fixture
    def sync_manager(self, mock_service):
        """Create a TrelloSyncManager with mock service."""
        return TrelloSyncManager(mock_service)

    def test_infer_stack_from_tags(self, sync_manager):
        """Test stack inference from task tags returns valid Stack dropdown value."""
        task = TaskData(
            id="TASK-001",
            title="Add endpoint",
            tags=["backend", "api"]
        )
        # Backend label maps to Flask Stack
        assert sync_manager.infer_stack(task) == "Flask"

    def test_infer_stack_from_title(self, sync_manager):
        """Test stack inference from task title returns valid Stack dropdown value."""
        task = TaskData(
            id="TASK-001",
            title="Fix React component bug",
            tags=[]
        )
        # Frontend label maps to React Stack
        assert sync_manager.infer_stack(task) == "React"

    def test_infer_stack_deployment(self, sync_manager):
        """Test stack inference for deployment tasks returns valid Stack dropdown value."""
        task = TaskData(
            id="TASK-001",
            title="Deploy to production",
            tags=["docker"]
        )
        # Deployment label maps to Infra Stack
        assert sync_manager.infer_stack(task) == "Infra"

    def test_infer_stack_security(self, sync_manager):
        """Test stack inference for security tasks returns valid Stack dropdown value."""
        task = TaskData(
            id="TASK-001",
            title="Add authentication",
            tags=[]
        )
        # Security/Admin label maps to Infra Stack
        assert sync_manager.infer_stack(task) == "Infra"

    def test_infer_stack_documentation(self, sync_manager):
        """Test stack inference for documentation tasks returns valid Stack dropdown value."""
        task = TaskData(
            id="TASK-001",
            title="Update README",
            tags=["doc"]
        )
        # Documentation label maps to Collection Stack
        assert sync_manager.infer_stack(task) == "Collection"

    def test_infer_stack_none(self, sync_manager):
        """Test stack inference returns None when cannot infer."""
        task = TaskData(
            id="TASK-001",
            title="Do something",
            tags=[]
        )
        assert sync_manager.infer_stack(task) is None

    def test_infer_label_returns_label_name(self, sync_manager):
        """Test infer_label returns label name (not Stack dropdown value)."""
        task = TaskData(
            id="TASK-001",
            title="Update README",
            tags=["doc"]
        )
        # infer_label should return "Documentation" (the label name)
        assert sync_manager.infer_label(task) == "Documentation"

    def test_label_to_stack_mapping(self, sync_manager):
        """Test label_to_stack converts labels to valid Stack dropdown values."""
        assert sync_manager.label_to_stack("Frontend") == "React"
        assert sync_manager.label_to_stack("Backend") == "Flask"
        assert sync_manager.label_to_stack("Deployment") == "Infra"
        assert sync_manager.label_to_stack("Documentation") == "Collection"
        assert sync_manager.label_to_stack("Bug/Issue") is None  # Not a stack
        assert sync_manager.label_to_stack(None) is None

    def test_build_card_description(self, sync_manager):
        """Test card description building."""
        task = TaskData(
            id="TASK-001",
            title="Test task",
            description="This is the objective.\n\nMore details here.",
            priority="P0",
            complexity=35,
            acceptance_criteria=["Tests pass", "Code reviewed"],
            plan_title="Sprint 14"
        )

        desc = sync_manager.build_card_description(task)

        assert "## Objective" in desc
        assert "This is the objective." in desc
        assert "## Acceptance Criteria" in desc
        assert "- [ ] Tests pass" in desc
        assert "- [ ] Code reviewed" in desc
        assert "Complexity: 35" in desc
        assert "Priority: P0" in desc
        assert "Plan: Sprint 14" in desc
        assert "Created by: PairCoder" in desc

    def test_build_card_description_minimal(self, sync_manager):
        """Test card description with minimal data."""
        task = TaskData(
            id="TASK-001",
            title="Simple task",
            complexity=20
        )

        desc = sync_manager.build_card_description(task)

        assert "Complexity: 20" in desc
        assert "Priority: P1" in desc  # default

    def test_ensure_bps_labels(self, mock_service, sync_manager):
        """Test ensuring BPS labels exist."""
        mock_service.ensure_label_exists.return_value = {"id": "lbl1", "name": "Backend", "color": "blue"}

        results = sync_manager.ensure_bps_labels()

        assert mock_service.ensure_label_exists.call_count == len(BPS_LABELS)
        assert all(success for success in results.values())

    def test_ensure_bps_labels_disabled(self, mock_service):
        """Test that label creation can be disabled."""
        config = TaskSyncConfig(create_missing_labels=False)
        manager = TrelloSyncManager(mock_service, config)

        results = manager.ensure_bps_labels()

        assert results == {}
        mock_service.ensure_label_exists.assert_not_called()

    def test_sync_task_creates_new_card(self, mock_service, sync_manager):
        """Test syncing a task creates a new card."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True
        mock_service.add_label_to_card.return_value = True

        task = TaskData(
            id="TASK-001",
            title="New feature",
            complexity=35,
            tags=["backend"]
        )

        result = sync_manager.sync_task_to_card(task, "Backlog")

        assert result == mock_card
        mock_service.create_card_with_custom_fields.assert_called_once()
        mock_service.set_effort_field.assert_called_once_with(mock_card, 35, "Effort")

    def test_sync_task_adds_multiple_labels(self, mock_service, sync_manager):
        """Test that multiple labels can be added to a single card."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True
        mock_service.add_label_to_card.return_value = True

        # Task with title that infers "Backend" and tags that match BPS labels
        task = TaskData(
            id="TASK-001",
            title="Add API endpoint",
            complexity=35,
            tags=["backend", "documentation"]  # Both are BPS labels
        )

        result = sync_manager.sync_task_to_card(task, "Backlog")

        assert result == mock_card
        # Should add: 1 for inferred stack (Backend) + 2 for matching tags
        # But Backend is both inferred and in tags, so it's called once for inference
        # and once for each tag (Backend, Documentation)
        # Actually, the code adds inferred label first, then tags that match BPS_LABELS
        label_calls = mock_service.add_label_to_card.call_args_list
        labels_added = [call[0][1] for call in label_calls]

        # Should have inferred "Backend" and tag "Documentation"
        assert "Backend" in labels_added
        assert "Documentation" in labels_added

    def test_sync_task_updates_existing_card(self, mock_service, sync_manager):
        """Test syncing a task updates existing card."""
        mock_card = Mock()
        mock_card.description = "Created by: PairCoder"  # Auto-generated, should be updated
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())
        mock_service.set_card_custom_fields.return_value = {}
        mock_service.set_effort_field.return_value = True
        mock_service.add_label_to_card.return_value = True

        task = TaskData(
            id="TASK-001",
            title="Existing feature",
            complexity=50
        )

        result = sync_manager.sync_task_to_card(task, update_existing=True)

        assert result == mock_card
        mock_service.set_card_custom_fields.assert_called_once()
        mock_service.create_card_with_custom_fields.assert_not_called()

    def test_sync_task_skips_existing_when_disabled(self, mock_service, sync_manager):
        """Test syncing skips existing card when update_existing=False."""
        mock_card = Mock()
        mock_service.find_card_with_prefix.return_value = (mock_card, Mock())

        task = TaskData(id="TASK-001", title="Feature")

        result = sync_manager.sync_task_to_card(task, update_existing=False)

        assert result == mock_card
        mock_service.set_card_custom_fields.assert_not_called()

    def test_sync_tasks_batch(self, mock_service, sync_manager):
        """Test syncing multiple tasks."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_service.create_card_with_custom_fields.return_value = Mock()
        mock_service.ensure_label_exists.return_value = {"id": "lbl1"}
        mock_service.set_effort_field.return_value = True
        mock_service.add_label_to_card.return_value = True

        tasks = [
            TaskData(id="TASK-001", title="Task 1", complexity=20),
            TaskData(id="TASK-002", title="Task 2", complexity=40),
            TaskData(id="TASK-003", title="Task 3", complexity=60),
        ]

        results = sync_manager.sync_tasks(tasks)

        assert len(results) == 3
        assert all(card is not None for card in results.values())


class TestTrelloServiceCustomFields:
    """Tests for TrelloService custom field methods."""

    def test_get_custom_fields(self):
        """Test getting custom fields from board."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            # Setup mock board and field definitions
            mock_board = Mock()
            mock_defn = Mock()
            mock_defn.id = "field1"
            mock_defn.name = "Project"
            mock_defn.field_type = "text"
            mock_defn.list_options = {}
            mock_board.get_custom_field_definitions.return_value = [mock_defn]

            service.board = mock_board

            fields = service.get_custom_fields()

            assert len(fields) == 1
            assert fields[0].name == "Project"
            assert fields[0].field_type == "text"

    def test_get_custom_fields_with_list_options(self):
        """Test getting list-type custom field with options."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_board = Mock()
            mock_defn = Mock()
            mock_defn.id = "field1"
            mock_defn.name = "Effort"
            mock_defn.field_type = "list"
            mock_defn.list_options = {"opt1": "S", "opt2": "M", "opt3": "L"}
            mock_board.get_custom_field_definitions.return_value = [mock_defn]

            service.board = mock_board

            fields = service.get_custom_fields()

            assert len(fields) == 1
            assert fields[0].field_type == "list"
            assert fields[0].options == {"opt1": "S", "opt2": "M", "opt3": "L"}

    def test_get_custom_field_by_name(self):
        """Test finding custom field by name."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_board = Mock()
            mock_defn1 = Mock()
            mock_defn1.id = "f1"
            mock_defn1.name = "Project"
            mock_defn1.field_type = "text"
            mock_defn1.list_options = {}

            mock_defn2 = Mock()
            mock_defn2.id = "f2"
            mock_defn2.name = "Effort"
            mock_defn2.field_type = "list"
            mock_defn2.list_options = {"o1": "S"}

            mock_board.get_custom_field_definitions.return_value = [mock_defn1, mock_defn2]

            service.board = mock_board

            field = service.get_custom_field_by_name("effort")  # case insensitive

            assert field is not None
            assert field.name == "Effort"

    def test_get_custom_field_by_name_not_found(self):
        """Test finding non-existent custom field."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_board = Mock()
            mock_board.get_custom_field_definitions.return_value = []

            service.board = mock_board

            field = service.get_custom_field_by_name("NonExistent")

            assert field is None

    def test_set_custom_field_value_text(self):
        """Test setting text custom field."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.id = "card123"

            field = CustomFieldDefinition(
                id="field1",
                name="Project",
                field_type="text",
                options={}
            )

            result = service.set_custom_field_value(mock_card, field, "My Project")

            assert result is True
            service.client.fetch_json.assert_called_once()
            call_args = service.client.fetch_json.call_args
            assert "/card/card123/customField/field1/item" in call_args[0][0]

    def test_set_custom_field_value_list(self):
        """Test setting list custom field."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.id = "card123"

            field = CustomFieldDefinition(
                id="field1",
                name="Effort",
                field_type="list",
                options={"opt1": "S", "opt2": "M", "opt3": "L"}
            )

            result = service.set_custom_field_value(mock_card, field, "M")

            assert result is True
            call_args = service.client.fetch_json.call_args
            assert call_args[1]["post_args"]["idValue"] == "opt2"

    def test_set_custom_field_value_list_not_found(self):
        """Test setting list field with invalid option."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()

            field = CustomFieldDefinition(
                id="field1",
                name="Effort",
                field_type="list",
                options={"opt1": "S", "opt2": "M"}
            )

            result = service.set_custom_field_value(mock_card, field, "XL")

            assert result is False

    def test_set_effort_field(self):
        """Test setting effort field from complexity."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_board = Mock()
            mock_defn = Mock()
            mock_defn.id = "effort1"
            mock_defn.name = "Effort"
            mock_defn.field_type = "list"
            mock_defn.list_options = {"o1": "S", "o2": "M", "o3": "L"}
            mock_board.get_custom_field_definitions.return_value = [mock_defn]

            service.board = mock_board
            mock_card = Mock()
            mock_card.id = "card123"

            result = service.set_effort_field(mock_card, complexity=35)

            assert result is True
            # Should set to "M" for complexity 35


class TestBPSLabels:
    """Tests for BPS label configuration."""

    def test_all_bps_labels_defined(self):
        """Test all expected BPS labels are defined."""
        expected = [
            "Frontend", "Backend", "Worker/Function", "Deployment",
            "Bug/Issue", "Security/Admin", "Documentation", "AI/ML"
        ]
        for label in expected:
            assert label in BPS_LABELS

    def test_bps_label_colors(self):
        """Test BPS label colors are valid Trello colors."""
        valid_colors = {"green", "yellow", "orange", "red", "purple", "blue", "sky", "lime", "pink", "black"}
        for label, color in BPS_LABELS.items():
            assert color in valid_colors, f"Invalid color {color} for label {label}"

    def test_exact_bps_color_mapping(self):
        """Test BPS labels have exact expected colors."""
        expected_colors = {
            "Frontend": "green",
            "Backend": "blue",
            "Worker/Function": "purple",
            "Deployment": "red",
            "Bug/Issue": "orange",
            "Security/Admin": "yellow",
            "Documentation": "sky",
            "AI/ML": "black",
        }
        for label, expected_color in expected_colors.items():
            assert BPS_LABELS[label] == expected_color, f"Label {label} should be {expected_color}, got {BPS_LABELS[label]}"

    def test_ensure_bps_labels_uses_correct_colors(self):
        """Test ensure_bps_labels passes correct colors to ensure_label_exists."""
        mock_service = Mock(spec=TrelloService)
        mock_service.ensure_label_exists.return_value = {"id": "lbl1"}

        manager = TrelloSyncManager(mock_service)
        manager.ensure_bps_labels()

        # Verify each label was created with the correct color
        calls = {
            call[0][0]: call[0][1]
            for call in mock_service.ensure_label_exists.call_args_list
        }
        assert calls["Frontend"] == "green"
        assert calls["Backend"] == "blue"
        assert calls["Worker/Function"] == "purple"
        assert calls["Deployment"] == "red"
        assert calls["Bug/Issue"] == "orange"
        assert calls["Security/Admin"] == "yellow"
        assert calls["Documentation"] == "sky"
        assert calls["AI/ML"] == "black"


class TestStackKeywords:
    """Tests for stack inference keywords."""

    def test_all_stacks_have_keywords(self):
        """Test all BPS stacks have inference keywords."""
        for stack in BPS_LABELS.keys():
            assert stack in STACK_KEYWORDS, f"No keywords defined for {stack}"

    def test_keywords_are_lowercase(self):
        """Test all keywords are lowercase."""
        for stack, keywords in STACK_KEYWORDS.items():
            for kw in keywords:
                assert kw == kw.lower(), f"Keyword '{kw}' for {stack} is not lowercase"


class TestTaskStatusToTrelloStatus:
    """Tests for task status to Trello status mapping."""

    def test_all_task_statuses_mapped(self):
        """Test all standard task statuses have Trello mappings."""
        expected_statuses = ["pending", "in_progress", "review", "blocked", "done"]
        for status in expected_statuses:
            assert status in TASK_STATUS_TO_TRELLO_STATUS, f"Status '{status}' not mapped"

    def test_mapping_values(self):
        """Test exact mapping values for BPS board."""
        assert TASK_STATUS_TO_TRELLO_STATUS["pending"] == "Planning"
        assert TASK_STATUS_TO_TRELLO_STATUS["in_progress"] == "In progress"
        assert TASK_STATUS_TO_TRELLO_STATUS["review"] == "Testing"
        assert TASK_STATUS_TO_TRELLO_STATUS["blocked"] == "Blocked"
        assert TASK_STATUS_TO_TRELLO_STATUS["done"] == "Done"

    def test_reverse_mapping_exists(self):
        """Test reverse mapping (Trello to task status) exists."""
        # Valid BPS Status options: Planning, Enqueued, In progress, Testing, Done, Waiting, Blocked
        assert len(TRELLO_STATUS_TO_TASK_STATUS) == 8  # 7 statuses + "Not sure"

    def test_reverse_mapping_consistent(self):
        """Test that forward and reverse mappings are consistent for unique values."""
        # Note: "ready" and "pending" both map to different Trello statuses
        # but "Blocked" and "Waiting" both map back to "blocked"
        # So we test key mappings individually
        assert TRELLO_STATUS_TO_TASK_STATUS["Planning"] == "pending"
        assert TRELLO_STATUS_TO_TASK_STATUS["In progress"] == "in_progress"
        assert TRELLO_STATUS_TO_TASK_STATUS["Done"] == "done"

    def test_trello_to_task_status_values(self):
        """Test reverse mapping values."""
        assert TRELLO_STATUS_TO_TASK_STATUS["Planning"] == "pending"
        assert TRELLO_STATUS_TO_TASK_STATUS["Enqueued"] == "ready"
        assert TRELLO_STATUS_TO_TASK_STATUS["In progress"] == "in_progress"
        assert TRELLO_STATUS_TO_TASK_STATUS["Testing"] == "review"
        assert TRELLO_STATUS_TO_TASK_STATUS["Blocked"] == "blocked"
        assert TRELLO_STATUS_TO_TASK_STATUS["Done"] == "done"


class TestSyncManagerStatusMapping:
    """Tests for TrelloSyncManager using status mapping."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock TrelloService."""
        service = Mock(spec=TrelloService)
        service.get_custom_fields.return_value = []
        service.get_labels.return_value = []
        return service

    def test_create_card_uses_status_mapping(self, mock_service):
        """Test that _create_card uses the status mapping for custom fields."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True
        mock_service.add_label_to_card.return_value = True

        manager = TrelloSyncManager(mock_service)
        task = TaskData(
            id="TASK-001",
            title="Test task",
            status="pending",  # Should map to "Planning"
            complexity=25,
        )

        manager._create_card(task, "Backlog")

        # Verify create_card_with_custom_fields was called with mapped status
        call_args = mock_service.create_card_with_custom_fields.call_args
        custom_fields = call_args[1]["custom_fields"]
        assert custom_fields["Status"] == "Planning"

    def test_create_card_maps_in_progress(self, mock_service):
        """Test in_progress status is mapped correctly."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True

        manager = TrelloSyncManager(mock_service)
        task = TaskData(
            id="TASK-001",
            title="Test task",
            status="in_progress",  # Should map to "In progress"
            complexity=25,
        )

        manager._create_card(task, "Backlog")

        call_args = mock_service.create_card_with_custom_fields.call_args
        custom_fields = call_args[1]["custom_fields"]
        assert custom_fields["Status"] == "In progress"

    def test_create_card_maps_done(self, mock_service):
        """Test done status is mapped correctly."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True

        manager = TrelloSyncManager(mock_service)
        task = TaskData(
            id="TASK-001",
            title="Test task",
            status="done",  # Should map to "Done"
            complexity=25,
        )

        manager._create_card(task, "Backlog")

        call_args = mock_service.create_card_with_custom_fields.call_args
        custom_fields = call_args[1]["custom_fields"]
        assert custom_fields["Status"] == "Done"

    def test_update_card_uses_status_mapping(self, mock_service):
        """Test that _update_card uses the status mapping for custom fields."""
        mock_card = Mock()
        mock_card.description = "Created by: PairCoder"
        mock_service.set_card_custom_fields.return_value = {}
        mock_service.set_effort_field.return_value = True

        manager = TrelloSyncManager(mock_service)
        task = TaskData(
            id="TASK-001",
            title="Test task",
            status="review",  # Should map to "Testing"
            complexity=25,
        )

        manager._update_card(mock_card, task)

        # Verify set_card_custom_fields was called with mapped status
        call_args = mock_service.set_card_custom_fields.call_args
        custom_fields = call_args[0][1]
        assert custom_fields["Status"] == "Testing"

    def test_sync_manager_with_custom_status_mapping(self, mock_service):
        """Test TrelloSyncManager with custom status mapping."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True

        config = TaskSyncConfig(
            status_mapping={
                "pending": "New",
                "in_progress": "Working",
                "done": "Complete",
            }
        )
        manager = TrelloSyncManager(mock_service, config)
        task = TaskData(
            id="TASK-001",
            title="Test task",
            status="pending",  # Should map to "New" with custom config
            complexity=25,
        )

        manager._create_card(task, "Backlog")

        call_args = mock_service.create_card_with_custom_fields.call_args
        custom_fields = call_args[1]["custom_fields"]
        assert custom_fields["Status"] == "New"


# Import reverse sync classes
from bpsai_pair.trello.sync import (
    TrelloToLocalSync,
    SyncConflict,
    SyncResult,
    LIST_TO_STATUS,
    create_reverse_sync,
)
from pathlib import Path
import tempfile


class TestListToStatusMapping:
    """Tests for list name to status mapping."""

    def test_backlog_lists_map_to_pending(self):
        """Test backlog list names map to pending status."""
        assert LIST_TO_STATUS["Intake / Backlog"] == "pending"
        assert LIST_TO_STATUS["Backlog"] == "pending"
        assert LIST_TO_STATUS["Planned / Ready"] == "pending"
        assert LIST_TO_STATUS["Ready"] == "pending"

    def test_progress_lists_map_to_in_progress(self):
        """Test in-progress list names map to in_progress status."""
        assert LIST_TO_STATUS["In Progress"] == "in_progress"

    def test_review_lists_map_to_review(self):
        """Test review list names map to review status."""
        assert LIST_TO_STATUS["Review / Testing"] == "review"
        assert LIST_TO_STATUS["In Review"] == "review"

    def test_done_lists_map_to_done(self):
        """Test done list names map to done status."""
        assert LIST_TO_STATUS["Deployed / Done"] == "done"
        assert LIST_TO_STATUS["Done"] == "done"

    def test_blocked_lists_map_to_blocked(self):
        """Test blocked list names map to blocked status."""
        assert LIST_TO_STATUS["Issues / Tech Debt"] == "blocked"
        assert LIST_TO_STATUS["Blocked"] == "blocked"


class TestSyncConflict:
    """Tests for SyncConflict dataclass."""

    def test_default_resolution(self):
        """Test default conflict resolution is trello_wins."""
        conflict = SyncConflict(
            task_id="TASK-001",
            field="status",
            local_value="pending",
            trello_value="in_progress"
        )
        assert conflict.resolution == "trello_wins"

    def test_custom_resolution(self):
        """Test custom conflict resolution."""
        conflict = SyncConflict(
            task_id="TASK-001",
            field="description",
            local_value="Local desc",
            trello_value="Trello desc",
            resolution="local_wins"
        )
        assert conflict.resolution == "local_wins"


class TestSyncResult:
    """Tests for SyncResult dataclass."""

    def test_default_values(self):
        """Test default values for SyncResult."""
        result = SyncResult(task_id="TASK-001", action="updated")
        assert result.changes == {}
        assert result.conflicts == []
        assert result.error is None

    def test_with_changes(self):
        """Test SyncResult with changes."""
        result = SyncResult(
            task_id="TASK-001",
            action="updated",
            changes={"status": {"from": "pending", "to": "in_progress"}}
        )
        assert "status" in result.changes
        assert result.changes["status"]["to"] == "in_progress"

    def test_with_error(self):
        """Test SyncResult with error."""
        result = SyncResult(
            task_id="TASK-001",
            action="error",
            error="Task not found"
        )
        assert result.action == "error"
        assert result.error == "Task not found"


class TestTrelloToLocalSync:
    """Tests for TrelloToLocalSync class."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock(spec=TrelloService)
        service.board = Mock()
        return service

    @pytest.fixture
    def temp_tasks_dir(self):
        """Create temporary tasks directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sync_manager(self, mock_service, temp_tasks_dir):
        """Create TrelloToLocalSync with mocks."""
        return TrelloToLocalSync(mock_service, temp_tasks_dir)

    def test_extract_task_id_valid(self, sync_manager):
        """Test extracting task ID from valid card name."""
        assert sync_manager.extract_task_id("[TASK-001] Implement feature") == "TASK-001"
        assert sync_manager.extract_task_id("[TASK-123] Bug fix") == "TASK-123"

    def test_extract_task_id_no_brackets(self, sync_manager):
        """Test extracting task ID from card name without brackets."""
        assert sync_manager.extract_task_id("Implement feature") is None
        assert sync_manager.extract_task_id("TASK-001 without brackets") is None

    def test_extract_task_id_incomplete_brackets(self, sync_manager):
        """Test extracting task ID from card name with incomplete brackets."""
        assert sync_manager.extract_task_id("[TASK-001 missing close") is None
        assert sync_manager.extract_task_id("TASK-001] missing open") is None

    def test_get_list_status_valid(self, sync_manager):
        """Test getting status from valid list name."""
        assert sync_manager.get_list_status("In Progress") == "in_progress"
        assert sync_manager.get_list_status("Done") == "done"
        assert sync_manager.get_list_status("Backlog") == "pending"

    def test_get_list_status_unknown(self, sync_manager):
        """Test getting status from unknown list name."""
        assert sync_manager.get_list_status("Custom List") is None
        assert sync_manager.get_list_status("My Tasks") is None

    def test_sync_card_no_task_id(self, sync_manager):
        """Test sync card without task ID in name."""
        mock_card = Mock()
        mock_card.name = "Card without task ID"

        result = sync_manager.sync_card_to_task(mock_card)

        assert result.action == "skipped"
        assert "Could not extract task ID" in result.error

    def test_sync_card_task_not_found(self, sync_manager):
        """Test sync card when task not found locally."""
        mock_card = Mock()
        mock_card.name = "[TASK-999] Non-existent task"

        # Mock task parser to return None
        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = None

        result = sync_manager.sync_card_to_task(mock_card)

        assert result.task_id == "TASK-999"
        assert result.action == "skipped"
        assert "not found locally" in result.error

    def test_sync_card_status_change(self, sync_manager, mock_service):
        """Test sync card with status change."""
        mock_card = Mock()
        mock_card.name = "[TASK-001] Test task"
        mock_card.due_date = None
        mock_list = Mock()
        mock_list.name = "In Progress"
        mock_card.get_list.return_value = mock_list

        # Mock checklist lookup to return None (no checklist)
        mock_service.get_checklist_by_name.return_value = None

        # Mock task with pending status
        mock_task = Mock()
        mock_task.status = Mock()
        mock_task.status.value = "pending"
        mock_task.body = ""

        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = mock_task

        result = sync_manager.sync_card_to_task(mock_card)

        assert result.task_id == "TASK-001"
        assert result.action == "updated"
        assert "status" in result.changes
        assert result.changes["status"]["from"] == "pending"
        assert result.changes["status"]["to"] == "in_progress"

    def test_sync_card_no_changes(self, sync_manager, mock_service):
        """Test sync card when no changes needed."""
        mock_card = Mock()
        mock_card.name = "[TASK-001] Test task"
        mock_card.due_date = None  # Explicitly set to None to avoid Mock truthy behavior
        mock_list = Mock()
        mock_list.name = "In Progress"
        mock_card.get_list.return_value = mock_list

        # Mock checklist lookup to return None (no checklist)
        mock_service.get_checklist_by_name.return_value = None

        # Mock task already in_progress
        mock_task = Mock()
        mock_task.status = Mock()
        mock_task.status.value = "in_progress"
        mock_task.body = ""

        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = mock_task

        result = sync_manager.sync_card_to_task(mock_card)

        assert result.task_id == "TASK-001"
        assert result.action == "skipped"
        assert result.changes == {}

    def test_sync_all_cards_empty(self, sync_manager):
        """Test sync all cards from empty board."""
        sync_manager.service.board.get_cards.return_value = []

        results = sync_manager.sync_all_cards()

        assert results == []

    def test_sync_all_cards_filters_list(self, sync_manager):
        """Test sync all cards filters by list name."""
        mock_card1 = Mock()
        mock_card1.name = "[TASK-001] Task 1"
        mock_card1.get_list.return_value.name = "In Progress"

        mock_card2 = Mock()
        mock_card2.name = "[TASK-002] Task 2"
        mock_card2.get_list.return_value.name = "Done"

        sync_manager.service.board.get_cards.return_value = [mock_card1, mock_card2]
        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = None

        # Filter to only "Done" list
        results = sync_manager.sync_all_cards(list_filter=["Done"])

        # Should only process card2 (in Done list)
        assert len(results) == 1
        assert results[0].task_id == "TASK-002"

    def test_get_sync_preview(self, sync_manager):
        """Test getting sync preview."""
        mock_card = Mock()
        mock_card.name = "[TASK-001] Test task"
        mock_list = Mock()
        mock_list.name = "Done"
        mock_card.get_list.return_value = mock_list

        mock_task = Mock()
        mock_task.status = Mock()
        mock_task.status.value = "in_progress"

        sync_manager.service.board.get_cards.return_value = [mock_card]
        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = mock_task

        preview = sync_manager.get_sync_preview()

        assert len(preview) == 1
        assert preview[0]["task_id"] == "TASK-001"
        assert preview[0]["action"] == "update"
        assert preview[0]["field"] == "status"
        assert preview[0]["from"] == "in_progress"
        assert preview[0]["to"] == "done"


class TestTaskDataCheckedCriteria:
    """Tests for TaskData with checked acceptance criteria."""

    def test_from_task_tracks_checked_items(self):
        """Test that TaskData.from_task tracks checked acceptance criteria."""
        mock_task = Mock()
        mock_task.id = "TASK-001"
        mock_task.title = "Test task"
        mock_task.status = "in_progress"
        mock_task.body = """
# Acceptance Criteria

- [x] First item done
- [ ] Second item not done
- [x] Third item done
- [ ] Fourth item
"""
        mock_task.priority = "P1"
        mock_task.complexity = 30
        mock_task.tags = []
        mock_task.plan = None

        task_data = TaskData.from_task(mock_task)

        assert len(task_data.acceptance_criteria) == 4
        assert "First item done" in task_data.acceptance_criteria
        assert "Second item not done" in task_data.acceptance_criteria
        assert len(task_data.checked_criteria) == 2
        assert "First item done" in task_data.checked_criteria
        assert "Third item done" in task_data.checked_criteria
        assert "Second item not done" not in task_data.checked_criteria

    def test_from_task_handles_uppercase_x(self):
        """Test that TaskData.from_task handles uppercase X in checkboxes."""
        mock_task = Mock()
        mock_task.id = "TASK-001"
        mock_task.title = "Test task"
        mock_task.status = "pending"
        mock_task.body = "- [X] Done with uppercase X"
        mock_task.priority = "P1"
        mock_task.complexity = 30
        mock_task.tags = []
        mock_task.plan = None

        task_data = TaskData.from_task(mock_task)

        assert "Done with uppercase X" in task_data.acceptance_criteria
        assert "Done with uppercase X" in task_data.checked_criteria

    def test_from_task_no_criteria(self):
        """Test TaskData.from_task with no acceptance criteria."""
        mock_task = Mock()
        mock_task.id = "TASK-001"
        mock_task.title = "Test task"
        mock_task.status = "pending"
        mock_task.body = "Just a description without checkboxes"
        mock_task.priority = "P1"
        mock_task.complexity = 30
        mock_task.tags = []
        mock_task.plan = None

        task_data = TaskData.from_task(mock_task)

        assert task_data.acceptance_criteria == []
        assert task_data.checked_criteria == []


class TestSyncManagerChecklist:
    """Tests for TrelloSyncManager checklist functionality."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock(spec=TrelloService)
        service.ensure_checklist.return_value = {
            "id": "checklist123",
            "name": "Acceptance Criteria",
            "items": []
        }
        return service

    @pytest.fixture
    def sync_manager(self, mock_service):
        """Create TrelloSyncManager with mock service."""
        return TrelloSyncManager(mock_service)

    def test_sync_checklist_creates_checklist(self, sync_manager, mock_service):
        """Test _sync_checklist creates checklist with items."""
        mock_card = Mock()
        acceptance_criteria = ["First item", "Second item", "Third item"]

        result = sync_manager._sync_checklist(mock_card, acceptance_criteria)

        assert result is not None
        mock_service.ensure_checklist.assert_called_once_with(
            card=mock_card,
            name="Acceptance Criteria",
            items=acceptance_criteria,
            checked_items=[]
        )

    def test_sync_checklist_with_checked_items(self, sync_manager, mock_service):
        """Test _sync_checklist passes checked items."""
        mock_card = Mock()
        acceptance_criteria = ["Item 1", "Item 2", "Item 3"]
        checked_criteria = ["Item 1", "Item 3"]

        sync_manager._sync_checklist(mock_card, acceptance_criteria, checked_criteria)

        mock_service.ensure_checklist.assert_called_once_with(
            card=mock_card,
            name="Acceptance Criteria",
            items=acceptance_criteria,
            checked_items=checked_criteria
        )

    def test_sync_checklist_empty_criteria(self, sync_manager, mock_service):
        """Test _sync_checklist with empty criteria returns None."""
        mock_card = Mock()

        result = sync_manager._sync_checklist(mock_card, [])

        assert result is None
        mock_service.ensure_checklist.assert_not_called()

    def test_sync_checklist_custom_name(self, sync_manager, mock_service):
        """Test _sync_checklist with custom checklist name."""
        mock_card = Mock()
        acceptance_criteria = ["Test item"]

        sync_manager._sync_checklist(
            mock_card, acceptance_criteria,
            checklist_name="Custom Checklist"
        )

        mock_service.ensure_checklist.assert_called_once()
        call_args = mock_service.ensure_checklist.call_args
        assert call_args[1]["name"] == "Custom Checklist"

    def test_create_card_includes_checklist(self, sync_manager, mock_service):
        """Test _create_card creates checklist from acceptance criteria."""
        mock_service.find_card_with_prefix.return_value = (None, None)
        mock_service.lists = {"Backlog": Mock()}
        mock_card = Mock()
        mock_service.lists["Backlog"].add_card.return_value = mock_card
        mock_service.create_card_with_custom_fields.return_value = mock_card

        task = TaskData(
            id="TASK-001",
            title="Test task",
            acceptance_criteria=["AC 1", "AC 2"],
            checked_criteria=["AC 1"]
        )

        sync_manager._create_card(task, "Backlog")

        mock_service.ensure_checklist.assert_called_once_with(
            card=mock_card,
            name="Acceptance Criteria",
            items=["AC 1", "AC 2"],
            checked_items=["AC 1"]
        )

    def test_update_card_syncs_checklist(self, sync_manager, mock_service):
        """Test _update_card syncs checklist."""
        mock_card = Mock()
        mock_card.description = "Created by: PairCoder"

        task = TaskData(
            id="TASK-001",
            title="Test task",
            acceptance_criteria=["AC 1", "AC 2"],
            checked_criteria=["AC 2"]
        )

        sync_manager._update_card(mock_card, task)

        mock_service.ensure_checklist.assert_called_once_with(
            card=mock_card,
            name="Acceptance Criteria",
            items=["AC 1", "AC 2"],
            checked_items=["AC 2"]
        )


class TestTrelloToLocalSyncChecklist:
    """Tests for TrelloToLocalSync checklist functionality."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock(spec=TrelloService)
        service.board = Mock()
        return service

    @pytest.fixture
    def temp_tasks_dir(self):
        """Create temporary tasks directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sync_manager(self, mock_service, temp_tasks_dir):
        """Create TrelloToLocalSync with mocks."""
        return TrelloToLocalSync(mock_service, temp_tasks_dir)

    def test_sync_checklist_to_task_updates_unchecked_to_checked(self, sync_manager, mock_service):
        """Test _sync_checklist_to_task updates unchecked items to checked."""
        mock_card = Mock()
        mock_service.get_checklist_by_name.return_value = {
            "id": "cl1",
            "name": "Acceptance Criteria",
            "items": [
                {"id": "item1", "name": "First item", "checked": True},
                {"id": "item2", "name": "Second item", "checked": False},
            ]
        }

        mock_task = Mock()
        mock_task.body = """
# Acceptance Criteria

- [ ] First item
- [ ] Second item
"""

        changes = sync_manager._sync_checklist_to_task(mock_card, mock_task)

        assert changes is not None
        assert len(changes["items_updated"]) == 1
        assert changes["items_updated"][0]["item"] == "First item"
        assert changes["items_updated"][0]["to"] == "checked"
        assert "- [x] First item" in mock_task.body
        assert "- [ ] Second item" in mock_task.body

    def test_sync_checklist_to_task_updates_checked_to_unchecked(self, sync_manager, mock_service):
        """Test _sync_checklist_to_task updates checked items to unchecked."""
        mock_card = Mock()
        mock_service.get_checklist_by_name.return_value = {
            "id": "cl1",
            "name": "Acceptance Criteria",
            "items": [
                {"id": "item1", "name": "First item", "checked": False},
            ]
        }

        mock_task = Mock()
        mock_task.body = "- [x] First item"

        changes = sync_manager._sync_checklist_to_task(mock_card, mock_task)

        assert changes is not None
        assert len(changes["items_updated"]) == 1
        assert changes["items_updated"][0]["item"] == "First item"
        assert changes["items_updated"][0]["to"] == "unchecked"
        assert "- [ ] First item" in mock_task.body

    def test_sync_checklist_to_task_no_checklist(self, sync_manager, mock_service):
        """Test _sync_checklist_to_task returns None when no checklist found."""
        mock_card = Mock()
        mock_service.get_checklist_by_name.return_value = None

        mock_task = Mock()
        mock_task.body = "- [ ] Some item"

        changes = sync_manager._sync_checklist_to_task(mock_card, mock_task)

        assert changes is None

    def test_sync_checklist_to_task_no_changes(self, sync_manager, mock_service):
        """Test _sync_checklist_to_task returns None when no changes needed."""
        mock_card = Mock()
        mock_service.get_checklist_by_name.return_value = {
            "id": "cl1",
            "name": "Acceptance Criteria",
            "items": [
                {"id": "item1", "name": "First item", "checked": True},
            ]
        }

        mock_task = Mock()
        mock_task.body = "- [x] First item"

        changes = sync_manager._sync_checklist_to_task(mock_card, mock_task)

        assert changes is None  # No changes needed

    def test_sync_checklist_to_task_preserves_indentation(self, sync_manager, mock_service):
        """Test _sync_checklist_to_task preserves original indentation."""
        mock_card = Mock()
        mock_service.get_checklist_by_name.return_value = {
            "id": "cl1",
            "name": "Acceptance Criteria",
            "items": [
                {"id": "item1", "name": "Indented item", "checked": True},
            ]
        }

        mock_task = Mock()
        mock_task.body = "    - [ ] Indented item"

        sync_manager._sync_checklist_to_task(mock_card, mock_task)

        assert "    - [x] Indented item" in mock_task.body

    def test_sync_card_to_task_includes_checklist(self, sync_manager, mock_service):
        """Test sync_card_to_task includes checklist changes."""
        mock_card = Mock()
        mock_card.name = "[TASK-001] Test task"
        mock_card.due_date = None
        mock_list = Mock()
        mock_list.name = "In Progress"
        mock_card.get_list.return_value = mock_list

        mock_service.get_checklist_by_name.return_value = {
            "id": "cl1",
            "name": "Acceptance Criteria",
            "items": [{"id": "item1", "name": "Test item", "checked": True}]
        }

        mock_task = Mock()
        mock_task.status = Mock()
        mock_task.status.value = "in_progress"
        mock_task.body = "- [ ] Test item"

        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = mock_task

        result = sync_manager.sync_card_to_task(mock_card)

        assert "checklist" in result.changes
        assert len(result.changes["checklist"]["items_updated"]) == 1


class TestTrelloServiceChecklist:
    """Tests for TrelloService checklist methods."""

    def test_get_card_checklists(self):
        """Test getting checklists from a card."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_checklist = Mock()
            mock_checklist.id = "cl1"
            mock_checklist.name = "My Checklist"
            mock_checklist.items = [
                {"id": "item1", "name": "Item 1", "checked": False, "pos": 1},
                {"id": "item2", "name": "Item 2", "checked": True, "pos": 2},
            ]
            mock_card.checklists = [mock_checklist]

            checklists = service.get_card_checklists(mock_card)

            assert len(checklists) == 1
            assert checklists[0]["id"] == "cl1"
            assert checklists[0]["name"] == "My Checklist"
            assert len(checklists[0]["items"]) == 2

    def test_get_checklist_by_name(self):
        """Test finding checklist by name."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_checklist = Mock()
            mock_checklist.id = "cl1"
            mock_checklist.name = "Acceptance Criteria"
            mock_checklist.items = []
            mock_card.checklists = [mock_checklist]

            checklist = service.get_checklist_by_name(mock_card, "acceptance criteria")

            assert checklist is not None
            assert checklist["name"] == "Acceptance Criteria"

    def test_get_checklist_by_name_not_found(self):
        """Test finding non-existent checklist."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.checklists = []

            checklist = service.get_checklist_by_name(mock_card, "Missing")

            assert checklist is None

    def test_create_checklist(self):
        """Test creating a new checklist."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_new_checklist = Mock()
            mock_new_checklist.id = "cl_new"
            mock_new_checklist.name = "New Checklist"
            mock_card.add_checklist.return_value = mock_new_checklist

            checklist = service.create_checklist(mock_card, "New Checklist")

            assert checklist is not None
            assert checklist["id"] == "cl_new"
            assert checklist["name"] == "New Checklist"
            mock_card.add_checklist.assert_called_once_with("New Checklist", [])

    def test_add_checklist_item(self):
        """Test adding item to checklist."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            service.client.fetch_json.return_value = {
                "id": "item_new",
                "name": "New Item",
                "state": "incomplete"
            }

            item = service.add_checklist_item(mock_card, "cl1", "New Item", checked=False)

            assert item is not None
            assert item["id"] == "item_new"
            assert item["name"] == "New Item"
            assert item["checked"] is False

    def test_add_checklist_item_checked(self):
        """Test adding checked item to checklist."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            service.client.fetch_json.return_value = {
                "id": "item_new",
                "name": "Done Item",
                "state": "complete"
            }

            item = service.add_checklist_item(mock_card, "cl1", "Done Item", checked=True)

            assert item is not None
            assert item["checked"] is True

    def test_update_checklist_item(self):
        """Test updating checklist item."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.id = "card123"

            result = service.update_checklist_item(mock_card, "cl1", "item1", checked=True)

            assert result is True
            service.client.fetch_json.assert_called_once()
            call_args = service.client.fetch_json.call_args
            assert "/cards/card123/checkItem/item1" in call_args[0][0]
            assert call_args[1]["post_args"]["state"] == "complete"

    def test_delete_checklist(self):
        """Test deleting a checklist."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            result = service.delete_checklist("cl123")

            assert result is True
            service.client.fetch_json.assert_called_once()
            call_args = service.client.fetch_json.call_args
            assert "/checklists/cl123" in call_args[0][0]
            assert call_args[1]["http_method"] == "DELETE"

    def test_ensure_checklist_creates_new(self):
        """Test ensure_checklist creates new checklist when not exists."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.checklists = []  # No existing checklists

            mock_new_checklist = Mock()
            mock_new_checklist.id = "cl_new"
            mock_new_checklist.name = "Acceptance Criteria"
            mock_card.add_checklist.return_value = mock_new_checklist

            service.client.fetch_json.return_value = {
                "id": "item1", "name": "Item 1", "state": "incomplete"
            }

            result = service.ensure_checklist(
                mock_card, "Acceptance Criteria",
                items=["Item 1", "Item 2"],
                checked_items=["Item 2"]
            )

            assert result is not None
            mock_card.add_checklist.assert_called_once()

    def test_ensure_checklist_updates_existing(self):
        """Test ensure_checklist updates existing checklist."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_checklist = Mock()
            mock_checklist.id = "cl1"
            mock_checklist.name = "Acceptance Criteria"
            mock_checklist.items = [
                {"id": "item1", "name": "Existing Item", "checked": False, "pos": 1}
            ]

            mock_card = Mock()
            mock_card.id = "card123"
            mock_card.checklists = [mock_checklist]

            service.client.fetch_json.return_value = {"id": "item2", "name": "New Item", "state": "incomplete"}

            result = service.ensure_checklist(
                mock_card, "Acceptance Criteria",
                items=["Existing Item", "New Item"],
                checked_items=[]
            )

            assert result is not None
            # Should add missing "New Item"
            assert service.client.fetch_json.called


# ==================== DUE DATE TESTS ====================

from datetime import datetime, timedelta, timezone
from bpsai_pair.trello.sync import (
    DueDateConfig,
    calculate_due_date_from_effort,
)


class TestDueDateConfig:
    """Tests for DueDateConfig class."""

    def test_default_effort_days(self):
        """Test default days for each effort level."""
        config = DueDateConfig()
        assert config.effort_days == {"S": 1, "M": 2, "L": 4}

    def test_custom_effort_days(self):
        """Test custom days for each effort level."""
        config = DueDateConfig(effort_days={"S": 2, "M": 5, "L": 10})
        assert config.effort_days["S"] == 2
        assert config.effort_days["M"] == 5
        assert config.effort_days["L"] == 10

    def test_get_days_for_effort(self):
        """Test getting days for effort level."""
        config = DueDateConfig()
        assert config.get_days_for_effort("S") == 1
        assert config.get_days_for_effort("M") == 2
        assert config.get_days_for_effort("L") == 4

    def test_get_days_for_effort_case_insensitive(self):
        """Test getting days is case insensitive."""
        config = DueDateConfig()
        assert config.get_days_for_effort("s") == 1
        assert config.get_days_for_effort("m") == 2
        assert config.get_days_for_effort("l") == 4

    def test_get_days_for_unknown_effort(self):
        """Test getting days for unknown effort defaults to M."""
        config = DueDateConfig()
        assert config.get_days_for_effort("XL") == 2  # default to M days
        assert config.get_days_for_effort("unknown") == 2


class TestCalculateDueDateFromEffort:
    """Tests for calculate_due_date_from_effort function."""

    def test_small_effort_one_day(self):
        """Test S effort adds 1 day."""
        base_date = datetime(2025, 12, 17, 10, 0, 0, tzinfo=timezone.utc)
        result = calculate_due_date_from_effort("S", base_date=base_date)
        expected = datetime(2025, 12, 18, 10, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_medium_effort_two_days(self):
        """Test M effort adds 2 days."""
        base_date = datetime(2025, 12, 17, 10, 0, 0, tzinfo=timezone.utc)
        result = calculate_due_date_from_effort("M", base_date=base_date)
        expected = datetime(2025, 12, 19, 10, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_large_effort_four_days(self):
        """Test L effort adds 4 days."""
        base_date = datetime(2025, 12, 17, 10, 0, 0, tzinfo=timezone.utc)
        result = calculate_due_date_from_effort("L", base_date=base_date)
        expected = datetime(2025, 12, 21, 10, 0, 0, tzinfo=timezone.utc)
        assert result == expected

    def test_uses_current_time_as_default(self):
        """Test uses current time if no base_date provided."""
        before = datetime.now(timezone.utc)
        result = calculate_due_date_from_effort("S")
        after = datetime.now(timezone.utc)

        # Result should be ~1 day from now
        expected_min = before + timedelta(days=1)
        expected_max = after + timedelta(days=1)
        assert expected_min <= result <= expected_max

    def test_custom_config(self):
        """Test with custom DueDateConfig."""
        config = DueDateConfig(effort_days={"S": 3, "M": 7, "L": 14})
        base_date = datetime(2025, 12, 17, 10, 0, 0, tzinfo=timezone.utc)
        result = calculate_due_date_from_effort("S", base_date=base_date, config=config)
        expected = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)
        assert result == expected


class TestTaskModelDueDate:
    """Tests for Task model due_date field."""

    def test_task_has_due_date_field(self):
        """Test Task model has due_date field."""
        from bpsai_pair.planning.models import Task
        task = Task(
            id="TASK-001",
            title="Test Task",
            plan_id="plan-1"
        )
        assert hasattr(task, 'due_date')
        assert task.due_date is None  # Default is None

    def test_task_with_due_date(self):
        """Test Task can be created with due_date."""
        from bpsai_pair.planning.models import Task
        due = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)
        task = Task(
            id="TASK-001",
            title="Test Task",
            plan_id="plan-1",
            due_date=due
        )
        assert task.due_date == due

    def test_task_to_dict_includes_due_date(self):
        """Test Task.to_dict includes due_date when set."""
        from bpsai_pair.planning.models import Task
        due = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)
        task = Task(
            id="TASK-001",
            title="Test Task",
            plan_id="plan-1",
            due_date=due
        )
        result = task.to_dict()
        assert "due_date" in result
        assert result["due_date"] == due.isoformat()

    def test_task_to_dict_excludes_none_due_date(self):
        """Test Task.to_dict excludes due_date when None."""
        from bpsai_pair.planning.models import Task
        task = Task(
            id="TASK-001",
            title="Test Task",
            plan_id="plan-1"
        )
        result = task.to_dict()
        assert "due_date" not in result or result.get("due_date") is None

    def test_task_from_dict_with_due_date(self):
        """Test Task.from_dict parses due_date."""
        from bpsai_pair.planning.models import Task
        data = {
            "id": "TASK-001",
            "title": "Test Task",
            "plan": "plan-1",
            "due_date": "2025-12-20T10:00:00+00:00"
        }
        task = Task.from_dict(data)
        assert task.due_date is not None
        assert task.due_date.year == 2025
        assert task.due_date.month == 12
        assert task.due_date.day == 20


class TestTaskDataDueDate:
    """Tests for TaskData due_date handling."""

    def test_taskdata_has_due_date(self):
        """Test TaskData has due_date field."""
        task_data = TaskData(
            id="TASK-001",
            title="Test Task"
        )
        assert hasattr(task_data, 'due_date')
        assert task_data.due_date is None

    def test_taskdata_with_due_date(self):
        """Test TaskData can be created with due_date."""
        due = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)
        task_data = TaskData(
            id="TASK-001",
            title="Test Task",
            due_date=due
        )
        assert task_data.due_date == due

    def test_taskdata_from_task_copies_due_date(self):
        """Test TaskData.from_task copies due_date from Task."""
        mock_task = Mock()
        mock_task.id = "TASK-001"
        mock_task.title = "Test Task"
        mock_task.status = "pending"
        mock_task.body = ""
        mock_task.priority = "P1"
        mock_task.complexity = 30
        mock_task.tags = []
        mock_task.plan = None
        mock_task.due_date = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)

        task_data = TaskData.from_task(mock_task)
        assert task_data.due_date == mock_task.due_date

    def test_taskdata_from_task_handles_missing_due_date(self):
        """Test TaskData.from_task handles missing due_date."""
        mock_task = Mock()
        mock_task.id = "TASK-001"
        mock_task.title = "Test Task"
        mock_task.status = "pending"
        mock_task.body = ""
        mock_task.priority = "P1"
        mock_task.complexity = 30
        mock_task.tags = []
        mock_task.plan = None
        del mock_task.due_date  # Remove attribute

        task_data = TaskData.from_task(mock_task)
        assert task_data.due_date is None


class TestTrelloServiceDueDate:
    """Tests for TrelloService due date methods."""

    def test_set_due_date(self):
        """Test setting due date on a card."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.id = "card123"
            due = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)

            result = service.set_due_date(mock_card, due)

            assert result is True
            mock_card.set_due.assert_called_once()

    def test_set_due_date_none(self):
        """Test clearing due date on a card."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.id = "card123"

            result = service.set_due_date(mock_card, None)

            assert result is True
            # Should call API to clear due date
            mock_card.set_due.assert_called_once_with(None)

    def test_get_due_date(self):
        """Test getting due date from a card."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.due_date = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)

            result = service.get_due_date(mock_card)

            assert result == mock_card.due_date

    def test_get_due_date_none(self):
        """Test getting due date from card without due date."""
        with patch("trello.TrelloClient"):
            service = TrelloService("key", "token")

            mock_card = Mock()
            mock_card.due_date = None

            result = service.get_due_date(mock_card)

            assert result is None


class TestTrelloSyncManagerDueDate:
    """Tests for TrelloSyncManager due date sync."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock(spec=TrelloService)
        service.get_custom_fields.return_value = []
        service.get_labels.return_value = []
        return service

    @pytest.fixture
    def sync_manager(self, mock_service):
        """Create TrelloSyncManager with mock service."""
        return TrelloSyncManager(mock_service)

    def test_create_card_sets_explicit_due_date(self, mock_service, sync_manager):
        """Test _create_card sets explicit due_date."""
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True
        mock_service.set_due_date.return_value = True

        due = datetime(2025, 12, 20, 10, 0, 0, tzinfo=timezone.utc)
        task = TaskData(
            id="TASK-001",
            title="Test Task",
            complexity=30,
            due_date=due
        )

        sync_manager._create_card(task, "Backlog")

        mock_service.set_due_date.assert_called_once_with(mock_card, due)

    def test_create_card_calculates_due_date_from_effort(self, mock_service, sync_manager):
        """Test _create_card calculates due_date from effort if not explicit."""
        mock_card = Mock()
        mock_service.create_card_with_custom_fields.return_value = mock_card
        mock_service.set_effort_field.return_value = True
        mock_service.set_due_date.return_value = True

        # S effort = complexity 0-25 = +1 day
        task = TaskData(
            id="TASK-001",
            title="Test Task",
            complexity=20,  # S effort
            due_date=None  # No explicit due date
        )

        sync_manager._create_card(task, "Backlog")

        # Should have called set_due_date with a calculated date
        assert mock_service.set_due_date.called
        call_args = mock_service.set_due_date.call_args
        calculated_due = call_args[0][1]
        # Should be about 1 day from now (S effort)
        now = datetime.now(timezone.utc)
        expected_min = now + timedelta(days=1) - timedelta(minutes=1)
        expected_max = now + timedelta(days=1) + timedelta(minutes=1)
        assert expected_min <= calculated_due <= expected_max

    def test_update_card_syncs_due_date(self, mock_service, sync_manager):
        """Test _update_card syncs due_date."""
        mock_card = Mock()
        mock_card.description = "Created by: PairCoder"
        mock_service.set_card_custom_fields.return_value = {}
        mock_service.set_effort_field.return_value = True
        mock_service.set_due_date.return_value = True

        due = datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc)
        task = TaskData(
            id="TASK-001",
            title="Test Task",
            complexity=30,
            due_date=due
        )

        sync_manager._update_card(mock_card, task)

        mock_service.set_due_date.assert_called_once_with(mock_card, due)


class TestTrelloToLocalSyncDueDate:
    """Tests for TrelloToLocalSync due date sync."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock(spec=TrelloService)
        service.board = Mock()
        return service

    @pytest.fixture
    def temp_tasks_dir(self):
        """Create temporary tasks directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sync_manager(self, mock_service, temp_tasks_dir):
        """Create TrelloToLocalSync with mocks."""
        return TrelloToLocalSync(mock_service, temp_tasks_dir)

    def test_sync_card_due_date_to_task(self, sync_manager, mock_service):
        """Test syncing due date from card to task."""
        mock_card = Mock()
        mock_card.name = "[TASK-001] Test task"
        mock_card.due_date = datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc)
        mock_list = Mock()
        mock_list.name = "In Progress"
        mock_card.get_list.return_value = mock_list

        mock_service.get_checklist_by_name.return_value = None
        mock_service.get_due_date.return_value = mock_card.due_date

        mock_task = Mock()
        mock_task.status = Mock()
        mock_task.status.value = "in_progress"
        mock_task.body = ""
        mock_task.due_date = None  # No due date locally

        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = mock_task

        result = sync_manager.sync_card_to_task(mock_card)

        assert "due_date" in result.changes
        assert result.changes["due_date"]["to"] == mock_card.due_date

    def test_sync_card_due_date_no_change(self, sync_manager, mock_service):
        """Test no change when due dates match."""
        due = datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc)

        mock_card = Mock()
        mock_card.name = "[TASK-001] Test task"
        mock_card.due_date = due
        mock_list = Mock()
        mock_list.name = "In Progress"
        mock_card.get_list.return_value = mock_list

        mock_service.get_checklist_by_name.return_value = None
        mock_service.get_due_date.return_value = due

        mock_task = Mock()
        mock_task.status = Mock()
        mock_task.status.value = "in_progress"
        mock_task.body = ""
        mock_task.due_date = due  # Same due date

        sync_manager._task_parser = Mock()
        sync_manager._task_parser.get_task_by_id.return_value = mock_task

        result = sync_manager.sync_card_to_task(mock_card)

        assert "due_date" not in result.changes
