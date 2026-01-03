"""
Data models for Paircoder flows.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class StepStatus(str, Enum):
    """Status of a flow step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class FlowValidationError(Exception):
    """Raised when a flow definition is invalid."""
    pass


@dataclass
class Step:
    """A single step in a flow."""
    id: str
    action: str
    description: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    model: Optional[str] = None  # "auto" or specific model
    prompt: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    path: Optional[str] = None  # For write-file action
    depends_on: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d["status"] = self.status.value
        return d

    def to_checklist_item(self, index: int) -> str:
        """Render as markdown checklist item."""
        checkbox = "[ ]" if self.status == StepStatus.PENDING else "[x]"
        desc = self.description or f"{self.action}: {self.id}"
        return f"{index}. {checkbox} **{self.id}**: {desc}"


@dataclass
class Flow:
    """A complete flow definition."""
    name: str
    description: str
    steps: List[Step]
    variables: Dict[str, Any] = field(default_factory=dict)
    version: str = "1"
    source_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "source_file": self.source_file,
            "variables": self.variables,
            "steps": [step.to_dict() for step in self.steps],
            "step_count": len(self.steps),
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_checklist(self) -> str:
        """Render as markdown checklist."""
        lines = [
            f"# Flow: {self.name}",
            "",
            f"> {self.description}",
            "",
            "## Steps",
            "",
        ]
        for i, step in enumerate(self.steps, 1):
            lines.append(step.to_checklist_item(i))
        return "\n".join(lines)

    def validate(self) -> List[str]:
        """Validate flow definition. Returns list of errors."""
        errors = []

        if not self.name:
            errors.append("Flow must have a name")

        if not self.steps:
            errors.append("Flow must have at least one step")

        # Check for duplicate step IDs
        step_ids = [s.id for s in self.steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Duplicate step IDs found")

        # Check dependencies reference valid steps
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.id}' depends on unknown step '{dep}'")

        # Check for circular dependencies (simple check)
        step_index = {s.id: i for i, s in enumerate(self.steps)}
        for step in self.steps:
            for dep in step.depends_on:
                if dep in step_index and step_index[dep] >= step_index[step.id]:
                    errors.append(
                        f"Step '{step.id}' depends on '{dep}' which comes later"
                    )

        return errors
