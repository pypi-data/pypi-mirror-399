"""CLI commands for skill validation and installation."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .validator import SkillValidator, find_skills_dir
from .installer import (
    install_skill,
    SkillInstallerError,
    SkillSource,
    parse_source,
    get_target_dir,
    extract_skill_name,
)
from .exporter import (
    export_skill,
    export_all_skills,
    check_portability,
    ExportFormat,
    SkillExporterError,
)
from .suggestion import (
    suggest_skills,
    PatternDetector,
    SkillSuggester,
    SkillDraftCreator,
    HistoryParser,
    SkillSuggestionError,
)
from .gap_detector import (
    SkillGap,
    SkillGapDetector,
    GapPersistence,
    detect_gaps_from_history,
    format_gap_notification,
)
from .generator import (
    GeneratedSkill,
    SkillGenerator,
    SkillGeneratorError,
    save_generated_skill,
    generate_skill_from_gap_id,
)
from .subagent_detector import (
    SubagentGap,
    SubagentGapDetector,
    SubagentGapPersistence,
    detect_subagent_gaps,
)
from .classifier import (
    GapType,
    ClassifiedGap,
    GapClassifier,
    AllGaps,
    detect_and_classify_all,
    format_classification_report,
)
from .gates import (
    GateStatus,
    GapQualityGate,
    QualityGateResult,
    evaluate_gap_quality,
)
from .scorer import (
    SkillScorer,
    SkillScore,
    score_skills,
)

console = Console()

skill_app = typer.Typer(
    help="Manage and validate Claude Code skills",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@skill_app.command("validate")
def skill_validate(
    skill_name: Optional[str] = typer.Argument(None, help="Specific skill to validate"),
    fix: bool = typer.Option(False, "--fix", help="Auto-correct simple issues"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Validate skills against Anthropic specs.

    Checks:
    - Frontmatter has only 'name' and 'description' fields
    - Description under 1024 characters
    - 3rd-person voice (warns on 2nd person)
    - File under 500 lines
    - Name matches directory name

    Use --fix to auto-correct simple issues.
    """
    import json

    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        console.print("[red]Could not find .claude/skills directory[/red]")
        raise typer.Exit(1)

    validator = SkillValidator(skills_dir)

    if skill_name:
        # Validate single skill
        skill_dir = skills_dir / skill_name
        if not skill_dir.exists():
            console.print(f"[red]Skill not found: {skill_name}[/red]")
            raise typer.Exit(1)

        if fix:
            fixed = validator.fix_skill(skill_dir)
            if fixed:
                console.print(f"[green]Fixed issues in {skill_name}[/green]")

        result = validator.validate_skill(skill_dir)
        if json_out:
            console.print(json.dumps(result, indent=2))
        else:
            _display_result(skill_name, result)
        raise typer.Exit(0 if result["valid"] else 1)

    # Validate all skills
    results = validator.validate_all()

    if not results:
        console.print("[dim]No skills found in .claude/skills/[/dim]")
        return

    if fix:
        console.print("[cyan]Attempting to fix issues...[/cyan]\n")
        for skill_name_key in results:
            skill_dir = skills_dir / skill_name_key
            fixed = validator.fix_skill(skill_dir)
            if fixed:
                console.print(f"  [green]Fixed: {skill_name_key}[/green]")
        console.print()
        # Re-validate after fixes
        results = validator.validate_all()

    if json_out:
        console.print(json.dumps(results, indent=2))
        return

    console.print(f"\n[bold]Validating {len(results)} skills...[/bold]\n")

    for skill_name_key, result in sorted(results.items()):
        _display_result(skill_name_key, result)

    # Summary
    summary = validator.get_summary(results)
    console.print(f"\n[bold]Summary:[/bold] {summary['passed']} pass, {summary['with_warnings']} warnings, {summary['failed']} errors")

    if summary["failed"] > 0:
        raise typer.Exit(1)


@skill_app.command("list")
def skill_list():
    """List all skills in .claude/skills/."""
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        console.print("[red]Could not find .claude/skills directory[/red]")
        raise typer.Exit(1)

    skills = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            skills.append(skill_dir.name)

    if not skills:
        console.print("[dim]No skills found.[/dim]")
        return

    table = Table(title=f"Skills ({len(skills)})")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="dim")

    for skill_name in sorted(skills):
        table.add_row(skill_name, f".claude/skills/{skill_name}/")

    console.print(table)


def _display_result(name: str, result: dict) -> None:
    """Display validation result for a skill.

    Args:
        name: Skill name
        result: Validation result dict
    """
    if result["valid"] and not result["warnings"]:
        console.print(f"[green]\u2705 {name}[/green]")
    elif result["valid"]:
        console.print(f"[yellow]\u26a0\ufe0f  {name}[/yellow]")
        for warning in result["warnings"]:
            console.print(f"   [dim]- {warning}[/dim]")
    else:
        console.print(f"[red]\u274c {name}[/red]")
        for error in result["errors"]:
            console.print(f"   [red]- {error}[/red]")
        for warning in result["warnings"]:
            console.print(f"   [dim]- {warning}[/dim]")


def find_project_root() -> Path:
    """Find project root by looking for .paircoder directory."""
    from ..core.ops import find_project_root as _find_project_root

    return _find_project_root()


@skill_app.command("install")
def skill_install(
    source: str = typer.Argument(..., help="Source URL or local path to skill"),
    project: bool = typer.Option(False, "--project", help="Install to project .claude/skills/"),
    personal: bool = typer.Option(False, "--personal", help="Install to ~/.claude/skills/"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Install with different name"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing skill"),
):
    """Install a skill from URL or local path.

    Examples:

        # Install from local path
        bpsai-pair skill install ~/my-skills/custom-review

        # Install from GitHub
        bpsai-pair skill install https://github.com/user/repo/tree/main/.claude/skills/skill

        # Install with different name
        bpsai-pair skill install ./my-skill --name renamed-skill

        # Install to personal directory
        bpsai-pair skill install ./my-skill --personal

        # Overwrite existing skill
        bpsai-pair skill install ./my-skill --force
    """
    try:
        # Parse source to show what we're doing
        source_type, parsed = parse_source(source)
        skill_name = name or extract_skill_name(source)

        console.print(f"\n[bold]Installing skill: {skill_name}[/bold]")

        if source_type == SkillSource.PATH:
            console.print(f"  Source: [dim]{parsed}[/dim]")
        else:
            console.print(f"  Source: [dim]{source}[/dim]")

        # If neither --project nor --personal specified, prompt (non-interactive defaults to project)
        if not project and not personal:
            # Default to project installation
            project = True

        # Get target directory for display
        target_dir = get_target_dir(project=project, personal=personal)
        console.print(f"  Target: [dim]{target_dir}[/dim]\n")

        console.print("[cyan]Downloading...[/cyan]" if source_type == SkillSource.URL else "[cyan]Copying...[/cyan]")

        # Install
        result = install_skill(
            source,
            project=project,
            personal=personal,
            name=name,
            force=force,
        )

        console.print("[cyan]Validating...[/cyan]")
        console.print("  [green]\u2713[/green] Frontmatter valid")
        console.print("  [green]\u2713[/green] Description under 1024 chars")
        console.print("  [green]\u2713[/green] No conflicts with existing skills" if not force else "  [yellow]\u2713[/yellow] Overwrote existing skill")

        console.print(f"\n[green]\u2705 Installed {result['skill_name']} to {result['installed_to']}/[/green]")

    except SkillInstallerError as e:
        console.print(f"\n[red]\u274c Installation failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]\u274c Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@skill_app.command("export")
def skill_export(
    skill_name: Optional[str] = typer.Argument(None, help="Skill to export (or use --all)"),
    format: str = typer.Option("cursor", "--format", "-f", help="Export format: cursor, continue, windsurf, codex, chatgpt, all"),
    all_skills: bool = typer.Option(False, "--all", "-a", help="Export all skills"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be created without creating"),
):
    """Export skills to other AI coding tool formats.

    Supported formats:
    - cursor: Export to .cursor/rules/
    - continue: Export to .continue/context/
    - windsurf: Export to .windsurfrules
    - codex: Export to ~/.codex/skills/ (OpenAI Codex CLI)
    - chatgpt: Export to ./chatgpt-skills/ (for custom GPTs)
    - all: Export to all formats at once

    Examples:

        # Export single skill to Cursor
        bpsai-pair skill export my-skill --format cursor

        # Export to Codex CLI
        bpsai-pair skill export my-skill --format codex

        # Export to ChatGPT format
        bpsai-pair skill export my-skill --format chatgpt

        # Export to all platforms at once
        bpsai-pair skill export my-skill --format all

        # Export all skills to Continue.dev
        bpsai-pair skill export --all --format continue

        # Dry run to see what would be created
        bpsai-pair skill export my-skill --format windsurf --dry-run
    """
    if not skill_name and not all_skills:
        console.print("[red]Error: Specify a skill name or use --all[/red]")
        raise typer.Exit(1)

    # Parse format
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        console.print(f"[red]Error: Invalid format '{format}'. Use: cursor, continue, windsurf, codex, chatgpt, all[/red]")
        raise typer.Exit(1)

    # Get directories
    try:
        skills_dir = find_skills_dir()
        project_dir = find_project_root()
    except FileNotFoundError:
        console.print("[red]Could not find .claude/skills directory[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print("[yellow]Dry run mode - no files will be created[/yellow]\n")

    try:
        if all_skills:
            console.print(f"[bold]Exporting all skills to {format}...[/bold]\n")
            results = export_all_skills(
                format=export_format,
                skills_dir=skills_dir,
                project_dir=project_dir,
                dry_run=dry_run,
            )

            if not results:
                console.print("[dim]No skills found to export.[/dim]")
                return

            success_count = sum(1 for r in results if r.get("success"))
            for result in results:
                if result.get("success"):
                    path_key = "would_create" if dry_run else "path"
                    console.print(f"  [green]\u2713[/green] {result['skill_name']} → {result.get(path_key, 'N/A')}")
                    for warning in result.get("warnings", []):
                        console.print(f"    [yellow]⚠ {warning}[/yellow]")
                else:
                    console.print(f"  [red]\u274c {result['skill_name']}: {result.get('error', 'Unknown error')}[/red]")

            console.print(f"\n[bold]Exported {success_count}/{len(results)} skills[/bold]")

        else:
            console.print(f"[bold]Exporting {skill_name} to {format}...[/bold]\n")

            # Check portability first (skip for 'all' format, it's checked per-format)
            skill_dir = skills_dir / skill_name
            if skill_dir.exists() and export_format != ExportFormat.ALL:
                warnings = check_portability(skill_dir)
                for warning in warnings:
                    console.print(f"[yellow]⚠ {warning}[/yellow]")
                if warnings:
                    console.print()

            result = export_skill(
                skill_name=skill_name,
                format=export_format,
                skills_dir=skills_dir,
                project_dir=project_dir,
                dry_run=dry_run,
            )

            # Handle 'all' format special result structure
            if result.get("format") == "all":
                # Display results for each format
                exported_to = result.get("exported_to", {})
                for fmt_name, path in exported_to.items():
                    console.print(f"  [green]\u2713[/green] {fmt_name}: {path}")

                # Display warnings
                for warning in result.get("warnings", []):
                    console.print(f"\n[yellow]⚠ {warning}[/yellow]")

                # Summary
                console.print(f"\n{result.get('summary', 'Export complete')}")
            elif dry_run:
                console.print(f"[dim]Would create: {result.get('would_create')}[/dim]")
            else:
                console.print(f"[green]\u2705 Exported to {result.get('path')}[/green]")

    except SkillExporterError as e:
        console.print(f"\n[red]\u274c Export failed: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]\u274c Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@skill_app.command("suggest")
def skill_suggest(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    create: Optional[int] = typer.Option(None, "--create", "-c", help="Create draft for suggestion N"),
    min_occurrences: int = typer.Option(3, "--min", "-m", help="Minimum pattern occurrences"),
):
    """Analyze session history and suggest new skills.

    Scans recent workflow patterns and suggests skills that could automate
    frequently repeated command sequences.

    Examples:

        # Show suggestions
        bpsai-pair skill suggest

        # Output as JSON
        bpsai-pair skill suggest --json

        # Create draft for first suggestion
        bpsai-pair skill suggest --create 1

        # Require at least 5 occurrences
        bpsai-pair skill suggest --min 5
    """
    import json

    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

    console.print("[cyan]Analyzing session patterns...[/cyan]\n")

    # Get suggestions
    suggestions = suggest_skills(
        history_dir=history_dir,
        skills_dir=skills_dir,
        min_occurrences=min_occurrences,
    )

    if json_out:
        output = {
            "suggestions": suggestions,
            "total": len(suggestions),
        }
        console.print(json.dumps(output, indent=2))
        return

    if not suggestions:
        console.print("[dim]No patterns found that would benefit from a skill.[/dim]")
        console.print("\n[dim]Tips:[/dim]")
        console.print("  - Patterns need at least 3 occurrences by default")
        console.print("  - Try using --min to lower the threshold")
        console.print("  - More session history helps detect patterns")
        return

    console.print(f"[bold]Suggested Skills ({len(suggestions)}):[/bold]\n")

    for i, suggestion in enumerate(suggestions, 1):
        name = suggestion.get("name", "unknown")
        confidence = suggestion.get("confidence", 0)
        description = suggestion.get("description", "")
        occurrences = suggestion.get("occurrences", 0)
        estimated_savings = suggestion.get("estimated_savings", "")
        overlaps = suggestion.get("overlaps_with", [])

        # Confidence indicator
        if confidence >= 80:
            conf_style = "green"
        elif confidence >= 60:
            conf_style = "yellow"
        else:
            conf_style = "dim"

        console.print(f"[bold]{i}. {name}[/bold] [{conf_style}](confidence: {confidence}%)[/{conf_style}]")
        console.print(f"   [dim]{description}[/dim]")
        console.print(f"   Pattern occurrences: {occurrences}")
        if estimated_savings:
            console.print(f"   Estimated savings: {estimated_savings}")
        if overlaps:
            console.print(f"   [yellow]⚠ May overlap with: {', '.join(overlaps)}[/yellow]")
        console.print()

    # Handle --create option
    if create is not None:
        if create < 1 or create > len(suggestions):
            console.print(f"[red]Invalid suggestion number. Choose 1-{len(suggestions)}[/red]")
            raise typer.Exit(1)

        suggestion = suggestions[create - 1]
        console.print(f"[cyan]Creating draft for: {suggestion['name']}[/cyan]")

        try:
            creator = SkillDraftCreator(skills_dir=skills_dir)
            result = creator.create_draft(suggestion)

            if result["success"]:
                console.print(f"[green]\u2705 Created draft: {result['path']}[/green]")

                validation = result.get("validation", {})
                if validation.get("valid"):
                    console.print("   [green]\u2713[/green] Passes validation")
                else:
                    console.print("   [yellow]\u26a0[/yellow] Review validation warnings")
                    for error in validation.get("errors", []):
                        console.print(f"      [red]{error}[/red]")

        except SkillSuggestionError as e:
            console.print(f"[red]\u274c Failed to create draft: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[dim]Use --create N to create a draft for suggestion N[/dim]")


@skill_app.command("gaps")
def skill_gaps(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    clear: bool = typer.Option(False, "--clear", help="Clear gap history"),
    analyze: bool = typer.Option(False, "--analyze", help="Run fresh analysis"),
):
    """List detected skill gaps from session history.

    Shows patterns that were repeated frequently but don't have matching skills.
    Use this to identify opportunities for new skill creation.

    Examples:

        # List detected gaps
        bpsai-pair skill gaps

        # Output as JSON
        bpsai-pair skill gaps --json

        # Clear gap history
        bpsai-pair skill gaps --clear

        # Run fresh analysis
        bpsai-pair skill gaps --analyze
    """
    import json

    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"

    persistence = GapPersistence(history_dir=history_dir)

    # Handle --clear
    if clear:
        persistence.clear_gaps()
        console.print("[green]Gap history cleared[/green]")
        return

    # Load or detect gaps
    if analyze:
        console.print("[cyan]Analyzing session history for gaps...[/cyan]\n")
        gaps = detect_gaps_from_history(
            history_dir=history_dir,
            skills_dir=skills_dir,
        )
        # Save newly detected gaps
        for gap in gaps:
            persistence.save_gap(gap)
    else:
        gaps = persistence.load_gaps()

    # JSON output
    if json_out:
        output = {
            "gaps": [g.to_dict() for g in gaps],
            "total": len(gaps),
        }
        console.print(json.dumps(output, indent=2))
        return

    # Display gaps
    if not gaps:
        console.print("[dim]No skill gaps detected.[/dim]")
        console.print("\n[dim]Tips:[/dim]")
        console.print("  - Use --analyze to run fresh detection")
        console.print("  - Gaps are detected from repeated workflows")
        console.print("  - Use `skill suggest` for pattern-based suggestions")
        return

    console.print(f"[bold]Detected Skill Gaps ({len(gaps)}):[/bold]\n")

    for i, gap in enumerate(gaps, 1):
        # Confidence indicator
        if gap.confidence >= 0.8:
            conf_style = "green"
        elif gap.confidence >= 0.5:
            conf_style = "yellow"
        else:
            conf_style = "dim"

        console.print(f"[bold]{i}. {gap.suggested_name}[/bold] [{conf_style}](confidence: {gap.confidence:.0%})[/{conf_style}]")
        console.print(f"   Pattern: {' → '.join(gap.pattern[:4])}{'...' if len(gap.pattern) > 4 else ''}")
        console.print(f"   Frequency: {gap.frequency} occurrences")
        console.print(f"   Estimated savings: {gap.time_saved_estimate}")
        console.print(f"   [dim]Detected: {gap.detected_at[:10]}[/dim]")
        console.print()

    console.print("[dim]Use `bpsai-pair skill generate N` to create a skill from gap N[/dim]")


@skill_app.command("generate")
def skill_generate(
    gap_id: Optional[int] = typer.Argument(None, help="Gap ID to generate from (1-based)"),
    auto_approve: bool = typer.Option(False, "--auto-approve", "-y", help="Save without confirmation"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing skill"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview without saving"),
):
    """Generate a skill from a detected gap.

    Creates a skill draft from patterns detected by `skill gaps`. The generated
    skill follows Anthropic specs and includes observed commands as workflow steps.

    Examples:

        # List available gaps
        bpsai-pair skill generate

        # Preview generated skill
        bpsai-pair skill generate 1 --preview

        # Generate and save with confirmation
        bpsai-pair skill generate 1

        # Auto-approve and save
        bpsai-pair skill generate 1 --auto-approve

        # Overwrite existing skill
        bpsai-pair skill generate 1 --force --auto-approve
    """
    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

    # Load gaps
    persistence = GapPersistence(history_dir=history_dir)
    gaps = persistence.load_gaps()

    if not gaps:
        console.print("[dim]No skill gaps found.[/dim]")
        console.print("\n[dim]Run `bpsai-pair skill gaps --analyze` to detect patterns.[/dim]")
        return

    # If no gap_id provided, list available gaps
    if gap_id is None:
        console.print("[bold]Available Gaps:[/bold]\n")
        for i, gap in enumerate(gaps, 1):
            console.print(f"  {i}. [cyan]{gap.suggested_name}[/cyan] (confidence: {gap.confidence:.0%})")
            console.print(f"     Pattern: {' → '.join(gap.pattern[:3])}{'...' if len(gap.pattern) > 3 else ''}")
        console.print(f"\n[dim]Use `bpsai-pair skill generate <N>` to generate from gap N[/dim]")
        return

    # Validate gap_id
    if gap_id < 1 or gap_id > len(gaps):
        console.print(f"[red]Invalid gap ID: {gap_id}. Valid range: 1-{len(gaps)}[/red]")
        raise typer.Exit(1)

    gap = gaps[gap_id - 1]
    console.print(f"[cyan]Generating skill from gap: {gap.suggested_name}[/cyan]\n")

    # Generate skill
    generator = SkillGenerator()
    generated = generator.generate_from_gap(gap)

    # Preview mode
    if preview:
        console.print("[bold]Generated Skill Preview:[/bold]\n")
        console.print("─" * 60)
        console.print(generated.content)
        console.print("─" * 60)
        console.print(f"\n[dim]Use `--auto-approve` to save this skill[/dim]")
        return

    # Show preview before saving (unless auto_approve)
    if not auto_approve:
        console.print("[bold]Generated Skill:[/bold]\n")
        console.print("─" * 60)
        # Show truncated preview
        lines = generated.content.split("\n")
        preview_lines = lines[:30]
        console.print("\n".join(preview_lines))
        if len(lines) > 30:
            console.print(f"\n... ({len(lines) - 30} more lines)")
        console.print("─" * 60)
        console.print()

        # Ask for confirmation
        confirm = typer.confirm("Save this skill?")
        if not confirm:
            console.print("[dim]Cancelled.[/dim]")
            return

    # Save the skill
    try:
        result = save_generated_skill(
            generated,
            skills_dir,
            force=force,
            auto_approve=True,
        )

        if result["success"]:
            console.print(f"[green]✅ Created skill: {result['path']}[/green]")

            validation = result.get("validation", {})
            if validation.get("valid"):
                console.print("   [green]✓[/green] Passes validation")
            else:
                console.print("   [yellow]⚠[/yellow] Review validation warnings:")
                for error in validation.get("errors", []):
                    console.print(f"      [red]{error}[/red]")
                for warning in validation.get("warnings", []):
                    console.print(f"      [yellow]{warning}[/yellow]")

            if result.get("requires_review"):
                console.print("\n[dim]Note: Review and customize the generated skill before use.[/dim]")

    except SkillGeneratorError as e:
        console.print(f"[red]✖ Failed to save: {e}[/red]")
        raise typer.Exit(1)


# ============================================================================
# Subagent Gap Commands
# ============================================================================

subagent_app = typer.Typer(
    help="Manage Claude Code subagents",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@subagent_app.command("gaps")
def subagent_gaps(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    clear: bool = typer.Option(False, "--clear", help="Clear gap history"),
    analyze: bool = typer.Option(False, "--analyze", help="Run fresh analysis"),
):
    """List detected subagent gaps from session history.

    Shows patterns that suggest subagents would be beneficial, such as
    context isolation needs, specialized personas, or resumable workflows.

    Examples:

        # List detected gaps
        bpsai-pair subagent gaps

        # Output as JSON
        bpsai-pair subagent gaps --json

        # Clear gap history
        bpsai-pair subagent gaps --clear

        # Run fresh analysis
        bpsai-pair subagent gaps --analyze
    """
    import json

    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"

    persistence = SubagentGapPersistence(history_dir=history_dir)

    # Handle --clear
    if clear:
        persistence.clear_gaps()
        console.print("[green]Subagent gap history cleared[/green]")
        return

    # Load or detect gaps
    if analyze:
        console.print("[cyan]Analyzing session history for subagent patterns...[/cyan]\n")
        gaps = detect_subagent_gaps(history_dir=history_dir)
        # Save newly detected gaps
        for gap in gaps:
            persistence.save_gap(gap)
    else:
        gaps = persistence.load_gaps()

    # JSON output
    if json_out:
        output = {
            "gaps": [g.to_dict() for g in gaps],
            "total": len(gaps),
        }
        console.print(json.dumps(output, indent=2))
        return

    # Display gaps
    if not gaps:
        console.print("[dim]No subagent gaps detected.[/dim]")
        console.print("\n[dim]Tips:[/dim]")
        console.print("  - Use --analyze to run fresh detection")
        console.print("  - Subagent gaps are detected from patterns like:")
        console.print("    • Requests for specific personas or roles")
        console.print("    • Context isolation needs")
        console.print("    • Multi-session/resumable workflows")
        console.print("    • Read-only analysis patterns")
        return

    console.print(f"[bold]Detected Subagent Gaps ({len(gaps)}):[/bold]\n")

    for i, gap in enumerate(gaps, 1):
        # Confidence indicator
        if gap.confidence >= 0.7:
            conf_style = "green"
        elif gap.confidence >= 0.5:
            conf_style = "yellow"
        else:
            conf_style = "dim"

        console.print(f"[bold]{i}. {gap.suggested_name}[/bold] [{conf_style}](confidence: {gap.confidence:.0%})[/{conf_style}]")
        console.print(f"   {gap.description}")

        if gap.indicators:
            console.print(f"   Indicators: {', '.join(gap.indicators)}")

        if gap.suggested_model:
            console.print(f"   Suggested model: {gap.suggested_model}")

        if gap.suggested_tools:
            console.print(f"   Suggested tools: {', '.join(gap.suggested_tools[:3])}{'...' if len(gap.suggested_tools) > 3 else ''}")

        features = []
        if gap.needs_context_isolation:
            features.append("context isolation")
        if gap.needs_resumability:
            features.append("resumable")
        if features:
            console.print(f"   Features: {', '.join(features)}")

        console.print(f"   Occurrences: {gap.occurrence_count}")
        console.print(f"   [dim]Detected: {gap.detected_at[:10]}[/dim]")
        console.print()

    console.print("[dim]Subagent creation from gaps will be available in a future release.[/dim]")


# ============================================================================
# Unified Gap Commands
# ============================================================================

gaps_app = typer.Typer(
    help="Unified gap detection and classification",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@gaps_app.command("detect")
def gaps_detect(
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    analyze: bool = typer.Option(False, "--analyze", help="Force fresh analysis"),
    with_gates: bool = typer.Option(True, "--with-gates/--no-gates", help="Evaluate quality gates"),
):
    """Detect and classify all gaps from session history.

    Runs both skill and subagent gap detection, then classifies each gap
    to determine whether it should become a skill, subagent, or either.

    Quality gates are evaluated by default to filter out low-value patterns.
    Use --no-gates to skip gate evaluation.

    Examples:

        # Detect and classify gaps with quality gates
        bpsai-pair gaps detect

        # Skip quality gate evaluation
        bpsai-pair gaps detect --no-gates

        # Output as JSON
        bpsai-pair gaps detect --json

        # Force fresh analysis
        bpsai-pair gaps detect --analyze
    """
    import json

    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"

    subagents_dir = project_dir / ".claude" / "agents"

    console.print("[cyan]Detecting and classifying gaps...[/cyan]\n")

    # Detect and classify
    classified = detect_and_classify_all(
        history_dir=history_dir,
        skills_dir=skills_dir,
        subagents_dir=subagents_dir,
    )

    # Evaluate quality gates if enabled
    gate_results: dict[str, QualityGateResult] = {}
    if with_gates:
        gate = GapQualityGate()
        for gap in classified:
            gate_results[gap.id] = gate.evaluate(gap)

    # JSON output
    if json_out:
        output = {
            "gaps": [g.to_dict() for g in classified],
            "total": len(classified),
            "by_type": {
                "skill": len([g for g in classified if g.gap_type == GapType.SKILL]),
                "subagent": len([g for g in classified if g.gap_type == GapType.SUBAGENT]),
                "ambiguous": len([g for g in classified if g.gap_type == GapType.AMBIGUOUS]),
            }
        }
        if with_gates:
            output["gates"] = {
                gap_id: {
                    "passed": result.can_generate,
                    "status": result.overall_status.value,
                    "blocking_gates": [r.gate_name for r in result.gate_results if r.status == GateStatus.BLOCK],
                    "warnings": [r.gate_name for r in result.gate_results if r.status == GateStatus.WARN],
                }
                for gap_id, result in gate_results.items()
            }
            output["summary"] = {
                "passed": len([r for r in gate_results.values() if r.can_generate]),
                "blocked": len([r for r in gate_results.values() if r.overall_status == GateStatus.BLOCK]),
                "warned": len([r for r in gate_results.values() if r.overall_status == GateStatus.WARN]),
            }
        console.print(json.dumps(output, indent=2))
        return

    # Display results
    if not classified:
        console.print("[dim]No gaps detected.[/dim]")
        console.print("\n[dim]Tips:[/dim]")
        console.print("  - Gaps are detected from repeated workflows in history")
        console.print("  - Use `skill suggest` for pattern-based skill suggestions")
        console.print("  - Use `subagent gaps` for subagent-specific detection")
        return

    # Group by type
    skills = [g for g in classified if g.gap_type == GapType.SKILL]
    subagents = [g for g in classified if g.gap_type == GapType.SUBAGENT]
    ambiguous = [g for g in classified if g.gap_type == GapType.AMBIGUOUS]

    console.print(f"[bold]Classified Gaps ({len(classified)} total):[/bold]\n")

    if skills:
        console.print("[bold green]SKILLS:[/bold green]")
        for gap in skills:
            gate_result = gate_results.get(gap.id) if with_gates else None
            _display_classified_gap(gap, gate_result)
        console.print()

    if subagents:
        console.print("[bold blue]SUBAGENTS:[/bold blue]")
        for gap in subagents:
            gate_result = gate_results.get(gap.id) if with_gates else None
            _display_classified_gap(gap, gate_result)
        console.print()

    if ambiguous:
        console.print("[bold yellow]AMBIGUOUS (user decision needed):[/bold yellow]")
        for gap in ambiguous:
            gate_result = gate_results.get(gap.id) if with_gates else None
            _display_classified_gap(gap, gate_result)
        console.print()

    # Summary
    console.print("[dim]Summary:[/dim]")
    console.print(f"  Skills: {len(skills)} | Subagents: {len(subagents)} | Ambiguous: {len(ambiguous)}")

    # Gate summary if enabled
    if with_gates and gate_results:
        passed = len([r for r in gate_results.values() if r.can_generate])
        blocked = len([r for r in gate_results.values() if r.overall_status == GateStatus.BLOCK])
        warned = len([r for r in gate_results.values() if r.overall_status == GateStatus.WARN])
        console.print(f"  Gates: [green]{passed} passed[/green] | [red]{blocked} blocked[/red] | [yellow]{warned} warned[/yellow]")


@gaps_app.command("list")
def gaps_list(
    gap_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type: skill, subagent, ambiguous"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all classified gaps.

    Shows gaps that have been detected and classified. Use --type to filter
    by classification.

    Examples:

        # List all gaps
        bpsai-pair gaps list

        # List only skill gaps
        bpsai-pair gaps list --type skill

        # List ambiguous gaps
        bpsai-pair gaps list --type ambiguous
    """
    import json

    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"

    subagents_dir = project_dir / ".claude" / "agents"

    # Detect and classify
    classified = detect_and_classify_all(
        history_dir=history_dir,
        skills_dir=skills_dir,
        subagents_dir=subagents_dir,
    )

    # Filter by type if specified
    if gap_type:
        try:
            filter_type = GapType(gap_type.lower())
            classified = [g for g in classified if g.gap_type == filter_type]
        except ValueError:
            console.print(f"[red]Invalid type: {gap_type}. Use: skill, subagent, ambiguous[/red]")
            raise typer.Exit(1)

    # JSON output
    if json_out:
        output = {
            "gaps": [g.to_dict() for g in classified],
            "total": len(classified),
        }
        console.print(json.dumps(output, indent=2))
        return

    if not classified:
        console.print("[dim]No gaps found.[/dim]")
        return

    console.print(f"[bold]Gaps ({len(classified)}):[/bold]\n")

    for gap in classified:
        _display_classified_gap(gap)


@gaps_app.command("show")
def gaps_show(
    gap_id: str = typer.Argument(..., help="Gap ID to show details for"),
):
    """Show detailed classification for a specific gap.

    Displays full classification details including scores, reasoning,
    and recommendations.

    Examples:

        # Show gap details
        bpsai-pair gaps show skill-testing-workflows
    """
    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"

    subagents_dir = project_dir / ".claude" / "agents"

    # Detect and classify
    classified = detect_and_classify_all(
        history_dir=history_dir,
        skills_dir=skills_dir,
        subagents_dir=subagents_dir,
    )

    # Find the gap
    gap = None
    for g in classified:
        if g.id == gap_id or g.suggested_name == gap_id:
            gap = g
            break

    if not gap:
        console.print(f"[red]Gap not found: {gap_id}[/red]")
        console.print("\n[dim]Available gaps:[/dim]")
        for g in classified[:5]:
            console.print(f"  - {g.id}")
        raise typer.Exit(1)

    # Display detailed view
    console.print(f"\n[bold]Gap: {gap.suggested_name}[/bold]")
    console.print(f"ID: {gap.id}")
    console.print(f"Type: [{'green' if gap.gap_type == GapType.SKILL else 'blue' if gap.gap_type == GapType.SUBAGENT else 'yellow'}]{gap.gap_type.value.upper()}[/]")
    console.print(f"Confidence: {gap.confidence:.0%}")
    console.print(f"\n{gap.description}")

    console.print("\n[bold]Classification Scores:[/bold]")
    _display_score_bar("Portability", gap.portability_score)
    _display_score_bar("Isolation", gap.isolation_score)
    _display_score_bar("Persona", gap.persona_score)
    _display_score_bar("Resumability", gap.resumability_score)
    _display_score_bar("Simplicity", gap.simplicity_score)

    console.print(f"\n[bold]Reasoning:[/bold]")
    console.print(f"  {gap.reasoning}")

    if gap.skill_recommendation:
        console.print("\n[bold green]Skill Recommendation:[/bold green]")
        console.print(f"  Name: {gap.skill_recommendation.suggested_name}")
        if gap.skill_recommendation.allowed_tools:
            console.print(f"  Tools: {', '.join(gap.skill_recommendation.allowed_tools)}")
        console.print(f"  Portability: {', '.join(gap.skill_recommendation.estimated_portability)}")

    if gap.subagent_recommendation:
        console.print("\n[bold blue]Subagent Recommendation:[/bold blue]")
        console.print(f"  Name: {gap.subagent_recommendation.suggested_name}")
        if gap.subagent_recommendation.suggested_model:
            console.print(f"  Model: {gap.subagent_recommendation.suggested_model}")
        if gap.subagent_recommendation.suggested_tools:
            console.print(f"  Tools: {', '.join(gap.subagent_recommendation.suggested_tools)}")
        if gap.subagent_recommendation.persona_hint:
            console.print(f"  Persona: {gap.subagent_recommendation.persona_hint[:60]}...")


def _display_classified_gap(
    gap: ClassifiedGap,
    gate_result: Optional[QualityGateResult] = None,
) -> None:
    """Display a single classified gap with optional gate status.

    Args:
        gap: ClassifiedGap to display
        gate_result: Optional quality gate evaluation result
    """
    # Type color
    if gap.gap_type == GapType.SKILL:
        type_style = "green"
    elif gap.gap_type == GapType.SUBAGENT:
        type_style = "blue"
    else:
        type_style = "yellow"

    # Confidence color
    if gap.confidence >= 0.7:
        conf_style = "green"
    elif gap.confidence >= 0.5:
        conf_style = "yellow"
    else:
        conf_style = "dim"

    # Gate status
    gate_str = ""
    if gate_result is not None:
        if gate_result.can_generate and gate_result.overall_status == GateStatus.PASS:
            gate_str = " [green]✓ PASS[/green]"
        elif gate_result.overall_status == GateStatus.BLOCK:
            gate_str = " [red]✗ BLOCKED[/red]"
        else:
            gate_str = " [yellow]⚠ WARNING[/yellow]"

    console.print(f"  [{type_style}]{gap.gap_type.value.upper():10}[/{type_style}] "
                  f"[bold]{gap.suggested_name}[/bold] "
                  f"[{conf_style}]({gap.confidence:.0%})[/{conf_style}]"
                  f"{gate_str}")
    console.print(f"             [dim]{gap.description[:60]}{'...' if len(gap.description) > 60 else ''}[/dim]")

    # Show blocking reasons if gate failed
    if gate_result is not None and not gate_result.can_generate:
        blocking = [r for r in gate_result.gate_results if r.status == GateStatus.BLOCK]
        warnings = [r for r in gate_result.gate_results if r.status == GateStatus.WARN]
        if blocking:
            reasons = ", ".join(r.reason for r in blocking)
            console.print(f"             [red]Blocked: {reasons}[/red]")
        elif warnings:
            reasons = ", ".join(r.reason for r in warnings)
            console.print(f"             [yellow]Warning: {reasons}[/yellow]")


def _display_score_bar(label: str, score: float) -> None:
    """Display a score as a visual bar.

    Args:
        label: Score label
        score: Score value (0-1)
    """
    filled = int(score * 10)
    bar = "█" * filled + "░" * (10 - filled)
    console.print(f"  {label:12} [{bar}] {score:.2f}")


# ============================================================================
# Gaps Check Command (Quality Gates)
# ============================================================================

@gaps_app.command("check")
def gaps_check(
    gap_id: str = typer.Argument(..., help="Gap ID or name to check"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Check quality gates for a specific gap.

    Evaluates a gap against pre-generation quality gates to determine
    if it should become a skill or be blocked.

    Examples:

        # Check a specific gap
        bpsai-pair gaps check skill-testing-workflows

        # Output as JSON
        bpsai-pair gaps check GAP-001 --json
    """
    import json

    try:
        project_dir = find_project_root()
    except Exception:
        console.print("[red]Could not find project root[/red]")
        raise typer.Exit(1)

    history_dir = project_dir / ".paircoder" / "history"
    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        skills_dir = project_dir / ".claude" / "skills"

    # Detect and classify to find the gap
    classified = detect_and_classify_all(
        history_dir=history_dir,
        skills_dir=skills_dir,
    )

    # Find the gap
    gap = None
    for g in classified:
        if g.id == gap_id or g.suggested_name == gap_id:
            gap = g
            break

    if not gap:
        console.print(f"[red]Gap not found: {gap_id}[/red]")
        if classified:
            console.print("\n[dim]Available gaps:[/dim]")
            for g in classified[:5]:
                console.print(f"  - {g.suggested_name} ({g.id})")
        raise typer.Exit(1)

    # Evaluate quality gates
    result = evaluate_gap_quality(gap, skills_dir=skills_dir)

    # JSON output
    if json_out:
        console.print(json.dumps(result.to_dict(), indent=2))
        return

    # Display results
    console.print(f"\n[bold]Quality Gate Results: {result.gap_name}[/bold]")
    console.print("=" * 50)

    # Overall status
    if result.overall_status == GateStatus.PASS:
        console.print("[green]Overall: ✅ PASS[/green]")
    elif result.overall_status == GateStatus.WARN:
        console.print("[yellow]Overall: ⚠️ WARN[/yellow]")
    else:
        console.print("[red]Overall: ❌ BLOCKED[/red]")

    console.print(f"\nCan Generate: {'Yes' if result.can_generate else 'No'}")
    console.print("\n[bold]Gate Results:[/bold]")

    for gate in result.gate_results:
        if gate.status == GateStatus.PASS:
            icon = "[green]✅[/green]"
        elif gate.status == GateStatus.WARN:
            icon = "[yellow]⚠️[/yellow]"
        else:
            icon = "[red]❌[/red]"

        score_bar = "█" * int(gate.score * 10) + "░" * (10 - int(gate.score * 10))
        console.print(f"  {icon} {gate.gate_name:12} [{score_bar}] {gate.score:.2f}")
        console.print(f"     {gate.reason}")
        if gate.details:
            console.print(f"     [dim]{gate.details}[/dim]")

    console.print(f"\n[bold]Recommendation:[/bold]\n  {result.recommendation}")


# ============================================================================
# Skill Score Command
# ============================================================================

@skill_app.command("score")
def skill_score_cmd(
    skill_name: Optional[str] = typer.Argument(None, help="Specific skill to score"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Score skills on quality dimensions.

    Evaluates skills on token efficiency, trigger clarity, completeness,
    usage frequency, and portability.

    Examples:

        # Score all skills
        bpsai-pair skill score

        # Score specific skill
        bpsai-pair skill score implementing-with-tdd

        # Output as JSON
        bpsai-pair skill score --json
    """
    import json

    try:
        skills_dir = find_skills_dir()
    except FileNotFoundError:
        console.print("[red]Could not find .claude/skills directory[/red]")
        raise typer.Exit(1)

    scorer = SkillScorer(skills_dir)

    if skill_name:
        # Score single skill
        score = scorer.score_skill(skill_name)
        if not score:
            console.print(f"[red]Skill not found: {skill_name}[/red]")
            raise typer.Exit(1)

        if json_out:
            console.print(json.dumps(score.to_dict(), indent=2))
            return

        _display_skill_score(score)
    else:
        # Score all skills
        scores = scorer.score_all()

        if not scores:
            console.print("[dim]No skills found to score.[/dim]")
            return

        if json_out:
            output = {
                "skills": [s.to_dict() for s in scores],
                "total": len(scores),
                "average_score": sum(s.overall_score for s in scores) // len(scores),
            }
            console.print(json.dumps(output, indent=2))
            return

        _display_score_table(scores)


def _display_skill_score(score: SkillScore) -> None:
    """Display a single skill score.

    Args:
        score: SkillScore to display
    """
    # Grade color
    grade_colors = {
        "A": "green",
        "B": "cyan",
        "C": "yellow",
        "D": "red",
        "F": "red",
    }
    grade_color = grade_colors.get(score.grade, "white")

    console.print(f"\n[bold]Skill: {score.skill_name}[/bold]")
    console.print("=" * 50)
    console.print(f"Overall Score: {score.overall_score}/100 (Grade: [{grade_color}]{score.grade}[/{grade_color}])")
    console.print("\n[bold]Dimension Scores:[/bold]")

    for dim in score.dimensions:
        score_bar = "█" * int(dim.score * 10) + "░" * (10 - int(dim.score * 10))
        weight_pct = int(dim.weight * 100)
        console.print(f"  {dim.name:18} [{score_bar}] {dim.score:.2f} (weight: {weight_pct}%)")
        console.print(f"    [dim]{dim.reason}[/dim]")

    if score.recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(score.recommendations, 1):
            console.print(f"  {i}. {rec}")


def _display_score_table(scores: List[SkillScore]) -> None:
    """Display skills as a score table.

    Args:
        scores: List of SkillScore
    """
    from rich.table import Table

    table = Table(title="Skill Quality Report")
    table.add_column("Skill", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Grade", justify="center")
    table.add_column("Token", justify="right")
    table.add_column("Trigger", justify="right")
    table.add_column("Complete", justify="right")
    table.add_column("Portable", justify="right")

    grade_colors = {
        "A": "green",
        "B": "cyan",
        "C": "yellow",
        "D": "red",
        "F": "red",
    }

    for score in scores:
        token = next((d for d in score.dimensions if d.name == "token_efficiency"), None)
        trigger = next((d for d in score.dimensions if d.name == "trigger_clarity"), None)
        complete = next((d for d in score.dimensions if d.name == "completeness"), None)
        portable = next((d for d in score.dimensions if d.name == "portability"), None)

        grade_style = grade_colors.get(score.grade, "white")

        table.add_row(
            score.skill_name,
            str(score.overall_score),
            f"[{grade_style}]{score.grade}[/{grade_style}]",
            f"{int(token.score * 100)}" if token else "-",
            f"{int(trigger.score * 100)}" if trigger else "-",
            f"{int(complete.score * 100)}" if complete else "-",
            f"{int(portable.score * 100)}" if portable else "-",
        )

    console.print(table)

    # Summary stats
    avg_score = sum(s.overall_score for s in scores) // len(scores)
    grade_counts = {}
    for s in scores:
        grade_counts[s.grade] = grade_counts.get(s.grade, 0) + 1

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total: {len(scores)} skills")
    console.print(f"  Average Score: {avg_score}")
    grade_str = ", ".join(f"{g}: {c}" for g, c in sorted(grade_counts.items()))
    console.print(f"  Grades: {grade_str}")

    # Identify skills needing attention
    low_scores = [s for s in scores if s.overall_score < 60]
    if low_scores:
        console.print(f"\n[yellow]Skills needing attention ({len(low_scores)}):[/yellow]")
        for s in low_scores[:3]:
            console.print(f"  - {s.skill_name}: {s.overall_score} ({s.grade})")
            if s.recommendations:
                console.print(f"    → {s.recommendations[0]}")
