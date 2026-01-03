"""Tests for Trello card description templates."""
import pytest
from bpsai_pair.trello.templates import (
    CardDescriptionTemplate,
    CardDescriptionData,
    should_preserve_description,
    DEFAULT_BPS_TEMPLATE,
)


class TestCardDescriptionData:
    """Tests for CardDescriptionData dataclass."""

    def test_default_values(self):
        """Test default values are set correctly."""
        data = CardDescriptionData(task_id="TASK-001", title="Test")
        assert data.acceptance_criteria == []
        assert data.tags == []
        assert data.complexity == 50
        assert data.priority == "P1"

    def test_with_all_fields(self):
        """Test with all fields populated."""
        data = CardDescriptionData(
            task_id="TASK-001",
            title="Test Task",
            objective="Do the thing",
            implementation_plan="Step 1, Step 2",
            acceptance_criteria=["Tests pass", "Code reviewed"],
            complexity=35,
            priority="P0",
            plan_title="Sprint 14",
            task_link="https://example.com/task",
            pr_link="https://github.com/pr/123",
            tags=["backend", "api"],
        )
        assert data.task_id == "TASK-001"
        assert data.objective == "Do the thing"
        assert len(data.acceptance_criteria) == 2


class TestCardDescriptionTemplate:
    """Tests for CardDescriptionTemplate class."""

    @pytest.fixture
    def template(self):
        """Create a template instance."""
        return CardDescriptionTemplate()

    def test_extract_sections_objective(self, template):
        """Test extracting objective section."""
        body = """# Objective
This is the objective.

# Implementation Plan
Step 1
Step 2
"""
        sections = template.extract_sections(body)
        assert "objective" in sections
        assert "This is the objective." in sections["objective"]

    def test_extract_sections_implementation(self, template):
        """Test extracting implementation plan section."""
        body = """## Implementation Plan
- Step 1
- Step 2
- Step 3

## Acceptance Criteria
- [ ] Test passes
"""
        sections = template.extract_sections(body)
        assert "implementation_plan" in sections
        assert "Step 1" in sections["implementation_plan"]

    def test_extract_sections_empty(self, template):
        """Test extracting sections from empty body."""
        sections = template.extract_sections("")
        assert sections == {}

    def test_extract_objective_from_first_paragraph(self, template):
        """Test extracting objective from first paragraph when no section."""
        body = """This is the first paragraph describing the task.

This is more details.

- Some bullet points
"""
        sections = template.extract_sections(body)
        objective = template.extract_objective(body, sections)
        assert "This is the first paragraph" in objective

    def test_extract_objective_from_section(self, template):
        """Test extracting objective from explicit section."""
        body = """# Objective
Explicit objective here.

# Other stuff
"""
        sections = template.extract_sections(body)
        objective = template.extract_objective(body, sections)
        assert "Explicit objective here." in objective

    def test_extract_implementation_plan_from_section(self, template):
        """Test extracting implementation plan from explicit section."""
        body = """# Implementation Plan
- Step 1: Do this
- Step 2: Do that
"""
        sections = template.extract_sections(body)
        plan = template.extract_implementation_plan(body, sections)
        assert "Step 1" in plan
        assert "Step 2" in plan

    def test_extract_implementation_plan_fallback(self, template):
        """Test fallback when no explicit implementation section."""
        body = """No implementation section.

But there are some bullets:
- First bullet
- Second bullet
"""
        sections = template.extract_sections(body)
        plan = template.extract_implementation_plan(body, sections)
        # Should find bullet points
        assert "First bullet" in plan or "_To be defined_" in plan

    def test_format_acceptance_criteria(self, template):
        """Test formatting acceptance criteria."""
        criteria = ["Tests pass", "Code reviewed", "Docs updated"]
        formatted = template.format_acceptance_criteria(criteria)

        assert "- [ ] Tests pass" in formatted
        assert "- [ ] Code reviewed" in formatted
        assert "- [ ] Docs updated" in formatted

    def test_format_acceptance_criteria_empty(self, template):
        """Test formatting empty acceptance criteria."""
        formatted = template.format_acceptance_criteria([])
        assert "_To be defined_" in formatted

    def test_format_links(self, template):
        """Test formatting links section."""
        links = template.format_links("TASK-001")
        assert "TASK-001" in links
        assert "PR: _pending_" in links

    def test_format_links_with_urls(self, template):
        """Test formatting links with actual URLs."""
        links = template.format_links(
            "TASK-001",
            task_link="https://example.com/task",
            pr_link="https://github.com/pr/123"
        )
        assert "https://example.com/task" in links
        assert "https://github.com/pr/123" in links

    def test_format_metadata(self, template):
        """Test formatting metadata footer."""
        data = CardDescriptionData(
            task_id="TASK-001",
            title="Test",
            complexity=35,
            priority="P0",
            plan_title="Sprint 14"
        )
        metadata = template.format_metadata(data)
        assert "Complexity: 35" in metadata
        assert "Priority: P0" in metadata
        assert "Plan: Sprint 14" in metadata

    def test_render_full_description(self, template):
        """Test rendering full card description."""
        data = CardDescriptionData(
            task_id="TASK-001",
            title="Implement feature",
            acceptance_criteria=["Tests pass", "Docs updated"],
            complexity=35,
            priority="P0",
            plan_title="Sprint 14"
        )
        body = """This is the objective of the task.

# Implementation Plan
- Step 1
- Step 2
"""
        description = template.render(data, body)

        # Check all sections present
        assert "## Objective" in description
        assert "This is the objective" in description
        assert "## Implementation Plan" in description
        assert "## Acceptance Criteria" in description
        assert "- [ ] Tests pass" in description
        assert "## Links" in description
        assert "TASK-001" in description
        assert "Complexity: 35" in description
        assert "Created by: PairCoder" in description

    def test_render_minimal_data(self, template):
        """Test rendering with minimal data."""
        data = CardDescriptionData(
            task_id="TASK-001",
            title="Simple task"
        )
        description = template.render(data, "")

        assert "## Objective" in description
        assert "## Acceptance Criteria" in description
        assert "Created by: PairCoder" in description

    def test_from_task_data(self):
        """Test convenience method from_task_data."""
        # Create a mock TaskData-like object
        class MockTaskData:
            id = "TASK-001"
            title = "Test Task"
            description = "Task objective here."
            acceptance_criteria = ["Test passes"]
            complexity = 25
            priority = "P1"
            plan_title = "Sprint 14"
            tags = ["backend"]

        result = CardDescriptionTemplate.from_task_data(MockTaskData())

        assert "## Objective" in result
        assert "Task objective here." in result
        assert "- [ ] Test passes" in result
        assert "Complexity: 25" in result

    def test_custom_template(self):
        """Test using custom template."""
        custom_template = """# {task_id}: {title}

{objective}

---
{metadata}"""

        # Note: Custom template would need different placeholders
        # This test verifies template can be customized
        template = CardDescriptionTemplate(custom_template)
        assert template.template == custom_template


class TestShouldPreserveDescription:
    """Tests for should_preserve_description function."""

    def test_empty_description_not_preserved(self):
        """Test empty description is not preserved."""
        assert should_preserve_description("") is False

    def test_generated_description_not_preserved(self):
        """Test auto-generated description is not preserved."""
        desc = """## Objective
Test task

---
Complexity: 35 | Priority: P0
Created by: PairCoder"""
        assert should_preserve_description(desc) is False

    def test_manual_description_preserved(self):
        """Test manually created description is preserved."""
        desc = """This is a custom description.
It doesn't have our marker.
"""
        assert should_preserve_description(desc) is True

    def test_custom_marker(self):
        """Test with custom marker."""
        desc = "Has custom marker"
        assert should_preserve_description(desc, "custom marker") is False
        assert should_preserve_description(desc, "other marker") is True


class TestBPSFormatCompliance:
    """Tests to verify BPS format compliance."""

    @pytest.fixture
    def template(self):
        return CardDescriptionTemplate()

    def test_bps_sections_present(self, template):
        """Test that all required BPS sections are in output."""
        data = CardDescriptionData(
            task_id="TASK-001",
            title="BPS Test",
            acceptance_criteria=["Test 1", "Test 2"],
            complexity=50,
            priority="P1",
            plan_title="Test Plan"
        )
        body = """This is the objective.

# Implementation Plan
- Do step 1
- Do step 2
"""
        result = template.render(data, body)

        # BPS required sections
        assert "## Objective" in result
        assert "## Implementation Plan" in result
        assert "## Acceptance Criteria" in result
        assert "## Links" in result
        assert "---" in result  # Footer separator
        assert "Created by: PairCoder" in result

    def test_bps_acceptance_criteria_checkboxes(self, template):
        """Test acceptance criteria are rendered as checkboxes."""
        data = CardDescriptionData(
            task_id="TASK-001",
            title="Test",
            acceptance_criteria=["Criterion A", "Criterion B"]
        )
        result = template.render(data, "")

        assert "- [ ] Criterion A" in result
        assert "- [ ] Criterion B" in result

    def test_bps_metadata_format(self, template):
        """Test metadata follows BPS format."""
        data = CardDescriptionData(
            task_id="TASK-001",
            title="Test",
            complexity=35,
            priority="P0",
            plan_title="Sprint 14"
        )
        metadata = template.format_metadata(data)

        # BPS format: Complexity: X | Priority: Y | Plan: Z
        assert "Complexity: 35" in metadata
        assert "Priority: P0" in metadata
        assert "Plan: Sprint 14" in metadata
        assert "|" in metadata  # Pipe separator

    def test_bps_links_section(self, template):
        """Test links section format."""
        links = template.format_links("TASK-001", pr_link="https://github.com/pr/1")

        assert "- Task:" in links
        assert "TASK-001" in links
        assert "- PR:" in links
        assert "https://github.com/pr/1" in links
