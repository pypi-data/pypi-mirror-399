"""Tests for workflow_guide module."""
import pytest
from pathlib import Path
from unittest.mock import Mock

from bpsai_pair.orchestration.workflow_guide import (
    WorkflowStage,
    WorkflowRequirement,
    WorkflowGuide,
    get_workflow_guide,
    STAGE_TO_LIST,
    LIST_TO_STAGE,
    STATUS_TO_STAGE,
    STAGE_REQUIREMENTS,
    WORKFLOW_RULES,
)


class TestWorkflowStage:
    """Tests for WorkflowStage enum."""

    def test_values(self):
        """Test all stage values exist."""
        assert WorkflowStage.INTAKE.value == "intake"
        assert WorkflowStage.PLANNED.value == "planned"
        assert WorkflowStage.IN_PROGRESS.value == "in_progress"
        assert WorkflowStage.REVIEW.value == "review"
        assert WorkflowStage.DONE.value == "done"
        assert WorkflowStage.BLOCKED.value == "blocked"

    def test_all_stages(self):
        """Test all 6 stages are defined."""
        assert len(WorkflowStage) == 6


class TestMappings:
    """Tests for mapping dictionaries."""

    def test_stage_to_list_all_stages(self):
        """Test all stages have list mappings."""
        for stage in WorkflowStage:
            assert stage in STAGE_TO_LIST

    def test_stage_to_list_values(self):
        """Test specific list name mappings."""
        assert STAGE_TO_LIST[WorkflowStage.INTAKE] == "Intake / Backlog"
        assert STAGE_TO_LIST[WorkflowStage.PLANNED] == "Planned / Ready"
        assert STAGE_TO_LIST[WorkflowStage.IN_PROGRESS] == "In Progress"
        assert STAGE_TO_LIST[WorkflowStage.REVIEW] == "Review / Testing"
        assert STAGE_TO_LIST[WorkflowStage.DONE] == "Deployed / Done"
        assert STAGE_TO_LIST[WorkflowStage.BLOCKED] == "Issues / Tech Debt"

    def test_list_to_stage_backlog_variants(self):
        """Test backlog list variants map correctly."""
        assert LIST_TO_STAGE["Intake / Backlog"] == WorkflowStage.INTAKE
        assert LIST_TO_STAGE["Backlog"] == WorkflowStage.INTAKE

    def test_list_to_stage_planned_variants(self):
        """Test planned list variants map correctly."""
        assert LIST_TO_STAGE["Planned / Ready"] == WorkflowStage.PLANNED
        assert LIST_TO_STAGE["Ready"] == WorkflowStage.PLANNED

    def test_list_to_stage_progress(self):
        """Test in progress list maps correctly."""
        assert LIST_TO_STAGE["In Progress"] == WorkflowStage.IN_PROGRESS

    def test_list_to_stage_review_variants(self):
        """Test review list variants map correctly."""
        assert LIST_TO_STAGE["Review / Testing"] == WorkflowStage.REVIEW
        assert LIST_TO_STAGE["Review"] == WorkflowStage.REVIEW
        assert LIST_TO_STAGE["Testing"] == WorkflowStage.REVIEW

    def test_list_to_stage_done_variants(self):
        """Test done list variants map correctly."""
        assert LIST_TO_STAGE["Deployed / Done"] == WorkflowStage.DONE
        assert LIST_TO_STAGE["Done"] == WorkflowStage.DONE

    def test_list_to_stage_blocked_variants(self):
        """Test blocked list variants map correctly."""
        assert LIST_TO_STAGE["Issues / Tech Debt"] == WorkflowStage.BLOCKED
        assert LIST_TO_STAGE["Blocked"] == WorkflowStage.BLOCKED

    def test_status_to_stage_pending(self):
        """Test pending status mappings."""
        assert STATUS_TO_STAGE["pending"] == WorkflowStage.INTAKE
        assert STATUS_TO_STAGE["backlog"] == WorkflowStage.INTAKE

    def test_status_to_stage_planned(self):
        """Test planned status mappings."""
        assert STATUS_TO_STAGE["ready"] == WorkflowStage.PLANNED
        assert STATUS_TO_STAGE["planned"] == WorkflowStage.PLANNED

    def test_status_to_stage_progress(self):
        """Test in_progress status mapping."""
        assert STATUS_TO_STAGE["in_progress"] == WorkflowStage.IN_PROGRESS

    def test_status_to_stage_review(self):
        """Test review status mappings."""
        assert STATUS_TO_STAGE["review"] == WorkflowStage.REVIEW
        assert STATUS_TO_STAGE["testing"] == WorkflowStage.REVIEW

    def test_status_to_stage_done(self):
        """Test done status mappings."""
        assert STATUS_TO_STAGE["done"] == WorkflowStage.DONE
        assert STATUS_TO_STAGE["deployed"] == WorkflowStage.DONE

    def test_status_to_stage_blocked(self):
        """Test blocked status mappings."""
        assert STATUS_TO_STAGE["blocked"] == WorkflowStage.BLOCKED
        assert STATUS_TO_STAGE["issue"] == WorkflowStage.BLOCKED


class TestWorkflowRequirement:
    """Tests for WorkflowRequirement dataclass."""

    def test_create_requirement(self):
        """Test creating a requirement."""
        req = WorkflowRequirement(
            stage=WorkflowStage.INTAKE,
            required_fields=["id", "title"],
            optional_fields=["description"],
            description="Test requirement",
        )
        assert req.stage == WorkflowStage.INTAKE
        assert "id" in req.required_fields
        assert "title" in req.required_fields
        assert "description" in req.optional_fields
        assert req.description == "Test requirement"


class TestStageRequirements:
    """Tests for STAGE_REQUIREMENTS dictionary."""

    def test_all_stages_have_requirements(self):
        """Test all stages have requirements defined."""
        for stage in WorkflowStage:
            assert stage in STAGE_REQUIREMENTS

    def test_intake_requirements(self):
        """Test intake stage requirements."""
        req = STAGE_REQUIREMENTS[WorkflowStage.INTAKE]
        assert "id" in req.required_fields
        assert "title" in req.required_fields

    def test_planned_requirements(self):
        """Test planned stage requirements."""
        req = STAGE_REQUIREMENTS[WorkflowStage.PLANNED]
        assert "objective" in req.required_fields
        assert "implementation_plan" in req.required_fields
        assert "acceptance_criteria" in req.required_fields

    def test_in_progress_requirements(self):
        """Test in_progress stage requirements."""
        req = STAGE_REQUIREMENTS[WorkflowStage.IN_PROGRESS]
        assert "current_step" in req.optional_fields

    def test_review_requirements(self):
        """Test review stage requirements."""
        req = STAGE_REQUIREMENTS[WorkflowStage.REVIEW]
        assert "implementation_summary" in req.required_fields
        assert "verification_steps" in req.required_fields

    def test_done_requirements(self):
        """Test done stage requirements."""
        req = STAGE_REQUIREMENTS[WorkflowStage.DONE]
        assert "verification" in req.required_fields

    def test_blocked_requirements(self):
        """Test blocked stage requirements."""
        req = STAGE_REQUIREMENTS[WorkflowStage.BLOCKED]
        assert "block_reason" in req.required_fields


class TestWorkflowGuide:
    """Tests for WorkflowGuide class."""

    def test_init_no_dir(self):
        """Test initialization without directory."""
        guide = WorkflowGuide()
        assert guide.paircoder_dir is None

    def test_init_with_dir(self, tmp_path):
        """Test initialization with directory."""
        guide = WorkflowGuide(paircoder_dir=tmp_path)
        assert guide.paircoder_dir == tmp_path

    def test_get_stage_for_status(self):
        """Test getting stage for status."""
        guide = WorkflowGuide()
        assert guide.get_stage_for_status("pending") == WorkflowStage.INTAKE
        assert guide.get_stage_for_status("in_progress") == WorkflowStage.IN_PROGRESS
        assert guide.get_stage_for_status("done") == WorkflowStage.DONE

    def test_get_stage_for_status_case_insensitive(self):
        """Test status lookup is case insensitive."""
        guide = WorkflowGuide()
        assert guide.get_stage_for_status("PENDING") == WorkflowStage.INTAKE
        assert guide.get_stage_for_status("In_Progress") == WorkflowStage.IN_PROGRESS

    def test_get_stage_for_status_unknown(self):
        """Test unknown status defaults to intake."""
        guide = WorkflowGuide()
        assert guide.get_stage_for_status("unknown") == WorkflowStage.INTAKE

    def test_get_list_for_stage(self):
        """Test getting list name for stage."""
        guide = WorkflowGuide()
        assert guide.get_list_for_stage(WorkflowStage.INTAKE) == "Intake / Backlog"
        assert guide.get_list_for_stage(WorkflowStage.DONE) == "Deployed / Done"

    def test_get_stage_for_list(self):
        """Test getting stage for list name."""
        guide = WorkflowGuide()
        assert guide.get_stage_for_list("In Progress") == WorkflowStage.IN_PROGRESS
        assert guide.get_stage_for_list("Done") == WorkflowStage.DONE

    def test_get_stage_for_list_unknown(self):
        """Test unknown list returns None."""
        guide = WorkflowGuide()
        assert guide.get_stage_for_list("Unknown List") is None

    def test_can_transition_valid(self):
        """Test valid transitions."""
        guide = WorkflowGuide()
        assert guide.can_transition(WorkflowStage.INTAKE, WorkflowStage.PLANNED)
        assert guide.can_transition(WorkflowStage.PLANNED, WorkflowStage.IN_PROGRESS)
        assert guide.can_transition(WorkflowStage.IN_PROGRESS, WorkflowStage.REVIEW)
        assert guide.can_transition(WorkflowStage.REVIEW, WorkflowStage.DONE)

    def test_can_transition_invalid(self):
        """Test invalid transitions."""
        guide = WorkflowGuide()
        assert not guide.can_transition(WorkflowStage.INTAKE, WorkflowStage.DONE)
        assert not guide.can_transition(WorkflowStage.DONE, WorkflowStage.INTAKE)

    def test_can_transition_to_blocked(self):
        """Test any stage can transition to blocked."""
        guide = WorkflowGuide()
        assert guide.can_transition(WorkflowStage.INTAKE, WorkflowStage.BLOCKED)
        assert guide.can_transition(WorkflowStage.PLANNED, WorkflowStage.BLOCKED)
        assert guide.can_transition(WorkflowStage.IN_PROGRESS, WorkflowStage.BLOCKED)
        assert guide.can_transition(WorkflowStage.REVIEW, WorkflowStage.BLOCKED)

    def test_can_transition_from_blocked(self):
        """Test transitions from blocked."""
        guide = WorkflowGuide()
        assert guide.can_transition(WorkflowStage.BLOCKED, WorkflowStage.INTAKE)
        assert guide.can_transition(WorkflowStage.BLOCKED, WorkflowStage.PLANNED)
        assert guide.can_transition(WorkflowStage.BLOCKED, WorkflowStage.IN_PROGRESS)

    def test_done_is_terminal(self):
        """Test DONE has no valid transitions."""
        guide = WorkflowGuide()
        assert not guide.can_transition(WorkflowStage.DONE, WorkflowStage.INTAKE)
        assert not guide.can_transition(WorkflowStage.DONE, WorkflowStage.PLANNED)

    def test_get_valid_transitions(self):
        """Test getting valid transitions."""
        guide = WorkflowGuide()
        transitions = guide.get_valid_transitions(WorkflowStage.INTAKE)
        assert WorkflowStage.PLANNED in transitions
        assert WorkflowStage.BLOCKED in transitions
        assert WorkflowStage.DONE not in transitions

    def test_get_valid_transitions_done(self):
        """Test DONE has no valid transitions."""
        guide = WorkflowGuide()
        transitions = guide.get_valid_transitions(WorkflowStage.DONE)
        assert transitions == []

    def test_get_requirements(self):
        """Test getting requirements for stage."""
        guide = WorkflowGuide()
        req = guide.get_requirements(WorkflowStage.PLANNED)
        assert isinstance(req, WorkflowRequirement)
        assert "objective" in req.required_fields

    def test_check_requirements_passes(self):
        """Test check_requirements with valid task."""
        guide = WorkflowGuide()
        task = Mock()
        task.id = "TASK-001"
        task.title = "Test task"

        passes, missing = guide.check_requirements(task, WorkflowStage.INTAKE)
        assert passes
        assert missing == []

    def test_check_requirements_fails_missing(self):
        """Test check_requirements with missing fields."""
        guide = WorkflowGuide()
        task = Mock()
        task.id = "TASK-001"
        task.title = None  # Missing

        passes, missing = guide.check_requirements(task, WorkflowStage.INTAKE)
        assert not passes
        assert "title" in missing

    def test_check_requirements_fails_empty_string(self):
        """Test check_requirements treats empty string as missing."""
        guide = WorkflowGuide()
        task = Mock()
        task.id = "TASK-001"
        task.title = "   "  # Whitespace only

        passes, missing = guide.check_requirements(task, WorkflowStage.INTAKE)
        assert not passes
        assert "title" in missing

    def test_check_requirements_planned(self):
        """Test check_requirements for PLANNED stage."""
        guide = WorkflowGuide()
        task = Mock()
        task.id = "TASK-001"
        task.title = "Test"
        task.objective = "Do something"
        task.implementation_plan = "Steps here"
        task.acceptance_criteria = "Criteria here"

        passes, missing = guide.check_requirements(task, WorkflowStage.PLANNED)
        assert passes

    def test_check_requirements_no_attribute(self):
        """Test check_requirements with missing attribute."""
        guide = WorkflowGuide()
        task = Mock(spec=[])  # Empty spec, no attributes

        passes, missing = guide.check_requirements(task, WorkflowStage.INTAKE)
        assert not passes
        assert "id" in missing
        assert "title" in missing

    def test_get_guidance_known_transition(self):
        """Test get_guidance for known transition."""
        guide = WorkflowGuide()
        guidance = guide.get_guidance(WorkflowStage.INTAKE, WorkflowStage.PLANNED)
        assert "moving to Planned" in guidance
        assert "objective" in guidance.lower()

    def test_get_guidance_planned_to_progress(self):
        """Test guidance for planned to in_progress."""
        guide = WorkflowGuide()
        guidance = guide.get_guidance(WorkflowStage.PLANNED, WorkflowStage.IN_PROGRESS)
        assert "Before starting work" in guidance

    def test_get_guidance_progress_to_review(self):
        """Test guidance for in_progress to review."""
        guide = WorkflowGuide()
        guidance = guide.get_guidance(WorkflowStage.IN_PROGRESS, WorkflowStage.REVIEW)
        assert "Before moving to Review" in guidance

    def test_get_guidance_review_to_done(self):
        """Test guidance for review to done."""
        guide = WorkflowGuide()
        guidance = guide.get_guidance(WorkflowStage.REVIEW, WorkflowStage.DONE)
        assert "Before marking as Done" in guidance

    def test_get_guidance_unknown_transition(self):
        """Test get_guidance for unknown transition returns default."""
        guide = WorkflowGuide()
        guidance = guide.get_guidance(WorkflowStage.BLOCKED, WorkflowStage.PLANNED)
        assert "Transition from blocked to planned" in guidance


class TestGetWorkflowGuide:
    """Tests for get_workflow_guide singleton."""

    def test_returns_guide(self):
        """Test get_workflow_guide returns a guide."""
        # Reset singleton
        import bpsai_pair.orchestration.workflow_guide as wg
        wg._workflow_guide = None

        guide = get_workflow_guide()
        assert isinstance(guide, WorkflowGuide)

    def test_returns_same_instance(self):
        """Test singleton returns same instance."""
        import bpsai_pair.orchestration.workflow_guide as wg
        wg._workflow_guide = None

        guide1 = get_workflow_guide()
        guide2 = get_workflow_guide()
        assert guide1 is guide2

    def test_with_path(self, tmp_path):
        """Test singleton can be initialized with path."""
        import bpsai_pair.orchestration.workflow_guide as wg
        wg._workflow_guide = None

        guide = get_workflow_guide(tmp_path)
        assert guide.paircoder_dir == tmp_path


class TestWorkflowRules:
    """Tests for WORKFLOW_RULES constant."""

    def test_rules_defined(self):
        """Test WORKFLOW_RULES is defined and has content."""
        assert WORKFLOW_RULES is not None
        assert len(WORKFLOW_RULES) > 0

    def test_rules_contains_stages(self):
        """Test rules contain all stage names."""
        assert "Intake / Backlog" in WORKFLOW_RULES
        assert "Planned / Ready" in WORKFLOW_RULES
        assert "In Progress" in WORKFLOW_RULES
        assert "Review / Testing" in WORKFLOW_RULES
        assert "Deployed / Done" in WORKFLOW_RULES
        assert "Issues / Tech Debt" in WORKFLOW_RULES

    def test_rules_contains_guidelines(self):
        """Test rules contain agent guidelines."""
        assert "Agent Guidelines" in WORKFLOW_RULES
