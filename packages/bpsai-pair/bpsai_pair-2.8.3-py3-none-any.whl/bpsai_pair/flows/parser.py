"""
Flow Parser - Unified parser supporting both v1 (YAML) and v2 (Markdown) formats.

Merged from parser.py (v1) and parser_v2.py (v2) as part of T24.11.

Supports:
- .yaml/.yml - Pure YAML format (v1 legacy, step-based flows)
- .flow.yml - Pure YAML format (v1 legacy, step-based flows)
- .flow.md - YAML frontmatter + Markdown body (v2, role-based flows)

The v2 .flow.md format example:
```
---
name: design-plan-implement
version: 1
description: >
  Turn a feature request into a validated design...
when_to_use:
  - feature_request
roles:
  navigator: { primary: true }
triggers:
  - feature_request
tags:
  - design
---

# Flow Title

## Phase 1 - Design
Instructions here...
```
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .models import Flow as FlowV1, Step, FlowValidationError


# ============================================================================
# Deprecation Warning for V1 Format
# ============================================================================

V1_DEPRECATION_MESSAGE = """
The v1 YAML flow format (with 'steps' containing 'action' fields) is deprecated.

Please migrate to the v2 .flow.md format:

  1. Rename your file from *.yaml to *.flow.md
  2. Convert to YAML frontmatter format:
     ---
     name: your-flow-name
     description: Your flow description
     triggers: [your_trigger]
     roles:
       driver: { primary: true }
     ---

     # Your Flow Title

     Flow instructions in markdown...

See: https://github.com/BPSAI/paircoder/docs/flows.md for migration guide.
"""


def _emit_v1_deprecation_warning(source: str = "flow") -> None:
    """Emit deprecation warning for v1 flow format."""
    warnings.warn(
        f"V1 flow format detected in {source}. {V1_DEPRECATION_MESSAGE}",
        DeprecationWarning,
        stacklevel=4  # Point to the caller's caller
    )


# ============================================================================
# V2 Format Support (YAML Frontmatter + Markdown)
# ============================================================================

# Regex to match YAML frontmatter
FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n?(.*)$",
    re.DOTALL
)


def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """
    Parse YAML frontmatter from a document.

    Args:
        content: Full file content with optional YAML frontmatter

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    match = FRONTMATTER_PATTERN.match(content)
    if match:
        frontmatter_str = match.group(1)
        body = match.group(2).strip()
        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            frontmatter = {}
        return frontmatter, body
    return {}, content


@dataclass
class FlowRole:
    """Role definition within a flow (v2 format)."""
    name: str
    primary: bool = False
    description: str = ""

    @classmethod
    def from_dict(cls, name: str, data) -> "FlowRole":
        if isinstance(data, dict):
            return cls(
                name=name,
                primary=data.get("primary", False),
                description=data.get("description", ""),
            )
        elif isinstance(data, bool):
            return cls(name=name, primary=data)
        return cls(name=name)


@dataclass
class FlowStep:
    """A step within a flow (v2 format)."""
    id: str
    role: str
    summary: str
    checklist: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    gates: list[str] = field(default_factory=list)
    subflow: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FlowStep":
        return cls(
            id=data.get("id", ""),
            role=data.get("role", ""),
            summary=data.get("summary", ""),
            checklist=data.get("checklist", []),
            outputs=data.get("outputs", []),
            gates=data.get("gates", []),
            subflow=data.get("subflow"),
        )


@dataclass
class Flow:
    """
    Represents a workflow definition (v2 format).

    Supports both .flow.yml and .flow.md formats.
    """
    name: str
    version: int = 1
    description: str = ""
    when_to_use: list[str] = field(default_factory=list)
    roles: list[FlowRole] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    requires: dict = field(default_factory=dict)
    preconditions: list[str] = field(default_factory=list)
    do_not_proceed_if: list[str] = field(default_factory=list)
    steps: list[FlowStep] = field(default_factory=list)
    body: str = ""  # Markdown body for .flow.md files
    source_path: Optional[Path] = None
    format: str = "yaml"  # "yaml" or "md"

    # V1 compatibility fields
    variables: Dict[str, Any] = field(default_factory=dict)
    source_file: Optional[str] = None

    @property
    def primary_roles(self) -> list[FlowRole]:
        """Get roles marked as primary."""
        return [r for r in self.roles if r.primary]

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
        }

        if self.when_to_use:
            result["when_to_use"] = self.when_to_use
        if self.roles:
            result["roles"] = {
                r.name: {"primary": r.primary, "description": r.description}
                for r in self.roles
            }
        if self.triggers:
            result["triggers"] = self.triggers
        if self.tags:
            result["tags"] = self.tags
        if self.requires:
            result["requires"] = self.requires
        if self.preconditions:
            result["preconditions"] = self.preconditions
        if self.do_not_proceed_if:
            result["do_not_proceed_if"] = self.do_not_proceed_if
        if self.steps:
            result["steps"] = [
                {
                    "id": s.id,
                    "role": s.role,
                    "summary": s.summary,
                    "checklist": s.checklist,
                    "outputs": s.outputs,
                    "gates": s.gates,
                    "subflow": s.subflow,
                }
                for s in self.steps
            ]
        if self.variables:
            result["variables"] = self.variables

        return result

    @classmethod
    def from_dict(cls, data: dict, body: str = "",
                  source_path: Optional[Path] = None,
                  format: str = "yaml") -> "Flow":
        """Create Flow from dictionary."""
        # Parse roles
        roles_data = data.get("roles", {})
        roles = []
        if isinstance(roles_data, dict):
            for name, role_data in roles_data.items():
                roles.append(FlowRole.from_dict(name, role_data))

        # Parse triggers
        triggers = data.get("triggers", [])
        if isinstance(triggers, list):
            # Handle list of dicts with "on" key
            triggers = [
                t.get("on", t) if isinstance(t, dict) else t
                for t in triggers
            ]

        # Parse steps
        steps_data = data.get("steps", [])
        steps = [FlowStep.from_dict(s) for s in steps_data if isinstance(s, dict)]

        return cls(
            name=data.get("name", ""),
            version=data.get("version", 1),
            description=data.get("description", ""),
            when_to_use=data.get("when_to_use", []),
            roles=roles,
            triggers=triggers,
            tags=data.get("tags", []),
            requires=data.get("requires", {}),
            preconditions=data.get("preconditions", []),
            do_not_proceed_if=data.get("do_not_proceed_if", []),
            steps=steps,
            body=body,
            source_path=source_path,
            format=format,
            variables=data.get("variables", {}),
            source_file=str(source_path) if source_path else None,
        )


# ============================================================================
# Unified Flow Parser
# ============================================================================

class FlowParser:
    """
    Parser for flow files.

    Supports:
    - .yaml/.yml - Pure YAML format (v1 legacy)
    - .flow.yml - Pure YAML format (v1 legacy)
    - .flow.md - YAML frontmatter + Markdown body (v2)
    """

    def __init__(self, flows_dir: Optional[Path] = None):
        """
        Initialize parser with optional flows directory.

        Args:
            flows_dir: Path to flows directory (e.g., .paircoder/flows/)
        """
        self.flows_dir = Path(flows_dir) if flows_dir else None

    # =========================================================================
    # V2 API (Primary - used by CLI)
    # =========================================================================

    def list_flows(self) -> list:
        """
        List all flow files in the directory.

        Returns list of dicts with flow info (v1 compat) or list of Paths (v2).
        When flows_dir is set and contains .flow.md files, returns v2 format.
        For backward compatibility with v1 tests, returns list of dicts for .yaml files.
        """
        if not self.flows_dir or not self.flows_dir.exists():
            return []

        # Check if we have v2 format files
        md_flows = list(self.flows_dir.glob("*.flow.md"))
        yml_flows = list(self.flows_dir.glob("*.flow.yml"))

        if md_flows or yml_flows:
            # V2 format - return Paths (deduplicated, prefer .md over .yml)
            flows = []
            flows.extend(md_flows)
            flows.extend(yml_flows)

            # Deduplicate by name (prefer .flow.md over .flow.yml)
            seen_names = {}
            for flow_path in flows:
                name = flow_path.stem.replace(".flow", "")
                if name in seen_names:
                    if flow_path.suffix == ".md":
                        seen_names[name] = flow_path
                else:
                    seen_names[name] = flow_path

            return sorted(seen_names.values())

        # V1 format - return list of dicts for backward compatibility
        flows = []
        for path in sorted(self.flows_dir.glob("*.yaml")):
            try:
                flow = self.parse_file(path)
                flows.append({
                    "name": flow.name,
                    "description": flow.description,
                    "steps": len(flow.steps) if hasattr(flow, 'steps') else 0,
                    "file": path.name,
                })
            except FlowValidationError:
                flows.append({
                    "name": path.stem,
                    "description": "(invalid)",
                    "steps": 0,
                    "file": path.name,
                    "error": True,
                })

        # Also check .yml extension
        for path in sorted(self.flows_dir.glob("*.yml")):
            if path.with_suffix(".yaml").exists():
                continue
            try:
                flow = self.parse_file(path)
                flows.append({
                    "name": flow.name,
                    "description": flow.description,
                    "steps": len(flow.steps) if hasattr(flow, 'steps') else 0,
                    "file": path.name,
                })
            except FlowValidationError:
                flows.append({
                    "name": path.stem,
                    "description": "(invalid)",
                    "steps": 0,
                    "file": path.name,
                    "error": True,
                })

        return flows

    def parse(self, flow_path: Path) -> Optional[Flow]:
        """
        Parse a single flow file (v2 API).

        Handles both .flow.yml and .flow.md formats.
        Returns v2 Flow object.
        """
        try:
            content = flow_path.read_text(encoding="utf-8")

            if flow_path.suffix == ".md" or flow_path.name.endswith(".flow.md"):
                # Parse as YAML frontmatter + Markdown
                frontmatter, body = parse_frontmatter(content)
                if not frontmatter:
                    return None
                return Flow.from_dict(
                    frontmatter,
                    body=body,
                    source_path=flow_path,
                    format="md"
                )
            else:
                # Parse as pure YAML
                data = yaml.safe_load(content)
                if not data:
                    return None
                return Flow.from_dict(
                    data,
                    source_path=flow_path,
                    format="yaml"
                )
        except (yaml.YAMLError, OSError) as e:
            print(f"Error parsing flow {flow_path}: {e}")
            return None

    def parse_all(self) -> list[Flow]:
        """Parse all flows in the directory."""
        flows = []
        flow_paths = self.list_flows()
        for item in flow_paths:
            # Handle both Path objects (v2) and dicts (v1 compat)
            if isinstance(item, Path):
                flow = self.parse(item)
                if flow:
                    flows.append(flow)
            elif isinstance(item, dict) and "file" in item:
                flow_path = self.flows_dir / item["file"]
                flow = self.parse(flow_path)
                if flow:
                    flows.append(flow)
        return flows

    def get_flow_by_name(self, name: str) -> Optional[Flow]:
        """
        Find and parse a flow by name.

        Args:
            name: Flow name (e.g., "design-plan-implement")
        """
        if not self.flows_dir:
            return None

        # Try .flow.md first (preferred)
        md_path = self.flows_dir / f"{name}.flow.md"
        if md_path.exists():
            return self.parse(md_path)

        # Try .flow.yml (legacy)
        yml_path = self.flows_dir / f"{name}.flow.yml"
        if yml_path.exists():
            return self.parse(yml_path)

        # Try .yaml (v1 legacy)
        yaml_path = self.flows_dir / f"{name}.yaml"
        if yaml_path.exists():
            return self.parse(yaml_path)

        # Search all flows by name field
        for flow in self.parse_all():
            if flow.name == name:
                return flow

        return None

    def get_flows_by_trigger(self, trigger: str) -> list[Flow]:
        """
        Get all flows that match a trigger.

        Args:
            trigger: Trigger name (e.g., "feature_request")
        """
        matching = []
        for flow in self.parse_all():
            if trigger in flow.triggers:
                matching.append(flow)
        return matching

    def format_flow_list(self) -> str:
        """Format a human-readable list of flows."""
        flows = self.parse_all()

        if not flows:
            return "No flows found."

        lines = [f"Found {len(flows)} flow(s):", ""]

        for flow in flows:
            format_badge = "[MD]" if flow.format == "md" else "[YML]"
            lines.append(f"• {flow.name} {format_badge}")
            if flow.description:
                desc = flow.description[:60]
                if len(flow.description) > 60:
                    desc += "..."
                lines.append(f"  {desc}")
            if flow.tags:
                lines.append(f"  Tags: {', '.join(flow.tags)}")
            lines.append("")

        return "\n".join(lines)

    # =========================================================================
    # V1 API (Backward Compatibility)
    # =========================================================================

    def parse_file(self, path: Path) -> FlowV1:
        """
        Parse a single flow file (v1 API).

        Returns v1 Flow object from models.py for backward compatibility.
        """
        if not path.exists():
            raise FlowValidationError(f"Flow file not found: {path}")

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise FlowValidationError(f"Invalid YAML in {path}: {e}")

        if not data or not isinstance(data, dict):
            raise FlowValidationError(f"Invalid flow file (expected YAML dict): {path}")

        return self._parse_v1_flow_data(data, source_file=str(path))

    def parse_string(self, content: str, source_name: str = "<string>") -> FlowV1:
        """
        Parse flow from YAML string (v1 API).

        Returns v1 Flow object from models.py for backward compatibility.
        """
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise FlowValidationError(f"Invalid YAML: {e}")

        if not data or not isinstance(data, dict):
            raise FlowValidationError("Invalid flow definition (expected YAML dict)")

        return self._parse_v1_flow_data(data, source_file=source_name)

    def _parse_v1_flow_data(
        self, data: Dict[str, Any], source_file: Optional[str] = None
    ) -> FlowV1:
        """Parse flow data dictionary into v1 Flow object.

        DEPRECATED: V1 format is deprecated. Use v2 .flow.md format instead.
        """
        # Emit deprecation warning
        _emit_v1_deprecation_warning(source_file or "<unknown>")

        # Required fields
        name = data.get("name")
        if not name:
            raise FlowValidationError("Flow must have a 'name' field")

        description = data.get("description", "")

        # Parse steps
        steps_data = data.get("steps", [])
        if not steps_data:
            raise FlowValidationError("Flow must have at least one step")

        steps = []
        for i, step_data in enumerate(steps_data):
            step = self._parse_v1_step(step_data, index=i)
            steps.append(step)

        # Optional fields
        variables = data.get("variables", {})
        version = str(data.get("version", "1"))

        flow = FlowV1(
            name=name,
            description=description,
            steps=steps,
            variables=variables,
            version=version,
            source_file=source_file,
        )

        # Validate
        errors = flow.validate()
        if errors:
            raise FlowValidationError(
                f"Flow validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )

        return flow

    def _parse_v1_step(self, data: Dict[str, Any], index: int) -> Step:
        """Parse a single step from data dictionary (v1 format)."""
        # Required fields
        step_id = data.get("id")
        if not step_id:
            raise FlowValidationError(f"Step {index + 1} must have an 'id' field")

        action = data.get("action")
        if not action:
            raise FlowValidationError(f"Step '{step_id}' must have an 'action' field")

        # Optional fields
        description = data.get("description")
        inputs = data.get("inputs", {})
        model = data.get("model")
        prompt = data.get("prompt")
        context = data.get("context", {})
        path = data.get("path")
        depends_on = data.get("depends_on")

        # Normalize depends_on to list
        if depends_on is None:
            depends_on = []
        elif isinstance(depends_on, str):
            depends_on = [depends_on]
        elif not isinstance(depends_on, list):
            depends_on = []

        return Step(
            id=step_id,
            action=action,
            description=description,
            inputs=inputs,
            model=model,
            prompt=prompt,
            context=context,
            path=path,
            depends_on=depends_on,
        )

    def find_flow(self, name: str) -> Optional[Path]:
        """
        Find a flow file by name (v1 API).

        Returns path to flow file or None.
        """
        if not self.flows_dir or not self.flows_dir.exists():
            return None

        # Try exact name with various extensions
        for ext in [".flow.md", ".flow.yml", ".yaml", ".yml"]:
            path = self.flows_dir / f"{name}{ext}"
            if path.exists():
                return path

        # Try to find by flow name in file
        for pattern in ["*.flow.md", "*.flow.yml", "*.yaml", "*.yml"]:
            for path in self.flows_dir.glob(pattern):
                try:
                    flow = self.parse(path)
                    if flow and flow.name == name:
                        return path
                except (FlowValidationError, Exception):
                    continue

        return None


# ============================================================================
# CLI Integration
# ============================================================================

def flow_list_command(flows_dir: Path) -> str:
    """
    Implementation for `bpsai-pair flow list` command.

    Returns formatted string of all flows.
    """
    parser = FlowParser(flows_dir)
    return parser.format_flow_list()


def flow_show_command(flows_dir: Path, name: str) -> str:
    """
    Implementation for `bpsai-pair flow show <name>` command.

    Returns formatted flow details or error message.
    """
    parser = FlowParser(flows_dir)
    flow = parser.get_flow_by_name(name)

    if not flow:
        return f"Flow not found: {name}"

    lines = [
        f"# {flow.name}",
        "",
        f"**Version:** {flow.version}",
        f"**Format:** {flow.format.upper()}",
        "",
    ]

    if flow.description:
        lines.extend([flow.description, ""])

    if flow.when_to_use:
        lines.append("## When to Use")
        for item in flow.when_to_use:
            lines.append(f"- {item}")
        lines.append("")

    if flow.roles:
        lines.append("## Roles")
        for role in flow.roles:
            primary = " (primary)" if role.primary else ""
            lines.append(f"- **{role.name}**{primary}")
            if role.description:
                lines.append(f"  {role.description}")
        lines.append("")

    if flow.triggers:
        lines.append(f"**Triggers:** {', '.join(flow.triggers)}")
        lines.append("")

    if flow.tags:
        lines.append(f"**Tags:** {', '.join(flow.tags)}")
        lines.append("")

    if flow.body:
        lines.extend(["---", "", flow.body])

    return "\n".join(lines)
