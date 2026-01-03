"""
Codex CLI adapter for executing PairCoder flows.

Translates .flow.md workflows into Codex-compatible prompts
and manages execution via the Codex CLI.
"""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional

logger = logging.getLogger(__name__)


ApprovalMode = Literal["suggest", "auto-edit", "full-auto"]


@dataclass
class FlowStep:
    """A single step in a workflow."""

    name: str
    instructions: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    risk_level: Literal["low", "medium", "high"] = "medium"


@dataclass
class Flow:
    """Parsed workflow definition."""

    name: str
    description: str = ""
    triggers: list[str] = field(default_factory=list)
    steps: list[FlowStep] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> "Flow":
        """Parse a .flow.md file into a Flow object."""
        content = path.read_text()
        return parse_flow(content, path.stem)


@dataclass
class StepResult:
    """Result of executing a single step."""

    step_name: str
    success: bool
    output: str = ""
    files_modified: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    error_message: Optional[str] = None


@dataclass
class FlowResult:
    """Result of executing an entire flow."""

    flow_name: str
    success: bool
    steps: list[StepResult] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    files_modified: list[str] = field(default_factory=list)

    @property
    def completed_steps(self) -> int:
        """Number of successfully completed steps."""
        return sum(1 for s in self.steps if s.success)


def parse_flow(content: str, name: str = "") -> Flow:
    """
    Parse .flow.md content into a structured Flow object.

    Args:
        content: Markdown content of the flow file
        name: Name of the flow (defaults to extracted from content)

    Returns:
        Parsed Flow object
    """
    flow = Flow(name=name)
    current_step: Optional[FlowStep] = None
    in_step = False

    for line in content.split("\n"):
        line = line.rstrip()

        # Extract flow name from title
        if line.startswith("# "):
            flow.name = line[2:].strip().replace("Flow: ", "")
            continue

        # Extract description
        if line.startswith("## Description"):
            continue
        if not flow.description and not line.startswith("#") and line.strip():
            if not in_step:
                flow.description = line.strip()
                continue

        # Extract triggers
        if "trigger" in line.lower() and ":" in line:
            triggers_text = line.split(":", 1)[1].strip()
            flow.triggers = [t.strip() for t in triggers_text.split(",")]
            continue

        # Detect step headers (### 1. Step Name or ### Step Name)
        if line.startswith("### "):
            # Save previous step
            if current_step:
                flow.steps.append(current_step)

            step_name = line[4:].strip()
            # Remove numbering like "1. " or "Step 1: "
            if step_name[0].isdigit():
                step_name = step_name.split(".", 1)[-1].strip()
                step_name = step_name.split(":", 1)[-1].strip()

            current_step = FlowStep(name=step_name)
            in_step = True
            continue

        # Extract step content
        if current_step and line.startswith("- "):
            instruction = line[2:].strip()
            if instruction.lower().startswith("output:"):
                current_step.outputs.append(instruction.split(":", 1)[1].strip())
            else:
                current_step.instructions.append(instruction)

    # Add final step
    if current_step:
        flow.steps.append(current_step)

    return flow


class CodexAdapter:
    """
    Adapter for executing PairCoder flows via Codex CLI.

    Translates flow steps into Codex prompts and manages
    execution with appropriate approval modes.
    """

    def __init__(
        self,
        approval_mode: ApprovalMode = "suggest",
        working_dir: Optional[Path] = None,
        timeout_seconds: int = 300,
        dry_run: bool = False,
    ):
        """
        Initialize the Codex adapter.

        Args:
            approval_mode: Codex approval mode
            working_dir: Working directory for commands
            timeout_seconds: Timeout for each step
            dry_run: If True, show commands without executing
        """
        self.approval_mode = approval_mode
        self.working_dir = working_dir or Path.cwd()
        self.timeout_seconds = timeout_seconds
        self.dry_run = dry_run

    def execute_flow(
        self,
        flow: Flow,
        context: Optional[dict[str, Any]] = None,
    ) -> FlowResult:
        """
        Execute a complete flow via Codex CLI.

        Args:
            flow: The flow to execute
            context: Optional context (task ID, focus, etc.)

        Returns:
            FlowResult with execution details
        """
        start_time = time.time()
        context = context or {}

        result = FlowResult(flow_name=flow.name, success=True)

        logger.info(f"Executing flow '{flow.name}' with {len(flow.steps)} steps")

        for i, step in enumerate(flow.steps, 1):
            logger.info(f"Step {i}/{len(flow.steps)}: {step.name}")

            step_result = self.execute_step(step, context, step_number=i)
            result.steps.append(step_result)

            if not step_result.success:
                result.success = False
                logger.error(f"Step failed: {step_result.error_message}")
                break

            result.files_modified.extend(step_result.files_modified)

        result.total_duration_seconds = time.time() - start_time
        logger.info(
            f"Flow completed: {result.completed_steps}/{len(flow.steps)} steps, "
            f"{result.total_duration_seconds:.1f}s"
        )

        return result

    def execute_step(
        self,
        step: FlowStep,
        context: dict[str, Any],
        step_number: int = 1,
    ) -> StepResult:
        """
        Execute a single flow step via Codex CLI.

        Args:
            step: The step to execute
            context: Execution context
            step_number: Step number for logging

        Returns:
            StepResult with execution details
        """
        start_time = time.time()
        prompt = self.translate_step(step, context)

        if self.dry_run:
            logger.info(f"[DRY RUN] Would execute: {prompt[:100]}...")
            return StepResult(
                step_name=step.name,
                success=True,
                output="[Dry run - no execution]",
                duration_seconds=0.0,
            )

        try:
            result = self._invoke_codex(prompt)

            return StepResult(
                step_name=step.name,
                success=result.returncode == 0,
                output=result.stdout,
                files_modified=self._extract_modified_files(result.stdout),
                duration_seconds=time.time() - start_time,
                error_message=result.stderr if result.returncode != 0 else None,
            )

        except subprocess.TimeoutExpired:
            return StepResult(
                step_name=step.name,
                success=False,
                error_message=f"Step timed out after {self.timeout_seconds}s",
                duration_seconds=time.time() - start_time,
            )
        except FileNotFoundError:
            return StepResult(
                step_name=step.name,
                success=False,
                error_message="Codex CLI not found. Install with: npm install -g @openai/codex",
                duration_seconds=time.time() - start_time,
            )
        except Exception as e:
            return StepResult(
                step_name=step.name,
                success=False,
                error_message=str(e),
                duration_seconds=time.time() - start_time,
            )

    def translate_step(self, step: FlowStep, context: dict[str, Any]) -> str:
        """
        Convert a flow step to a Codex prompt.

        Args:
            step: The step to translate
            context: Execution context

        Returns:
            Codex-compatible prompt string
        """
        parts = [f"Execute step: {step.name}"]

        if context.get("task"):
            parts.append(f"Task: {context['task']}")

        if context.get("focus"):
            parts.append(f"Focus: {context['focus']}")

        if step.instructions:
            parts.append("Instructions:")
            for instruction in step.instructions:
                parts.append(f"- {instruction}")

        if step.outputs:
            parts.append("Expected outputs:")
            for output in step.outputs:
                parts.append(f"- {output}")

        return "\n".join(parts)

    def _invoke_codex(self, prompt: str) -> subprocess.CompletedProcess:
        """Invoke Codex CLI with the given prompt."""
        cmd = ["codex", f"--approval-mode={self.approval_mode}", prompt]

        return subprocess.run(
            cmd,
            cwd=self.working_dir,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )

    def _extract_modified_files(self, output: str) -> list[str]:
        """Extract list of modified files from Codex output."""
        files = []
        for line in output.split("\n"):
            # Look for common patterns indicating file modification
            if "modified:" in line.lower() or "created:" in line.lower():
                parts = line.split(":")
                if len(parts) >= 2:
                    files.append(parts[1].strip())
            elif line.strip().endswith((".py", ".js", ".ts", ".md", ".yaml", ".yml")):
                files.append(line.strip())
        return files

    def validate_flow(self, flow: Flow) -> list[str]:
        """
        Validate a flow for Codex compatibility.

        Args:
            flow: The flow to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        if not flow.name:
            issues.append("Flow has no name")

        if not flow.steps:
            issues.append("Flow has no steps")

        for i, step in enumerate(flow.steps, 1):
            if not step.name:
                issues.append(f"Step {i} has no name")
            if not step.instructions:
                issues.append(f"Step '{step.name}' has no instructions")

        # Check total content size (Codex has 32KB context limit)
        total_content = flow.description + "".join(
            " ".join(s.instructions) for s in flow.steps
        )
        if len(total_content) > 30000:  # ~7500 tokens
            issues.append("Flow content may exceed Codex context limit")

        return issues


def load_flow(path: Path) -> Flow:
    """
    Load and parse a flow file.

    Args:
        path: Path to the .flow.md file

    Returns:
        Parsed Flow object
    """
    if not path.exists():
        raise FileNotFoundError(f"Flow file not found: {path}")

    return Flow.from_file(path)
