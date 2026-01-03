"""
Trello CLI commands for PairCoder.
"""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from .auth import load_token, store_token, clear_token, is_connected
from .client import TrelloService

app = typer.Typer(name="trello", help="Trello integration commands")
console = Console()


def get_client() -> TrelloService:
    """Get an authenticated Trello client.

    Returns:
        TrelloService instance

    Raises:
        typer.Exit: If not connected to Trello
    """
    creds = load_token()
    if not creds:
        console.print("[red]Not connected to Trello. Run: bpsai-pair trello connect[/red]")
        raise typer.Exit(1)
    return TrelloService(api_key=creds["api_key"], token=creds["token"])


def _load_config() -> dict:
    """Load project config with error handling."""
    try:
        from ..core.config import Config
        from ..core.ops import find_project_root
        from pathlib import Path
        import yaml

        root = find_project_root()
        config_file = root / ".paircoder" / "config.yaml"
        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}
    except Exception:
        return {}


def _save_config(config: dict) -> None:
    """Save project config."""
    try:
        from ..core.ops import find_project_root
        from pathlib import Path
        import yaml

        root = find_project_root()
        config_dir = root / ".paircoder"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.yaml"

        with open(config_file, 'w', encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not save config: {e}[/yellow]")


@app.command()
def connect(
    api_key: str = typer.Option(..., prompt=True, help="Trello API key"),
    token: str = typer.Option(..., prompt=True, hide_input=True, help="Trello token"),
):
    """Connect to Trello (validates and stores credentials)."""
    try:
        client = TrelloService(api_key=api_key, token=token)
    except ImportError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if not client.healthcheck():
        console.print("[red]Failed to validate Trello credentials[/red]")
        raise typer.Exit(1)

    store_token(token=token, api_key=api_key)
    console.print("[green]✓ Connected to Trello[/green]")


@app.command()
def status():
    """Check Trello connection status."""
    if is_connected():
        console.print("[green]✓ Connected to Trello[/green]")

        config = _load_config()
        board_id = config.get("trello", {}).get("board_id")
        board_name = config.get("trello", {}).get("board_name")

        if board_id:
            console.print(f"  Board: {board_name} ({board_id})")
        else:
            console.print("  [yellow]No board configured. Run: bpsai-pair trello use-board <id>[/yellow]")
    else:
        console.print("[yellow]Not connected. Run: bpsai-pair trello connect[/yellow]")


@app.command()
def disconnect():
    """Remove stored Trello credentials."""
    clear_token()
    console.print("[green]✓ Disconnected from Trello[/green]")


@app.command()
def boards(
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List available Trello boards."""
    import json

    client = get_client()
    board_list = client.list_boards()

    # Filter out closed boards
    open_boards = [b for b in board_list if not b.closed]

    if as_json:
        boards_data = [
            {
                "id": board.id,
                "name": board.name,
                "url": board.url,
                "shortUrl": getattr(board, "shortUrl", board.url),
            }
            for board in open_boards
        ]
        console.print(json.dumps(boards_data, indent=2))
        return

    table = Table(title="Trello Boards")
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="green", no_wrap=True)  # no_wrap prevents truncation
    table.add_column("URL", style="blue")

    for board in open_boards:
        table.add_row(board.name, board.id, board.url)

    console.print(table)


@app.command("use-board")
def use_board(board_id: str = typer.Argument(..., help="Board ID to use")):
    """Set the active Trello board for this project."""
    client = get_client()
    board = client.set_board(board_id)

    config = _load_config()
    if "trello" not in config:
        config["trello"] = {}
    config["trello"]["board_id"] = board_id
    config["trello"]["board_name"] = board.name
    config["trello"]["enabled"] = True
    _save_config(config)

    console.print(f"[green]✓ Using board: {board.name}[/green]")

    lists = client.get_board_lists()
    console.print(f"\nLists: {', '.join(lists.keys())}")


@app.command()
def lists():
    """Show lists on the active board."""
    config = _load_config()
    board_id = config.get("trello", {}).get("board_id")

    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    client = get_client()
    client.set_board(board_id)

    table = Table(title=f"Lists on {config['trello'].get('board_name', board_id)}")
    table.add_column("Name")
    table.add_column("Cards", justify="right")

    for name, lst in client.get_board_lists().items():
        card_count = len(lst.list_cards())
        table.add_row(name, str(card_count))

    console.print(table)


@app.command("config")
def trello_config(
    show: bool = typer.Option(False, "--show", help="Show current config"),
    set_list: Optional[str] = typer.Option(None, "--set-list", help="Set list mapping (format: status=ListName)"),
    set_field: Optional[str] = typer.Option(None, "--set-field", help="Set custom field (format: field=FieldName)"),
    agent: Optional[str] = typer.Option(None, "--agent", help="Set agent identity (claude/codex)"),
):
    """View or modify Trello configuration."""
    config = _load_config()
    trello = config.get("trello", {})

    # Merge with defaults
    defaults = {
        "enabled": False,
        "board_id": None,
        "board_name": None,
        "lists": {
            "backlog": "Backlog",
            "sprint": "Sprint",
            "in_progress": "In Progress",
            "review": "In Review",
            "done": "Done",
            "blocked": "Blocked",
        },
        "custom_fields": {
            "agent_task": "Agent Task",
            "priority": "Priority",
        },
        "agent_identity": "claude",
        "auto_sync": True,
    }

    for key, default in defaults.items():
        if key not in trello:
            trello[key] = default
        elif isinstance(default, dict) and isinstance(trello.get(key), dict):
            trello[key] = {**default, **trello[key]}

    if show or (not set_list and not set_field and not agent):
        console.print("[bold]Trello Configuration[/bold]\n")
        console.print(f"Enabled: {trello['enabled']}")
        console.print(f"Board: {trello['board_name']} ({trello['board_id']})")
        console.print(f"Agent: {trello['agent_identity']}")
        console.print(f"Auto-sync: {trello['auto_sync']}")
        console.print("\n[dim]List Mappings:[/dim]")
        for status, list_name in trello.get('lists', {}).items():
            console.print(f"  {status}: {list_name}")
        console.print("\n[dim]Custom Fields:[/dim]")
        for field, name in trello.get('custom_fields', {}).items():
            console.print(f"  {field}: {name}")
        return

    updates_made = False

    if set_list:
        if "=" not in set_list:
            console.print("[red]Invalid format. Use: --set-list status=ListName[/red]")
            raise typer.Exit(1)
        status, list_name = set_list.split("=", 1)
        if "lists" not in trello:
            trello["lists"] = {}
        trello["lists"][status] = list_name
        console.print(f"[green]✓ Set list mapping: {status} → {list_name}[/green]")
        updates_made = True

    if set_field:
        if "=" not in set_field:
            console.print("[red]Invalid format. Use: --set-field field=FieldName[/red]")
            raise typer.Exit(1)
        field, name = set_field.split("=", 1)
        if "custom_fields" not in trello:
            trello["custom_fields"] = {}
        trello["custom_fields"][field] = name
        console.print(f"[green]✓ Set custom field: {field} → {name}[/green]")
        updates_made = True

    if agent:
        if agent not in ["claude", "codex"]:
            console.print("[red]Agent must be 'claude' or 'codex'[/red]")
            raise typer.Exit(1)
        trello["agent_identity"] = agent
        console.print(f"[green]✓ Set agent identity: {agent}[/green]")
        updates_made = True

    if updates_made:
        config["trello"] = trello
        _save_config(config)


@app.command("progress")
def progress_comment(
    task_id: str = typer.Argument(..., help="Task ID (e.g., TASK-001)"),
    message: str = typer.Argument(None, help="Progress message"),
    blocked: Optional[str] = typer.Option(None, "--blocked", "-b", help="Report blocking issue"),
    waiting: Optional[str] = typer.Option(None, "--waiting", "-w", help="Report waiting for dependency"),
    step: Optional[str] = typer.Option(None, "--step", "-s", help="Report completed step"),
    started: bool = typer.Option(False, "--started", help="Report task started"),
    completed: bool = typer.Option(False, "--completed", "-c", help="Report task completed"),
    review: bool = typer.Option(False, "--review", "-r", help="Report submitted for review"),
    agent: str = typer.Option("claude", "--agent", "-a", help="Agent name for comment"),
):
    """Post a progress comment to a Trello card.

    Examples:
        # Report progress
        bpsai-pair trello progress TASK-001 "Completed authentication module"

        # Report blocking issue
        bpsai-pair trello progress TASK-001 --blocked "Waiting for API access"

        # Report step completion
        bpsai-pair trello progress TASK-001 --step "Unit tests passing"

        # Report task started
        bpsai-pair trello progress TASK-001 --started

        # Report completion with summary
        bpsai-pair trello progress TASK-001 --completed "Added user auth with OAuth2"
    """
    from pathlib import Path
    from .progress import create_progress_reporter
    from ..core.ops import find_paircoder_dir

    paircoder_dir = find_paircoder_dir()
    if not paircoder_dir.exists():
        console.print("[red]Not in a PairCoder project directory[/red]")
        raise typer.Exit(1)

    reporter = create_progress_reporter(paircoder_dir, task_id, agent)
    if not reporter:
        console.print("[red]Could not create progress reporter. Check Trello connection.[/red]")
        raise typer.Exit(1)

    success = False

    if started:
        success = reporter.report_start()
        if success:
            console.print(f"[green]Posted: Task started[/green]")
    elif blocked:
        success = reporter.report_blocked(blocked)
        if success:
            console.print(f"[green]Posted: Blocked - {blocked}[/green]")
    elif waiting:
        success = reporter.report_waiting(waiting)
        if success:
            console.print(f"[green]Posted: Waiting for {waiting}[/green]")
    elif step:
        success = reporter.report_step_complete(step)
        if success:
            console.print(f"[green]Posted: Completed step - {step}[/green]")
    elif completed:
        summary = message or "Task completed"
        success = reporter.report_completion(summary)
        if success:
            console.print(f"[green]Posted: Task completed[/green]")
    elif review:
        success = reporter.report_review()
        if success:
            console.print(f"[green]Posted: Submitted for review[/green]")
    elif message:
        success = reporter.report_progress(message)
        if success:
            console.print(f"[green]Posted: {message}[/green]")
    else:
        console.print("[yellow]No progress update specified. Use --help for options.[/yellow]")
        raise typer.Exit(1)

    if not success:
        console.print("[red]Failed to post progress comment[/red]")
        raise typer.Exit(1)


@app.command("sync")
def trello_sync(
    from_trello: bool = typer.Option(False, "--from-trello", help="Sync changes FROM Trello to local tasks"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview changes without applying"),
    list_name: Optional[str] = typer.Option(None, "--list", "-l", help="Only sync cards from specific list"),
):
    """Sync tasks between Trello and local files.

    By default, previews what would be synced. Use --from-trello to pull
    changes from Trello cards and update local task files.

    Examples:
        # Preview what would be synced
        bpsai-pair trello sync --preview

        # Pull changes from Trello to local
        bpsai-pair trello sync --from-trello

        # Only sync cards from a specific list
        bpsai-pair trello sync --from-trello --list "In Progress"
    """
    from pathlib import Path
    from rich.table import Table
    from .sync import TrelloToLocalSync
    from .auth import load_token
    from ..core.ops import find_paircoder_dir

    paircoder_dir = find_paircoder_dir()
    if not paircoder_dir.exists():
        console.print("[red]Not in a PairCoder project directory[/red]")
        raise typer.Exit(1)

    config = _load_config()
    board_id = config.get("trello", {}).get("board_id")
    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    token_data = load_token()
    if not token_data:
        console.print("[red]Not connected to Trello. Run: bpsai-pair trello connect[/red]")
        raise typer.Exit(1)

    # Create sync instance
    try:
        from .client import TrelloService
        service = TrelloService(token_data["api_key"], token_data["token"])
        service.set_board(board_id)
        sync_manager = TrelloToLocalSync(service, paircoder_dir / "tasks")
    except Exception as e:
        console.print(f"[red]Failed to connect to Trello: {e}[/red]")
        raise typer.Exit(1)

    if preview or not from_trello:
        # Preview mode
        console.print("\n[bold]Sync Preview (Trello → Local)[/bold]\n")

        preview_results = sync_manager.get_sync_preview()
        if not preview_results:
            console.print("[dim]No cards with task IDs found on board[/dim]")
            return

        table = Table()
        table.add_column("Task ID", style="cyan")
        table.add_column("Action", style="yellow")
        table.add_column("Details")

        updates_pending = 0
        for item in preview_results:
            task_id = item["task_id"]
            action = item["action"]

            if action == "update":
                details = f"{item['field']}: {item['from']} → {item['to']}"
                table.add_row(task_id, "[green]update[/green]", details)
                updates_pending += 1
            elif action == "skip":
                reason = item.get("reason", "No changes")
                table.add_row(task_id, "[dim]skip[/dim]", f"[dim]{reason}[/dim]")
            elif action == "error":
                table.add_row(task_id, "[red]error[/red]", item.get("reason", "Unknown error"))

        console.print(table)
        console.print(f"\n[bold]{updates_pending}[/bold] task(s) would be updated")

        if updates_pending > 0 and not from_trello:
            console.print("\n[dim]Run with --from-trello to apply changes[/dim]")

    else:
        # Apply changes
        console.print("\n[bold]Syncing from Trello → Local[/bold]\n")

        list_filter = [list_name] if list_name else None
        results = sync_manager.sync_all_cards(list_filter=list_filter)

        if not results:
            console.print("[dim]No cards with task IDs found on board[/dim]")
            return

        updated = 0
        skipped = 0
        errors = 0

        for result in results:
            if result.action == "updated":
                updated += 1
                changes_str = ", ".join(
                    f"{k}: {v['from']} → {v['to']}"
                    for k, v in result.changes.items()
                )
                console.print(f"  [green]✓[/green] {result.task_id}: {changes_str}")

                # Show conflicts if any
                for conflict in result.conflicts:
                    console.print(f"    [yellow]⚠ Conflict: {conflict.field} ({conflict.resolution})[/yellow]")

            elif result.action == "skipped":
                skipped += 1
            elif result.action == "error":
                errors += 1
                console.print(f"  [red]✗[/red] {result.task_id}: {result.error}")

        console.print(f"\n[bold]Summary:[/bold] {updated} updated, {skipped} skipped, {errors} errors")


@app.command("init-board")
def init_board(
    name: str = typer.Option(..., "--name", "-n", help="Name for the new board"),
    from_template: str = typer.Option(
        "BPS AI Project Template",
        "--from-template", "-t",
        help="Name of the template board to copy"
    ),
    keep_cards: bool = typer.Option(False, "--keep-cards", help="Copy cards from template"),
    set_active: bool = typer.Option(True, "--set-active/--no-set-active", help="Set as active board for this project"),
):
    """Create a new Trello board from a template.

    Creates a board by copying from a template board, preserving:
    - All lists and their order
    - Custom field definitions
    - Labels with colors
    - Butler automation rules

    Examples:
        # Create board from default BPS template
        bpsai-pair trello init-board --name "My New Project"

        # Create from custom template
        bpsai-pair trello init-board --name "My Project" --from-template "My Template"

        # Copy template cards too
        bpsai-pair trello init-board --name "My Project" --keep-cards
    """
    from rich.progress import Progress, SpinnerColumn, TextColumn

    client = get_client()

    # Check if template exists
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Finding template board...", total=None)

        template = client.find_board_by_name(from_template)
        if not template:
            progress.stop()
            console.print(f"[red]Template board '{from_template}' not found[/red]")
            console.print("\n[dim]Available boards:[/dim]")
            for board in client.list_boards():
                if not board.closed:
                    console.print(f"  - {board.name}")
            raise typer.Exit(1)

        progress.update(task, description=f"Creating board from '{template.name}'...")

        try:
            new_board = client.copy_board_from_template(
                template_name=from_template,
                new_board_name=name,
                keep_cards=keep_cards
            )
        except ValueError as e:
            progress.stop()
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1)

        if not new_board:
            progress.stop()
            console.print("[red]Failed to create board from template[/red]")
            raise typer.Exit(1)

        progress.update(task, description="Getting board info...")

        # Get info about the new board
        board_info = client.get_board_info(new_board)

    console.print(f"\n[green]✓ Created board: {new_board.name}[/green]")
    console.print(f"  URL: {new_board.url}")
    console.print(f"  ID: {new_board.id}")

    if 'lists' in board_info:
        console.print(f"\n  [bold]Lists:[/bold] {', '.join(board_info['lists'])}")
    if 'custom_fields' in board_info and board_info['custom_fields']:
        console.print(f"  [bold]Custom Fields:[/bold] {', '.join(board_info['custom_fields'])}")
    if 'labels' in board_info and board_info['labels']:
        console.print(f"  [bold]Labels:[/bold] {', '.join(board_info['labels'])}")

    # Set as active board if requested
    if set_active:
        config = _load_config()
        if "trello" not in config:
            config["trello"] = {}
        config["trello"]["board_id"] = new_board.id
        config["trello"]["board_name"] = new_board.name
        config["trello"]["enabled"] = True
        _save_config(config)
        console.print(f"\n[green]✓ Set as active board for this project[/green]")
    else:
        console.print(f"\n[dim]To use this board, run:[/dim]")
        console.print(f"  bpsai-pair trello use-board {new_board.id}")


@app.command("list-fields")
def list_fields():
    """List all custom fields on the active board (table format).

    Shows field names, types, and available options for dropdown fields.

    Examples:
        bpsai-pair trello list-fields
    """
    config = _load_config()
    board_id = config.get("trello", {}).get("board_id")

    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    client = get_client()
    client.set_board(board_id)

    fields = client.get_custom_fields()

    if not fields:
        console.print("[yellow]No custom fields found on this board[/yellow]")
        raise typer.Exit(0)

    table = Table(title="Custom Fields")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Options", style="dim")

    for field in fields:
        options = ""
        if field.field_type == "list" and field.options:
            options = ", ".join(field.options.values())
        table.add_row(field.name, field.field_type, options)

    console.print(table)


@app.command("fields")
def fields_cmd(
    board: Optional[str] = typer.Option(None, "--board", "-b", help="Board ID (uses config default if not specified)"),
    refresh: bool = typer.Option(False, "--refresh", help="Force refresh from API"),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Show custom fields and their valid options for a board.

    This command shows all custom fields on the board with their types
    and valid option values. Use this to discover what values can be
    set on cards.

    Examples:
        bpsai-pair trello fields
        bpsai-pair trello fields --json
        bpsai-pair trello fields --refresh
        bpsai-pair trello fields --board abc123
    """
    import json

    from .fields import get_cached_board_fields

    config = _load_config()
    board_id = board or config.get("trello", {}).get("board_id")

    if not board_id:
        console.print("[red]Board ID required. Either:[/red]")
        console.print("  1. Use --board <board-id>")
        console.print("  2. Set trello.board_id in .paircoder/config.yaml")
        console.print("\n[dim]Run 'bpsai-pair trello boards --json' to see available boards.[/dim]")
        raise typer.Exit(1)

    client = get_client()
    client.set_board(board_id)

    fields = get_cached_board_fields(board_id, client, force_refresh=refresh)

    if not fields:
        console.print("[yellow]No custom fields found on this board[/yellow]")
        raise typer.Exit(0)

    if as_json:
        console.print(json.dumps(fields, indent=2))
        return

    # Display fields with options in a readable format
    for field_name, field_data in sorted(fields.items()):
        console.print(f"\n[bold]{field_name}[/bold] ({field_data['type']})")

        if field_data["options"]:
            for opt in sorted(field_data["options"].keys()):
                console.print(f"  • {opt}")
        elif field_data["type"] == "text":
            console.print("  (free text)")
        elif field_data["type"] == "checkbox":
            console.print("  (true/false)")
        elif field_data["type"] == "number":
            console.print("  (numeric value)")
        elif field_data["type"] == "date":
            console.print("  (ISO date format)")

    console.print()  # Final newline


@app.command("set-field")
def set_field(
    card_id: str = typer.Argument(..., help="Card ID or URL"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Set Project field"),
    stack: Optional[str] = typer.Option(None, "--stack", "-s", help="Set Stack field"),
    status: Optional[str] = typer.Option(None, "--status", help="Set Status field"),
    effort: Optional[str] = typer.Option(None, "--effort", "-e", help="Set Effort field"),
    repo_url: Optional[str] = typer.Option(None, "--repo-url", "-r", help="Set Repo URL field"),
    field: Optional[str] = typer.Option(None, "--field", "-f", help="Custom field name"),
    value: Optional[str] = typer.Option(None, "--value", "-v", help="Value for --field"),
):
    """Set custom field values on a Trello card.

    Can set common fields directly with flags, or any field with --field/--value.

    Examples:
        # Set project field
        bpsai-pair trello set-field abc123 --project "Support App"

        # Set multiple fields
        bpsai-pair trello set-field abc123 --project "App" --stack "React" --status "In Progress"

        # Set custom field by name
        bpsai-pair trello set-field abc123 --field "Deployment Tag" --value "v2.1.0"
    """
    config = _load_config()
    board_id = config.get("trello", {}).get("board_id")

    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    # Extract card ID from URL if needed
    if "trello.com" in card_id:
        # URL format: https://trello.com/c/CARD_ID/...
        parts = card_id.split("/")
        for i, part in enumerate(parts):
            if part == "c" and i + 1 < len(parts):
                card_id = parts[i + 1]
                break

    client = get_client()
    client.set_board(board_id)

    # Get the card
    try:
        card = client.client.get_card(card_id)
    except Exception as e:
        console.print(f"[red]Failed to get card: {e}[/red]")
        raise typer.Exit(1)

    # Build field values dict
    field_values = {}
    trello_config = config.get("trello", {})
    custom_fields_config = trello_config.get("custom_fields", {})

    if project:
        field_values[custom_fields_config.get("project", "Project")] = project
    if stack:
        field_values[custom_fields_config.get("stack", "Stack")] = stack
    if status:
        field_values[custom_fields_config.get("status", "Status")] = status
    if effort:
        field_values[custom_fields_config.get("effort", "Effort")] = effort
    if repo_url:
        field_values[custom_fields_config.get("repo_url", "Repo URL")] = repo_url
    if field and value:
        field_values[field] = value

    if not field_values:
        console.print("[yellow]No fields specified. Use --project, --stack, --status, etc.[/yellow]")
        raise typer.Exit(1)

    # Set the fields
    results = client.set_card_custom_fields(card, field_values)

    success_count = sum(1 for v in results.values() if v)
    fail_count = len(results) - success_count

    console.print(f"\n[bold]Card:[/bold] {card.name}")
    for field_name, success in results.items():
        status_icon = "[green]✓[/green]" if success else "[red]✗[/red]"
        console.print(f"  {status_icon} {field_name}: {field_values[field_name]}")

    if fail_count > 0:
        console.print(f"\n[yellow]Some fields may not exist on this board. Run 'bpsai-pair trello list-fields' to see available fields.[/yellow]")


@app.command("apply-defaults")
def apply_defaults(
    card_id: str = typer.Argument(..., help="Card ID or URL"),
):
    """Apply project default values to a Trello card.

    Reads defaults from .paircoder/config.yaml trello.defaults section
    and applies them to the specified card.

    Config example:
        trello:
          defaults:
            project: "Support App"
            stack: "React"
            repo_url: "https://github.com/org/repo"

    Examples:
        bpsai-pair trello apply-defaults abc123
    """
    config = _load_config()
    board_id = config.get("trello", {}).get("board_id")

    if not board_id:
        console.print("[red]No board configured. Run: bpsai-pair trello use-board <id>[/red]")
        raise typer.Exit(1)

    trello_config = config.get("trello", {})
    defaults = trello_config.get("defaults", {})

    if not defaults:
        console.print("[yellow]No defaults configured in .paircoder/config.yaml[/yellow]")
        console.print("\n[dim]Add a defaults section:[/dim]")
        console.print("""
trello:
  defaults:
    project: "Your Project Name"
    stack: "Your Stack"
    repo_url: "https://github.com/..."
""")
        raise typer.Exit(1)

    # Extract card ID from URL if needed
    if "trello.com" in card_id:
        parts = card_id.split("/")
        for i, part in enumerate(parts):
            if part == "c" and i + 1 < len(parts):
                card_id = parts[i + 1]
                break

    client = get_client()
    client.set_board(board_id)

    # Get the card
    try:
        card = client.client.get_card(card_id)
    except Exception as e:
        console.print(f"[red]Failed to get card: {e}[/red]")
        raise typer.Exit(1)

    # Map default keys to custom field names
    custom_fields_config = trello_config.get("custom_fields", {})
    field_mapping = {
        "project": custom_fields_config.get("project", "Project"),
        "stack": custom_fields_config.get("stack", "Stack"),
        "status": custom_fields_config.get("status", "Status"),
        "effort": custom_fields_config.get("effort", "Effort"),
        "repo_url": custom_fields_config.get("repo_url", "Repo URL"),
        "deployment_tag": custom_fields_config.get("deployment_tag", "Deployment Tag"),
    }

    # Build field values from defaults
    field_values = {}
    for key, value in defaults.items():
        field_name = field_mapping.get(key, key)  # Use key directly if not mapped
        field_values[field_name] = value

    # Set the fields
    results = client.set_card_custom_fields(card, field_values)

    success_count = sum(1 for v in results.values() if v)

    console.print(f"\n[bold]Card:[/bold] {card.name}")
    for field_name, success in results.items():
        status_icon = "[green]✓[/green]" if success else "[red]✗[/red]"
        console.print(f"  {status_icon} {field_name}: {field_values[field_name]}")

    console.print(f"\n[green]Applied {success_count}/{len(results)} default fields[/green]")


# Register webhook subcommands
from .webhook_commands import app as webhook_app
app.add_typer(webhook_app, name="webhook")
