"""Tests for plan token estimation command."""

import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def paircoder_project(tmp_path):
    """Create a minimal .paircoder project structure."""
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

    # Create .paircoder directory structure
    paircoder_dir = tmp_path / ".paircoder"
    paircoder_dir.mkdir()
    (paircoder_dir / "plans").mkdir()
    (paircoder_dir / "tasks").mkdir()
    (paircoder_dir / "context").mkdir()

    # Create config with token_estimates
    config = {
        "version": "2.6.1",
        "token_estimates": {
            "base_context": 15000,
            "per_complexity_point": 500,
            "by_task_type": {
                "feature": 1.2,
                "bugfix": 0.8,
                "docs": 0.6,
                "refactor": 1.5,
                "chore": 0.9,
            },
            "per_file_touched": 2000,
        },
    }
    with open(paircoder_dir / "config.yaml", "w") as f:
        yaml.dump(config, f)

    # Create state.md
    (paircoder_dir / "context" / "state.md").write_text("# Current State\n")

    return tmp_path


@pytest.fixture
def project_with_plan(paircoder_project):
    """Create a project with a sample plan and tasks."""
    paircoder_dir = paircoder_project / ".paircoder"

    # Create a plan file (must be .plan.yaml)
    plan_content = {
        "id": "plan-2025-12-test-plan",
        "title": "Test Plan",
        "type": "feature",
        "status": "in_progress",
    }
    with open(paircoder_dir / "plans" / "plan-2025-12-test-plan.plan.yaml", "w") as f:
        yaml.dump(plan_content, f)

    # Create task files
    task1 = """---
id: T1.1
title: First Task
plan: plan-2025-12-test-plan
type: feature
priority: P1
complexity: 40
status: pending
depends_on: []
tags:
- testing
---

# Objective

First task objective.

# Files to Modify

- src/module1.py
- src/module2.py
"""
    (paircoder_dir / "tasks" / "T1.1.task.md").write_text(task1)

    task2 = """---
id: T1.2
title: Second Task
plan: plan-2025-12-test-plan
type: bugfix
priority: P0
complexity: 25
status: pending
depends_on: []
tags:
- testing
---

# Objective

Second task objective.

# Files to Modify

- src/buggy_file.py
"""
    (paircoder_dir / "tasks" / "T1.2.task.md").write_text(task2)

    task3 = """---
id: T1.3
title: Third Task
plan: plan-2025-12-test-plan
type: docs
priority: P2
complexity: 15
status: pending
depends_on: []
tags:
- testing
---

# Objective

Third task objective.
"""
    (paircoder_dir / "tasks" / "T1.3.task.md").write_text(task3)

    return paircoder_project


class TestPlanEstimateCommand:
    """Tests for the plan estimate CLI command."""

    def test_plan_estimate_command_exists(self, project_with_plan):
        """Verify the plan estimate command exists."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "--help"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "estimate" in result.stdout.lower() or "token" in result.stdout.lower()

    def test_plan_estimate_shows_breakdown(self, project_with_plan):
        """Verify estimate shows breakdown by component."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-test-plan"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = result.stdout

        # Should show base context
        assert "base" in output.lower() or "context" in output.lower()
        # Should show tasks breakdown
        assert "task" in output.lower()
        # Should show total
        assert "total" in output.lower()

    def test_plan_estimate_uses_config_values(self, project_with_plan):
        """Verify estimate uses token_estimates from config.yaml."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-test-plan"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Base context of 15000 should appear
        assert "15,000" in result.stdout or "15000" in result.stdout

    def test_plan_estimate_factors_task_types(self, project_with_plan):
        """Verify task types affect the estimate."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-test-plan", "--json"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        import json
        data = json.loads(result.stdout)

        # Check that task types are accounted for
        assert "tasks" in data
        tasks = data["tasks"]

        # Feature task with 1.2x multiplier
        feature_task = next((t for t in tasks if t["type"] == "feature"), None)
        assert feature_task is not None

        # Bugfix task with 0.8x multiplier
        bugfix_task = next((t for t in tasks if t["type"] == "bugfix"), None)
        assert bugfix_task is not None

        # Docs task with 0.6x multiplier (should be lowest)
        docs_task = next((t for t in tasks if t["type"] == "docs"), None)
        assert docs_task is not None

    def test_plan_estimate_includes_file_tokens(self, project_with_plan):
        """Verify files touched contributes to estimate."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-test-plan", "--json"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        import json
        data = json.loads(result.stdout)

        # Task T1.1 has 2 files (4000 tokens at 2000 per file)
        # Task T1.2 has 1 file (2000 tokens)
        # Task T1.3 has 0 files (0 tokens)
        assert data["total_file_tokens"] == 6000

    def test_plan_estimate_warns_above_threshold(self, project_with_plan):
        """Verify warning when plan exceeds threshold."""
        # Create a plan with high-complexity tasks
        paircoder_dir = project_with_plan / ".paircoder"

        # Create a big plan
        big_plan = {
            "id": "plan-2025-12-big-plan",
            "title": "Big Plan",
            "type": "feature",
            "status": "in_progress",
        }
        with open(paircoder_dir / "plans" / "plan-2025-12-big-plan.plan.yaml", "w") as f:
            yaml.dump(big_plan, f)

        # Create 5 high-complexity tasks
        for i in range(1, 6):
            task = f"""---
id: BIG.{i}
title: Big Task {i}
plan: plan-2025-12-big-plan
type: feature
priority: P1
complexity: 80
status: pending
---

# Objective

Big task {i}.

# Files to Modify

- src/file{i}_a.py
- src/file{i}_b.py
- src/file{i}_c.py
"""
            (paircoder_dir / "tasks" / f"BIG.{i}.task.md").write_text(task)

        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-big-plan"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should warn about exceeding threshold
        assert "exceed" in result.stdout.lower() or "warning" in result.stdout.lower() or "⚠" in result.stdout

    def test_plan_estimate_suggests_batching(self, project_with_plan):
        """Verify batching suggestion when threshold exceeded."""
        paircoder_dir = project_with_plan / ".paircoder"

        # Create a very big plan
        very_big_plan = {
            "id": "plan-2025-12-very-big-plan",
            "title": "Very Big Plan",
            "type": "feature",
            "status": "in_progress",
        }
        with open(paircoder_dir / "plans" / "plan-2025-12-very-big-plan.plan.yaml", "w") as f:
            yaml.dump(very_big_plan, f)

        # Create 10 high-complexity tasks
        for i in range(1, 11):
            task = f"""---
id: VBIG.{i}
title: Very Big Task {i}
plan: plan-2025-12-very-big-plan
type: feature
priority: P1
complexity: 80
status: pending
---

# Objective

Very big task {i}.

# Files to Modify

- src/file{i}_a.py
- src/file{i}_b.py
- src/file{i}_c.py
- src/file{i}_d.py
"""
            (paircoder_dir / "tasks" / f"VBIG.{i}.task.md").write_text(task)

        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-very-big-plan"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should suggest batching
        assert "batch" in result.stdout.lower() or "split" in result.stdout.lower()

    def test_plan_estimate_custom_threshold(self, project_with_plan):
        """Verify custom threshold can be specified."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-test-plan", "--threshold", "20000"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        # With low threshold, even small plan should warn
        assert result.returncode == 0
        assert "exceed" in result.stdout.lower() or "warning" in result.stdout.lower() or "⚠" in result.stdout

    def test_plan_estimate_json_output(self, project_with_plan):
        """Verify JSON output format."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "plan-2025-12-test-plan", "--json"],
            cwd=project_with_plan,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        import json
        data = json.loads(result.stdout)

        # Required fields
        assert "plan_id" in data
        assert "base_context" in data
        assert "total_tokens" in data
        assert "tasks" in data
        assert "threshold" in data
        assert "exceeds_threshold" in data

    def test_plan_estimate_plan_not_found(self, paircoder_project):
        """Verify error when plan doesn't exist."""
        result = subprocess.run(
            ["bpsai-pair", "plan", "estimate", "nonexistent-plan"],
            cwd=paircoder_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stdout.lower() or "not found" in result.stderr.lower()


class TestPlanTokenEstimator:
    """Tests for the PlanTokenEstimator class."""

    def test_estimate_single_task(self):
        """Test token estimation for a single task."""
        from bpsai_pair.planning.token_estimator import PlanTokenEstimator, PlanTokenEstimate

        estimator = PlanTokenEstimator()

        # Mock task
        class MockTask:
            id = "T1"
            type = "feature"
            complexity = 40
            files_touched = ["file1.py", "file2.py"]

        estimate = estimator.estimate_task(MockTask())

        # Base: 15000
        # Complexity: 40 * 500 * 1.2 = 24000
        # Files: 2 * 2000 = 4000
        # Total: 43000
        assert estimate.total_tokens == 15000 + 24000 + 4000

    def test_estimate_plan(self):
        """Test token estimation for a full plan."""
        from bpsai_pair.planning.token_estimator import PlanTokenEstimator

        estimator = PlanTokenEstimator()

        class MockTask:
            def __init__(self, task_id, task_type, complexity, files):
                self.id = task_id
                self.type = task_type
                self.complexity = complexity
                self.files_touched = files

        tasks = [
            MockTask("T1", "feature", 40, ["f1.py", "f2.py"]),
            MockTask("T2", "bugfix", 25, ["f3.py"]),
            MockTask("T3", "docs", 15, []),
        ]

        result = estimator.estimate_plan("test-plan", tasks)

        assert result.plan_id == "test-plan"
        assert result.task_count == 3
        assert result.total_tokens > 0

    def test_batching_suggestion(self):
        """Test that batching is suggested correctly."""
        from bpsai_pair.planning.token_estimator import PlanTokenEstimator

        estimator = PlanTokenEstimator()

        class MockTask:
            def __init__(self, task_id, task_type, complexity, files):
                self.id = task_id
                self.type = task_type
                self.complexity = complexity
                self.files_touched = files

        # Create 10 high-complexity tasks
        tasks = [
            MockTask(f"T{i}", "feature", 80, [f"f{j}.py" for j in range(4)])
            for i in range(10)
        ]

        result = estimator.estimate_plan("big-plan", tasks, threshold=50000)

        assert result.exceeds_threshold
        assert result.suggested_batches is not None
        assert len(result.suggested_batches) > 1

    def test_format_estimate_output(self):
        """Test formatted output for estimates."""
        from bpsai_pair.planning.token_estimator import PlanTokenEstimator

        estimator = PlanTokenEstimator()

        class MockTask:
            def __init__(self, task_id, task_type, complexity, files):
                self.id = task_id
                self.type = task_type
                self.complexity = complexity
                self.files_touched = files

        tasks = [MockTask("T1", "feature", 40, ["f1.py"])]

        result = estimator.estimate_plan("test-plan", tasks)
        output = estimator.format_estimate(result)

        assert "test-plan" in output.lower() or "Plan" in output
        assert "token" in output.lower()
