"""
Tests for the flows module (PCV2-012).

Tests JSON structure stability for flow run --json output.
"""
import json
import pytest
from pathlib import Path
from typer.testing import CliRunner

# Import v1 models for backward compatibility tests
from bpsai_pair.flows.models import Flow, Step, FlowValidationError, StepStatus
# Import unified parser
from bpsai_pair.flows import FlowParser
from bpsai_pair.cli import app

runner = CliRunner()


# ============================================================================
# Model Tests
# ============================================================================


class TestStep:
    """Test Step model."""

    def test_step_creation(self):
        """Test basic step creation."""
        step = Step(id="test", action="read-files")
        assert step.id == "test"
        assert step.action == "read-files"
        assert step.status == StepStatus.PENDING

    def test_step_to_dict(self):
        """Test step serialization."""
        step = Step(
            id="gather",
            action="read-files",
            description="Gather source files",
            inputs={"patterns": ["*.py"]},
        )
        d = step.to_dict()

        assert d["id"] == "gather"
        assert d["action"] == "read-files"
        assert d["description"] == "Gather source files"
        assert d["inputs"] == {"patterns": ["*.py"]}
        assert d["status"] == "pending"

    def test_step_to_checklist_item(self):
        """Test step renders as checklist item."""
        step = Step(id="test", action="run", description="Run tests")
        item = step.to_checklist_item(1)

        assert "1." in item
        assert "[ ]" in item
        assert "**test**" in item
        assert "Run tests" in item


class TestFlow:
    """Test Flow model."""

    def test_flow_creation(self):
        """Test basic flow creation."""
        steps = [Step(id="s1", action="a1")]
        flow = Flow(name="test", description="Test flow", steps=steps)

        assert flow.name == "test"
        assert flow.description == "Test flow"
        assert len(flow.steps) == 1

    def test_flow_to_dict_structure(self):
        """Test flow JSON structure stability - critical for API consumers."""
        steps = [
            Step(id="gather", action="read-files", description="Read files"),
            Step(id="process", action="llm-call", description="Process"),
        ]
        flow = Flow(
            name="code-review",
            description="Review code",
            steps=steps,
            variables={"reviewer": "team"},
            version="1",
        )
        d = flow.to_dict()

        # Required top-level keys (API contract)
        assert "name" in d
        assert "description" in d
        assert "version" in d
        assert "steps" in d
        assert "step_count" in d
        assert "variables" in d

        # Values match
        assert d["name"] == "code-review"
        assert d["description"] == "Review code"
        assert d["step_count"] == 2
        assert d["variables"] == {"reviewer": "team"}

        # Steps structure
        assert len(d["steps"]) == 2
        assert d["steps"][0]["id"] == "gather"
        assert d["steps"][0]["action"] == "read-files"

    def test_flow_to_json(self):
        """Test flow JSON serialization is valid JSON."""
        steps = [Step(id="s1", action="a1")]
        flow = Flow(name="test", description="Test", steps=steps)
        j = flow.to_json()

        # Should be valid JSON
        parsed = json.loads(j)
        assert parsed["name"] == "test"

    def test_flow_to_checklist(self):
        """Test flow markdown checklist rendering."""
        steps = [
            Step(id="s1", action="a1", description="Step 1"),
            Step(id="s2", action="a2", description="Step 2"),
        ]
        flow = Flow(name="test", description="Test flow", steps=steps)
        md = flow.to_checklist()

        assert "# Flow: test" in md
        assert "> Test flow" in md
        assert "## Steps" in md
        assert "1. [ ]" in md
        assert "2. [ ]" in md

    def test_flow_validation_empty_name(self):
        """Test validation catches empty name."""
        flow = Flow(name="", description="", steps=[Step(id="s1", action="a1")])
        errors = flow.validate()
        assert any("name" in e.lower() for e in errors)

    def test_flow_validation_no_steps(self):
        """Test validation catches empty steps."""
        flow = Flow(name="test", description="", steps=[])
        errors = flow.validate()
        assert any("step" in e.lower() for e in errors)

    def test_flow_validation_duplicate_ids(self):
        """Test validation catches duplicate step IDs."""
        steps = [
            Step(id="same", action="a1"),
            Step(id="same", action="a2"),
        ]
        flow = Flow(name="test", description="", steps=steps)
        errors = flow.validate()
        assert any("duplicate" in e.lower() for e in errors)

    def test_flow_validation_invalid_dependency(self):
        """Test validation catches invalid dependencies."""
        steps = [
            Step(id="s1", action="a1", depends_on=["nonexistent"]),
        ]
        flow = Flow(name="test", description="", steps=steps)
        errors = flow.validate()
        assert any("unknown" in e.lower() for e in errors)


# ============================================================================
# Parser Tests
# ============================================================================


class TestFlowParser:
    """Test FlowParser."""

    def test_parse_string_simple(self):
        """Test parsing simple YAML string."""
        yaml_content = """
name: simple
description: A simple flow
steps:
  - id: step1
    action: read-files
"""
        parser = FlowParser()
        flow = parser.parse_string(yaml_content)

        assert flow.name == "simple"
        assert len(flow.steps) == 1
        assert flow.steps[0].id == "step1"

    def test_parse_string_with_inputs(self):
        """Test parsing with step inputs."""
        yaml_content = """
name: with-inputs
description: Flow with inputs
steps:
  - id: gather
    action: read-files
    inputs:
      patterns:
        - "*.py"
        - "*.js"
"""
        parser = FlowParser()
        flow = parser.parse_string(yaml_content)

        assert flow.steps[0].inputs == {"patterns": ["*.py", "*.js"]}

    def test_parse_string_with_variables(self):
        """Test parsing with flow variables."""
        yaml_content = """
name: with-vars
description: Flow with variables
variables:
  reviewer: team
  threshold: 80
steps:
  - id: s1
    action: a1
"""
        parser = FlowParser()
        flow = parser.parse_string(yaml_content)

        assert flow.variables == {"reviewer": "team", "threshold": 80}

    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML raises error."""
        parser = FlowParser()
        with pytest.raises(FlowValidationError):
            parser.parse_string("invalid: yaml: content: [")

    def test_parse_missing_name(self):
        """Test parsing without name raises error."""
        parser = FlowParser()
        with pytest.raises(FlowValidationError):
            parser.parse_string("description: no name\nsteps:\n  - id: s1\n    action: a1")

    def test_parse_missing_steps(self):
        """Test parsing without steps raises error."""
        parser = FlowParser()
        with pytest.raises(FlowValidationError):
            parser.parse_string("name: no-steps\ndescription: test")

    def test_parse_null_depends_on(self):
        """Test parsing with null depends_on doesn't crash (regression test)."""
        yaml_content = """
name: null-depends
description: Flow with null depends_on
steps:
  - id: s1
    action: a1
    depends_on: null
  - id: s2
    action: a2
    depends_on:
"""
        parser = FlowParser()
        flow = parser.parse_string(yaml_content)

        assert flow.name == "null-depends"
        assert len(flow.steps) == 2
        assert flow.steps[0].depends_on == []
        assert flow.steps[1].depends_on == []

    def test_parse_string_depends_on(self):
        """Test parsing with string depends_on normalizes to list."""
        yaml_content = """
name: string-depends
description: Flow with string depends_on
steps:
  - id: s1
    action: a1
  - id: s2
    action: a2
    depends_on: s1
"""
        parser = FlowParser()
        flow = parser.parse_string(yaml_content)

        assert flow.steps[1].depends_on == ["s1"]

    def test_parse_file(self, tmp_path):
        """Test parsing from file."""
        flow_file = tmp_path / "test.yaml"
        flow_file.write_text("""
name: file-test
description: Test from file
steps:
  - id: s1
    action: a1
""")
        parser = FlowParser()
        flow = parser.parse_file(flow_file)

        assert flow.name == "file-test"
        assert flow.source_file == str(flow_file)

    def test_list_flows(self, tmp_path):
        """Test listing flows in directory."""
        flows_dir = tmp_path / "flows"
        flows_dir.mkdir()

        # Create valid flow
        (flows_dir / "valid.yaml").write_text("""
name: valid-flow
description: A valid flow
steps:
  - id: s1
    action: a1
""")

        # Create invalid flow
        (flows_dir / "invalid.yaml").write_text("invalid content")

        parser = FlowParser(flows_dir)
        flows = parser.list_flows()

        assert len(flows) == 2
        valid = next(f for f in flows if f["name"] == "valid-flow")
        assert valid["steps"] == 1
        assert not valid.get("error")

        invalid = next(f for f in flows if f["name"] == "invalid")
        assert invalid.get("error")

    def test_parse_v1_emits_deprecation_warning(self):
        """Test that parsing v1 format emits deprecation warning."""
        import warnings

        yaml_content = """
name: deprecated-flow
description: A deprecated v1 flow
steps:
  - id: s1
    action: a1
"""
        parser = FlowParser()

        # Capture deprecation warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)
            flow = parser.parse_string(yaml_content)

            # Should have emitted a deprecation warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "V1 flow format" in str(w[0].message)
            assert "deprecated" in str(w[0].message).lower()

        # Flow should still parse correctly
        assert flow.name == "deprecated-flow"
        assert len(flow.steps) == 1

    def test_parse_v1_file_emits_deprecation_warning(self, tmp_path):
        """Test that parsing v1 file emits deprecation warning with filename."""
        import warnings

        flow_file = tmp_path / "old-format.yaml"
        flow_file.write_text("""
name: old-format
description: Old format flow
steps:
  - id: s1
    action: a1
""")
        parser = FlowParser()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", DeprecationWarning)
            flow = parser.parse_file(flow_file)

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old-format.yaml" in str(w[0].message)


# ============================================================================
# JSON Structure Stability Tests (Critical for API)
# ============================================================================


class TestJSONStructureStability:
    """
    Test JSON output structure stability.

    These tests ensure the JSON API contract is maintained.
    Breaking changes here would affect downstream consumers.
    """

    def test_flow_run_json_structure(self):
        """Test flow run --json has stable structure."""
        yaml_content = """
name: test-flow
description: Test flow for JSON structure
variables:
  var1: value1
steps:
  - id: step1
    action: read-files
    description: First step
  - id: step2
    action: llm-call
    description: Second step
    model: auto
"""
        parser = FlowParser()
        flow = parser.parse_string(yaml_content)
        result = flow.to_dict()

        # Required top-level keys
        required_keys = {"name", "description", "version", "steps", "step_count", "variables"}
        assert required_keys.issubset(set(result.keys()))

        # Step structure
        for step in result["steps"]:
            step_required = {"id", "action", "status"}
            assert step_required.issubset(set(step.keys()))

    def test_checklist_json_structure(self):
        """Test checklist JSON structure matches expected format."""
        steps = [
            Step(id="s1", action="a1", description="Step 1"),
            Step(id="s2", action="a2", description="Step 2"),
        ]
        flow = Flow(name="test", description="Test", steps=steps)
        result = flow.to_dict()

        # Build checklist structure as CLI does
        checklist = [
            {
                "step": i + 1,
                "id": step.id,
                "action": step.action,
                "description": step.description or f"{step.action}: {step.id}",
                "status": step.status.value,
            }
            for i, step in enumerate(flow.steps)
        ]

        # Verify structure
        assert len(checklist) == 2
        assert checklist[0]["step"] == 1
        assert checklist[0]["id"] == "s1"
        assert checklist[0]["status"] == "pending"
        assert checklist[1]["step"] == 2

    def test_json_is_valid_json(self):
        """Test all JSON output is valid parseable JSON."""
        steps = [Step(id="s1", action="a1")]
        flow = Flow(name="test", description="Test", steps=steps, variables={"k": "v"})

        # to_json should produce valid JSON
        j = flow.to_json()
        parsed = json.loads(j)
        assert isinstance(parsed, dict)

        # to_dict should be JSON-serializable
        d = flow.to_dict()
        j2 = json.dumps(d)
        parsed2 = json.loads(j2)
        assert parsed == parsed2


# ============================================================================
# CLI Integration Tests
# ============================================================================


class TestFlowCLI:
    """Test flow CLI commands."""

    def test_flow_list_empty(self, tmp_path, monkeypatch):
        """Test flow list with no flows."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()  # Make it a git repo

        result = runner.invoke(app, ["flow", "list"])
        assert result.exit_code == 0
        assert "No flows" in result.stdout

    def test_flow_list_json(self, tmp_path, monkeypatch):
        """Test flow list --json output."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)
        (flows_dir / "test.flow.md").write_text("""---
name: test-flow
description: Test flow
triggers: [test]
---

# Test Flow
""")

        result = runner.invoke(app, ["flow", "list", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert "flows" in data
        assert "count" in data
        assert data["count"] == 1

    def test_flow_run_json(self, tmp_path, monkeypatch):
        """Test flow run --json output structure."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)
        (flows_dir / "code-review.flow.md").write_text("""---
name: code-review
description: Review code changes
triggers: [review]
---

# Code Review Flow

1. Gather files
2. Analyze code
""")

        result = runner.invoke(app, ["flow", "run", "code-review", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.stdout)

        # Verify structure
        assert data["name"] == "code-review"
        assert data["description"] == "Review code changes"

    def test_flow_run_with_vars(self, tmp_path, monkeypatch):
        """Test flow run with variables."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)
        (flows_dir / "test.flow.md").write_text("""---
name: test
description: Test flow
triggers: [test]
---

# Test Flow
""")

        result = runner.invoke(
            app, ["flow", "run", "test", "--var", "custom=value", "--json"]
        )
        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert data["variables"]["custom"] == "value"

    def test_flow_validate_valid(self, tmp_path, monkeypatch):
        """Test flow validate with valid flow."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)
        (flows_dir / "valid.flow.md").write_text("""---
name: valid
description: Valid flow
triggers: [test]
---

# Valid Flow
""")

        result = runner.invoke(app, ["flow", "validate", "valid"])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

    def test_flow_validate_json(self, tmp_path, monkeypatch):
        """Test flow validate --json output."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        flows_dir = tmp_path / ".paircoder" / "flows"
        flows_dir.mkdir(parents=True)
        (flows_dir / "test.flow.md").write_text("""---
name: test
description: Test flow
triggers: [test]
---

# Test Flow
""")

        result = runner.invoke(app, ["flow", "validate", "test", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert data["valid"] is True
        assert data["flow"] == "test"
        assert "errors" in data

    def test_flow_not_found(self, tmp_path, monkeypatch):
        """Test flow run with non-existent flow."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()

        result = runner.invoke(app, ["flow", "run", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()
