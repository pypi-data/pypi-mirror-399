"""
Trello sync module for syncing tasks to Trello cards with custom fields.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging
import re

from .client import TrelloService, EffortMapping
from .templates import CardDescriptionTemplate, CardDescriptionData, should_preserve_description
from .fields import FieldValidator, map_value_to_option, get_default_mappings_for_field
from ..core.constants import extract_task_id_from_card_name

logger = logging.getLogger(__name__)


# ==================== DUE DATE CONFIGURATION ====================

@dataclass
class DueDateConfig:
    """Configuration for calculating due dates from effort levels."""
    # Days to add for each effort level
    effort_days: Dict[str, int] = field(default_factory=lambda: {"S": 1, "M": 2, "L": 4})

    def get_days_for_effort(self, effort: str) -> int:
        """Get the number of days for an effort level.

        Args:
            effort: Effort level (S, M, L) - case insensitive

        Returns:
            Number of days to add, defaults to M (2 days) if unknown
        """
        effort_upper = effort.upper()
        return self.effort_days.get(effort_upper, self.effort_days.get("M", 2))


def calculate_due_date_from_effort(
    effort: str,
    base_date: Optional[datetime] = None,
    config: Optional[DueDateConfig] = None
) -> datetime:
    """Calculate a due date based on effort level.

    Args:
        effort: Effort level (S, M, L)
        base_date: Starting date (defaults to now in UTC)
        config: DueDateConfig instance (uses defaults if not provided)

    Returns:
        Due date as datetime
    """
    if config is None:
        config = DueDateConfig()

    if base_date is None:
        base_date = datetime.now(timezone.utc)

    days = config.get_days_for_effort(effort)
    return base_date + timedelta(days=days)


# BPS Label color mapping
BPS_LABELS = {
    "Frontend": "green",
    "Backend": "blue",
    "Worker/Function": "purple",
    "Deployment": "red",
    "Bug/Issue": "orange",
    "Security/Admin": "yellow",
    "Documentation": "sky",
    "AI/ML": "black",
}

# Task status to Trello Status custom field mapping
# Maps local task status values to Trello Status dropdown options
# Valid BPS board options: Planning, Enqueued, In progress, Testing, Done, Waiting, Blocked
TASK_STATUS_TO_TRELLO_STATUS = {
    "pending": "Planning",
    "ready": "Enqueued",
    "planned": "Planning",
    "in_progress": "In progress",
    "review": "Testing",
    "testing": "Testing",
    "blocked": "Blocked",
    "waiting": "Waiting",
    "done": "Done",
    "deployed": "Done",
}

# Trello Status to task status mapping (reverse of above)
# Maps Status custom field dropdown values back to task status
TRELLO_STATUS_TO_TASK_STATUS = {
    "Planning": "pending",
    "Enqueued": "ready",
    "In progress": "in_progress",
    "Testing": "review",
    "Done": "done",
    "Waiting": "blocked",
    "Blocked": "blocked",
    "Not sure": "blocked",
}

# Keywords to infer labels from task title/tags
STACK_KEYWORDS = {
    "Frontend": ["frontend", "ui", "react", "vue", "angular", "css", "html", "component"],
    "Backend": ["backend", "api", "flask", "fastapi", "django", "server", "endpoint"],
    "Worker/Function": ["worker", "function", "lambda", "celery", "task", "job", "queue", "cli"],
    "Deployment": ["deploy", "docker", "k8s", "kubernetes", "ci", "cd", "pipeline"],
    "Bug/Issue": ["bug", "fix", "issue", "error", "crash"],
    "Security/Admin": ["security", "auth", "admin", "permission", "role", "soc2"],
    "Documentation": ["doc", "readme", "guide", "tutorial", "comment"],
    "AI/ML": ["ai", "ml", "model", "llm", "claude", "gpt", "embedding"],
}

# Map inferred labels to valid Stack dropdown values
# Valid Stack values: React, Flask, Worker/Function, Infra, Collection
LABEL_TO_STACK_MAPPING = {
    "Frontend": "React",
    "Backend": "Flask",
    "Worker/Function": "Worker/Function",
    "Deployment": "Infra",
    "Bug/Issue": None,  # Not a stack, just a label
    "Security/Admin": "Infra",
    "Documentation": "Collection",
    "AI/ML": "Worker/Function",
}


@dataclass
class TaskSyncConfig:
    """Configuration for syncing tasks to Trello."""
    # Custom field mappings
    project_field: str = "Project"
    stack_field: str = "Stack"
    status_field: str = "Status"
    effort_field: str = "Effort"
    repo_url_field: str = "Repo URL"
    deployment_tag_field: str = "Deployment Tag"

    # Default values for custom fields
    default_project: Optional[str] = None  # e.g., "PairCoder"
    default_stack: Optional[str] = None  # e.g., "Worker/Function"
    default_repo_url: Optional[str] = None  # e.g., "https://github.com/org/repo"

    # Effort mapping ranges
    effort_mapping: EffortMapping = field(default_factory=EffortMapping)

    # Status mapping (task status -> Trello Status dropdown value)
    status_mapping: Dict[str, str] = field(default_factory=lambda: TASK_STATUS_TO_TRELLO_STATUS.copy())

    # Whether to create missing labels
    create_missing_labels: bool = True

    # Default list for new cards (Intake/Backlog for Butler workflow)
    default_list: str = "Intake/Backlog"

    # Card description template (None uses default BPS template)
    card_template: Optional[str] = None

    # Whether to preserve manually edited card descriptions
    preserve_manual_edits: bool = True

    # Whether to use Butler workflow (set Status field instead of moving cards)
    use_butler_workflow: bool = True

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "TaskSyncConfig":
        """Create TaskSyncConfig from a config dictionary.

        Expected config structure (from config.yaml):
        ```yaml
        trello:
          sync:
            custom_fields:
              project: "Project"
              stack: "Stack"
              status: "Status"
              effort: "Effort"
            effort_mapping:
              S: [0, 25]
              M: [26, 50]
              L: [51, 100]
            default_list: "Backlog"
            create_missing_labels: true
            preserve_manual_edits: true
        ```

        Args:
            config: Configuration dictionary (usually from config.yaml's trello.sync section)

        Returns:
            Configured TaskSyncConfig instance
        """
        sync_config = config.get("sync", {})
        custom_fields = sync_config.get("custom_fields", {})

        # Parse effort mapping if provided
        effort_config = sync_config.get("effort_mapping", {})
        if effort_config:
            effort_mapping = EffortMapping(
                small=(effort_config.get("S", [0, 25])[0], effort_config.get("S", [0, 25])[1]),
                medium=(effort_config.get("M", [26, 50])[0], effort_config.get("M", [26, 50])[1]),
                large=(effort_config.get("L", [51, 100])[0], effort_config.get("L", [51, 100])[1]),
            )
        else:
            effort_mapping = EffortMapping()

        # Parse status mapping if provided
        status_config = sync_config.get("status_mapping", {})
        if status_config:
            status_mapping = status_config.copy()
        else:
            status_mapping = TASK_STATUS_TO_TRELLO_STATUS.copy()

        # Get default values from config (trello.defaults section)
        defaults = config.get("defaults", {})

        return cls(
            project_field=custom_fields.get("project", "Project"),
            stack_field=custom_fields.get("stack", "Stack"),
            status_field=custom_fields.get("status", "Status"),
            effort_field=custom_fields.get("effort", "Effort"),
            repo_url_field=custom_fields.get("repo_url", "Repo URL"),
            deployment_tag_field=custom_fields.get("deployment_tag", "Deployment Tag"),
            default_project=defaults.get("project"),  # e.g., "PairCoder"
            default_stack=defaults.get("stack"),  # e.g., "Worker/Function"
            default_repo_url=defaults.get("repo_url"),  # e.g., "https://github.com/org/repo"
            effort_mapping=effort_mapping,
            status_mapping=status_mapping,
            create_missing_labels=sync_config.get("create_missing_labels", True),
            default_list=sync_config.get("default_list", "Intake/Backlog"),
            card_template=sync_config.get("card_template"),
            preserve_manual_edits=sync_config.get("preserve_manual_edits", True),
            use_butler_workflow=sync_config.get("use_butler_workflow", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to config dictionary format.

        Returns:
            Dictionary suitable for saving to config.yaml
        """
        result = {
            "sync": {
                "custom_fields": {
                    "project": self.project_field,
                    "stack": self.stack_field,
                    "status": self.status_field,
                    "effort": self.effort_field,
                    "repo_url": self.repo_url_field,
                    "deployment_tag": self.deployment_tag_field,
                },
                "effort_mapping": {
                    "S": list(self.effort_mapping.small),
                    "M": list(self.effort_mapping.medium),
                    "L": list(self.effort_mapping.large),
                },
                "status_mapping": self.status_mapping.copy(),
                "default_list": self.default_list,
                "create_missing_labels": self.create_missing_labels,
                "preserve_manual_edits": self.preserve_manual_edits,
                "use_butler_workflow": self.use_butler_workflow,
            }
        }
        # Add defaults section if any defaults are set
        if self.default_project or self.default_stack or self.default_repo_url:
            result["defaults"] = {}
            if self.default_project:
                result["defaults"]["project"] = self.default_project
            if self.default_stack:
                result["defaults"]["stack"] = self.default_stack
            if self.default_repo_url:
                result["defaults"]["repo_url"] = self.default_repo_url
        return result

    def get_trello_status(self, task_status: str) -> str:
        """Map task status to Trello Status custom field value.

        Args:
            task_status: Local task status (e.g., 'pending', 'in_progress')

        Returns:
            Trello Status dropdown value (e.g., 'Enqueued', 'In Progress')
        """
        return self.status_mapping.get(task_status, task_status.replace('_', ' ').title())


@dataclass
class TaskData:
    """Task data for syncing to Trello."""
    id: str
    title: str
    description: str = ""
    status: str = "pending"
    priority: str = "P1"
    complexity: int = 50
    tags: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    checked_criteria: List[str] = field(default_factory=list)  # Items that are checked
    plan_title: Optional[str] = None
    due_date: Optional[datetime] = None

    @classmethod
    def from_task(cls, task: Any) -> "TaskData":
        """Create TaskData from a Task object."""
        # Extract acceptance criteria from task body if present
        acceptance_criteria = []
        checked_criteria = []
        if hasattr(task, 'body') and task.body:
            # Look for checklist items in body
            for line in task.body.split('\n'):
                line = line.strip()
                if line.startswith('- [x]') or line.startswith('- [X]'):
                    # Checked item - remove checkbox prefix
                    item = re.sub(r'^- \[[xX]\]\s*', '', line)
                    acceptance_criteria.append(item)
                    checked_criteria.append(item)
                elif line.startswith('- [ ]'):
                    # Unchecked item - remove checkbox prefix
                    item = re.sub(r'^- \[ \]\s*', '', line)
                    acceptance_criteria.append(item)

        return cls(
            id=task.id,
            title=task.title,
            description=getattr(task, 'body', '') or '',
            status=task.status,
            priority=getattr(task, 'priority', 'P1'),
            complexity=getattr(task, 'complexity', 50),
            tags=getattr(task, 'tags', []) or [],
            acceptance_criteria=acceptance_criteria,
            checked_criteria=checked_criteria,
            plan_title=getattr(task, 'plan', None),
            due_date=getattr(task, 'due_date', None),
        )


class TrelloSyncManager:
    """Manages syncing tasks to Trello with custom fields."""

    def __init__(self, service: TrelloService, config: Optional[TaskSyncConfig] = None):
        """Initialize sync manager.

        Args:
            service: Configured TrelloService
            config: Sync configuration (uses defaults if not provided)
        """
        self.service = service
        self.config = config or TaskSyncConfig()
        self._field_validator: Optional[FieldValidator] = None

    @property
    def field_validator(self) -> Optional[FieldValidator]:
        """Lazy-load field validator for the board."""
        if self._field_validator is None:
            try:
                if self.service.board:
                    self._field_validator = FieldValidator(
                        self.service.board.id,
                        self.service,
                        use_cache=True
                    )
            except (AttributeError, TypeError):
                # Handle mock objects or missing board
                pass
        return self._field_validator

    def validate_and_map_custom_fields(
        self,
        custom_fields: Dict[str, str]
    ) -> Dict[str, str]:
        """Validate and map custom field values before setting them.

        This method:
        1. Validates each field value against the board's actual options
        2. Maps aliases (e.g., 'cli' -> 'Worker/Function') to valid values
        3. Logs warnings for invalid values that will be skipped

        Args:
            custom_fields: Dict of field_name -> value to validate

        Returns:
            Dict of validated field_name -> value (invalid fields removed)
        """
        if not self.field_validator:
            logger.warning("No field validator available, skipping validation")
            return custom_fields

        validated = {}
        for field_name, value in custom_fields.items():
            is_valid, mapped_value, option_id, error = self.field_validator.map_and_validate(
                field_name, value
            )
            if error:
                logger.warning(f"Skipping invalid field: {error}")
            elif mapped_value is not None:
                validated[field_name] = mapped_value
                if mapped_value != value:
                    logger.debug(f"Mapped {field_name}: '{value}' -> '{mapped_value}'")
            else:
                # For non-dropdown fields, keep original value
                validated[field_name] = value

        return validated

    def infer_label(self, task: TaskData) -> Optional[str]:
        """Infer label category from task title and tags.

        Args:
            task: Task data

        Returns:
            Label name (e.g., "Frontend", "Documentation") or None
        """
        # Check tags first
        for tag in task.tags:
            tag_lower = tag.lower()
            for label, keywords in STACK_KEYWORDS.items():
                if tag_lower in keywords or any(kw in tag_lower for kw in keywords):
                    return label

        # Check title
        title_lower = task.title.lower()
        for label, keywords in STACK_KEYWORDS.items():
            if any(kw in title_lower for kw in keywords):
                return label

        return None

    def label_to_stack(self, label: Optional[str]) -> Optional[str]:
        """Convert an inferred label to a valid Stack dropdown value.

        Args:
            label: Inferred label name (e.g., "Documentation")

        Returns:
            Valid Stack dropdown value (e.g., "Collection") or None
        """
        if not label:
            return None
        return LABEL_TO_STACK_MAPPING.get(label)

    # Keep old method name for backwards compatibility
    def infer_stack(self, task: TaskData) -> Optional[str]:
        """Infer valid Stack dropdown value from task.

        Args:
            task: Task data

        Returns:
            Valid Stack dropdown value or None
        """
        label = self.infer_label(task)
        return self.label_to_stack(label)

    def build_card_description(self, task: TaskData) -> str:
        """Build BPS-formatted card description.

        Args:
            task: Task data

        Returns:
            Formatted description string
        """
        # Use the CardDescriptionTemplate for proper BPS formatting
        return CardDescriptionTemplate.from_task_data(
            task,
            template=self.config.card_template
        )

    def should_update_description(self, existing_desc: str) -> bool:
        """Check if we should update an existing card description.

        Args:
            existing_desc: Current card description

        Returns:
            True if we should update, False to preserve manual edits
        """
        if not self.config.preserve_manual_edits:
            return True

        return not should_preserve_description(existing_desc)

    def ensure_bps_labels(self) -> Dict[str, bool]:
        """Ensure all BPS labels exist on the board.

        Returns:
            Dict mapping label names to creation success
        """
        results = {}

        if not self.config.create_missing_labels:
            return results

        for label_name, color in BPS_LABELS.items():
            label = self.service.ensure_label_exists(label_name, color)
            results[label_name] = label is not None

        return results

    def sync_task_to_card(
        self,
        task: TaskData,
        list_name: Optional[str] = None,
        update_existing: bool = True
    ) -> Optional[Any]:
        """Sync a task to a Trello card.

        Args:
            task: Task data to sync
            list_name: Target list name (uses config default if not provided)
            update_existing: Whether to update existing cards or skip

        Returns:
            Card object or None if failed
        """
        target_list = list_name or self.config.default_list

        # Check if card already exists
        existing_card, existing_list = self.service.find_card_with_prefix(task.id)

        if existing_card:
            if not update_existing:
                logger.info(f"Card for {task.id} already exists, skipping")
                return existing_card

            # Update existing card
            return self._update_card(existing_card, task)
        else:
            # Create new card
            return self._create_card(task, target_list)

    def _create_card(self, task: TaskData, list_name: str) -> Optional[Any]:
        """Create a new Trello card for a task.

        Args:
            task: Task data
            list_name: Target list name

        Returns:
            Created card or None
        """
        # Build card name with task ID prefix
        card_name = f"[{task.id}] {task.title}"
        description = self.build_card_description(task)

        # Build custom fields
        custom_fields = {}

        # Project field - use config default if set, otherwise plan_title
        project = self.config.default_project or task.plan_title
        if project:
            custom_fields[self.config.project_field] = project

        # Stack field - use config default if set, otherwise infer from task
        stack = self.config.default_stack or self.infer_stack(task)
        if stack:
            custom_fields[self.config.stack_field] = stack

        # Status field - use proper mapping for Butler workflow
        custom_fields[self.config.status_field] = self.config.get_trello_status(task.status)

        # Repo URL field - use config default if set
        if self.config.default_repo_url:
            custom_fields[self.config.repo_url_field] = self.config.default_repo_url

        # Validate and map custom field values before setting
        validated_fields = self.validate_and_map_custom_fields(custom_fields)

        # Create card
        card = self.service.create_card_with_custom_fields(
            list_name=list_name,
            name=card_name,
            desc=description,
            custom_fields=validated_fields
        )

        if not card:
            return None

        # Set effort field (separate because it uses complexity mapping)
        self.service.set_effort_field(card, task.complexity, self.config.effort_field)

        # Add labels (use infer_label for label names, not Stack dropdown values)
        label = self.infer_label(task)
        if label:
            self.service.add_label_to_card(card, label)

        # Add labels from tags
        for tag in task.tags:
            tag_title = tag.title()
            if tag_title in BPS_LABELS:
                self.service.add_label_to_card(card, tag_title)

        # Create acceptance criteria checklist if task has acceptance criteria
        if task.acceptance_criteria:
            self._sync_checklist(card, task.acceptance_criteria, task.checked_criteria)

        # Set due date - use explicit date if provided, otherwise calculate from effort
        due_date = task.due_date
        if due_date is None:
            # Calculate due date from effort/complexity
            effort = self.config.effort_mapping.get_effort(task.complexity)
            due_date = calculate_due_date_from_effort(effort)
        self.service.set_due_date(card, due_date)

        logger.info(f"Created card for {task.id}: {card_name}")
        return card

    def _update_card(self, card: Any, task: TaskData) -> Any:
        """Update an existing card with task data.

        Args:
            card: Existing Trello card
            task: Task data

        Returns:
            Updated card
        """
        # Check if we should update the description or preserve manual edits
        existing_desc = getattr(card, 'description', '') or ''
        if self.should_update_description(existing_desc):
            description = self.build_card_description(task)
            card.set_description(description)
        else:
            logger.info(f"Preserving manual edits for {task.id}")

        # Update custom fields
        custom_fields = {}

        # Project field - use config default if set, otherwise plan_title
        project = self.config.default_project or task.plan_title
        if project:
            custom_fields[self.config.project_field] = project

        # Stack field - use config default if set, otherwise infer from task
        stack = self.config.default_stack or self.infer_stack(task)
        if stack:
            custom_fields[self.config.stack_field] = stack

        # Status field - use proper mapping for Butler workflow
        custom_fields[self.config.status_field] = self.config.get_trello_status(task.status)

        # Repo URL field - use config default if set
        if self.config.default_repo_url:
            custom_fields[self.config.repo_url_field] = self.config.default_repo_url

        # Validate and map custom field values before setting
        validated_fields = self.validate_and_map_custom_fields(custom_fields)
        self.service.set_card_custom_fields(card, validated_fields)
        self.service.set_effort_field(card, task.complexity, self.config.effort_field)

        # Add labels (use infer_label for label names, not Stack dropdown values)
        label = self.infer_label(task)
        if label:
            self.service.add_label_to_card(card, label)

        for tag in task.tags:
            tag_title = tag.title()
            if tag_title in BPS_LABELS:
                self.service.add_label_to_card(card, tag_title)

        # Sync acceptance criteria checklist
        if task.acceptance_criteria:
            self._sync_checklist(card, task.acceptance_criteria, task.checked_criteria)

        # Sync due date
        if task.due_date is not None:
            self.service.set_due_date(card, task.due_date)

        logger.info(f"Updated card for {task.id}")
        return card

    def _sync_checklist(
        self,
        card: Any,
        acceptance_criteria: List[str],
        checked_criteria: Optional[List[str]] = None,
        checklist_name: str = "Acceptance Criteria"
    ) -> Optional[Dict[str, Any]]:
        """Sync acceptance criteria to a card checklist.

        Args:
            card: Trello card object
            acceptance_criteria: List of acceptance criteria strings
            checked_criteria: List of criteria that should be checked
            checklist_name: Name for the checklist

        Returns:
            Checklist dict or None if failed
        """
        if not acceptance_criteria:
            return None

        checked_criteria = checked_criteria or []

        # Use service.ensure_checklist to create or update
        return self.service.ensure_checklist(
            card=card,
            name=checklist_name,
            items=acceptance_criteria,
            checked_items=checked_criteria
        )

    def sync_tasks(
        self,
        tasks: List[TaskData],
        list_name: Optional[str] = None,
        update_existing: bool = True
    ) -> Dict[str, Optional[Any]]:
        """Sync multiple tasks to Trello cards.

        Args:
            tasks: List of task data
            list_name: Target list name
            update_existing: Whether to update existing cards

        Returns:
            Dict mapping task IDs to cards (or None if failed)
        """
        # Ensure BPS labels exist
        self.ensure_bps_labels()

        results = {}
        for task in tasks:
            card = self.sync_task_to_card(task, list_name, update_existing)
            results[task.id] = card

        return results


def create_sync_manager(
    api_key: str,
    token: str,
    board_id: str,
    config: Optional[TaskSyncConfig] = None
) -> TrelloSyncManager:
    """Create a configured TrelloSyncManager.

    Args:
        api_key: Trello API key
        token: Trello API token
        board_id: Board ID to sync to
        config: Sync configuration

    Returns:
        Configured TrelloSyncManager
    """
    service = TrelloService(api_key, token)
    service.set_board(board_id)

    return TrelloSyncManager(service, config)


# List name to status mapping for reverse sync
# Includes both spaced and non-spaced variants for flexible matching
LIST_TO_STATUS = {
    # Backlog/Pending variants
    "Intake/Backlog": "pending",
    "Intake / Backlog": "pending",
    "Backlog": "pending",
    "Planned/Ready": "pending",
    "Planned / Ready": "pending",
    "Ready": "pending",
    # In Progress variants
    "In Progress": "in_progress",
    # Review variants
    "Review/Testing": "review",
    "Review / Testing": "review",
    "In Review": "review",
    # Done variants
    "Deployed/Done": "done",
    "Deployed / Done": "done",
    "Done": "done",
    # Blocked variants
    "Issues/Tech Debt": "blocked",
    "Issues / Tech Debt": "blocked",
    "Blocked": "blocked",
}


def _normalize_list_name(name: str) -> str:
    """Normalize list name for matching (remove spaces around slashes)."""
    import re
    return re.sub(r'\s*/\s*', '/', name).strip()


def _get_status_for_list_flexible(list_name: str) -> Optional[str]:
    """Get status for a list name with flexible matching.
    
    Args:
        list_name: Trello list name
        
    Returns:
        Status string or None
    """
    # Try exact match first
    if list_name in LIST_TO_STATUS:
        return LIST_TO_STATUS[list_name]
    
    # Try normalized match
    normalized = _normalize_list_name(list_name)
    for key, status in LIST_TO_STATUS.items():
        if _normalize_list_name(key) == normalized:
            return status
    
    # Try pattern matching
    list_lower = list_name.lower()
    if "done" in list_lower or "deployed" in list_lower:
        return "done"
    if "progress" in list_lower:
        return "in_progress"
    if "review" in list_lower or "testing" in list_lower:
        return "review"
    if "blocked" in list_lower or "issue" in list_lower:
        return "blocked"
    if "backlog" in list_lower or "intake" in list_lower or "ready" in list_lower:
        return "pending"
    
    return None


@dataclass
class SyncConflict:
    """Represents a sync conflict between Trello and local."""
    task_id: str
    field: str
    local_value: Any
    trello_value: Any
    resolution: str = "trello_wins"  # or "local_wins", "skip"


@dataclass
class SyncResult:
    """Result of a sync operation."""
    task_id: str
    action: str  # "updated", "skipped", "conflict", "error"
    changes: Dict[str, Any] = field(default_factory=dict)
    conflicts: List[SyncConflict] = field(default_factory=list)
    error: Optional[str] = None


class TrelloToLocalSync:
    """Syncs changes from Trello back to local task files."""

    def __init__(self, service: TrelloService, tasks_dir: Path):
        """Initialize the reverse sync manager.

        Args:
            service: TrelloService instance with board set
            tasks_dir: Path to .paircoder/tasks directory
        """
        self.service = service
        self.tasks_dir = tasks_dir
        self._task_parser = None

    @property
    def task_parser(self):
        """Lazy load TaskParser."""
        if self._task_parser is None:
            from ..planning.parser import TaskParser
            self._task_parser = TaskParser(self.tasks_dir)
        return self._task_parser

    def extract_task_id(self, card_name: str) -> Optional[str]:
        """Extract task ID from card name like '[TASK-066] Title' or '[T18.1] Title'.

        Args:
            card_name: Card name with potential task ID prefix

        Returns:
            Task ID or None if not found
        """
        return extract_task_id_from_card_name(card_name)

    def get_list_status(self, list_name: str) -> Optional[str]:
        """Map Trello list name to task status.

        Args:
            list_name: Trello list name

        Returns:
            Task status string or None if no mapping
        """
        return _get_status_for_list_flexible(list_name)

    def _sync_checklist_to_task(
        self,
        card: Any,
        task: Any,
        checklist_name: str = "Acceptance Criteria"
    ) -> Optional[Dict[str, Any]]:
        """Sync checklist state from Trello card back to task body.

        Updates checkbox items in the task body based on Trello checklist state.

        Args:
            card: Trello card object
            task: Task object
            checklist_name: Name of the checklist to sync

        Returns:
            Dict with changes made, or None if no changes
        """
        # Get the checklist from the card
        checklist = self.service.get_checklist_by_name(card, checklist_name)
        if not checklist:
            return None

        # Build a map of item name -> checked state
        checklist_state = {}
        for item in checklist.get('items', []):
            item_name = item.get('name', '').strip()
            item_checked = item.get('checked', False)
            checklist_state[item_name] = item_checked

        if not checklist_state:
            return None

        # Get the task body
        body = getattr(task, 'body', '') or ''
        if not body:
            return None

        # Track changes
        changes = {"items_updated": []}
        new_lines = []
        body_changed = False

        for line in body.split('\n'):
            stripped = line.strip()

            # Check if this is a checkbox line
            if stripped.startswith('- [ ]') or stripped.startswith('- [x]') or stripped.startswith('- [X]'):
                # Extract the item text
                item_text = re.sub(r'^- \[[ xX]\]\s*', '', stripped)

                # Check if this item is in our checklist
                if item_text in checklist_state:
                    is_checked_in_trello = checklist_state[item_text]
                    is_checked_locally = stripped.startswith('- [x]') or stripped.startswith('- [X]')

                    if is_checked_in_trello != is_checked_locally:
                        # Update the checkbox state
                        # Preserve original indentation
                        indent = line[:len(line) - len(line.lstrip())]
                        if is_checked_in_trello:
                            new_line = f"{indent}- [x] {item_text}"
                        else:
                            new_line = f"{indent}- [ ] {item_text}"
                        new_lines.append(new_line)
                        changes["items_updated"].append({
                            "item": item_text,
                            "from": "checked" if is_checked_locally else "unchecked",
                            "to": "checked" if is_checked_in_trello else "unchecked"
                        })
                        body_changed = True
                        continue

            new_lines.append(line)

        # Update task body if changed
        if body_changed:
            task.body = '\n'.join(new_lines)
            return changes

        return None

    def sync_card_to_task(self, card: Any, detect_conflicts: bool = True) -> SyncResult:
        """Sync a single Trello card back to local task.

        Args:
            card: Trello card object
            detect_conflicts: Whether to detect and report conflicts

        Returns:
            SyncResult with details of the sync operation
        """
        card_name = card.name
        task_id = self.extract_task_id(card_name)

        if not task_id:
            return SyncResult(
                task_id="unknown",
                action="skipped",
                error=f"Could not extract task ID from: {card_name}"
            )

        # Load local task
        task = self.task_parser.get_task_by_id(task_id)
        if not task:
            return SyncResult(
                task_id=task_id,
                action="skipped",
                error=f"Task not found locally: {task_id}"
            )

        changes = {}
        conflicts = []

        # Get card's current list
        list_name = card.get_list().name if hasattr(card, 'get_list') else None
        if list_name:
            new_status = self.get_list_status(list_name)
            if new_status:
                old_status = task.status.value if hasattr(task.status, 'value') else str(task.status)
                if old_status != new_status:
                    if detect_conflicts:
                        conflicts.append(SyncConflict(
                            task_id=task_id,
                            field="status",
                            local_value=old_status,
                            trello_value=new_status,
                            resolution="trello_wins"
                        ))
                    changes["status"] = {"from": old_status, "to": new_status}

                    # Apply the change (Trello wins for status)
                    from ..planning.models import TaskStatus
                    task.status = TaskStatus(new_status)

        # Check due date if present
        if hasattr(card, 'due_date') and card.due_date:
            card_due = card.due_date
            task_due = getattr(task, 'due_date', None)
            if card_due != task_due:
                changes["due_date"] = {"from": task_due, "to": card_due}
                if hasattr(task, 'due_date'):
                    task.due_date = card_due

        # Sync checklist state back to task body
        checklist_changes = self._sync_checklist_to_task(card, task)
        if checklist_changes:
            changes["checklist"] = checklist_changes

        # Save task if there were changes
        if changes:
            try:
                self.task_parser.save(task)
                return SyncResult(
                    task_id=task_id,
                    action="updated",
                    changes=changes,
                    conflicts=conflicts
                )
            except Exception as e:
                return SyncResult(
                    task_id=task_id,
                    action="error",
                    error=str(e)
                )

        return SyncResult(
            task_id=task_id,
            action="skipped",
            changes={}
        )

    def sync_all_cards(self, list_filter: Optional[List[str]] = None) -> List[SyncResult]:
        """Sync all cards from Trello board to local tasks.

        Args:
            list_filter: Optional list of list names to sync from

        Returns:
            List of SyncResults for each card processed
        """
        results = []

        # Get all cards from board
        try:
            cards = self.service.board.get_cards()
        except Exception as e:
            logger.error(f"Failed to get cards from board: {e}")
            return [SyncResult(task_id="board", action="error", error=str(e))]

        for card in cards:
            # Filter by list if specified
            if list_filter:
                try:
                    card_list = card.get_list()
                    if card_list.name not in list_filter:
                        continue
                except Exception:
                    continue

            # Skip cards without task IDs
            task_id = self.extract_task_id(card.name)
            if not task_id:
                continue

            result = self.sync_card_to_task(card)
            results.append(result)

        return results

    def get_sync_preview(self) -> List[Dict[str, Any]]:
        """Preview what would be synced without making changes.

        Returns:
            List of dicts describing potential changes
        """
        preview = []

        try:
            cards = self.service.board.get_cards()
        except Exception as e:
            logger.error(f"Failed to get cards: {e}")
            return []

        for card in cards:
            task_id = self.extract_task_id(card.name)
            if not task_id:
                continue

            task = self.task_parser.get_task_by_id(task_id)
            if not task:
                preview.append({
                    "task_id": task_id,
                    "card_name": card.name,
                    "action": "skip",
                    "reason": "Task not found locally"
                })
                continue

            # Check for status difference
            try:
                list_name = card.get_list().name
                trello_status = self.get_list_status(list_name)
                local_status = task.status.value if hasattr(task.status, 'value') else str(task.status)

                if trello_status and trello_status != local_status:
                    preview.append({
                        "task_id": task_id,
                        "card_name": card.name,
                        "action": "update",
                        "field": "status",
                        "from": local_status,
                        "to": trello_status
                    })
                else:
                    preview.append({
                        "task_id": task_id,
                        "card_name": card.name,
                        "action": "skip",
                        "reason": "No changes"
                    })
            except Exception as e:
                preview.append({
                    "task_id": task_id,
                    "card_name": card.name,
                    "action": "error",
                    "reason": str(e)
                })

        return preview


def create_reverse_sync(
    api_key: str,
    token: str,
    board_id: str,
    tasks_dir: Path
) -> TrelloToLocalSync:
    """Create a TrelloToLocalSync instance.

    Args:
        api_key: Trello API key
        token: Trello API token
        board_id: Board ID to sync from
        tasks_dir: Path to .paircoder/tasks directory

    Returns:
        Configured TrelloToLocalSync instance
    """
    service = TrelloService(api_key, token)
    service.set_board(board_id)
    return TrelloToLocalSync(service, tasks_dir)
