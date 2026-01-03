"""
Flows module for Paircoder v2.

Declarative workflow engine for multi-step agent tasks.

Supports two flow formats:
- V1 (Legacy): YAML with steps array (.yaml, .yml)
- V2 (Current): YAML frontmatter + Markdown (.flow.md)

The v1 models (Flow, Step from models.py) are kept for backward compatibility.
The v2 models (Flow, FlowRole, FlowStep from parser.py) are used by the CLI.
"""
# V1 models (backward compatibility)
from .models import Flow as FlowV1, Step, FlowValidationError, StepStatus

# V2 models and unified parser
from .parser import Flow, FlowRole, FlowStep, FlowParser, parse_frontmatter

# CLI helpers
from .parser import flow_list_command, flow_show_command

__all__ = [
    # V1 models (backward compat)
    "FlowV1",
    "Step",
    "StepStatus",
    "FlowValidationError",
    # V2 models (current)
    "Flow",
    "FlowRole",
    "FlowStep",
    # Parser
    "FlowParser",
    "parse_frontmatter",
    # CLI helpers
    "flow_list_command",
    "flow_show_command",
]
