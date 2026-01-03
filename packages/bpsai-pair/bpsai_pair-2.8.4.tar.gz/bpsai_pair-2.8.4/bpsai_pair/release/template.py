"""Template CLI commands for PairCoder.

Provides commands for cookiecutter template management including
drift detection, listing, and auto-sync.

Extracted from planning/cli_commands.py as part of EPIC-003 Phase 2.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

# Import shared helper from release commands
from .commands import get_template_path, find_paircoder_dir
from ..core.ops import ProjectRootNotFoundError

console = Console()

app = typer.Typer(
    help="Cookiecutter template management commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)


def compute_line_diff(source_content: str, template_content: str) -> int:
    """Compute the number of different lines between source and template."""
    import difflib

    source_lines = source_content.splitlines()
    template_lines = template_content.splitlines()

    diff = list(difflib.unified_diff(template_lines, source_lines, lineterm=""))
    # Count lines that are actually different (starting with + or -)
    # but not the header lines
    changed_lines = 0
    for line in diff:
        if line.startswith("+") or line.startswith("-"):
            if not line.startswith("+++") and not line.startswith("---"):
                changed_lines += 1

    return changed_lines


@app.command("check")
def template_check(
    fail_on_drift: bool = typer.Option(False, "--fail-on-drift", help="Exit with code 1 if drift detected"),
    fix: bool = typer.Option(False, "--fix", help="Auto-sync template from source files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed diff information"),
):
    """Check for drift between source files and cookie cutter template.

    Compares key project files with their equivalents in the cookie cutter
    template to detect when the template needs updating.

    Examples:
        # Check for drift
        bpsai-pair template check

        # Fail in CI if drift detected
        bpsai-pair template check --fail-on-drift

        # Auto-fix by syncing template from source
        bpsai-pair template check --fix
    """
    try:
        paircoder_dir = find_paircoder_dir()
    except ProjectRootNotFoundError:
        console.print("[red]❌ Not in a PairCoder project[/red]")
        console.print("   Run 'bpsai-pair init' to initialize a project, or run from a git repository.")
        raise typer.Exit(1)

    project_root = paircoder_dir.parent

    template_path = get_template_path(paircoder_dir)

    console.print(f"\n[bold]Cookie Cutter Template Status[/bold]\n")

    if not template_path:
        console.print("[yellow]⚠️  Template not found[/yellow]")
        console.print("Expected at: tools/cli/bpsai_pair/data/cookiecutter-paircoder")
        if fail_on_drift:
            raise typer.Exit(1)
        return

    # Template files are under {{cookiecutter.project_slug}}
    template_project_dir = template_path / "{{cookiecutter.project_slug}}"
    if not template_project_dir.exists():
        console.print(f"[yellow]⚠️  Template project directory not found[/yellow]")
        if fail_on_drift:
            raise typer.Exit(1)
        return

    # Files to compare (source path -> template path relative to project)
    files_to_check = [
        (".paircoder/config.yaml", ".paircoder/config.yaml"),
        (".paircoder/context/state.md", ".paircoder/context/state.md"),
        (".paircoder/context/project.md", ".paircoder/context/project.md"),
        (".paircoder/context/workflow.md", ".paircoder/context/workflow.md"),
        ("CLAUDE.md", "CLAUDE.md"),
        (".paircoder/capabilities.yaml", ".paircoder/capabilities.yaml"),
    ]

    results = []
    has_drift = False
    files_to_sync = []

    for source_rel, template_rel in files_to_check:
        source_path = project_root / source_rel
        template_file = template_project_dir / template_rel

        if not source_path.exists():
            results.append((source_rel, "⚠️", "Source file not found"))
            continue

        if not template_file.exists():
            results.append((source_rel, "⚠️", "Not in template"))
            continue

        # Compare files
        source_content = source_path.read_text()
        template_content = template_file.read_text()

        # Skip cookiecutter variable substitution lines for comparison
        # Template might have {{ cookiecutter.xxx }} which won't match
        def normalize_for_compare(content: str) -> str:
            """Normalize content for comparison, ignoring cookiecutter variables."""
            import re
            # Replace cookiecutter variables with placeholder
            return re.sub(r'\{\{[\s]*cookiecutter\.[^}]+\}\}', '{{COOKIECUTTER_VAR}}', content)

        source_normalized = normalize_for_compare(source_content)
        template_normalized = normalize_for_compare(template_content)

        if source_normalized == template_normalized:
            results.append((source_rel, "✅", "In sync"))
        else:
            line_diff = compute_line_diff(source_normalized, template_normalized)
            has_drift = True
            results.append((source_rel, "⚠️", f"Drift detected ({line_diff} lines changed)"))
            files_to_sync.append((source_path, template_file, source_rel))

    # Display results
    from rich.table import Table as RichTable
    table = RichTable(title=None, show_header=True, header_style="bold")
    table.add_column("File", style="cyan")
    table.add_column("Status")
    table.add_column("Details")

    for file_path, status, details in results:
        table.add_row(file_path, status, details)

    console.print(table)

    # Summary
    in_sync = sum(1 for _, s, _ in results if s == "✅")
    drifted = sum(1 for f, s, d in results if s == "⚠️" and "Drift" in d)
    warnings = sum(1 for _, s, _ in results if s == "⚠️")

    console.print()
    if has_drift:
        console.print(f"[yellow]⚠️  {len(files_to_sync)} file(s) have drifted from template[/yellow]")

        if fix:
            console.print("\n[bold]Syncing template from source...[/bold]")
            for source_path, template_file, rel_path in files_to_sync:
                # Read source and write to template
                content = source_path.read_text()
                template_file.write_text(content)
                console.print(f"  [green]✓[/green] Updated {rel_path}")
            console.print(f"\n[green]Synced {len(files_to_sync)} file(s) to template[/green]")
        else:
            console.print("\n[dim]Run with --fix to sync template from source files[/dim]")

        if fail_on_drift and not fix:
            raise typer.Exit(1)
    else:
        console.print(f"[green]✓ All {in_sync} checked files are in sync[/green]")


@app.command("list")
def template_list():
    """List files tracked for template sync."""
    try:
        paircoder_dir = find_paircoder_dir()
    except ProjectRootNotFoundError:
        console.print("[red]❌ Not in a PairCoder project[/red]")
        console.print("   Run 'bpsai-pair init' to initialize a project, or run from a git repository.")
        raise typer.Exit(1)

    template_path = get_template_path(paircoder_dir)

    console.print(f"\n[bold]Template Files[/bold]\n")

    if not template_path:
        console.print("[yellow]⚠️  Template not found[/yellow]")
        return

    template_project_dir = template_path / "{{cookiecutter.project_slug}}"
    if not template_project_dir.exists():
        console.print("[yellow]⚠️  Template project directory not found[/yellow]")
        return

    # List all files in template
    console.print(f"Template: {template_path.name}")
    console.print()

    for item in sorted(template_project_dir.rglob("*")):
        if item.is_file():
            rel_path = item.relative_to(template_project_dir)
            console.print(f"  {rel_path}")
