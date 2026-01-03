"""
CLI Commands for Planning System (Typer version)

Implements the following commands:
- bpsai-pair plan new|list|show|tasks|add-task
- bpsai-pair task list|show|update|next

To integrate into main CLI:
    from .planning.commands import plan_app, task_app
    app.add_typer(plan_app, name="plan")
    app.add_typer(task_app, name="task")
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json

import typer
from rich.console import Console
from rich.table import Table

from .models import Plan, Task, TaskStatus, PlanStatus, PlanType, Sprint
from .parser import PlanParser, TaskParser
from .state import StateManager
from .token_estimator import PlanTokenEstimator, DEFAULT_THRESHOLD

# Import task lifecycle management
try:
    from ..tasks import TaskArchiver, TaskLifecycle, ChangelogGenerator, TaskState
except ImportError:
    TaskArchiver = None
    TaskLifecycle = None
    ChangelogGenerator = None
    TaskState = None


console = Console()


def find_paircoder_dir() -> Path:
    """Find .paircoder directory in current or parent directories."""
    from ..core.ops import find_paircoder_dir as _find_paircoder_dir
    return _find_paircoder_dir()


def get_state_manager() -> StateManager:
    """Get a StateManager instance for the current project."""
    return StateManager(find_paircoder_dir())


# ============================================================================
# PLAN COMMANDS
# ============================================================================

plan_app = typer.Typer(
    help="Manage plans (goals, tasks, sprints)",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@plan_app.command("new")
def plan_new(
    slug: str = typer.Argument(..., help="Short identifier (e.g., 'workspace-filter')"),
    plan_type: str = typer.Option(
        "feature", "--type", "-t",
        help="Type: feature|bugfix|refactor|chore"
    ),
    title: Optional[str] = typer.Option(None, "--title", "-T", help="Plan title"),
    flow: str = typer.Option("design-plan-implement", "--flow", "-f", help="Associated flow"),
    goal: Optional[List[str]] = typer.Option(None, "--goal", "-g", help="Plan goals (repeatable)"),
):
    """Create a new plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")

    # Generate plan ID
    date_str = datetime.now().strftime("%Y-%m")
    plan_id = f"plan-{date_str}-{slug}"

    # Check if plan already exists
    existing = plan_parser.get_plan_by_id(plan_id)
    if existing:
        console.print(f"[red]Plan already exists: {plan_id}[/red]")
        raise typer.Exit(1)

    # Validate plan type
    try:
        ptype = PlanType(plan_type)
    except ValueError:
        console.print(f"[red]Invalid plan type: {plan_type}[/red]")
        console.print("Valid types: feature, bugfix, refactor, chore")
        raise typer.Exit(1)

    # Create plan
    plan = Plan(
        id=plan_id,
        title=title or slug.replace("-", " ").title(),
        type=ptype,
        status=PlanStatus.PLANNED,
        created_at=datetime.now(),
        flows=[flow],
        goals=list(goal) if goal else [],
    )

    # Save plan
    plan_path = plan_parser.save(plan)

    console.print(f"[green]Created plan:[/green] {plan_id}")
    console.print(f"  Path: {plan_path}")
    console.print(f"  Type: {plan_type}")
    console.print(f"  Flow: {flow}")

    if goal:
        console.print("  Goals:")
        for g in goal:
            console.print(f"    - {g}")

    console.print("")
    console.print("[dim]Next steps:[/dim]")
    console.print(f"  1. Add tasks: bpsai-pair plan add-task {plan_id}")
    console.print(f"  2. Or run flow: bpsai-pair flow run {flow} --plan {plan_id}")


@plan_app.command("list")
def plan_list(
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter: planned|in_progress|complete|archived"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all plans."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    plans = plan_parser.parse_all()

    # Filter by status if specified
    if status:
        plans = [p for p in plans if p.status.value == status]

    if json_out:
        data = [p.to_dict() for p in plans]
        console.print(json.dumps(data, indent=2, default=str))
        return

    if not plans:
        console.print("[dim]No plans found.[/dim]")
        return

    table = Table(title=f"Plans ({len(plans)})")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Tasks", justify="right")

    for plan in plans:
        # Count actual task files with matching plan_id
        task_count = len(task_parser.get_tasks_for_plan(plan.id))
        table.add_row(
            plan.id,
            plan.title,
            plan.type.value,
            f"{plan.status_emoji} {plan.status.value}",
            str(task_count),
        )

    console.print(table)


@plan_app.command("show")
def plan_show(
    plan_id: str = typer.Argument(..., help="Plan ID"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show details of a specific plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    plan = plan_parser.get_plan_by_id(plan_id)

    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    if json_out:
        console.print(json.dumps(plan.to_dict(), indent=2, default=str))
        return

    console.print(f"[bold]{plan.status_emoji} {plan.id}[/bold]")
    console.print(f"{'=' * 60}")
    console.print(f"[cyan]Title:[/cyan] {plan.title}")
    console.print(f"[cyan]Type:[/cyan] {plan.type.value}")
    console.print(f"[cyan]Status:[/cyan] {plan.status.value}")

    if plan.owner:
        console.print(f"[cyan]Owner:[/cyan] {plan.owner}")
    if plan.created_at:
        console.print(f"[cyan]Created:[/cyan] {plan.created_at.strftime('%Y-%m-%d')}")

    if plan.flows:
        console.print(f"\n[cyan]Flows:[/cyan] {', '.join(plan.flows)}")

    if plan.goals:
        console.print("\n[cyan]Goals:[/cyan]")
        for goal in plan.goals:
            console.print(f"  - {goal}")

    if plan.sprints:
        console.print("\n[cyan]Sprints:[/cyan]")
        for sprint in plan.sprints:
            console.print(f"  [{sprint.id}] {sprint.title}")
            if sprint.goal:
                console.print(f"       Goal: {sprint.goal}")
            console.print(f"       Tasks: {len(sprint.task_ids)}")

    # Load actual task files for status
    tasks = task_parser.parse_all(plan.slug)
    if tasks:
        console.print("\n[cyan]Tasks:[/cyan]")
        for task in tasks:
            console.print(f"  {task.status_emoji} {task.id}: {task.title}")
            console.print(f"       Priority: {task.priority} | Complexity: {task.complexity}")


@plan_app.command("tasks")
def plan_tasks(
    plan_id: str = typer.Argument(..., help="Plan ID"),
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter: pending|in_progress|review|done|blocked"
    ),
):
    """List tasks for a specific plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    tasks = task_parser.parse_all(plan.slug)

    if status:
        tasks = [t for t in tasks if t.status.value == status]

    if not tasks:
        console.print(f"[dim]No tasks found for plan: {plan_id}[/dim]")
        return

    table = Table(title=f"Tasks for {plan_id}")
    table.add_column("Status", width=3)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Priority")
    table.add_column("Complexity", justify="right")
    table.add_column("Sprint")

    for task in tasks:
        table.add_row(
            task.status_emoji,
            task.id,
            task.title,
            task.priority,
            str(task.complexity),
            task.sprint or "-",
        )

    console.print(table)


@plan_app.command("status")
def plan_status(
    plan_id: str = typer.Argument("current", help="Plan ID or 'current' for active plan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show individual task list"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show plan status with sprint/task breakdown."""
    paircoder_dir = find_paircoder_dir()
    state_manager = get_state_manager()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    # If "current", get from state
    if plan_id == "current":
        plan_id = state_manager.get_active_plan_id()
        if not plan_id:
            console.print("[yellow]No active plan. Specify a plan ID.[/yellow]")
            console.print("[dim]List plans: bpsai-pair plan list[/dim]")
            raise typer.Exit(1)

    # Load plan
    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    # Load tasks for this plan (filter by plan_id in frontmatter)
    tasks = task_parser.get_tasks_for_plan(plan.id)

    # Calculate task counts
    task_counts = {"pending": 0, "in_progress": 0, "done": 0, "blocked": 0, "cancelled": 0}
    for task in tasks:
        status_key = task.status.value
        if status_key in task_counts:
            task_counts[status_key] += 1

    total_tasks = len(tasks)
    done_count = task_counts["done"]
    progress_pct = int((done_count / total_tasks) * 100) if total_tasks > 0 else 0

    # Group tasks by sprint
    sprints_tasks = {}
    no_sprint = []
    for task in tasks:
        if task.sprint:
            if task.sprint not in sprints_tasks:
                sprints_tasks[task.sprint] = []
            sprints_tasks[task.sprint].append(task)
        else:
            no_sprint.append(task)

    # Find blockers with reasons
    blockers = []
    for task in tasks:
        if task.status == TaskStatus.BLOCKED:
            if task.depends_on:
                reason = f"depends on {', '.join(task.depends_on)}"
            else:
                reason = "blocked"
            blockers.append((task.id, task.title, reason))

    # JSON output
    if json_out:
        data = {
            "plan_id": plan.id,
            "title": plan.title,
            "status": plan.status.value,
            "type": plan.type.value,
            "goals": plan.goals,
            "progress_percent": progress_pct,
            "task_counts": task_counts,
            "total_tasks": total_tasks,
            "sprints": {
                sprint_id: {
                    "tasks": len(tasks_list),
                    "done": sum(1 for t in tasks_list if t.status == TaskStatus.DONE),
                }
                for sprint_id, tasks_list in sprints_tasks.items()
            },
            "blockers": [{"id": b[0], "title": b[1], "reason": b[2]} for b in blockers],
        }
        console.print(json.dumps(data, indent=2))
        return

    # Rich output
    console.print(f"\n[bold]Plan:[/bold] {plan.id}")
    console.print(f"[bold]Title:[/bold] {plan.title}")
    console.print(f"[bold]Status:[/bold] {plan.status_emoji} {plan.status.value}")
    console.print(f"[bold]Type:[/bold] {plan.type.value}")

    # Goals
    if plan.goals:
        console.print("\n[bold]Goals:[/bold]")
        for goal in plan.goals:
            check = "✓" if "complete" in goal.lower() or "done" in goal.lower() else "○"
            console.print(f"  {check} {goal}")

    # Sprint progress
    if sprints_tasks:
        console.print("\n[bold]Sprint Progress:[/bold]")
        for sprint_id in sorted(sprints_tasks.keys()):
            sprint_tasks = sprints_tasks[sprint_id]
            sprint_total = len(sprint_tasks)
            sprint_done = sum(1 for t in sprint_tasks if t.status == TaskStatus.DONE)
            sprint_pct = int((sprint_done / sprint_total) * 100) if sprint_total > 0 else 0

            # Progress bar (16 chars)
            filled = int(sprint_pct / 6.25)  # 16 blocks = 100%
            bar = "█" * filled + "░" * (16 - filled)
            console.print(f"  {sprint_id} [{bar}] {sprint_pct:3d}%  ({sprint_done}/{sprint_total} tasks)")

    # Overall task status
    console.print("\n[bold]Task Status:[/bold]")
    console.print(f"  ✓ Done:        {task_counts['done']}")
    console.print(f"  ● In Progress: {task_counts['in_progress']}")
    console.print(f"  ○ Pending:     {task_counts['pending']}")
    console.print(f"  ⊘ Blocked:     {task_counts['blocked']}")
    if task_counts['cancelled'] > 0:
        console.print(f"  ✗ Cancelled:   {task_counts['cancelled']}")

    # Overall progress
    filled = int(progress_pct / 6.25)
    bar = "█" * filled + "░" * (16 - filled)
    console.print(f"\n[bold]Overall:[/bold] [{bar}] {progress_pct}% ({done_count}/{total_tasks} tasks)")

    # Blockers
    if blockers:
        console.print("\n[bold]Blockers:[/bold]")
        for task_id, title, reason in blockers:
            console.print(f"  [red]⊘[/red] {task_id}: {title}")
            console.print(f"    [dim]→ {reason}[/dim]")

    # Verbose: show all tasks
    if verbose:
        console.print("\n[bold]All Tasks:[/bold]")
        table = Table(show_header=True)
        table.add_column("Status", width=3)
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("Sprint")
        table.add_column("Priority")

        for task in sorted(tasks, key=lambda t: (t.sprint or "", t.priority, t.id)):
            table.add_row(
                task.status_emoji,
                task.id,
                task.title[:40] + "..." if len(task.title) > 40 else task.title,
                task.sprint or "-",
                task.priority,
            )

        console.print(table)

    console.print("")


@plan_app.command("sync-trello")
def plan_sync_trello(
    plan_id: str = typer.Argument(..., help="Plan ID to sync"),
    board_id: Optional[str] = typer.Option(None, "--board", "-b", help="Target Trello board ID (uses config default if not specified)"),
    target_list: Optional[str] = typer.Option(None, "--target-list", "-t", help="Target list for cards (default: Intake/Backlog, use 'Planned/Ready' for sprint planning)"),
    create_lists: bool = typer.Option(False, "--create-lists/--no-create-lists", help="Create sprint lists if missing"),
    link_cards: bool = typer.Option(True, "--link/--no-link", help="Store card IDs in task files"),
    apply_defaults: bool = typer.Option(False, "--apply-defaults", "-d", help="Apply project defaults from config to new cards"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without making changes"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Sync plan tasks to Trello board as cards.

    Uses board_id from .paircoder/config.yaml if --board is not specified.

    By default, cards are created in 'Intake/Backlog'. For sprint planning,
    use --target-list "Planned/Ready" to place cards directly in the ready queue.

    Use --apply-defaults to set custom fields from config.yaml trello.defaults section.
    """
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    # Load plan
    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    # Load tasks
    tasks = task_parser.get_tasks_for_plan(plan_id)
    if not tasks:
        console.print(f"[yellow]No tasks found for plan: {plan_id}[/yellow]")
        raise typer.Exit(1)

    # Load config to get board_id if not provided
    import yaml
    config_file = paircoder_dir / "config.yaml"
    full_config = {}
    if config_file.exists():
        with open(config_file) as f:
            full_config = yaml.safe_load(f) or {}

    # Use config board_id as default if --board not specified
    effective_board_id = board_id or full_config.get("trello", {}).get("board_id")

    results = {
        "plan_id": plan_id,
        "board_id": effective_board_id,
        "lists_created": [],
        "cards_created": [],
        "cards_updated": [],
        "errors": [],
        "dry_run": dry_run,
    }

    # Group tasks by sprint
    sprints_tasks = {}
    for task in tasks:
        sprint_name = task.sprint or "Backlog"
        if sprint_name not in sprints_tasks:
            sprints_tasks[sprint_name] = []
        sprints_tasks[sprint_name].append(task)

    if dry_run:
        # Preview mode
        console.print(f"\n[bold]Would sync plan:[/bold] {plan_id}")
        if effective_board_id:
            console.print(f"[bold]Target board:[/bold] {effective_board_id}")
        else:
            console.print(f"[bold]Target board:[/bold] [yellow](not specified)[/yellow]")
        console.print(f"\n[bold]Tasks to sync:[/bold]")

        for sprint_name, sprint_tasks in sorted(sprints_tasks.items()):
            console.print(f"\n  [cyan]{sprint_name}[/cyan]:")
            for task in sprint_tasks:
                console.print(f"    [{task.id}] {task.title}")
                results["cards_created"].append({
                    "task_id": task.id,
                    "title": task.title,
                    "sprint": sprint_name,
                })

        console.print(f"\n[dim]Total: {len(tasks)} tasks in {len(sprints_tasks)} lists[/dim]")

        if json_out:
            console.print(json.dumps(results, indent=2))
        return

    # Check for Trello connection
    if not effective_board_id:
        console.print("[red]Board ID required. Either:[/red]")
        console.print("  1. Use --board <board-id>")
        console.print("  2. Set trello.board_id in .paircoder/config.yaml")
        console.print("\n[dim]Run 'bpsai-pair trello boards --json' to see available boards.[/dim]")
        raise typer.Exit(1)

    board_id = effective_board_id  # Use effective board_id for the rest of the function

    try:
        from ..trello.auth import load_token
        from ..trello.client import TrelloService
        from ..trello.sync import TrelloSyncManager, TaskData, TaskSyncConfig

        token_data = load_token()
        if not token_data:
            console.print("[red]Not connected to Trello. Run 'bpsai-pair trello connect' first.[/red]")
            raise typer.Exit(1)

        service = TrelloService(
            api_key=token_data["api_key"],
            token=token_data["token"]
        )

        # Set board
        service.set_board(board_id)
        results["board_id"] = board_id

        # Use config already loaded earlier
        trello_config = full_config.get("trello", {})

        # Create sync config from file or use defaults
        sync_config = TaskSyncConfig.from_config(trello_config)
        sync_manager = TrelloSyncManager(service, sync_config)

        console.print(f"\n[bold]Syncing plan:[/bold] {plan_id}")
        console.print(f"[bold]Target board:[/bold] {service.board.name}")
        if target_list:
            console.print(f"[bold]Target list:[/bold] {target_list}")
        else:
            console.print(f"[dim]Target list:[/dim] {sync_config.default_list} (default - use --target-list 'Planned/Ready' for sprint planning)")

        # Ensure BPS labels exist on the board
        console.print("\n[dim]Ensuring BPS labels exist...[/dim]")
        label_results = sync_manager.ensure_bps_labels()
        labels_created = sum(1 for v in label_results.values() if v)
        if labels_created:
            console.print(f"  [green]+ Created {labels_created} BPS labels[/green]")

        # Process each sprint
        for sprint_name, sprint_tasks in sorted(sprints_tasks.items()):
            console.print(f"\n  [cyan]{sprint_name}[/cyan]:")

            # Determine which list to use for new cards
            # Use --target-list if provided, otherwise fall back to config default
            effective_list = target_list or sync_config.default_list
            board_lists = service.get_board_lists()
            if effective_list not in board_lists:
                if create_lists:
                    service.board.add_list(effective_list)
                    service.lists = {lst.name: lst for lst in service.board.all_lists()}
                    results["lists_created"].append(effective_list)
                    console.print(f"    [green]+ Created list: {effective_list}[/green]")
                else:
                    results["errors"].append(f"List not found: {effective_list}")
                    console.print(f"    [red]✗ List not found: {effective_list}[/red]")
                    continue

            # Sync cards for tasks using TrelloSyncManager
            for task in sprint_tasks:
                try:
                    # Convert to TaskData with plan title for Project field
                    task_data = TaskData.from_task(task)
                    task_data.plan_title = plan.title if plan else plan_id

                    # Check if card already exists
                    existing_card, _ = service.find_card_with_prefix(task.id)

                    # For new cards: use the effective list (from --target-list or default)
                    # For existing cards: pass None to update in place without moving
                    card_target_list = None if existing_card else effective_list

                    # Sync using TrelloSyncManager (handles custom fields, labels, descriptions)
                    card = sync_manager.sync_task_to_card(
                        task=task_data,
                        list_name=card_target_list,
                        update_existing=True
                    )

                    if card:
                        if existing_card:
                            results["cards_updated"].append({
                                "task_id": task.id,
                                "card_id": card.id,
                            })
                            console.print(f"    [yellow]↻[/yellow] {task.id}: {task.title}")
                        else:
                            results["cards_created"].append({
                                "task_id": task.id,
                                "card_id": card.id,
                            })
                            # Show inferred stack if any
                            stack = sync_manager.infer_stack(task_data)
                            stack_info = f" [{stack}]" if stack else ""
                            console.print(f"    [green]+[/green] {task.id}: {task.title}{stack_info}")

                            # Update task file with card ID if requested
                            if link_cards:
                                _update_task_with_card_id(task, card.id, task_parser)

                            # Apply project defaults if requested
                            if apply_defaults:
                                defaults = trello_config.get("defaults", {})
                                if defaults:
                                    custom_fields_config = trello_config.get("custom_fields", {})
                                    field_mapping = {
                                        "project": custom_fields_config.get("project", "Project"),
                                        "stack": custom_fields_config.get("stack", "Stack"),
                                        "repo_url": custom_fields_config.get("repo_url", "Repo URL"),
                                        "deployment_tag": custom_fields_config.get("deployment_tag", "Deployment Tag"),
                                    }
                                    field_values = {}
                                    for key, val in defaults.items():
                                        field_name = field_mapping.get(key, key)
                                        field_values[field_name] = val
                                    if field_values:
                                        service.set_card_custom_fields(card, field_values)
                    else:
                        results["errors"].append(f"Failed to sync card for {task.id}")
                        console.print(f"    [red]✗[/red] {task.id}: Failed to sync")

                except Exception as e:
                    error_msg = f"Failed to create card for {task.id}: {str(e)}"
                    results["errors"].append(error_msg)
                    console.print(f"    [red]✗[/red] {task.id}: {str(e)}")

        # Summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Lists created: {len(results['lists_created'])}")
        console.print(f"  Cards created: {len(results['cards_created'])}")
        console.print(f"  Cards updated: {len(results['cards_updated'])}")
        if results["errors"]:
            console.print(f"  [red]Errors: {len(results['errors'])}[/red]")

        if json_out:
            console.print(json.dumps(results, indent=2))

    except ImportError:
        console.print("[red]py-trello not installed. Install with: pip install 'bpsai-pair[trello]'[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def _update_task_with_card_id(task: Task, card_id: str, task_parser: TaskParser) -> bool:
    """Update task file with Trello card ID."""
    try:
        # Find task file
        task_file = task_parser._find_task_file(task.id)
        if not task_file:
            return False

        content = task_file.read_text()

        # Insert trello_card_id into frontmatter
        if "trello_card_id:" not in content:
            # Find end of frontmatter
            lines = content.split("\n")
            new_lines = []
            in_frontmatter = False
            inserted = False

            for line in lines:
                if line.strip() == "---":
                    if in_frontmatter and not inserted:
                        # Insert before closing ---
                        new_lines.append(f'trello_card_id: "{card_id}"')
                        inserted = True
                    in_frontmatter = not in_frontmatter
                new_lines.append(line)

            task_file.write_text("\n".join(new_lines))
            return True

        return False
    except Exception:
        return False


@plan_app.command("estimate")
def plan_estimate(
    plan_id: str = typer.Argument(..., help="Plan ID to estimate"),
    threshold: int = typer.Option(
        DEFAULT_THRESHOLD, "--threshold", "-t",
        help="Token threshold for warnings (default 50000)"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
    show_tasks: bool = typer.Option(True, "--show-tasks/--no-tasks", help="Show per-task breakdown"),
):
    """Estimate token usage for a plan and suggest batching if needed.

    Analyzes all tasks in a plan to estimate total token usage.
    Warns when the plan exceeds comfortable session limits and
    suggests how to split the work into manageable batches.

    Example:
        bpsai-pair plan estimate plan-2025-12-sprint-19-methodology
    """
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    # Find the plan
    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    # Get tasks for this plan
    tasks = task_parser.get_tasks_for_plan(plan_id)
    if not tasks:
        console.print(f"[yellow]No tasks found for plan: {plan_id}[/yellow]")
        raise typer.Exit(0)

    # Parse files_touched from task files
    for task in tasks:
        _populate_files_touched(task, paircoder_dir / "tasks")

    # Create estimator and estimate
    config_path = paircoder_dir / "config.yaml"
    estimator = PlanTokenEstimator.from_config_file(config_path)
    estimate = estimator.estimate_plan(plan_id, tasks, threshold=threshold)

    if json_out:
        console.print(json.dumps(estimate.to_dict(), indent=2))
    else:
        output = estimator.format_estimate(estimate, show_tasks=show_tasks)
        console.print(output)


def _populate_files_touched(task: Task, tasks_dir: Path) -> None:
    """Parse files_touched from task file's 'Files to Modify' section.

    Args:
        task: Task object to populate
        tasks_dir: Directory containing task files
    """
    # Find task file
    task_file = None
    for ext in [".task.md", ".md"]:
        candidate = tasks_dir / f"{task.id}{ext}"
        if candidate.exists():
            task_file = candidate
            break

    if not task_file:
        task.files_touched = []
        return

    try:
        content = task_file.read_text()

        # Find "Files to Modify" section
        files = []
        in_files_section = False

        for line in content.split("\n"):
            line_stripped = line.strip()

            # Check for section header
            if line_stripped.startswith("# Files") or line_stripped.startswith("## Files"):
                in_files_section = True
                continue

            # Check for next section
            if in_files_section and line_stripped.startswith("#"):
                break

            # Parse file entries
            if in_files_section and line_stripped.startswith("- "):
                file_path = line_stripped[2:].strip()
                # Handle backticks around file paths
                file_path = file_path.strip("`")
                if file_path:
                    files.append(file_path)

        task.files_touched = files
    except Exception:
        task.files_touched = []


@plan_app.command("add-task")
def plan_add_task(
    plan_id: str = typer.Argument(..., help="Plan ID"),
    task_id: str = typer.Option(..., "--id", help="Task ID (e.g., TASK-007)"),
    title: str = typer.Option(..., "--title", "-t", help="Task title"),
    task_type: str = typer.Option("feature", "--type", help="Task type"),
    priority: str = typer.Option("P1", "--priority", "-p", help="Priority (P0, P1, P2)"),
    complexity: int = typer.Option(50, "--complexity", "-c", help="Complexity (0-100)"),
    sprint: Optional[str] = typer.Option(None, "--sprint", "-s", help="Sprint ID"),
):
    """Add a task to a plan."""
    paircoder_dir = find_paircoder_dir()
    plan_parser = PlanParser(paircoder_dir / "plans")
    task_parser = TaskParser(paircoder_dir / "tasks")

    plan = plan_parser.get_plan_by_id(plan_id)
    if not plan:
        console.print(f"[red]Plan not found: {plan_id}[/red]")
        raise typer.Exit(1)

    # Create task
    task = Task(
        id=task_id,
        title=title,
        plan_id=plan.id,
        type=task_type,
        priority=priority,
        complexity=complexity,
        status=TaskStatus.PENDING,
        sprint=sprint,
    )

    # Save task
    task_path = task_parser.save(task)

    console.print(f"[green]Created task:[/green] {task_id}")
    console.print(f"  Path: {task_path}")
    console.print(f"  Plan: {plan_id}")


# ============================================================================
# TASK COMMANDS
# ============================================================================

task_app = typer.Typer(
    help="Manage tasks",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@task_app.command("list")
def task_list(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Filter by plan ID"),
    status: Optional[str] = typer.Option(
        None, "--status", "-s",
        help="Filter: pending|in_progress|review|done|blocked"
    ),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List tasks."""
    paircoder_dir = find_paircoder_dir()
    task_parser = TaskParser(paircoder_dir / "tasks")
    plan_parser = PlanParser(paircoder_dir / "plans")

    # Determine plan slug
    plan_slug = None
    if plan_id:
        plan = plan_parser.get_plan_by_id(plan_id)
        if plan:
            plan_slug = plan.slug

    tasks = task_parser.parse_all(plan_slug)

    if status:
        tasks = [t for t in tasks if t.status.value == status]

    if json_out:
        data = [t.to_dict() for t in tasks]
        console.print(json.dumps(data, indent=2))
        return

    if not tasks:
        console.print("[dim]No tasks found.[/dim]")
        return

    # Check for manual edits
    manual_edits = _check_for_manual_edits(paircoder_dir, tasks)
    if manual_edits:
        console.print()
        for edit in manual_edits:
            console.print(f"[yellow]⚠️  Warning: {edit['task_id']} status changed outside CLI (hooks may not have fired)[/yellow]")
            console.print(f"   [dim]File status: {edit['current_status']} | Last CLI status: {edit['last_cli_status']}[/dim]")
            console.print(f"   [dim]To sync: bpsai-pair task update {edit['task_id']} --resync[/dim]")
        console.print()

    table = Table(title=f"Tasks ({len(tasks)})")
    table.add_column("Status", width=3)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Plan")
    table.add_column("Priority")
    table.add_column("Complexity", justify="right")

    for task in tasks:
        table.add_row(
            task.status_emoji,
            task.id,
            task.title[:40] + "..." if len(task.title) > 40 else task.title,
            task.plan_id or "-",
            task.priority,
            str(task.complexity),
        )

    console.print(table)


def _check_for_manual_edits(paircoder_dir: Path, tasks: list) -> list:
    """Check for manual edits to task files.

    Args:
        paircoder_dir: Path to .paircoder directory
        tasks: List of Task objects

    Returns:
        List of dicts with detected manual edit info
    """
    import os
    from .cli_update_cache import get_cli_update_cache, detect_manual_edit

    cli_cache = get_cli_update_cache(paircoder_dir)
    manual_edits = []

    for task in tasks:
        # Get task file path
        task_file = paircoder_dir / "tasks" / f"{task.id}.task.md"
        if not task_file.exists():
            continue

        # Get file modification time
        file_mtime = datetime.fromtimestamp(os.path.getmtime(task_file))

        # Check for manual edit
        result = detect_manual_edit(
            cache=cli_cache,
            task_id=task.id,
            file_mtime=file_mtime,
            current_status=task.status.value,
        )

        if result["detected"]:
            manual_edits.append({
                "task_id": task.id,
                "current_status": result["current_status"],
                "last_cli_status": result["last_cli_status"],
                "last_cli_update": result["last_cli_update"],
                "file_mtime": result["file_mtime"],
            })

    return manual_edits


def _show_time_tracking(task: Task, paircoder_dir: Path) -> None:
    """Show estimated vs actual hours for a task.

    Args:
        task: The task to show time tracking for
        paircoder_dir: Path to .paircoder directory
    """
    # Always show estimated hours
    estimate = task.estimated_hours
    console.print(f"\n[cyan]Estimated:[/cyan] {estimate.expected_hours:.1f}h ({estimate.size_band.upper()}) [{estimate.min_hours:.1f}h - {estimate.max_hours:.1f}h]")

    # Try to get actual hours from time tracking
    actual_hours = task.get_actual_hours(paircoder_dir)

    if actual_hours is not None:
        # Calculate variance
        variance_hours = actual_hours - estimate.expected_hours
        if estimate.expected_hours > 0:
            variance_percent = (variance_hours / estimate.expected_hours) * 100
        else:
            variance_percent = 0.0

        console.print(f"[cyan]Actual:[/cyan] {actual_hours:.1f}h")

        # Show variance with color coding
        sign = "+" if variance_hours > 0 else ""
        if abs(variance_percent) <= 10:
            color = "green"  # Accurate estimate
        elif variance_hours > 0:
            color = "red"  # Took longer than estimated
        else:
            color = "yellow"  # Finished early

        console.print(f"[cyan]Variance:[/cyan] [{color}]{sign}{variance_hours:.1f}h ({sign}{variance_percent:.1f}%)[/{color}]")


@task_app.command("show")
def task_show(
    task_id: str = typer.Argument(..., help="Task ID"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID to narrow search"),
):
    """Show details of a specific task."""
    paircoder_dir = find_paircoder_dir()
    task_parser = TaskParser(paircoder_dir / "tasks")
    plan_parser = PlanParser(paircoder_dir / "plans")

    plan_slug = None
    if plan_id:
        plan = plan_parser.get_plan_by_id(plan_id)
        if plan:
            plan_slug = plan.slug

    task = task_parser.get_task_by_id(task_id, plan_slug)

    if not task:
        console.print(f"[red]Task not found: {task_id}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold]{task.status_emoji} {task.id}[/bold]")
    console.print(f"{'=' * 60}")
    console.print(f"[cyan]Title:[/cyan] {task.title}")
    console.print(f"[cyan]Plan:[/cyan] {task.plan_id}")
    console.print(f"[cyan]Type:[/cyan] {task.type}")
    console.print(f"[cyan]Priority:[/cyan] {task.priority}")
    console.print(f"[cyan]Complexity:[/cyan] {task.complexity}")
    console.print(f"[cyan]Status:[/cyan] {task.status.value}")
    console.print(f"[cyan]Est. Tokens:[/cyan] {task.estimated_tokens_str}")

    if task.sprint:
        console.print(f"[cyan]Sprint:[/cyan] {task.sprint}")

    if task.tags:
        console.print(f"[cyan]Tags:[/cyan] {', '.join(task.tags)}")

    # Show estimated vs actual hours
    _show_time_tracking(task, paircoder_dir)

    if task.body:
        console.print(f"\n{'-' * 60}")
        console.print(task.body)


@task_app.command("update")
def task_update(
    task_id: str = typer.Argument(..., help="Task ID"),
    status: str = typer.Option(
        None, "--status", "-s",
        help="New status: pending|in_progress|review|done|blocked|cancelled"
    ),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID to narrow search"),
    no_hooks: bool = typer.Option(False, "--no-hooks", help="Skip running hooks"),
    skip_state_check: bool = typer.Option(
        False, "--skip-state-check",
        help="Skip checking if state.md was updated (not recommended)"
    ),
    resync: bool = typer.Option(
        False, "--resync",
        help="Re-trigger hooks for current status (use after manual file edits)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Force update, bypass Trello enforcement (not recommended)"
    ),
):
    """Update a task's status.

    Automatically runs hooks (Trello sync, timer, metrics) on status changes.
    Use --no-hooks to skip hook execution.

    When completing a task (--status done), state.md must be updated first.
    Use --skip-state-check to bypass this check (logs a warning).

    If a task file was manually edited, use --resync to re-trigger hooks
    for the current status without changing it.

    For Trello-connected projects, use 'ttask done' instead of '--status done'.
    This ensures acceptance criteria are verified and the card is properly moved.
    """
    # ENFORCEMENT: Block status=done on Trello projects unless forced
    if status and status.lower() == "done" and not force:
        if _is_trello_enabled():
            console.print("\n[red]❌ BLOCKED: This project uses Trello integration.[/red]")
            console.print("")
            console.print("[yellow]Use the Trello command to complete tasks:[/yellow]")
            console.print("")
            console.print("  1. Find the card ID:")
            console.print(f"     [cyan]bpsai-pair ttask list | grep {task_id}[/cyan]")
            console.print("")
            console.print("  2. Complete with ttask done:")
            console.print("     [cyan]bpsai-pair ttask done <TRELLO-ID> --summary \"What was done\"[/cyan]")
            console.print("")
            console.print("[dim]This ensures:[/dim]")
            console.print("[dim]  • Acceptance criteria are verified/checked[/dim]")
            console.print("[dim]  • Completion summary is recorded[/dim]")
            console.print("[dim]  • Card is moved to the correct list[/dim]")
            console.print("[dim]  • Local task file is updated automatically[/dim]")
            console.print("")
            console.print("[dim]To bypass (not recommended): --force[/dim]")
            raise typer.Exit(1)
    elif status and status.lower() == "done" and force:
        if _is_trello_enabled():
            console.print("[yellow]⚠ Bypassing Trello enforcement with --force[/yellow]")
            _log_bypass("task update --status done", task_id, "forced bypass of Trello enforcement")

    paircoder_dir = find_paircoder_dir()
    task_parser = TaskParser(paircoder_dir / "tasks")
    plan_parser = PlanParser(paircoder_dir / "plans")

    plan_slug = None
    if plan_id:
        plan = plan_parser.get_plan_by_id(plan_id)
        if plan:
            plan_slug = plan.slug

    # Get the task before updating (for hook context)
    task = task_parser.get_task_by_id(task_id, plan_slug)
    if not task:
        console.print(f"[red]Task not found: {task_id}[/red]")
        raise typer.Exit(1)

    old_status = task.status.value

    # Handle --resync: use current status from file and trigger hooks
    if resync:
        if status:
            console.print("[yellow]Warning: --status ignored when using --resync[/yellow]")
        status = old_status  # Use current status from file

        # Record CLI update to cache
        from .cli_update_cache import get_cli_update_cache
        cli_cache = get_cli_update_cache(paircoder_dir)
        cli_cache.record_update(task_id, status)

        console.print(f"[cyan]Resyncing {task_id} (status: {status})[/cyan]")

        # Run hooks for current status
        if not no_hooks:
            _run_status_hooks(paircoder_dir, task_id, status, task)

        console.print(f"[green]✓ Resync complete for {task_id}[/green]")
        return

    # Require --status when not using --resync
    if not status:
        console.print("[red]--status is required (or use --resync to re-trigger hooks)[/red]")
        raise typer.Exit(1)

    # Check state.md update requirement when completing a task
    if status == "done" and not skip_state_check:
        check_result = _check_state_md_updated(paircoder_dir, task_id)
        if not check_result["updated"]:
            console.print(f"\n[red]Cannot complete task: state.md not updated since task started.[/red]\n")
            console.print(f"Please update [cyan].paircoder/context/state.md[/cyan] with:")
            console.print(f"  - Mark [yellow]{task_id}[/yellow] as done in task list")
            console.print(f"  - Add session entry under [yellow]\"What Was Just Done\"[/yellow]")
            console.print(f"  - Update [yellow]\"What's Next\"[/yellow] section\n")
            console.print(f"Then retry: [cyan]bpsai-pair task update {task_id} --status done[/cyan]")
            console.print(f"\n[dim]Use --skip-state-check to bypass (not recommended)[/dim]")
            raise typer.Exit(1)
    elif status == "done" and skip_state_check:
        console.print("[yellow]Warning: Skipping state.md check - task completion not documented[/yellow]")

    # Update the status
    success = task_parser.update_status(task_id, status, plan_slug)

    if success:
        emoji_map = {
            "pending": "\u23f3",
            "in_progress": "\U0001f504",
            "review": "\U0001f50d",
            "done": "\u2705",
            "blocked": "\U0001f6ab",
            "cancelled": "\u274c",
        }
        checkmark = "\u2713"
        console.print(f"{emoji_map.get(status, checkmark)} Updated {task_id} -> {status}")

        # Record CLI update to cache (for manual edit detection)
        from .cli_update_cache import get_cli_update_cache
        cli_cache = get_cli_update_cache(paircoder_dir)
        cli_cache.record_update(task_id, status)

        # Run hooks if status actually changed and hooks not disabled
        if not no_hooks and old_status != status:
            _run_status_hooks(paircoder_dir, task_id, status, task)
    else:
        console.print(f"[red]Failed to update task: {task_id}[/red]")
        raise typer.Exit(1)


def _is_trello_enabled() -> bool:
    """Check if Trello integration is enabled for this project."""
    try:
        paircoder_dir = find_paircoder_dir()
        config_path = paircoder_dir / "config.yaml"
        if not config_path.exists():
            return False

        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

        trello_config = config.get("trello", {})
        return trello_config.get("enabled", False) and trello_config.get("board_id")
    except Exception:
        return False


def _log_bypass(command: str, task_id: str, reason: str = "forced") -> None:
    """Log when safety checks are bypassed."""
    try:
        paircoder_dir = find_paircoder_dir()
        log_path = paircoder_dir / "history" / "bypass_log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "task_id": task_id,
            "reason": reason,
        }

        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Best effort logging


def _check_state_md_updated(paircoder_dir: Path, task_id: str) -> dict:
    """Check if state.md was updated since the task started.

    Uses the task's timer start time (from time-tracking-cache.json) to determine
    when the task was started. If no timer exists, checks if state.md was modified
    after the task file's modification time.

    Args:
        paircoder_dir: Path to .paircoder directory
        task_id: The task ID being completed

    Returns:
        dict with:
            - updated: bool - True if state.md was updated since task started
            - reason: str - Explanation of the check result
    """
    import os

    state_path = paircoder_dir / "context" / "state.md"

    # If state.md doesn't exist, we can't check
    if not state_path.exists():
        return {"updated": True, "reason": "state.md not found - skipping check"}

    state_mtime = os.path.getmtime(state_path)

    # Try to get task start time from timer cache
    timer_cache_path = paircoder_dir / "time-tracking-cache.json"
    task_start_time = None

    if timer_cache_path.exists():
        try:
            import json
            with open(timer_cache_path) as f:
                cache_data = json.load(f)

            # Check for active timer for this task
            active = cache_data.get("_active", {})
            if active.get("task_id") == task_id and active.get("start"):
                start_str = active["start"]
                task_start_time = datetime.fromisoformat(start_str).timestamp()

            # Also check for completed entries for this task (last entry)
            if task_start_time is None and task_id in cache_data:
                entries = cache_data[task_id].get("entries", [])
                if entries:
                    # Use the last entry's start time
                    last_entry = entries[-1]
                    if last_entry.get("start"):
                        task_start_time = datetime.fromisoformat(last_entry["start"]).timestamp()

        except (json.JSONDecodeError, KeyError, ValueError):
            pass

    # If we couldn't get timer start time, use task file modification time
    if task_start_time is None:
        task_files = list(paircoder_dir.glob(f"tasks/**/{task_id}.task.md"))
        task_files.extend(list(paircoder_dir.glob(f"tasks/{task_id}.task.md")))
        if task_files:
            # Use the file creation or modification time as fallback
            task_file = task_files[0]
            task_start_time = os.path.getmtime(task_file)

    # If we still can't determine start time, allow the update
    if task_start_time is None:
        return {"updated": True, "reason": "Could not determine task start time - skipping check"}

    # Check if state.md was modified after task started
    if state_mtime > task_start_time:
        return {"updated": True, "reason": "state.md updated after task started"}
    else:
        return {
            "updated": False,
            "reason": f"state.md was last modified before task started",
        }


def _run_status_hooks(paircoder_dir: Path, task_id: str, new_status: str, task) -> None:
    """Run hooks based on status change.

    Args:
        paircoder_dir: Path to .paircoder directory
        task_id: The task ID
        new_status: The new status value
        task: The task object
    """
    try:
        from ..core.hooks import HookRunner, HookContext, load_config

        config = load_config(paircoder_dir)
        runner = HookRunner(config, paircoder_dir)

        if not runner.enabled:
            return

        # Map status to event name
        status_to_event = {
            "in_progress": "on_task_start",
            "review": "on_task_review",
            "done": "on_task_complete",
            "blocked": "on_task_block",
        }

        event = status_to_event.get(new_status)
        if not event:
            return

        # Create hook context
        ctx = HookContext(
            task_id=task_id,
            task=task,
            event=event,
            agent="cli",
            extra={"summary": f"Task updated to {new_status}"},
        )

        # Run the hooks
        results = runner.run_hooks(event, ctx)

        # Report hook results
        for result in results:
            if result.success:
                if result.result and result.result.get("trello_synced"):
                    target_list = result.result.get("target_list", "")
                    console.print(f"  [dim]→ Trello: moved to '{target_list}'[/dim]")
                elif result.result and result.result.get("timer_started"):
                    timer_id = result.result.get("timer_id", "")
                    console.print(f"  [dim]→ Timer started[/dim]")
                elif result.result and result.result.get("timer_stopped"):
                    formatted_duration = result.result.get("formatted_duration", "")
                    formatted_total = result.result.get("formatted_total", "")
                    if formatted_duration and formatted_total:
                        console.print(f"  [dim]→ Timer stopped: {formatted_duration} (total: {formatted_total})[/dim]")
                    else:
                        duration = result.result.get("duration_seconds", 0)
                        console.print(f"  [dim]→ Timer stopped ({duration:.0f}s)[/dim]")
            else:
                if result.error and "Not connected" not in result.error:
                    console.print(f"  [yellow]→ {result.hook}: {result.error}[/yellow]")

    except ImportError:
        pass  # Hooks module not available
    except Exception as e:
        console.print(f"  [yellow]→ Hooks error: {e}[/yellow]")


@task_app.command("next")
def task_next(
    start: bool = typer.Option(False, "--start", "-s", help="Automatically start the next task"),
):
    """Show the next task to work on.

    Use --start to automatically set the task to in_progress.
    """
    state_manager = get_state_manager()
    task = state_manager.get_next_task()

    if not task:
        console.print("[dim]No tasks available. Create a plan first![/dim]")
        return

    # If --start flag, auto-assign the task
    if start and task.status != TaskStatus.IN_PROGRESS:
        from .auto_assign import auto_assign_next

        paircoder_dir = find_paircoder_dir()
        task = auto_assign_next(paircoder_dir, plan_id=task.plan_id)

        if task:
            console.print(f"[green]✓ Auto-started task:[/green] {task.id}")
        else:
            console.print("[red]Failed to auto-start task[/red]")
            return

    console.print(f"[bold]Next task:[/bold] {task.status_emoji} {task.id}")
    console.print(f"[cyan]Title:[/cyan] {task.title}")
    console.print(f"[cyan]Priority:[/cyan] {task.priority} | Complexity: {task.complexity}")

    if task.body:
        # Show first section of body
        lines = task.body.split("\n")
        preview = "\n".join(lines[:10])
        console.print(f"\n{preview}")
        if len(lines) > 10:
            console.print(f"\n[dim]... ({len(lines) - 10} more lines)[/dim]")

    if task.status != TaskStatus.IN_PROGRESS:
        console.print(f"\n[dim]To start: bpsai-pair task next --start[/dim]")
        console.print(f"[dim]Or: bpsai-pair task update {task.id} --status in_progress[/dim]")


@task_app.command("auto-next")
def task_auto_next(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan ID to filter tasks"),
):
    """Automatically assign and start the next pending task.

    This command finds the highest-priority pending task and sets it to in_progress.
    Tasks are prioritized by: priority (P0 > P1 > P2), then complexity (lower first).

    Example:
        # Auto-start next task from any plan
        bpsai-pair task auto-next

        # Auto-start next task from specific plan
        bpsai-pair task auto-next --plan plan-2025-12-sprint-13-autonomy
    """
    from .auto_assign import auto_assign_next

    paircoder_dir = find_paircoder_dir()
    task = auto_assign_next(paircoder_dir, plan_id=plan_id)

    if not task:
        console.print("[yellow]No pending tasks available[/yellow]")
        return

    console.print(f"[green]✓ Auto-assigned:[/green] {task.id}")
    console.print(f"[cyan]Title:[/cyan] {task.title}")
    console.print(f"[cyan]Priority:[/cyan] {task.priority} | Complexity: {task.complexity}")
    console.print(f"[cyan]Status:[/cyan] {task.status_emoji} {task.status.value}")


@task_app.command("archive")
def task_archive(
    task_ids: Optional[List[str]] = typer.Argument(None, help="Task IDs to archive"),
    completed: bool = typer.Option(False, "--completed", help="Archive all completed tasks"),
    sprint: Optional[str] = typer.Option(None, "--sprint", "-s", help="Archive tasks from sprint(s), comma-separated"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Version for changelog entry"),
    no_changelog: bool = typer.Option(False, "--no-changelog", help="Skip changelog update"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be archived"),
):
    """Archive completed tasks."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    # Determine plan slug
    if not plan_id:
        # Try to get from active plan in state
        state_manager = get_state_manager()
        state = state_manager.load_state()
        if state and state.active_plan_id:
            plan_id = state.active_plan_id.replace("plan-", "").split("-", 2)[-1] if "-" in state.active_plan_id else state.active_plan_id
        else:
            console.print("[red]No plan specified and no active plan found[/red]")
            raise typer.Exit(1)

    # Normalize plan slug (remove plan- prefix and date)
    plan_slug = plan_id
    if plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    archiver = TaskArchiver(root_dir)
    lifecycle = TaskLifecycle(paircoder_dir / "tasks")

    # Collect tasks to archive
    tasks_to_archive = []
    plan_dir = paircoder_dir / "tasks" / plan_slug

    if not plan_dir.exists():
        console.print(f"[red]Plan directory not found: {plan_dir}[/red]")
        raise typer.Exit(1)

    if task_ids:
        # Archive specific tasks
        for task_id in task_ids:
            task_file = plan_dir / f"{task_id}.task.md"
            if task_file.exists():
                task = lifecycle.load_task(task_file)
                tasks_to_archive.append(task)
            else:
                console.print(f"[yellow]Task not found: {task_id}[/yellow]")
    elif sprint:
        # Archive by sprint
        sprints = [s.strip() for s in sprint.split(",")]
        tasks_to_archive = lifecycle.get_tasks_by_sprint(plan_dir, sprints)
    elif completed:
        # Archive all completed
        tasks_to_archive = lifecycle.get_tasks_by_status(
            plan_dir, [TaskState.COMPLETED, TaskState.CANCELLED]
        )
    else:
        console.print("[red]Specify --completed, --sprint, or task IDs[/red]")
        raise typer.Exit(1)

    if not tasks_to_archive:
        console.print("[dim]No tasks to archive.[/dim]")
        return

    # Show what will be archived
    if dry_run:
        console.print("[bold]Would archive:[/bold]")
        for task in tasks_to_archive:
            console.print(f"  {task.id}: {task.title} ({task.status.value})")
        console.print(f"\n[dim]Total: {len(tasks_to_archive)} tasks[/dim]")
        return

    # Perform archive
    console.print(f"Archiving {len(tasks_to_archive)} tasks...")
    result = archiver.archive_batch(tasks_to_archive, plan_slug, version)

    for task in result.archived:
        console.print(f"  [green]\u2713[/green] {task.id}: {task.title}")

    for skip in result.skipped:
        console.print(f"  [yellow]\u23f8[/yellow] {skip}")

    for error in result.errors:
        console.print(f"  [red]\u2717[/red] {error}")

    # Update changelog
    if not no_changelog and result.archived and version:
        changelog_path = root_dir / "CHANGELOG.md"
        changelog = ChangelogGenerator(changelog_path)
        changelog.update_changelog(result.archived, version)
        console.print(f"\n[green]Updated CHANGELOG.md with {version}[/green]")

    console.print(f"\n[green]Archived {len(result.archived)} tasks to:[/green]")
    console.print(f"  {result.archive_path}")


@task_app.command("restore")
def task_restore(
    task_id: str = typer.Argument(..., help="Task ID to restore"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
):
    """Restore a task from archive."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    # Determine plan slug
    if not plan_id:
        state_manager = get_state_manager()
        state = state_manager.load_state()
        if state and state.active_plan_id:
            plan_id = state.active_plan_id

    plan_slug = plan_id
    if plan_slug and plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    archiver = TaskArchiver(root_dir)

    try:
        restored_path = archiver.restore_task(task_id, plan_slug)
        console.print(f"[green]\u2713 Restored {task_id} to:[/green]")
        console.print(f"  {restored_path}")
    except FileNotFoundError:
        console.print(f"[red]Archived task not found: {task_id}[/red]")
        raise typer.Exit(1)


@task_app.command("list-archived")
def task_list_archived(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
    json_out: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List archived tasks."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    plan_slug = plan_id
    if plan_slug and plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    archiver = TaskArchiver(root_dir)
    archived = archiver.list_archived(plan_slug)

    if json_out:
        from dataclasses import asdict
        data = [asdict(t) for t in archived]
        console.print(json.dumps(data, indent=2))
        return

    if not archived:
        console.print("[dim]No archived tasks found.[/dim]")
        return

    table = Table(title=f"Archived Tasks ({len(archived)})")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Sprint")
    table.add_column("Archived At")

    for task in archived:
        table.add_row(
            task.id,
            task.title[:40] + "..." if task.title and len(task.title) > 40 else task.title or "",
            task.sprint or "-",
            task.archived_at[:10] if task.archived_at else "-",
        )

    console.print(table)


@task_app.command("cleanup")
def task_cleanup(
    retention_days: int = typer.Option(90, "--retention", "-r", help="Retention period in days"),
    dry_run: bool = typer.Option(True, "--dry-run/--confirm", help="Dry run or confirm deletion"),
):
    """Clean up old archived tasks."""
    if TaskArchiver is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    archiver = TaskArchiver(root_dir)
    to_remove = archiver.cleanup(retention_days, dry_run)

    if not to_remove:
        console.print(f"[dim]No tasks older than {retention_days} days.[/dim]")
        return

    if dry_run:
        console.print(f"[bold]Would remove ({len(to_remove)} tasks older than {retention_days} days):[/bold]")
        for item in to_remove:
            console.print(f"  {item}")
        console.print("\n[dim]Run with --confirm to delete[/dim]")
    else:
        console.print(f"[green]Removed {len(to_remove)} archived tasks:[/green]")
        for item in to_remove:
            console.print(f"  [red]\u2717[/red] {item}")


@task_app.command("changelog-preview")
def task_changelog_preview(
    sprint: Optional[str] = typer.Option(None, "--sprint", "-s", help="Sprint(s) to preview, comma-separated"),
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Plan slug"),
    version: str = typer.Option("vX.Y.Z", "--version", "-v", help="Version string"),
):
    """Preview changelog entry for tasks."""
    if TaskArchiver is None or ChangelogGenerator is None:
        console.print("[red]Task lifecycle module not available[/red]")
        raise typer.Exit(1)

    paircoder_dir = find_paircoder_dir()
    root_dir = paircoder_dir.parent

    # Determine plan slug
    if not plan_id:
        state_manager = get_state_manager()
        state = state_manager.load_state()
        if state and state.active_plan_id:
            plan_id = state.active_plan_id

    plan_slug = plan_id
    if plan_slug and plan_slug.startswith("plan-"):
        parts = plan_slug.split("-")
        if len(parts) > 3:
            plan_slug = "-".join(parts[3:])

    lifecycle = TaskLifecycle(paircoder_dir / "tasks")
    plan_dir = paircoder_dir / "tasks" / plan_slug

    if not plan_dir.exists():
        console.print(f"[red]Plan directory not found: {plan_dir}[/red]")
        raise typer.Exit(1)

    # Get tasks
    if sprint:
        sprints = [s.strip() for s in sprint.split(",")]
        tasks = lifecycle.get_tasks_by_sprint(plan_dir, sprints)
    else:
        tasks = lifecycle.get_tasks_by_status(plan_dir, [TaskState.COMPLETED])

    if not tasks:
        console.print("[dim]No completed tasks found.[/dim]")
        return

    # Convert to ArchivedTask format for changelog generator
    from ..tasks.archiver import ArchivedTask
    archived_tasks = [
        ArchivedTask(
            id=t.id,
            title=t.title,
            sprint=t.sprint,
            status=t.status.value,
            completed_at=t.completed_at.isoformat() if t.completed_at else None,
            archived_at="",
            changelog_entry=t.changelog_entry,
            tags=t.tags,
        )
        for t in tasks
    ]

    changelog = ChangelogGenerator(root_dir / "CHANGELOG.md")
    preview = changelog.preview(archived_tasks, version)

    console.print("[bold]Changelog Preview:[/bold]\n")
    console.print(preview)


# ============================================================================
# INTENT DETECTION COMMANDS
# ============================================================================

intent_app = typer.Typer(
    help="Intent detection and planning mode commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@intent_app.command("detect")
def intent_detect(
    text: str = typer.Argument(..., help="Text to analyze for intent"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Detect work intent from text."""
    from .intent_detection import IntentDetector

    detector = IntentDetector()
    matches = detector.detect_all(text)

    if json_out:
        import json as json_module
        output = [{
            "intent": m.intent.value,
            "confidence": m.confidence,
            "suggested_flow": m.suggested_flow,
            "triggers": m.triggers,
        } for m in matches]
        console.print(json_module.dumps(output, indent=2))
        return

    if not matches:
        console.print("[dim]No clear intent detected[/dim]")
        return

    console.print("[bold]Detected Intents:[/bold]\n")
    for match in matches:
        confidence_color = "green" if match.confidence >= 0.8 else "yellow" if match.confidence >= 0.6 else "dim"
        console.print(f"[{confidence_color}]{match.intent.value}[/{confidence_color}] ({match.confidence:.0%})")
        if match.suggested_flow:
            console.print(f"  Suggested flow: {match.suggested_flow}")
        if match.triggers:
            console.print(f"  Triggers: {', '.join(match.triggers[:3])}")
        console.print()


@intent_app.command("should-plan")
def intent_should_plan(
    text: str = typer.Argument(..., help="Text to analyze"),
    json_out: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Check if text should trigger planning mode."""
    from .intent_detection import IntentDetector

    detector = IntentDetector()
    should_plan, match = detector.should_enter_planning_mode(text)

    if json_out:
        import json as json_module
        output = {
            "should_plan": should_plan,
            "intent": match.intent.value if match else None,
            "confidence": match.confidence if match else 0,
            "suggested_flow": match.suggested_flow if match else None,
        }
        console.print(json_module.dumps(output, indent=2))
        return

    if should_plan and match:
        console.print(f"[green]YES - Planning mode recommended[/green]")
        console.print(f"  Intent: {match.intent.value} ({match.confidence:.0%})")
        console.print(f"  Suggested flow: {match.suggested_flow}")
    else:
        console.print("[dim]No - Direct action is fine[/dim]")


@intent_app.command("suggest-flow")
def intent_suggest_flow(
    text: str = typer.Argument(..., help="Text to analyze"),
):
    """Suggest appropriate flow for text."""
    from .intent_detection import IntentDetector

    detector = IntentDetector()
    flow = detector.get_flow_suggestion(text)

    if flow:
        console.print(f"[green]Suggested flow: {flow}[/green]")
        console.print(f"\n[dim]Run: bpsai-pair flow run {flow}[/dim]")
    else:
        console.print("[dim]No specific flow suggested for this request.[/dim]")


# ============================================================================
# STANDUP COMMANDS
# ============================================================================

standup_app = typer.Typer(
    help="Daily standup summary commands",
    context_settings={"help_option_names": ["-h", "--help"]}
)


@standup_app.command("generate")
def standup_generate(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Filter by plan ID"),
    since: int = typer.Option(24, "--since", "-s", help="Hours to look back for completed tasks"),
    format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown, slack, trello"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write to file instead of stdout"),
):
    """Generate a daily standup summary.

    Shows completed tasks, in-progress work, and blockers.

    Examples:
        # Generate markdown summary
        bpsai-pair standup generate

        # Generate Slack-formatted summary
        bpsai-pair standup generate --format slack

        # Look back 48 hours
        bpsai-pair standup generate --since 48

        # Save to file
        bpsai-pair standup generate -o standup.md
    """
    from .standup import generate_standup

    paircoder_dir = find_paircoder_dir()

    summary = generate_standup(
        paircoder_dir=paircoder_dir,
        plan_id=plan_id,
        since_hours=since,
        format=format,
    )

    if output:
        from pathlib import Path
        Path(output).write_text(summary)
        console.print(f"[green]Wrote standup summary to {output}[/green]")
    else:
        console.print(summary)


@standup_app.command("post")
def standup_post(
    plan_id: Optional[str] = typer.Option(None, "--plan", "-p", help="Filter by plan ID"),
    since: int = typer.Option(24, "--since", "-s", help="Hours to look back"),
):
    """Post standup summary to Trello board's Notes list.

    Adds a comment to the weekly summary card with today's standup.
    """
    from .standup import StandupGenerator

    paircoder_dir = find_paircoder_dir()

    # Load config to get board ID
    config_file = paircoder_dir / "config.yaml"
    if not config_file.exists():
        console.print("[red]No config.yaml found[/red]")
        raise typer.Exit(1)

    import yaml
    config = yaml.safe_load(config_file.read_text()) or {}
    board_id = config.get("trello", {}).get("board_id")

    if not board_id:
        import yaml
        config_file = paircoder_dir / "config.yaml"
        if config_file.exists():
            with open(config_file) as f:
                full_config = yaml.safe_load(f) or {}
                board_id = full_config.get("trello", {}).get("board_id")

        if not board_id:
            console.print("[red]Board ID required. Use --board <board-id> or configure default board.[/red]")
            console.print("[dim]List boards: bpsai-pair trello boards[/dim]")
            console.print("[dim]Set default: bpsai-pair trello use-board <board-id>[/dim]")
            raise typer.Exit(1)
        else:
            console.print(f"[dim]Using board from config: {board_id}[/dim]")

    generator = StandupGenerator(paircoder_dir)
    summary = generator.generate(since_hours=since, plan_id=plan_id)
    comment = summary.to_trello_comment()

    # Post to Trello
    try:
        from ..trello.auth import load_token
        from ..trello.client import TrelloService

        token_data = load_token()
        if not token_data:
            console.print("[red]Not connected to Trello[/red]")
            raise typer.Exit(1)

        service = TrelloService(
            api_key=token_data["api_key"],
            token=token_data["token"]
        )
        service.set_board(board_id)

        # Find or create weekly summary card in Notes list
        notes_cards = service.get_cards_in_list("Notes / Ops Log")
        summary_card = None

        week_str = datetime.now().strftime("Week %W")
        for card in notes_cards:
            if week_str in card.name or "Weekly Summary" in card.name:
                summary_card = card
                break

        if summary_card:
            service.add_comment(summary_card, comment)
            console.print(f"[green]Posted standup to '{summary_card.name}'[/green]")
        else:
            console.print(f"[yellow]No weekly summary card found in Notes / Ops Log[/yellow]")
            console.print("[dim]Create a card with 'Week' or 'Weekly Summary' in the title[/dim]")
            console.print("\n[bold]Generated Summary:[/bold]")
            console.print(comment)

    except ImportError:
        console.print("[red]Trello module not available[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error posting to Trello: {e}[/red]")
        raise typer.Exit(1)


# ============================================================================
# STATUS COMMAND (enhanced)
# ============================================================================

def planning_status() -> str:
    """
    Get planning status for the enhanced status command.

    Call this from the main status command to include planning info.
    """
    state_manager = get_state_manager()
    return state_manager.format_status_report()
