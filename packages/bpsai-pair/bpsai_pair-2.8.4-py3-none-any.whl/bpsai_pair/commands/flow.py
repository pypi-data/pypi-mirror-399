"""Flow commands for managing flows (Paircoder-native skills).

Extracted from cli.py as part of EPIC-003 CLI Architecture Refactor.

NOTE: Flows are DEPRECATED in favor of cross-platform Agent Skills.
See docs/MIGRATION.md for migration guidance.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from ..core.deprecation import (
    deprecated_command,
    show_migration_hint_once,
    suppress_deprecation_warnings,
)

# Initialize Rich console
console = Console()

# Environment variable support
FLOWS_DIR = os.getenv("PAIRCODER_FLOWS_DIR", ".paircoder/flows")

# Track if we've shown the migration hint this session
_migration_hint_shown = False


def print_json(data: dict) -> None:
    """Print JSON to stdout without Rich formatting."""
    sys.stdout.write(json.dumps(data, indent=2))
    sys.stdout.write("\n")
    sys.stdout.flush()


# Try relative imports first, fall back to absolute
try:
    from ..core import ops
    from ..flows.parser import FlowParser
except ImportError:
    from bpsai_pair.core import ops
    from bpsai_pair.flows.parser import FlowParser


def repo_root() -> Path:
    """Get repo root with better error message."""
    p = ops.find_project_root()
    if not ops.GitOps.is_repo(p):
        console.print(
            "[red]✗ Not in a git repository.[/red]\n"
            "Please run from your project root directory (where .git exists).\n"
            "[dim]Hint: cd to your project directory first[/dim]"
        )
        raise typer.Exit(1)
    return p


def _flows_root(root: Path) -> Path:
    return root / ".paircoder" / "flows"


def _find_flow_v2(root: Path, name: str):
    """Find a flow by name using the v2 parser."""
    # Search paths in order of priority
    search_paths = [
        root / FLOWS_DIR,  # Primary location (.paircoder/flows)
        root / "flows",     # Fallback location
    ]

    for flows_dir in search_paths:
        if not flows_dir.exists():
            continue
        parser = FlowParser(flows_dir)
        flow = parser.get_flow_by_name(name)
        if flow:
            return flow

    return None


# Flow sub-app
app = typer.Typer(
    help="Manage flows (Paircoder-native skills) [DEPRECATED - use skills instead]",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@app.callback()
def flow_callback(
    no_deprecation_warnings: bool = typer.Option(
        False,
        "--no-deprecation-warnings",
        help="Suppress deprecation warnings (for CI/CD pipelines)",
        is_eager=True,
    ),
) -> None:
    """Manage flows (Paircoder-native skills). [DEPRECATED]

    Flows are deprecated in favor of cross-platform Agent Skills.
    Use 'bpsai-pair skill' commands instead.

    To suppress deprecation warnings in CI/CD, use --no-deprecation-warnings.
    """
    if no_deprecation_warnings:
        suppress_deprecation_warnings(True)
    else:
        # Show migration hint once per day
        global _migration_hint_shown
        if not _migration_hint_shown:
            show_migration_hint_once("flows_to_skills")
            _migration_hint_shown = True


@app.command("list")
@deprecated_command(
    message="Flows are deprecated in favor of cross-platform Agent Skills.",
    alternative="bpsai-pair skill list",
    removal_version="2.11.0",
)
def flow_list(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """List available flows. [DEPRECATED - use 'skill list' instead]"""
    root = repo_root()
    flows_dir = _flows_root(root)

    if not flows_dir.exists():
        if json_out:
            print_json({
                "flows": [],
                "count": 0,
                "path": str(flows_dir),
            })
        else:
            console.print("[dim]No flows directory found at .paircoder/flows[/dim]")
        raise typer.Exit(0)

    # Use v2 parser which supports both .flow.yml and .flow.md
    parser = FlowParser(flows_dir)
    flows = parser.parse_all()

    if json_out:
        print_json({
            "flows": [f.to_dict() for f in flows],
            "count": len(flows),
            "path": str(flows_dir),
        })
    else:
        table = Table(title="Available Flows")
        table.add_column("Name", style="cyan")
        table.add_column("Description")
        table.add_column("Format")
        table.add_column("Triggers")

        for f in flows:
            # Truncate description to fit table
            desc = f.description[:50] + "..." if len(f.description) > 50 else f.description
            desc = desc.replace("\n", " ").strip()
            triggers = ", ".join(f.triggers[:3]) if f.triggers else "-"
            table.add_row(
                f.name,
                desc,
                f.format.upper(),
                triggers,
            )

        console.print(table)


@app.command("show")
@deprecated_command(
    message="Flows are deprecated. Consider migrating to skills.",
    alternative="bpsai-pair skill show <name>",
    removal_version="2.11.0",
)
def flow_show(
    name: str = typer.Argument(..., help="Flow name"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Show details of a flow. [DEPRECATED - use 'skill show' instead]"""
    root = repo_root()
    flows_dir = _flows_root(root)

    # Use v2 parser which supports both .flow.yml and .flow.md
    parser = FlowParser(flows_dir)
    flow = parser.get_flow_by_name(name)

    if not flow:
        console.print(f"[red]Flow not found: {name}[/red]")
        raise typer.Exit(1)

    if json_out:
        print_json(flow.to_dict())
    else:
        # Display flow details
        console.print(f"[bold cyan]{flow.name}[/bold cyan]")
        console.print(f"[dim]Format: {flow.format.upper()} | Version: {flow.version}[/dim]")
        console.print()

        if flow.description:
            console.print(f"[bold]Description:[/bold]")
            console.print(f"  {flow.description.strip()}")
            console.print()

        if flow.when_to_use:
            console.print(f"[bold]When to use:[/bold]")
            for item in flow.when_to_use:
                console.print(f"  - {item}")
            console.print()

        if flow.roles:
            console.print(f"[bold]Roles:[/bold]")
            for role in flow.roles:
                primary = " (primary)" if role.primary else ""
                console.print(f"  - {role.name}{primary}")
            console.print()

        if flow.triggers:
            console.print(f"[bold]Triggers:[/bold] {', '.join(flow.triggers)}")
            console.print()

        if flow.body:
            console.print(f"[bold]Flow Body:[/bold]")
            console.print("-" * 60)
            console.print(flow.body)


@app.command("run")
@deprecated_command(
    message="Flows are deprecated. Skills are automatically invoked by Claude.",
    alternative="Skills don't need explicit 'run' - Claude uses them automatically",
    removal_version="2.11.0",
)
def flow_run(
    name: str = typer.Argument(..., help="Flow name or filename"),
    var: Optional[List[str]] = typer.Option(
        None, "--var", "-v", help="Variable assignment (key=value)"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run a flow and output as checklist. [DEPRECATED - skills auto-invoke]"""
    root = repo_root()

    # Find the flow using v2 parser
    flow = _find_flow_v2(root, name)
    if not flow:
        console.print(f"[red]Flow not found: {name}[/red]")
        console.print(f"[dim]Available flows: bpsai-pair flow list[/dim]")
        raise typer.Exit(1)

    # Parse variables (v2 flows may not have variables, use empty dict as default)
    variables = {}
    if var:
        for v in var:
            if "=" not in v:
                console.print(f"[red]Invalid variable format: {v}[/red]")
                console.print("[dim]Use: --var key=value[/dim]")
                raise typer.Exit(1)
            key, value = v.split("=", 1)
            variables[key] = value

    if json_out:
        result = flow.to_dict()
        result["variables"] = variables
        print_json(result)
    else:
        # Display flow with steps/body
        console.print(f"[bold cyan]{flow.name}[/bold cyan]")
        console.print(f"[dim]Format: {flow.format.upper()}[/dim]")
        console.print()

        if flow.description:
            console.print(f"{flow.description.strip()}")
            console.print()

        if flow.steps:
            console.print("[bold]Steps:[/bold]")
            for i, step in enumerate(flow.steps, 1):
                console.print(f"  {i}. [{step.role}] {step.summary}")
                if step.checklist:
                    for item in step.checklist:
                        console.print(f"       - {item}")
            console.print()

        if flow.body:
            console.print("[bold]Instructions:[/bold]")
            console.print("-" * 60)
            console.print(flow.body)

        if variables:
            console.print("\n[dim]Variables:[/dim]")
            for k, v in variables.items():
                console.print(f"  [cyan]{k}[/cyan]: {v}")


@app.command("validate")
@deprecated_command(
    message="Flows are deprecated. Use skill validation instead.",
    alternative="bpsai-pair skill validate",
    removal_version="2.11.0",
)
def flow_validate(
    name: str = typer.Argument(..., help="Flow name or filename"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Validate a flow definition. [DEPRECATED - use 'skill validate']"""
    root = repo_root()

    # Find the flow using v2 parser
    flow = _find_flow_v2(root, name)
    if not flow:
        if json_out:
            print_json({"valid": False, "error": f"Flow not found: {name}"})
        else:
            console.print(f"[red]Flow not found: {name}[/red]")
        raise typer.Exit(1)

    # Basic validation for v2 flows
    errors = []
    if not flow.name:
        errors.append("Flow name is required")
    if not flow.description:
        errors.append("Flow description is recommended")

    if json_out:
        print_json({
            "valid": len(errors) == 0,
            "flow": flow.name,
            "format": flow.format,
            "file": str(flow.source_path) if flow.source_path else None,
            "errors": errors,
            "step_count": len(flow.steps),
            "has_body": bool(flow.body),
        })
    else:
        if errors:
            console.print(f"[red]Flow '{flow.name}' has validation errors:[/red]")
            for error in errors:
                console.print(f"  - {error}")
            raise typer.Exit(1)
        else:
            console.print(f"[green]Flow '{flow.name}' is valid[/green]")
            console.print(f"  Format: {flow.format.upper()}")
            console.print(f"  Steps: {len(flow.steps)}")
            if flow.source_path:
                console.print(f"  File: {flow.source_path}")
