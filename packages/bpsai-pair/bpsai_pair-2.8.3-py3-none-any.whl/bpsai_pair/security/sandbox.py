"""Docker sandbox runner for isolated command execution.

This module provides secure command execution in isolated Docker containers:
- SandboxConfig: Configuration for sandbox environment
- SandboxRunner: Execute commands in isolated containers
- SandboxResult: Results with file change tracking
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

import yaml

try:
    import docker
except ImportError:
    docker = None


# Docker diff kind values
DIFF_MODIFIED = 0
DIFF_CREATED = 1
DIFF_DELETED = 2

DIFF_KIND_TO_ACTION = {
    DIFF_MODIFIED: "modified",
    DIFF_CREATED: "created",
    DIFF_DELETED: "deleted",
}


@dataclass
class MountConfig:
    """Configuration for a volume mount.

    Attributes:
        source: Host path to mount
        target: Container path to mount to
        readonly: Whether mount is read-only
    """

    source: str
    target: str
    readonly: bool = False

    def to_docker_mount(self) -> dict:
        """Convert to Docker mount configuration dict."""
        return {
            "bind": self.target,
            "mode": "ro" if self.readonly else "rw"
        }


@dataclass
class FileChange:
    """Represents a file change in the sandbox.

    Attributes:
        path: Path to the changed file (relative to workspace)
        action: Type of change (created, modified, deleted)
    """

    path: str
    action: Literal["created", "modified", "deleted"]


@dataclass
class SandboxResult:
    """Result of running a command in the sandbox.

    Attributes:
        exit_code: Command exit code
        stdout: Standard output
        stderr: Standard error
        changes: List of file changes detected
    """

    exit_code: int
    stdout: str
    stderr: str
    changes: list[FileChange] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if command succeeded (exit code 0)."""
        return self.exit_code == 0

    @property
    def has_changes(self) -> bool:
        """Check if any file changes were detected."""
        return len(self.changes) > 0


@dataclass
class SandboxConfig:
    """Configuration for the Docker sandbox.

    Attributes:
        enabled: Whether sandbox is enabled
        image: Docker image to use
        memory_limit: Memory limit (e.g., "2g")
        cpu_limit: CPU limit (number of CPUs)
        network: Network mode (none, bridge, host)
        mounts: List of volume mounts
        env_passthrough: Environment variables to pass through
    """

    enabled: bool = True
    image: str = "paircoder/sandbox:latest"
    memory_limit: str = "2g"
    cpu_limit: float = 2.0
    network: str = "none"
    mounts: list[MountConfig] = field(default_factory=list)
    env_passthrough: list[str] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: Path) -> "SandboxConfig":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML config file

        Returns:
            SandboxConfig instance
        """
        with open(path) as f:
            data = yaml.safe_load(f)

        sandbox_data = data.get("sandbox", {})

        mounts = []
        for mount_data in sandbox_data.get("mounts", []):
            mounts.append(MountConfig(
                source=mount_data.get("source", ""),
                target=mount_data.get("target", ""),
                readonly=mount_data.get("readonly", False)
            ))

        return cls(
            enabled=sandbox_data.get("enabled", True),
            image=sandbox_data.get("image", cls.image),
            memory_limit=sandbox_data.get("memory_limit", cls.memory_limit),
            cpu_limit=sandbox_data.get("cpu_limit", cls.cpu_limit),
            network=sandbox_data.get("network", cls.network),
            mounts=mounts,
            env_passthrough=sandbox_data.get("env_passthrough", [])
        )

    def to_docker_kwargs(self) -> dict:
        """Convert config to Docker run kwargs.

        Returns:
            Dict of kwargs for docker.containers.run()
        """
        return {
            "mem_limit": self.memory_limit,
            "nano_cpus": int(self.cpu_limit * 1e9),
            "network_mode": self.network,
        }


class SandboxRunner:
    """Runs commands in isolated Docker containers.

    Provides secure command execution with:
    - Network isolation (disabled by default)
    - Resource limits (memory, CPU)
    - File change tracking
    - Cleanup on completion

    Attributes:
        workspace: Path to workspace directory
        config: Sandbox configuration
    """

    def __init__(
        self,
        workspace: Path,
        config: Optional[SandboxConfig] = None
    ):
        """Initialize the sandbox runner.

        Args:
            workspace: Path to workspace directory to mount
            config: Sandbox configuration (uses default if None)
        """
        self.workspace = workspace
        self.config = config or SandboxConfig()
        self._current_container = None

    @staticmethod
    def is_docker_available() -> bool:
        """Check if Docker is available.

        Returns:
            True if Docker is available and running
        """
        if docker is None:
            return False

        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    def _get_docker_client(self):
        """Get Docker client, raising error if not available."""
        if docker is None:
            raise RuntimeError("Docker Python SDK not installed. Install with: pip install docker")

        try:
            return docker.from_env()
        except Exception as e:
            raise RuntimeError(f"Docker not available: {e}")

    def _build_volumes(self) -> dict:
        """Build volumes dict for Docker run."""
        volumes = {
            str(self.workspace): {
                "bind": "/workspace",
                "mode": "rw"
            }
        }

        for mount in self.config.mounts:
            volumes[mount.source] = mount.to_docker_mount()

        return volumes

    def _build_environment(self) -> dict:
        """Build environment dict from passthrough config."""
        env = {}
        for var_name in self.config.env_passthrough:
            value = os.environ.get(var_name)
            if value is not None:
                env[var_name] = value
        return env

    def _parse_diff(self, diff_output: list) -> list[FileChange]:
        """Parse Docker diff output to FileChange list.

        Args:
            diff_output: List of diff entries from container.diff()

        Returns:
            List of FileChange objects
        """
        changes = []
        workspace_prefix = "/workspace"

        for entry in diff_output:
            path = entry.get("Path", "")
            kind = entry.get("Kind", 0)

            # Only track changes in workspace
            if path.startswith(workspace_prefix):
                relative_path = path[len(workspace_prefix):].lstrip("/")
                action = DIFF_KIND_TO_ACTION.get(kind, "modified")
                changes.append(FileChange(path=relative_path, action=action))

        return changes

    def run_command(self, command: str) -> SandboxResult:
        """Run a command in the sandbox.

        Args:
            command: Command string to execute

        Returns:
            SandboxResult with exit code, output, and file changes

        Raises:
            RuntimeError: If Docker is not available
        """
        if not self.config.enabled:
            return self._run_local(command)

        client = self._get_docker_client()

        # Build Docker run kwargs
        run_kwargs = self.config.to_docker_kwargs()
        run_kwargs.update({
            "image": self.config.image,
            "command": "sleep infinity",  # Keep container running
            "volumes": self._build_volumes(),
            "environment": self._build_environment(),
            "working_dir": "/workspace",
            "detach": True,
            "remove": False,  # We'll remove manually after getting diff
        })

        container = None
        try:
            # Create and start container
            container = client.containers.run(**run_kwargs)
            self._current_container = container

            # Execute command in container
            exec_result = container.exec_run(
                cmd=["sh", "-c", command],
                workdir="/workspace"
            )

            # Get file changes before removing container
            try:
                diff = container.diff() or []
            except Exception:
                diff = []

            changes = self._parse_diff(diff)

            # Decode output
            stdout = exec_result.output.decode("utf-8", errors="replace") if exec_result.output else ""

            return SandboxResult(
                exit_code=exec_result.exit_code,
                stdout=stdout,
                stderr="",  # Docker exec_run combines stdout/stderr
                changes=changes
            )

        finally:
            # Always cleanup container
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            self._current_container = None

    def _run_local(self, command: str) -> SandboxResult:
        """Run command locally when sandbox is disabled.

        Args:
            command: Command to execute

        Returns:
            SandboxResult with exit code and output
        """
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(self.workspace),
            capture_output=True,
            text=True
        )

        return SandboxResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            changes=[]  # No change tracking in local mode
        )

    def _copy_from_container(self, container, src_path: str, dest_path: str) -> None:
        """Copy file from container to host.

        Args:
            container: Docker container
            src_path: Path in container
            dest_path: Path on host
        """
        import tarfile
        import io

        # Get file as tar archive
        bits, _ = container.get_archive(src_path)

        # Extract to destination
        tar_stream = io.BytesIO()
        for chunk in bits:
            tar_stream.write(chunk)
        tar_stream.seek(0)

        with tarfile.open(fileobj=tar_stream) as tar:
            tar.extractall(path=str(Path(dest_path).parent))

    def apply_changes(self, result: SandboxResult) -> None:
        """Apply changes from sandbox to host filesystem.

        Args:
            result: SandboxResult containing changes to apply

        Note:
            When using bind mounts (default), changes are already
            applied to the host filesystem. This method is for
            copy-based workflows.
        """
        # With bind mounts, changes are already on the host
        # This method exists for future copy-based sandbox modes
        pass

    def discard_changes(self, result: SandboxResult) -> None:
        """Discard changes from sandbox.

        Args:
            result: SandboxResult containing changes to discard

        Note:
            Container is already removed in run_command().
            With bind mounts, changes cannot be discarded after execution.
            This method is for future copy-based sandbox modes.
        """
        # Container already removed in run_command()
        # With bind mounts, changes are already on the host
        pass
