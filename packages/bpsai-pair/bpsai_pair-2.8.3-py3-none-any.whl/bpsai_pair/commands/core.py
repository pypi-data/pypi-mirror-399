"""Core commands for bpsai-pair CLI.

These are the top-level commands registered directly on the main app:
- init: Initialize repo with governance, context, prompts, scripts, and workflows
- feature: Create feature branch and scaffold context
- pack: Create agent context package
- context-sync: Update the Context Loop in state.md
- status: Show current context loop status
- validate: Validate repo structure and context consistency
- ci: Run local CI checks

Extracted from cli.py as part of EPIC-003 CLI Architecture Refactor (Sprint 22).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Try relative imports first, fall back to absolute
try:
    from ..core import ops
    from ..core.config import Config
    from ..core.presets import get_preset, get_preset_names, list_presets
except ImportError:
    from bpsai_pair.core import ops
    from bpsai_pair.core.config import Config
    from bpsai_pair.core.presets import get_preset, get_preset_names, list_presets


def print_json(data: dict) -> None:
    """Print JSON to stdout without Rich formatting."""
    sys.stdout.write(json.dumps(data, indent=2))
    sys.stdout.write("\n")
    sys.stdout.flush()


# Initialize Rich console
console = Console()

# Environment variable support
CONTEXT_DIR = os.getenv("PAIRCODER_CONTEXT_DIR", ".paircoder/context")


def repo_root() -> Path:
    """Get repo root with better error message."""
    try:
        p = ops.find_project_root()
    except ops.ProjectRootNotFoundError:
        console.print(
            "[red]x Not in a git repository.[/red]\n"
            "Please run from your project root directory (where .git exists).\n"
            "[dim]Hint: cd to your project directory first[/dim]"
        )
        raise typer.Exit(1)
    if not ops.GitOps.is_repo(p):
        console.print(
            "[red]x Not in a git repository.[/red]\n"
            "Please run from your project root directory (where .git exists).\n"
            "[dim]Hint: cd to your project directory first[/dim]"
        )
        raise typer.Exit(1)
    return p


def _select_ci_workflow(root: Path, ci_type: str) -> None:
    """Select the appropriate CI workflow based on preset ci_type.

    Renames the preset-specific workflow to ci.yml and removes the others.

    Args:
        root: Project root directory
        ci_type: "node", "python", or "fullstack"
    """
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return

    ci_yml = workflows_dir / "ci.yml"
    ci_node = workflows_dir / "ci-node.yml"
    ci_python = workflows_dir / "ci-python.yml"

    # Select the appropriate workflow based on ci_type
    if ci_type == "node" and ci_node.exists():
        # Use Node-only workflow
        if ci_yml.exists():
            ci_yml.unlink()
        ci_node.rename(ci_yml)
        if ci_python.exists():
            ci_python.unlink()
    elif ci_type == "python" and ci_python.exists():
        # Use Python-only workflow
        if ci_yml.exists():
            ci_yml.unlink()
        ci_python.rename(ci_yml)
        if ci_node.exists():
            ci_node.unlink()
    else:
        # fullstack or fallback: keep ci.yml (has both), remove variants
        if ci_node.exists():
            ci_node.unlink()
        if ci_python.exists():
            ci_python.unlink()


def ensure_v2_config(root: Path) -> Path:
    """Ensure v2 config exists at .paircoder/config.yaml.

    - If only legacy .paircoder.yml exists, it will be read and re-saved into v2 format.
    - If nothing exists, a default config will be written in v2 format.
    """
    v2_path = root / ".paircoder" / "config.yaml"
    if v2_path.exists():
        return v2_path

    # Load from legacy/env/defaults and persist in v2 location
    cfg = Config.load(root)
    cfg.save(root, use_v2=True)
    return v2_path


def init_command(
    template: Optional[str] = typer.Argument(
        None, help="Path to template (optional, uses bundled template if not provided)"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Interactive mode to gather project info"
    ),
    preset: Optional[str] = typer.Option(
        None, "--preset", "-p",
        help="Use a preset configuration (python-cli, python-api, react, fullstack, library, minimal, autonomous)"
    ),
    project_name: Optional[str] = typer.Option(
        None, "--name", "-n", help="Project name (used with --preset)"
    ),
    goal: Optional[str] = typer.Option(
        None, "--goal", "-g", help="Primary goal (used with --preset)"
    ),
):
    """Initialize repo with governance, context, prompts, scripts, and workflows.

    Use --preset for quick setup with project-type-specific defaults:

        bpsai-pair init --preset python-cli --name "My CLI" --goal "Build awesome CLI"

    Available presets: python-cli, python-api, react, fullstack, library, minimal, autonomous

    Use --interactive for guided setup, or no flags for minimal scaffolding.
    """
    import yaml

    # Import here to avoid circular imports
    try:
        from .. import init_bundled_cli
    except ImportError:
        from bpsai_pair import init_bundled_cli

    root = repo_root()

    preexisting_config = Config.find_config_file(root)

    # Handle preset-based initialization
    if preset:
        preset_obj = get_preset(preset)
        if not preset_obj:
            console.print(f"[red]x Unknown preset: {preset}[/red]")
            console.print(f"[dim]Available presets: {', '.join(get_preset_names())}[/dim]")
            raise typer.Exit(1)

        # Get project name and goal
        p_name = project_name or typer.prompt("Project name", default="My Project")
        p_goal = goal or typer.prompt("Primary goal", default="Build awesome software")

        # Generate config from preset
        config_dict = preset_obj.to_config_dict(p_name, p_goal)

        # Ensure .paircoder directory exists
        paircoder_dir = root / ".paircoder"
        paircoder_dir.mkdir(exist_ok=True)

        # Write config file
        config_file = paircoder_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        console.print(f"[green]![/green] Applied preset: {preset}")
        console.print(f"  Project: {p_name}")
        console.print(f"  Goal: {p_goal}")
        console.print(f"  Coverage target: {preset_obj.coverage_target}%")
        console.print(f"  Flows: {', '.join(preset_obj.enabled_flows)}")

    elif interactive:
        # Interactive mode to gather project information
        pname = typer.prompt("Project name", default="My Project")
        primary_goal = typer.prompt("Primary goal", default="Build awesome software")
        coverage = typer.prompt("Coverage target (%)", default="80")

        # Ask about preset selection
        console.print("\n[bold]Available presets:[/bold]")
        for p in list_presets():
            console.print(f"  {p.name}: {p.description}")

        use_preset = typer.confirm("\nWould you like to use a preset?", default=False)
        if use_preset:
            preset_choice = typer.prompt(
                "Select preset",
                default="python-cli"
            )
            preset_obj = get_preset(preset_choice)
            if preset_obj:
                config_dict = preset_obj.to_config_dict(pname, primary_goal)
                config_dict["project"]["coverage_target"] = int(coverage)

                paircoder_dir = root / ".paircoder"
                paircoder_dir.mkdir(exist_ok=True)
                config_file = paircoder_dir / "config.yaml"
                with open(config_file, 'w') as f:
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                console.print(f"[green]![/green] Applied preset: {preset_choice}")
            else:
                console.print(f"[yellow]! Unknown preset, using defaults[/yellow]")
                config = Config(
                    project_name=pname,
                    primary_goal=primary_goal,
                    coverage_target=int(coverage)
                )
                config.save(root, use_v2=True)
        else:
            # Create a config file without preset
            config = Config(
                project_name=pname,
                primary_goal=primary_goal,
                coverage_target=int(coverage)
            )
            config.save(root, use_v2=True)

    # Use bundled template if none provided
    if template is None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing scaffolding...", total=None)
            result = init_bundled_cli.main()
            progress.update(task, completed=True)

        # Select preset-specific CI workflow if a preset was used
        if preset:
            _select_ci_workflow(root, preset_obj.ci_type)

        console.print("[green]![/green] Initialized repo with pair-coding scaffolding")
        # Ensure v2 configuration exists (canonical: .paircoder/config.yaml)
        if not preset:  # Don't overwrite preset config
            ensure_v2_config(root)
        console.print("[dim]Review diffs and commit changes[/dim]")

        # Show next steps including Trello setup
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Review and commit the generated files")
        console.print("  2. Read .paircoder/context/state.md to understand the workflow")
        console.print("\n[bold]Optional - Connect to Trello:[/bold]")
        console.print("  1. Get API key from [link=https://trello.com/power-ups/admin]trello.com/power-ups/admin[/link]")
        console.print("  2. Set environment variables:")
        console.print("     [dim]export TRELLO_API_KEY=your_key[/dim]")
        console.print("     [dim]export TRELLO_TOKEN=your_token[/dim]")
        console.print("  3. Run: [bold]bpsai-pair trello connect[/bold]")
        console.print("  4. Run: [bold]bpsai-pair trello use-board <board-id>[/bold]")
        console.print("\n[dim]See .paircoder/docs/USER_GUIDE.md for full documentation[/dim]")
    else:
        # Use provided template (simplified for now)
        console.print(f"[yellow]Using template: {template}[/yellow]")
        # Ensure v2 configuration exists (canonical: .paircoder/config.yaml)
        if not preset:  # Don't overwrite preset config
            ensure_v2_config(root)
        # If this repo had no config before init ran, ensure we have a canonical v2 config file.
        # This keeps v1 repos stable (no surprise migrations) while making new scaffolds v2-native.
        if preexisting_config is None and not preset:
            v2_config = root / ".paircoder" / "config.yaml"
            v2_config_yml = root / ".paircoder" / "config.yml"
            if not v2_config.exists() and not v2_config_yml.exists():
                # Use defaults/env (or the legacy config that the template may have created)
                # and persist them to the canonical v2 location.
                Config.load(root).save(root, use_v2=True)


def feature_command(
    name: str = typer.Argument(..., help="Feature branch name (without prefix)"),
    primary: str = typer.Option("", "--primary", "-p", help="Primary goal to stamp into context"),
    phase: str = typer.Option("", "--phase", help="Phase goal for Next action"),
    force: bool = typer.Option(False, "--force", "-f", help="Bypass dirty-tree check"),
    type: str = typer.Option(
        "feature",
        "--type",
        "-t",
        help="Branch type: feature|fix|refactor",
        case_sensitive=False,
    ),
):
    """Create feature branch and scaffold context (cross-platform)."""
    root = repo_root()

    # Validate branch type
    branch_type = type.lower()
    if branch_type not in {"feature", "fix", "refactor"}:
        console.print(
            f"[red]x Invalid branch type: {type}[/red]\n"
            "Must be one of: feature, fix, refactor"
        )
        raise typer.Exit(1)

    # Use Python ops instead of shell script
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Creating {branch_type}/{name}...", total=None)

        try:
            ops.FeatureOps.create_feature(
                root=root,
                name=name,
                branch_type=branch_type,
                primary_goal=primary,
                phase=phase,
                force=force
            )
            progress.update(task, completed=True)

            console.print(f"[green]![/green] Created branch [bold]{branch_type}/{name}[/bold]")
            console.print(f"[green]![/green] Updated context with primary goal and phase")
            console.print("[dim]Next: Connect your agent and share /context files[/dim]")

        except ValueError as e:
            progress.update(task, completed=True)
            console.print(f"[red]x {e}[/red]")
            raise typer.Exit(1)


def pack_command(
    output: str = typer.Option("agent_pack.tgz", "--out", "-o", help="Output archive name"),
    extra: Optional[List[str]] = typer.Option(None, "--extra", "-e", help="Additional paths to include"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview files without creating archive"),
    list_only: bool = typer.Option(False, "--list", "-l", help="List files to be included"),
    lite: bool = typer.Option(False, "--lite", help="Minimal pack for Codex CLI (< 32KB)"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Create agent context package (cross-platform)."""
    root = repo_root()
    output_path = root / output

    # Use Python ops for packing
    files = ops.ContextPacker.pack(
        root=root,
        output=output_path,
        extra_files=extra,
        dry_run=(dry_run or list_only),
        lite=lite,
    )

    if json_out:
        result = {
            "files": [str(f.relative_to(root)) for f in files],
            "count": len(files),
            "dry_run": dry_run,
            "list_only": list_only
        }
        if not (dry_run or list_only):
            result["output"] = str(output)
            result["size"] = output_path.stat().st_size if output_path.exists() else 0
        print_json(result)
    elif list_only:
        for f in files:
            console.print(str(f.relative_to(root)))
    elif dry_run:
        console.print(f"[yellow]Would pack {len(files)} files:[/yellow]")
        for f in files[:10]:  # Show first 10
            console.print(f"  - {f.relative_to(root)}")
        if len(files) > 10:
            console.print(f"  [dim]... and {len(files) - 10} more[/dim]")
    else:
        console.print(f"[green]![/green] Created [bold]{output}[/bold]")
        size_kb = output_path.stat().st_size / 1024
        console.print(f"  Size: {size_kb:.1f} KB")
        console.print(f"  Files: {len(files)}")
        console.print("[dim]Upload this archive to your agent session[/dim]")


def context_sync_command(
    overall: Optional[str] = typer.Option(None, "--overall", help="Overall goal override"),
    last: Optional[str] = typer.Option(None, "--last", "-l", help="What changed and why"),
    next_step: Optional[str] = typer.Option(None, "--next", "--nxt", "-n", help="Next smallest valuable step"),
    blockers: str = typer.Option("", "--blockers", "-b", help="Blockers/Risks"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
    auto: bool = typer.Option(False, "--auto", help="Auto-mode: skip silently if no explicit values (for hooks)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress errors and always exit 0 (for hooks)"),
):
    """Update the Context Loop in /context/state.md (or legacy development.md).

    Use --auto for cross-platform hooks (instead of '2>/dev/null || true').
    In auto mode, the command exits silently if --last and --next are not provided.
    """
    # In auto/quiet mode with no values provided, just exit silently
    if (auto or quiet) and not last and not next_step:
        return

    # Require --last and --next in non-auto mode
    if not last or not next_step:
        if quiet:
            return
        console.print("[red]x --last and --next are required[/red]")
        console.print("[dim]Use --auto for hook mode that exits silently[/dim]")
        raise typer.Exit(1)

    try:
        root = repo_root()
    except (SystemExit, typer.Exit):
        if quiet or auto:
            return
        raise
    context_dir = root / CONTEXT_DIR

    # Check for state.md (v2) first, then fallback to development.md (legacy)
    state_file = context_dir / "state.md"
    dev_file = context_dir / "development.md"

    if state_file.exists():
        context_file = state_file
        is_v2 = True
    elif dev_file.exists():
        context_file = dev_file
        is_v2 = False
    else:
        if quiet or auto:
            return
        console.print(
            f"[red]x No context file found[/red]\n"
            "Run 'bpsai-pair init' first to set up the project structure"
        )
        raise typer.Exit(1)

    try:
        # Update context
        content = context_file.read_text()

        if is_v2:
            # v2 state.md format - update sections
            # Update "What Was Just Done" section
            content = re.sub(
                r'(## What Was Just Done\n\n).*?(?=\n## |\Z)',
                f'\\1- {last}\n\n',
                content,
                flags=re.DOTALL
            )
            # Update "What's Next" section
            content = re.sub(
                r"(## What's Next\n\n).*?(?=\n## |\Z)",
                f'\\g<1>1. {next_step}\n\n',
                content,
                flags=re.DOTALL
            )
            # Update "Blockers" section if provided
            if blockers:
                content = re.sub(
                    r'(## Blockers\n\n).*?(?=\n## |\Z)',
                    f'\\1{blockers if blockers else "None"}\n\n',
                    content,
                    flags=re.DOTALL
                )
            # Update "Active Plan" if overall provided
            if overall:
                content = re.sub(
                    r'(\*\*Plan:\*\*) .*',
                    f'\\1 {overall}',
                    content
                )
        else:
            # Legacy development.md format
            if overall:
                content = re.sub(r'Overall goal is:.*', f'Overall goal is: {overall}', content)
            content = re.sub(r'Last action was:.*', f'Last action was: {last}', content)
            content = re.sub(r'Next action will be:.*', f'Next action will be: {next_step}', content)
            if blockers:
                content = re.sub(r'Blockers(/Risks)?:.*', f'Blockers/Risks: {blockers}', content)

        context_file.write_text(content)

        if json_out:
            result = {
                "updated": True,
                "file": str(context_file.relative_to(root)),
                "format": "v2" if is_v2 else "legacy",
                "context": {
                    "overall": overall,
                    "last": last,
                    "next": next_step,
                    "blockers": blockers
                }
            }
            print_json(result)
        else:
            console.print("[green]![/green] Context Sync updated")
            console.print(f"  [dim]Last: {last}[/dim]")
            console.print(f"  [dim]Next: {next_step}[/dim]")
    except Exception as e:
        if quiet or auto:
            return
        raise


def status_command(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Show current context loop status and recent changes."""
    root = repo_root()
    context_dir = root / CONTEXT_DIR

    # Check for state.md (v2) first, then fallback to development.md (legacy)
    state_file = context_dir / "state.md"
    dev_file = context_dir / "development.md"

    # Get current branch
    current_branch = ops.GitOps.current_branch(root)
    is_clean = ops.GitOps.is_clean(root)

    # Parse context sync - check v2 format first
    context_data = {}

    if state_file.exists():
        content = state_file.read_text()

        # v2 state.md format
        plan_match = re.search(r'\*\*Plan:\*\*\s*(.*)', content)
        status_match = re.search(r'\*\*Status:\*\*\s*(.*)', content)
        # Get first bullet from "What Was Just Done"
        last_section = re.search(r'## What Was Just Done\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        # Get first item from "What's Next"
        next_section = re.search(r"## What's Next\n\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
        blockers_section = re.search(r'## Blockers\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)

        last_text = "Not set"
        if last_section:
            lines = [l.strip() for l in last_section.group(1).strip().split('\n') if l.strip()]
            if lines:
                last_text = lines[0].lstrip('- ')

        next_text = "Not set"
        if next_section:
            lines = [l.strip() for l in next_section.group(1).strip().split('\n') if l.strip()]
            if lines:
                next_text = lines[0].lstrip('0123456789. ')

        blockers_text = "None"
        if blockers_section:
            blockers_text = blockers_section.group(1).strip() or "None"

        context_data = {
            "phase": status_match.group(1) if status_match else "Not set",
            "overall": plan_match.group(1) if plan_match else "Not set",
            "last": last_text,
            "next": next_text,
            "blockers": blockers_text
        }
    elif dev_file.exists():
        content = dev_file.read_text()

        # Legacy development.md format
        overall_match = re.search(r'Overall goal is:\s*(.*)', content)
        last_match = re.search(r'Last action was:\s*(.*)', content)
        next_match = re.search(r'Next action will be:\s*(.*)', content)
        blockers_match = re.search(r'Blockers(/Risks)?:\s*(.*)', content)
        phase_match = re.search(r'\*\*Phase:\*\*\s*(.*)', content)

        context_data = {
            "phase": phase_match.group(1) if phase_match else "Not set",
            "overall": overall_match.group(1) if overall_match else "Not set",
            "last": last_match.group(1) if last_match else "Not set",
            "next": next_match.group(1) if next_match else "Not set",
            "blockers": blockers_match.group(2) if blockers_match else "None"
        }

    # Check for recent pack
    pack_files = list(root.glob("*.tgz"))
    latest_pack = None
    if pack_files:
        latest_pack = max(pack_files, key=lambda p: p.stat().st_mtime)

    age_hours = None
    if latest_pack:
        age_hours = (datetime.now() - datetime.fromtimestamp(latest_pack.stat().st_mtime)).total_seconds() / 3600

    if json_out:
        result = {
            "branch": current_branch,
            "clean": is_clean,
            "context": context_data,
            "latest_pack": str(latest_pack.name) if latest_pack else None,
            "pack_age": age_hours
        }
        print_json(result)
    else:
        # Create a nice table
        table = Table(title="PairCoder Status", show_header=False)
        table.add_column("Field", style="cyan", width=20)
        table.add_column("Value", style="white")

        # Git status
        table.add_row("Branch", f"[bold]{current_branch}[/bold]")
        table.add_row("Working Tree", "[green]Clean[/green]" if is_clean else "[yellow]Modified[/yellow]")

        # Context status
        if context_data:
            table.add_row("Phase", context_data["phase"])
            table.add_row("Overall Goal", context_data["overall"][:60] + "..." if len(context_data["overall"]) > 60 else context_data["overall"])
            table.add_row("Last Action", context_data["last"][:60] + "..." if len(context_data["last"]) > 60 else context_data["last"])
            table.add_row("Next Action", context_data["next"][:60] + "..." if len(context_data["next"]) > 60 else context_data["next"])
            if context_data["blockers"] and context_data["blockers"] != "None":
                table.add_row("Blockers", f"[red]{context_data['blockers']}[/red]")

        # Pack status
        if latest_pack:
            age_str = f"{age_hours:.1f} hours ago" if age_hours < 24 else f"{age_hours/24:.1f} days ago"
            table.add_row("Latest Pack", f"{latest_pack.name} ({age_str})")

        console.print(table)

        # Suggestions
        if not is_clean:
            console.print("\n[yellow]! Working tree has uncommitted changes[/yellow]")
            console.print("[dim]Consider committing or stashing before creating a pack[/dim]")

        if not latest_pack or (latest_pack and age_hours is not None and age_hours > 24):
            console.print("\n[dim]Tip: Run 'bpsai-pair pack' to create a fresh context pack[/dim]")


def validate_command(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix issues"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Validate repo structure and context consistency."""
    root = repo_root()
    issues = []
    fixes = []

    # Check required files (v2.1 paths with legacy fallback)
    required_files_v2 = [
        (Path(".paircoder/context/state.md"), Path("context/development.md")),
        (Path(".paircoder/config.yaml"), None),
        (Path("AGENTS.md"), Path("context/agents.md")),
        (Path("CLAUDE.md"), None),
        (Path(".agentpackignore"), None),
    ]

    for v2_path, legacy_path in required_files_v2:
        full_v2 = root / v2_path
        full_legacy = root / legacy_path if legacy_path else None

        # Check v2 path first, then legacy
        if full_v2.exists():
            continue  # v2 path exists, all good
        elif full_legacy and full_legacy.exists():
            issues.append(f"Using legacy path {legacy_path}, migrate to {v2_path}")
            continue  # Legacy exists, warn but don't block
        else:
            issues.append(f"Missing required file: {v2_path}")
            if fix:
                # Create with minimal content at v2 path
                full_v2.parent.mkdir(parents=True, exist_ok=True)
                if v2_path.name == "state.md":
                    full_v2.write_text("# Current State\n\n## Active Plan\n\nNo active plan.\n")
                elif v2_path.name == "config.yaml":
                    full_v2.write_text("version: 2.1\nproject_name: unnamed\n")
                elif v2_path.name == "AGENTS.md":
                    full_v2.write_text("# AGENTS.md\n\nSee `.paircoder/` for project context.\n")
                elif v2_path.name == "CLAUDE.md":
                    full_v2.write_text("# CLAUDE.md\n\nSee `.paircoder/context/state.md` for current state.\n")
                elif v2_path.name == ".agentpackignore":
                    full_v2.write_text(".git/\n.venv/\n__pycache__/\nnode_modules/\n")
                else:
                    full_v2.touch()
                fixes.append(f"Created {v2_path}")

    # Check context sync format (v2.1 state.md or legacy development.md)
    state_file = root / ".paircoder" / "context" / "state.md"
    dev_file = root / CONTEXT_DIR / "development.md"

    if state_file.exists():
        content = state_file.read_text()
        # v2.1 state.md uses different sections
        required_sections = ["## Active Plan", "## Current Focus"]
        for section in required_sections:
            if section not in content:
                issues.append(f"Missing state section: {section}")
    elif dev_file.exists():
        content = dev_file.read_text()
        # Legacy development.md sections
        required_sections = [
            "Overall goal is:",
            "Last action was:",
            "Next action will be:",
        ]
        for section in required_sections:
            if section not in content:
                issues.append(f"Missing context sync section: {section}")
                if fix:
                    content += f"\n{section} (to be updated)\n"
                    dev_file.write_text(content)
                    fixes.append(f"Added section: {section}")

    # Check for uncommitted context changes
    if not ops.GitOps.is_clean(root):
        context_files = [
            ".paircoder/context/state.md",
            "context/development.md",
            "AGENTS.md",
        ]
        for cf in context_files:
            if (root / cf).exists():
                result = subprocess.run(
                    ["git", "diff", "--name-only", cf],
                    cwd=root,
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    issues.append(f"Uncommitted changes in {cf}")

    if json_out:
        result = {
            "valid": len(issues) == 0,
            "issues": issues,
            "fixes_applied": fixes if fix else []
        }
        print_json(result)
    else:
        if issues:
            console.print("[red]x Validation failed[/red]")
            console.print("\nIssues found:")
            for issue in issues:
                console.print(f"  - {issue}")

            if fixes:
                console.print("\n[green]Fixed:[/green]")
                for fix_msg in fixes:
                    console.print(f"  ! {fix_msg}")
            elif not fix:
                console.print("\n[dim]Run with --fix to attempt automatic fixes[/dim]")
        else:
            console.print("[green]! All validation checks passed[/green]")


def ci_command(
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Run local CI checks (cross-platform)."""
    root = repo_root()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Running CI checks...", total=None)

        results = ops.LocalCI.run_all(root)

        progress.update(task, completed=True)

    if json_out:
        print_json(results)
    else:
        console.print("[bold]Local CI Results[/bold]\n")

        # Python results
        if results["python"]:
            console.print("[cyan]Python:[/cyan]")
            for check, status in results["python"].items():
                icon = "!" if "passed" in status else "x"
                color = "green" if "passed" in status else "yellow"
                console.print(f"  [{color}]{icon}[/{color}] {check}: {status}")

        # Node results
        if results["node"]:
            console.print("\n[cyan]Node.js:[/cyan]")
            for check, status in results["node"].items():
                icon = "!" if "passed" in status else "x"
                color = "green" if "passed" in status else "yellow"
                console.print(f"  [{color}]{icon}[/{color}] {check}: {status}")

        if not results["python"] and not results["node"]:
            console.print("[dim]No Python or Node.js project detected[/dim]")


def history_log_command(
    file_path: Optional[str] = typer.Argument(None, help="File path to log (or use CLAUDE_TOOL_INPUT_FILE_PATH env var)"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output, exit 0 on errors"),
):
    """Log a file change to the history log (cross-platform).

    This command is designed for use in Claude Code hooks as a cross-platform
    alternative to shell commands. It creates the history directory if needed
    and appends the timestamp and file path to changes.log.

    The file path can be provided as an argument or read from the
    CLAUDE_TOOL_INPUT_FILE_PATH environment variable (set by Claude Code).

    Use --quiet for hooks (suppresses errors, always exits 0).
    """
    try:
        # Get file path from argument or environment variable
        path_to_log = file_path or os.environ.get("CLAUDE_TOOL_INPUT_FILE_PATH")
        if not path_to_log:
            if quiet:
                return
            console.print("[red]No file path provided and CLAUDE_TOOL_INPUT_FILE_PATH not set[/red]")
            raise typer.Exit(1)

        root = repo_root()
        history_dir = root / ".paircoder" / "history"
        history_dir.mkdir(parents=True, exist_ok=True)

        log_file = history_dir / "changes.log"
        timestamp = datetime.now().isoformat(timespec="seconds")
        entry = f"{timestamp} {path_to_log}\n"

        with open(log_file, "a") as f:
            f.write(entry)

        if not quiet:
            console.print(f"[green]![/green] Logged: {path_to_log}")
    except Exception as e:
        if quiet:
            return  # Silent exit for hooks
        console.print(f"[red]Error logging file change: {e}[/red]")
        raise typer.Exit(1)


def register_core_commands(app: typer.Typer) -> None:
    """Register all core commands on the main app.

    Args:
        app: The main Typer application
    """
    app.command("init")(init_command)
    app.command("feature")(feature_command)
    app.command("pack")(pack_command)
    app.command("context-sync")(context_sync_command)
    # Alias for context-sync
    app.command("sync", hidden=True)(context_sync_command)
    app.command("status")(status_command)
    app.command("validate")(validate_command)
    app.command("ci")(ci_command)
    app.command("history-log", hidden=True)(history_log_command)
