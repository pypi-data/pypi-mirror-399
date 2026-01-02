"""
Agent handoff protocol for context transfer between AI coding agents.

Provides packaging and unpacking of context bundles for seamless
task delegation across agent boundaries (Claude, Codex, Cursor, etc.).

This module includes:
- HandoffPackage: Basic handoff data structure
- EnhancedHandoffPackage: Extended structure with chain tracking
- HandoffChain: Track sequence of handoffs for debugging
- HandoffSerializer: Save/load handoffs to disk
- prepare_handoff(): Create handoff from current state
- receive_handoff(): Receive and parse handoff from another agent
"""

from __future__ import annotations

import json
import logging
import tarfile
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Literal, Optional, Tuple, Union

logger = logging.getLogger(__name__)


AgentType = Literal["claude", "codex", "cursor", "generic"]


@dataclass
class HandoffPackage:
    """Represents a packaged context bundle for agent handoff."""

    task_id: str
    source_agent: AgentType
    target_agent: AgentType
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    token_estimate: int = 0
    files_included: list[str] = field(default_factory=list)
    conversation_summary: str = ""
    task_description: str = ""
    current_state: str = ""
    instructions: str = ""

    def to_metadata(self) -> dict[str, Any]:
        """Convert to metadata dictionary for JSON serialization."""
        return {
            "version": "1.0",
            "task_id": self.task_id,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "created_at": self.created_at.isoformat(),
            "token_estimate": self.token_estimate,
            "files_included": self.files_included,
            "conversation_summary": self.conversation_summary,
        }

    def generate_handoff_md(self) -> str:
        """Generate HANDOFF.md content for the receiving agent."""
        return f"""# Agent Handoff: {self.task_id}

> **From:** {self.source_agent}
> **To:** {self.target_agent}
> **Created:** {self.created_at.strftime('%Y-%m-%d %H:%M UTC')}

## Task

{self.task_description}

## Current State

{self.current_state}

## Key Files

{self._format_files_list()}

## Instructions

{self.instructions}

## Constraints

- **Token budget:** ~{self.token_estimate} tokens
- **Scope:** Complete the specific task described above
- **Do not:** Make changes outside the scope of this task

## Conversation Summary

{self.conversation_summary or "No prior conversation context."}
"""

    def _format_files_list(self) -> str:
        """Format the files list for markdown."""
        if not self.files_included:
            return "No specific files included."
        return "\n".join(f"- `{f}`" for f in self.files_included)


class HandoffManager:
    """
    Manages creation and extraction of handoff packages.

    Handles context packaging for agent transfers, including
    agent-specific formatting and token estimation.
    """

    # Token estimates per character (rough approximation)
    CHARS_PER_TOKEN = 4

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the handoff manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path.cwd()

    def pack(
        self,
        task_id: str,
        target_agent: AgentType = "generic",
        source_agent: AgentType = "claude",
        include_files: Optional[list[Path]] = None,
        exclude_patterns: Optional[list[str]] = None,
        conversation_summary: str = "",
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Create a handoff package for the specified task.

        Args:
            task_id: ID of the task being handed off
            target_agent: Target agent type
            source_agent: Source agent type
            include_files: Specific files to include
            exclude_patterns: Patterns to exclude
            conversation_summary: Summary of work done
            output_path: Path for output file

        Returns:
            Path to the created handoff package
        """
        exclude_patterns = exclude_patterns or [
            "__pycache__",
            ".git",
            "node_modules",
            ".venv",
            "*.pyc",
        ]

        # Load task details
        task_info = self._load_task(task_id)

        # Determine files to include
        files_to_include = include_files or self._detect_relevant_files(task_id)

        # Calculate token estimate
        token_estimate = self._estimate_tokens(files_to_include)

        # Create package
        package = HandoffPackage(
            task_id=task_id,
            source_agent=source_agent,
            target_agent=target_agent,
            token_estimate=token_estimate,
            files_included=[str(f) for f in files_to_include],
            conversation_summary=conversation_summary,
            task_description=task_info.get("description", ""),
            current_state=task_info.get("state", ""),
            instructions=self._generate_instructions(target_agent, task_info),
        )

        # Determine output path
        if output_path is None:
            output_path = self.project_root / f"handoff-{task_id}-{target_agent}.tgz"

        # Create the tarball
        self._create_tarball(package, files_to_include, output_path)

        logger.info(
            f"Created handoff package: {output_path} "
            f"({token_estimate} tokens, {len(files_to_include)} files)"
        )

        return output_path

    def unpack(
        self,
        package_path: Path,
        target_dir: Optional[Path] = None,
    ) -> HandoffPackage:
        """
        Extract and validate a handoff package.

        Args:
            package_path: Path to the handoff package
            target_dir: Directory to extract into

        Returns:
            HandoffPackage with metadata
        """
        if target_dir is None:
            target_dir = self.project_root / ".paircoder" / "incoming"

        target_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(package_path, "r:gz") as tar:
            tar.extractall(target_dir, filter="data")

        # Load metadata
        metadata_path = target_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
        else:
            metadata = {}

        package = HandoffPackage(
            task_id=metadata.get("task_id", "unknown"),
            source_agent=metadata.get("source_agent", "unknown"),
            target_agent=metadata.get("target_agent", "generic"),
            token_estimate=metadata.get("token_estimate", 0),
            files_included=metadata.get("files_included", []),
            conversation_summary=metadata.get("conversation_summary", ""),
        )

        logger.info(f"Unpacked handoff: {package.task_id} from {package.source_agent}")

        return package

    def _load_task(self, task_id: str) -> dict[str, Any]:
        """Load task details from task file."""
        # Search for task file
        task_dirs = [
            self.project_root / ".paircoder" / "tasks",
        ]

        for task_dir in task_dirs:
            if not task_dir.exists():
                continue

            # Search recursively for task file
            for task_file in task_dir.rglob(f"{task_id}*.md"):
                content = task_file.read_text()
                return {
                    "description": self._extract_section(content, "Description", "Objective"),
                    "state": self._extract_section(content, "Current State", "Status"),
                    "acceptance_criteria": self._extract_section(content, "Acceptance Criteria"),
                }

        return {"description": f"Task {task_id}", "state": "In progress"}

    def _extract_section(self, content: str, *section_names: str) -> str:
        """Extract a section from markdown content."""
        for name in section_names:
            marker = f"## {name}"
            if marker in content:
                start = content.find(marker) + len(marker)
                # Find next section or end
                next_section = content.find("\n## ", start)
                if next_section == -1:
                    return content[start:].strip()
                return content[start:next_section].strip()
        return ""

    def _detect_relevant_files(self, task_id: str) -> list[Path]:
        """Auto-detect files relevant to the task."""
        relevant = []

        # Include task file itself
        task_dirs = self.project_root / ".paircoder" / "tasks"
        if task_dirs.exists():
            for task_file in task_dirs.rglob(f"{task_id}*.md"):
                relevant.append(task_file)

        # Include state file
        state_file = self.project_root / ".paircoder" / "context" / "state.md"
        if state_file.exists():
            relevant.append(state_file)

        # Include recently modified files from git
        try:
            import subprocess

            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~5"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        file_path = self.project_root / line
                        if file_path.exists() and file_path not in relevant:
                            relevant.append(file_path)
        except Exception:
            pass

        return relevant[:20]  # Limit to 20 files

    def _estimate_tokens(self, files: list[Path]) -> int:
        """Estimate token count for files."""
        total_chars = 0
        for file_path in files:
            try:
                if file_path.exists() and file_path.is_file():
                    total_chars += len(file_path.read_text())
            except Exception:
                pass

        return total_chars // self.CHARS_PER_TOKEN

    def _generate_instructions(self, target_agent: AgentType, task_info: dict) -> str:
        """Generate agent-specific instructions."""
        base_instructions = task_info.get("acceptance_criteria", "Complete the task as described.")

        agent_specifics = {
            "claude": "Use your skills in `.claude/skills/` if applicable. Update task status when done.",
            "codex": "Follow AGENTS.md conventions. Use full-auto mode for implementation.",
            "cursor": "Work interactively in the IDE. Reference .cursorrules if present.",
            "generic": "Follow project conventions. Update state when done.",
        }

        return f"{base_instructions}\n\n**Agent-specific:** {agent_specifics.get(target_agent, '')}"

    def _create_tarball(
        self,
        package: HandoffPackage,
        files: list[Path],
        output_path: Path,
    ) -> None:
        """Create the handoff tarball."""
        with tarfile.open(output_path, "w:gz") as tar:
            # Add HANDOFF.md
            handoff_content = package.generate_handoff_md().encode("utf-8")
            handoff_info = tarfile.TarInfo(name="HANDOFF.md")
            handoff_info.size = len(handoff_content)
            tar.addfile(handoff_info, BytesIO(handoff_content))

            # Add metadata.json
            metadata_content = json.dumps(package.to_metadata(), indent=2).encode("utf-8")
            metadata_info = tarfile.TarInfo(name="metadata.json")
            metadata_info.size = len(metadata_content)
            tar.addfile(metadata_info, BytesIO(metadata_content))

            # Add context files
            for file_path in files:
                if file_path.exists() and file_path.is_file():
                    try:
                        rel_path = file_path.relative_to(self.project_root)
                        arcname = f"context/{rel_path}"
                        tar.add(file_path, arcname=arcname)
                    except ValueError:
                        # File outside project root
                        tar.add(file_path, arcname=f"context/{file_path.name}")


def _generate_handoff_id() -> str:
    """Generate a unique handoff ID."""
    return f"handoff-{uuid.uuid4().hex[:8]}"


@dataclass
class EnhancedHandoffPackage:
    """
    Enhanced handoff package with structured context for agent transfers.

    Extends the basic HandoffPackage with:
    - Acceptance criteria tracking
    - Work completed/remaining state
    - Chain tracking for debugging multi-hop handoffs
    - Token budget estimation

    Example:
        >>> package = EnhancedHandoffPackage(
        ...     task_id="TASK-001",
        ...     source_agent="planner",
        ...     target_agent="reviewer",
        ...     task_description="Review auth implementation",
        ...     work_completed="Basic auth done",
        ...     remaining_work="OAuth support needed",
        ... )
        >>> context = package.generate_context_markdown()
    """

    # Required fields
    task_id: str
    source_agent: str
    target_agent: str

    # Task context
    task_description: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    files_touched: list[str] = field(default_factory=list)

    # State tracking
    current_state: str = ""
    work_completed: str = ""
    remaining_work: str = ""

    # Resource planning
    token_budget: int = 0

    # Chain tracking
    handoff_id: str = field(default_factory=_generate_handoff_id)
    previous_handoff_id: Optional[str] = None
    chain_depth: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Optional file contents (for inline handoff)
    file_contents: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": "2.0",
            "task_id": self.task_id,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "task_description": self.task_description,
            "acceptance_criteria": self.acceptance_criteria,
            "files_touched": self.files_touched,
            "current_state": self.current_state,
            "work_completed": self.work_completed,
            "remaining_work": self.remaining_work,
            "token_budget": self.token_budget,
            "handoff_id": self.handoff_id,
            "previous_handoff_id": self.previous_handoff_id,
            "chain_depth": self.chain_depth,
            "created_at": self.created_at.isoformat(),
            "file_contents": self.file_contents,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EnhancedHandoffPackage":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)

        return cls(
            task_id=data["task_id"],
            source_agent=data["source_agent"],
            target_agent=data["target_agent"],
            task_description=data.get("task_description", ""),
            acceptance_criteria=data.get("acceptance_criteria", []),
            files_touched=data.get("files_touched", []),
            current_state=data.get("current_state", ""),
            work_completed=data.get("work_completed", ""),
            remaining_work=data.get("remaining_work", ""),
            token_budget=data.get("token_budget", 0),
            handoff_id=data.get("handoff_id", _generate_handoff_id()),
            previous_handoff_id=data.get("previous_handoff_id"),
            chain_depth=data.get("chain_depth", 0),
            created_at=created_at,
            file_contents=data.get("file_contents", {}),
        )

    def generate_context_markdown(self) -> str:
        """
        Generate markdown context for the receiving agent.

        Creates a comprehensive handoff document that includes
        task details, acceptance criteria, work status, and
        chain information for debugging.
        """
        ac_list = "\n".join(f"- {ac}" for ac in self.acceptance_criteria) or "- None specified"
        files_list = "\n".join(f"- `{f}`" for f in self.files_touched) or "- No files tracked"

        chain_info = f"**Chain Depth:** {self.chain_depth}"
        if self.previous_handoff_id:
            chain_info += f"\n**Previous Handoff:** {self.previous_handoff_id}"

        file_contents_section = ""
        if self.file_contents:
            file_contents_section = "\n## File Contents\n\n"
            for path, content in self.file_contents.items():
                ext = Path(path).suffix.lstrip(".")
                file_contents_section += f"### `{path}`\n\n```{ext}\n{content}\n```\n\n"

        return f"""# Agent Handoff: {self.task_id}

> **Handoff ID:** {self.handoff_id}
> **From:** {self.source_agent}
> **To:** {self.target_agent}
> **Created:** {self.created_at.strftime('%Y-%m-%d %H:%M UTC')}

## Task Description

{self.task_description or "No description provided."}

## Acceptance Criteria

{ac_list}

## Current State

{self.current_state or "Not specified."}

## Work Completed

{self.work_completed or "No work completed yet."}

## Remaining Work

{self.remaining_work or "Not specified."}

## Files Touched

{files_list}

## Chain Information

{chain_info}

## Constraints

- **Token budget:** ~{self.token_budget} tokens
- **Scope:** Complete the specific task described above
- **Do not:** Make changes outside the scope of this task
{file_contents_section}"""


@dataclass
class HandoffChain:
    """
    Tracks a sequence of handoffs for a task.

    Useful for debugging multi-agent workflows and understanding
    how context flows between agents.

    Example:
        >>> chain = HandoffChain(task_id="TASK-001")
        >>> chain.add(handoff1)
        >>> chain.add(handoff2)
        >>> print(chain.get_history())
    """

    task_id: str
    handoffs: list[EnhancedHandoffPackage] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def current_depth(self) -> int:
        """Get the current chain depth."""
        return len(self.handoffs)

    def add(self, package: EnhancedHandoffPackage) -> None:
        """Add a handoff to the chain."""
        self.handoffs.append(package)

    def get_history(self) -> list[dict[str, Any]]:
        """Get the handoff history as a list of summaries."""
        return [
            {
                "handoff_id": h.handoff_id,
                "source_agent": h.source_agent,
                "target_agent": h.target_agent,
                "work_completed": h.work_completed,
                "created_at": h.created_at.isoformat(),
            }
            for h in self.handoffs
        ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "handoffs": [h.to_dict() for h in self.handoffs],
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HandoffChain":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)

        chain = cls(
            task_id=data["task_id"],
            created_at=created_at,
        )
        for h_data in data.get("handoffs", []):
            chain.handoffs.append(EnhancedHandoffPackage.from_dict(h_data))

        return chain


class HandoffSerializer:
    """
    Handles saving and loading handoff packages to/from disk.

    Saves to .paircoder/handoffs/{handoff_id}.json by default.

    Example:
        >>> serializer = HandoffSerializer()
        >>> serializer.save(package)
        >>> loaded = serializer.load("handoff-abc123")
    """

    def __init__(self, handoffs_dir: Optional[Path] = None):
        """
        Initialize the serializer.

        Args:
            handoffs_dir: Directory for handoff files
        """
        self.handoffs_dir = handoffs_dir or Path(".paircoder/handoffs")

    def _ensure_dir(self) -> None:
        """Ensure the handoffs directory exists."""
        self.handoffs_dir.mkdir(parents=True, exist_ok=True)

    def save(self, package: EnhancedHandoffPackage) -> Path:
        """
        Save a handoff package to disk.

        Args:
            package: The handoff package to save

        Returns:
            Path to the saved file
        """
        self._ensure_dir()

        path = self.handoffs_dir / f"{package.handoff_id}.json"
        with open(path, "w") as f:
            json.dump(package.to_dict(), f, indent=2)

        logger.info(f"Saved handoff: {package.handoff_id} -> {path}")
        return path

    def load(self, handoff_id: str) -> EnhancedHandoffPackage:
        """
        Load a handoff package from disk.

        Args:
            handoff_id: ID of the handoff to load

        Returns:
            The loaded handoff package

        Raises:
            FileNotFoundError: If handoff file doesn't exist
        """
        path = self.handoffs_dir / f"{handoff_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Handoff not found: {handoff_id}")

        with open(path) as f:
            data = json.load(f)

        return EnhancedHandoffPackage.from_dict(data)

    def list_all(self) -> list[EnhancedHandoffPackage]:
        """
        List all saved handoffs.

        Returns:
            List of all handoff packages
        """
        if not self.handoffs_dir.exists():
            return []

        handoffs = []
        for path in self.handoffs_dir.glob("*.json"):
            if path.name.startswith("chain-"):
                continue  # Skip chain files
            try:
                with open(path) as f:
                    data = json.load(f)
                handoffs.append(EnhancedHandoffPackage.from_dict(data))
            except Exception as e:
                logger.warning(f"Failed to load handoff {path}: {e}")

        return handoffs

    def save_chain(self, chain: HandoffChain) -> Path:
        """
        Save a handoff chain to disk.

        Args:
            chain: The handoff chain to save

        Returns:
            Path to the saved file
        """
        self._ensure_dir()

        path = self.handoffs_dir / f"chain-{chain.task_id}.json"
        with open(path, "w") as f:
            json.dump(chain.to_dict(), f, indent=2)

        logger.info(f"Saved handoff chain: {chain.task_id} -> {path}")
        return path

    def load_chain(self, task_id: str) -> HandoffChain:
        """
        Load or create a handoff chain for a task.

        Args:
            task_id: ID of the task

        Returns:
            The handoff chain (new or existing)
        """
        path = self.handoffs_dir / f"chain-{task_id}.json"

        if path.exists():
            with open(path) as f:
                data = json.load(f)
            chain = HandoffChain.from_dict(data)

            # Deduplicate by handoff_id (in case of concurrent saves)
            seen_ids = set()
            unique_handoffs = []
            for h in chain.handoffs:
                if h.handoff_id not in seen_ids:
                    seen_ids.add(h.handoff_id)
                    unique_handoffs.append(h)
            chain.handoffs = unique_handoffs

            return chain

        # Create new chain from individual handoffs
        chain = HandoffChain(task_id=task_id)
        for handoff in self.list_all():
            if handoff.task_id == task_id:
                chain.add(handoff)

        # Sort by created_at
        chain.handoffs.sort(key=lambda h: h.created_at)

        return chain


def prepare_handoff(
    task_id: str,
    source_agent: str,
    target_agent: str,
    task_description: str = "",
    acceptance_criteria: Optional[list[str]] = None,
    files_touched: Optional[list[str]] = None,
    current_state: str = "",
    work_completed: str = "",
    remaining_work: str = "",
    previous_handoff_id: Optional[str] = None,
    working_dir: Optional[Path] = None,
    include_file_contents: bool = False,
    save: bool = False,
    handoffs_dir: Optional[Path] = None,
) -> EnhancedHandoffPackage:
    """
    Prepare a handoff package for transferring context to another agent.

    This function creates a structured handoff package that captures:
    - Task context and acceptance criteria
    - Work completed and remaining
    - Files involved
    - Chain tracking information

    Args:
        task_id: ID of the task being handed off
        source_agent: Name of the agent creating the handoff
        target_agent: Name of the agent receiving the handoff
        task_description: Description of the task
        acceptance_criteria: List of acceptance criteria
        files_touched: List of file paths involved
        current_state: Current state of the work
        work_completed: Summary of completed work
        remaining_work: Summary of remaining work
        previous_handoff_id: ID of previous handoff in chain
        working_dir: Working directory for file operations
        include_file_contents: Whether to include file contents inline
        save: Whether to save the handoff to disk
        handoffs_dir: Directory for saving handoffs

    Returns:
        EnhancedHandoffPackage ready for transfer

    Example:
        >>> package = prepare_handoff(
        ...     task_id="TASK-001",
        ...     source_agent="planner",
        ...     target_agent="reviewer",
        ...     task_description="Review auth implementation",
        ...     work_completed="OAuth2 support added",
        ...     remaining_work="Code review needed",
        ... )
    """
    working_dir = working_dir or Path.cwd()
    acceptance_criteria = acceptance_criteria or []
    files_touched = files_touched or []

    # Calculate chain depth
    chain_depth = 0
    if previous_handoff_id:
        # Try to load previous handoff to get chain depth
        try:
            serializer = HandoffSerializer(handoffs_dir=handoffs_dir)
            prev = serializer.load(previous_handoff_id)
            chain_depth = prev.chain_depth + 1
        except FileNotFoundError:
            chain_depth = 1

    # Estimate token budget
    token_budget = 0
    file_contents: dict[str, str] = {}

    if files_touched:
        for file_path in files_touched:
            full_path = working_dir / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    content = full_path.read_text()
                    # Estimate ~4 chars per token
                    token_budget += len(content) // 4

                    if include_file_contents:
                        file_contents[file_path] = content
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")

    # Add overhead for context
    token_budget += 500  # Base overhead

    package = EnhancedHandoffPackage(
        task_id=task_id,
        source_agent=source_agent,
        target_agent=target_agent,
        task_description=task_description,
        acceptance_criteria=acceptance_criteria,
        files_touched=files_touched,
        current_state=current_state,
        work_completed=work_completed,
        remaining_work=remaining_work,
        token_budget=token_budget,
        previous_handoff_id=previous_handoff_id,
        chain_depth=chain_depth,
        file_contents=file_contents,
    )

    if save:
        serializer = HandoffSerializer(handoffs_dir=handoffs_dir)
        serializer.save(package)

        # Update chain
        chain = serializer.load_chain(task_id)
        chain.add(package)
        serializer.save_chain(chain)

    return package


def receive_handoff(
    handoff_id: str,
    handoffs_dir: Optional[Path] = None,
    generate_context: bool = False,
) -> Union[EnhancedHandoffPackage, Tuple[EnhancedHandoffPackage, str]]:
    """
    Receive and parse a handoff from another agent.

    Args:
        handoff_id: ID of the handoff to receive
        handoffs_dir: Directory containing handoff files
        generate_context: Whether to generate context markdown

    Returns:
        If generate_context is False: EnhancedHandoffPackage
        If generate_context is True: Tuple of (package, context_markdown)

    Raises:
        FileNotFoundError: If handoff doesn't exist

    Example:
        >>> package, context = receive_handoff(
        ...     "handoff-abc123",
        ...     generate_context=True,
        ... )
        >>> print(context)  # Ready for agent consumption
    """
    serializer = HandoffSerializer(handoffs_dir=handoffs_dir)
    package = serializer.load(handoff_id)

    if generate_context:
        context = package.generate_context_markdown()
        return package, context

    return package
