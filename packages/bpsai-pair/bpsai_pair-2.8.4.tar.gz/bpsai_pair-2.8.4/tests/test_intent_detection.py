"""Tests for intent detection module."""
import pytest

from bpsai_pair.planning.intent_detection import (
    WorkIntent,
    IntentMatch,
    IntentDetector,
    PlanningModeManager,
    FLOW_SUGGESTIONS,
)


class TestWorkIntent:
    """Tests for WorkIntent enum."""

    def test_all_intents_defined(self):
        """Test all expected intents exist."""
        expected = ["FEATURE", "BUG_FIX", "REFACTOR", "DOCUMENTATION",
                    "TESTING", "REVIEW", "QUESTION", "TRIVIAL", "UNKNOWN"]
        for intent_name in expected:
            assert hasattr(WorkIntent, intent_name)


class TestIntentMatch:
    """Tests for IntentMatch dataclass."""

    def test_is_planning_required_feature(self):
        """Test feature intent requires planning."""
        match = IntentMatch(
            intent=WorkIntent.FEATURE,
            confidence=0.9,
            triggers=["build a new"],
        )
        assert match.is_planning_required() is True

    def test_is_planning_required_low_confidence(self):
        """Test low confidence doesn't require planning."""
        match = IntentMatch(
            intent=WorkIntent.FEATURE,
            confidence=0.5,
            triggers=["feature"],
        )
        assert match.is_planning_required() is False

    def test_is_planning_required_refactor(self):
        """Test refactor requires planning with high confidence."""
        match = IntentMatch(
            intent=WorkIntent.REFACTOR,
            confidence=0.9,
            triggers=["refactor"],
        )
        assert match.is_planning_required() is True

    def test_is_planning_required_bug_fix(self):
        """Test bug fix doesn't require planning."""
        match = IntentMatch(
            intent=WorkIntent.BUG_FIX,
            confidence=0.95,
            triggers=["fix the bug"],
        )
        assert match.is_planning_required() is False


class TestIntentDetector:
    """Tests for IntentDetector."""

    @pytest.fixture
    def detector(self):
        """Create a detector instance."""
        return IntentDetector()

    def test_detect_feature_build(self, detector):
        """Test detecting feature request with 'build'."""
        match = detector.detect("I want to build a new authentication system")
        assert match.intent == WorkIntent.FEATURE
        assert match.confidence >= 0.7

    def test_detect_feature_create(self, detector):
        """Test detecting feature request with 'create'."""
        match = detector.detect("Create a dashboard component")
        assert match.intent == WorkIntent.FEATURE
        assert match.confidence >= 0.7

    def test_detect_feature_implement(self, detector):
        """Test detecting feature request with 'implement'."""
        match = detector.detect("Implement user profile functionality")
        assert match.intent == WorkIntent.FEATURE
        assert match.confidence >= 0.7

    def test_detect_bug_fix(self, detector):
        """Test detecting bug fix intent."""
        match = detector.detect("Fix the bug in the login system")
        assert match.intent == WorkIntent.BUG_FIX
        assert match.confidence >= 0.8

    def test_detect_bug_fix_error(self, detector):
        """Test detecting bug fix with error message."""
        match = detector.detect("The app isn't working correctly")
        assert match.intent == WorkIntent.BUG_FIX
        assert match.confidence >= 0.7

    def test_detect_refactor(self, detector):
        """Test detecting refactor intent."""
        match = detector.detect("Refactor the database module")
        assert match.intent == WorkIntent.REFACTOR
        assert match.confidence >= 0.9

    def test_detect_refactor_cleanup(self, detector):
        """Test detecting refactor with 'clean up'."""
        match = detector.detect("Clean up the authentication code")
        assert match.intent == WorkIntent.REFACTOR
        assert match.confidence >= 0.7

    def test_detect_documentation(self, detector):
        """Test detecting documentation intent."""
        match = detector.detect("Update the README documentation")
        assert match.intent == WorkIntent.DOCUMENTATION
        assert match.confidence >= 0.8

    def test_detect_testing(self, detector):
        """Test detecting testing intent."""
        match = detector.detect("Write unit tests for the parser")
        assert match.intent == WorkIntent.TESTING
        assert match.confidence >= 0.8

    def test_detect_review(self, detector):
        """Test detecting review intent."""
        match = detector.detect("Review the recent changes")
        assert match.intent == WorkIntent.REVIEW
        assert match.confidence >= 0.8

    def test_detect_question(self, detector):
        """Test detecting question intent."""
        match = detector.detect("How does the authentication work?")
        assert match.intent == WorkIntent.QUESTION
        assert match.confidence >= 0.7

    def test_detect_trivial(self, detector):
        """Test detecting trivial intent."""
        match = detector.detect("Fix the typo in the variable name")
        assert match.intent == WorkIntent.TRIVIAL
        assert match.confidence >= 0.8

    def test_detect_unknown(self, detector):
        """Test unknown when no patterns match."""
        detector_strict = IntentDetector(confidence_threshold=0.99)
        match = detector_strict.detect("hello world")
        assert match.intent == WorkIntent.UNKNOWN

    def test_detect_all_returns_multiple(self, detector):
        """Test detect_all returns multiple matches."""
        # This text could be both a feature and testing
        matches = detector.detect_all("Add a new feature with tests")
        assert len(matches) >= 1
        # All matches should have confidence >= threshold
        for match in matches:
            assert match.confidence >= detector.confidence_threshold

    def test_suggested_flow_for_feature(self, detector):
        """Test suggested flow for feature."""
        match = detector.detect("Build a new API endpoint")
        assert match.suggested_flow == "design-plan-implement"

    def test_suggested_flow_for_bug(self, detector):
        """Test suggested flow for bug fix."""
        match = detector.detect("Fix the broken login")
        assert match.suggested_flow == "tdd-implement"

    def test_should_enter_planning_mode_feature(self, detector):
        """Test should enter planning for feature."""
        should_plan, match = detector.should_enter_planning_mode(
            "Build a complete user management system with authentication"
        )
        assert should_plan is True
        assert match is not None
        assert match.intent == WorkIntent.FEATURE

    def test_should_not_enter_planning_trivial(self, detector):
        """Test should not enter planning for trivial."""
        should_plan, match = detector.should_enter_planning_mode(
            "Fix the typo"
        )
        assert should_plan is False

    def test_get_flow_suggestion(self, detector):
        """Test get_flow_suggestion."""
        flow = detector.get_flow_suggestion("Build a dashboard")
        assert flow == "design-plan-implement"

    def test_extract_info_quoted_items(self, detector):
        """Test extraction of quoted items."""
        match = detector.detect('Create a feature called "UserProfile"')
        assert "quoted_items" in match.extracted_info or "name" in match.extracted_info

    def test_extract_info_error_types(self, detector):
        """Test extraction of error types."""
        match = detector.detect("Getting a TypeError and ValueError")
        if match.intent == WorkIntent.BUG_FIX:
            assert "errors" in match.extracted_info


class TestPlanningModeManager:
    """Tests for PlanningModeManager."""

    def test_init_defaults(self):
        """Test default initialization."""
        manager = PlanningModeManager()
        assert manager.auto_enter is True
        assert manager.in_planning_mode is False

    def test_init_disabled(self):
        """Test initialization with auto_enter disabled."""
        manager = PlanningModeManager(auto_enter=False)
        assert manager.auto_enter is False

    def test_process_input_triggers_planning(self):
        """Test process_input triggers planning mode."""
        manager = PlanningModeManager()
        result = manager.process_input(
            "Build a comprehensive notification system for the application"
        )
        assert result["should_enter_planning"] is True
        assert result["suggested_flow"] is not None
        assert manager.in_planning_mode is True

    def test_process_input_no_planning(self):
        """Test process_input doesn't trigger for trivial."""
        manager = PlanningModeManager()
        result = manager.process_input("fix typo")
        assert result["should_enter_planning"] is False
        assert manager.in_planning_mode is False

    def test_process_input_disabled(self):
        """Test process_input when disabled."""
        manager = PlanningModeManager(auto_enter=False)
        result = manager.process_input(
            "Build a new feature"
        )
        assert result["should_enter_planning"] is False

    def test_exit_planning_mode(self):
        """Test exiting planning mode."""
        manager = PlanningModeManager()
        manager.process_input("Build a new system")
        assert manager.in_planning_mode is True

        manager.exit_planning_mode()
        assert manager.in_planning_mode is False
        assert manager.current_intent is None

    def test_get_status(self):
        """Test get_status."""
        manager = PlanningModeManager()
        manager.process_input("Build a dashboard")

        status = manager.get_status()
        assert "in_planning_mode" in status
        assert "auto_enter" in status
        assert "current_intent" in status


class TestFlowSuggestions:
    """Tests for flow suggestions mapping."""

    def test_feature_suggests_design_plan(self):
        """Test feature suggests design-plan-implement."""
        assert FLOW_SUGGESTIONS[WorkIntent.FEATURE] == "design-plan-implement"

    def test_bug_suggests_tdd(self):
        """Test bug fix suggests tdd-implement."""
        assert FLOW_SUGGESTIONS[WorkIntent.BUG_FIX] == "tdd-implement"

    def test_refactor_suggests_design_plan(self):
        """Test refactor suggests design-plan-implement."""
        assert FLOW_SUGGESTIONS[WorkIntent.REFACTOR] == "design-plan-implement"

    def test_review_suggests_review(self):
        """Test review suggests review flow."""
        assert FLOW_SUGGESTIONS[WorkIntent.REVIEW] == "review"
