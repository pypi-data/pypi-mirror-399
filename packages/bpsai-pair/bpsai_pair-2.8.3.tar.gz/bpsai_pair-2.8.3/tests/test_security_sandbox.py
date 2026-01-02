"""Tests for Docker sandbox runner."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from dataclasses import asdict


class TestSandboxConfig:
    """Tests for SandboxConfig dataclass."""

    def test_default_config(self):
        """Test SandboxConfig with default values."""
        from bpsai_pair.security.sandbox import SandboxConfig

        config = SandboxConfig()
        assert config.enabled is True
        assert config.image == "paircoder/sandbox:latest"
        assert config.memory_limit == "2g"
        assert config.cpu_limit == 2.0
        assert config.network == "none"

    def test_custom_config(self):
        """Test SandboxConfig with custom values."""
        from bpsai_pair.security.sandbox import SandboxConfig

        config = SandboxConfig(
            enabled=False,
            image="custom/image:v1",
            memory_limit="4g",
            cpu_limit=4.0,
            network="bridge"
        )
        assert config.enabled is False
        assert config.image == "custom/image:v1"
        assert config.memory_limit == "4g"
        assert config.cpu_limit == 4.0
        assert config.network == "bridge"

    def test_config_with_mounts(self):
        """Test SandboxConfig with custom mounts."""
        from bpsai_pair.security.sandbox import SandboxConfig, MountConfig

        mount = MountConfig(
            source="/host/path",
            target="/container/path",
            readonly=True
        )
        config = SandboxConfig(mounts=[mount])
        assert len(config.mounts) == 1
        assert config.mounts[0].readonly is True

    def test_config_with_env_passthrough(self):
        """Test SandboxConfig with environment passthrough."""
        from bpsai_pair.security.sandbox import SandboxConfig

        config = SandboxConfig(env_passthrough=["GITHUB_TOKEN", "API_KEY"])
        assert "GITHUB_TOKEN" in config.env_passthrough
        assert "API_KEY" in config.env_passthrough

    def test_load_from_yaml(self, tmp_path):
        """Test loading config from YAML file."""
        from bpsai_pair.security.sandbox import SandboxConfig
        import yaml

        config_data = {
            "sandbox": {
                "enabled": True,
                "image": "test/image:v1",
                "memory_limit": "1g",
                "cpu_limit": 1.0,
                "network": "host"
            }
        }
        config_file = tmp_path / "sandbox.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = SandboxConfig.from_yaml(config_file)
        assert config.image == "test/image:v1"
        assert config.memory_limit == "1g"

    def test_config_to_docker_kwargs(self):
        """Test converting config to Docker run kwargs."""
        from bpsai_pair.security.sandbox import SandboxConfig

        config = SandboxConfig(
            memory_limit="2g",
            cpu_limit=2.0,
            network="none"
        )
        kwargs = config.to_docker_kwargs()
        assert "mem_limit" in kwargs
        assert "nano_cpus" in kwargs
        assert "network_mode" in kwargs


class TestMountConfig:
    """Tests for MountConfig dataclass."""

    def test_mount_config_creation(self):
        """Test MountConfig creation."""
        from bpsai_pair.security.sandbox import MountConfig

        mount = MountConfig(
            source="/host/path",
            target="/container/path",
            readonly=False
        )
        assert mount.source == "/host/path"
        assert mount.target == "/container/path"
        assert mount.readonly is False

    def test_mount_config_to_docker_mount(self):
        """Test converting MountConfig to Docker mount dict."""
        from bpsai_pair.security.sandbox import MountConfig

        mount = MountConfig(
            source="/host/path",
            target="/container/path",
            readonly=True
        )
        docker_mount = mount.to_docker_mount()
        assert docker_mount["bind"] == "/container/path"
        assert docker_mount["mode"] == "ro"


class TestSandboxResult:
    """Tests for SandboxResult dataclass."""

    def test_result_creation(self):
        """Test SandboxResult creation."""
        from bpsai_pair.security.sandbox import SandboxResult

        result = SandboxResult(
            exit_code=0,
            stdout="Hello, World!",
            stderr="",
            changes=[]
        )
        assert result.exit_code == 0
        assert result.stdout == "Hello, World!"
        assert result.success is True

    def test_result_with_failure(self):
        """Test SandboxResult with non-zero exit code."""
        from bpsai_pair.security.sandbox import SandboxResult

        result = SandboxResult(
            exit_code=1,
            stdout="",
            stderr="Error occurred",
            changes=[]
        )
        assert result.exit_code == 1
        assert result.success is False

    def test_result_with_changes(self):
        """Test SandboxResult with file changes."""
        from bpsai_pair.security.sandbox import SandboxResult, FileChange

        changes = [
            FileChange(path="file1.txt", action="created"),
            FileChange(path="file2.txt", action="modified"),
        ]
        result = SandboxResult(
            exit_code=0,
            stdout="",
            stderr="",
            changes=changes
        )
        assert len(result.changes) == 2
        assert result.has_changes is True

    def test_result_without_changes(self):
        """Test SandboxResult without file changes."""
        from bpsai_pair.security.sandbox import SandboxResult

        result = SandboxResult(
            exit_code=0,
            stdout="",
            stderr="",
            changes=[]
        )
        assert result.has_changes is False


class TestFileChange:
    """Tests for FileChange dataclass."""

    def test_file_change_created(self):
        """Test FileChange for created file."""
        from bpsai_pair.security.sandbox import FileChange

        change = FileChange(path="new_file.txt", action="created")
        assert change.path == "new_file.txt"
        assert change.action == "created"

    def test_file_change_modified(self):
        """Test FileChange for modified file."""
        from bpsai_pair.security.sandbox import FileChange

        change = FileChange(path="existing.txt", action="modified")
        assert change.action == "modified"

    def test_file_change_deleted(self):
        """Test FileChange for deleted file."""
        from bpsai_pair.security.sandbox import FileChange

        change = FileChange(path="removed.txt", action="deleted")
        assert change.action == "deleted"


class TestSandboxRunner:
    """Tests for SandboxRunner class."""

    def test_runner_creation(self):
        """Test SandboxRunner creation."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        assert runner.workspace == Path("/workspace")
        assert runner.config == config

    def test_runner_default_config(self):
        """Test SandboxRunner with default config."""
        from bpsai_pair.security.sandbox import SandboxRunner

        runner = SandboxRunner(workspace=Path("/workspace"))
        assert runner.config is not None
        assert runner.config.enabled is True

    @patch("bpsai_pair.security.sandbox.docker")
    def test_run_command_success(self, mock_docker):
        """Test running command successfully in sandbox."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        # Mock Docker client
        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(
            exit_code=0,
            output=b"Hello, World!"
        )
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)

        result = runner.run_command("echo 'Hello, World!'")
        assert result.exit_code == 0
        assert "Hello" in result.stdout

    @patch("bpsai_pair.security.sandbox.docker")
    def test_run_command_failure(self, mock_docker):
        """Test running command that fails in sandbox."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(
            exit_code=1,
            output=b"Command not found"
        )
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)

        result = runner.run_command("nonexistent_command")
        assert result.exit_code == 1
        assert result.success is False

    @patch("bpsai_pair.security.sandbox.docker")
    def test_run_command_with_network_disabled(self, mock_docker):
        """Test that network is disabled by default."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig(network="none")
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        runner.run_command("echo test")

        # Verify network_mode was set to none
        call_kwargs = mock_docker.from_env.return_value.containers.run.call_args
        assert call_kwargs[1].get("network_mode") == "none"

    @patch("bpsai_pair.security.sandbox.docker")
    def test_run_command_with_network_enabled(self, mock_docker):
        """Test enabling network for specific command."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig(network="bridge")
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        runner.run_command("curl https://example.com")

        call_kwargs = mock_docker.from_env.return_value.containers.run.call_args
        assert call_kwargs[1].get("network_mode") == "bridge"

    @patch("bpsai_pair.security.sandbox.docker")
    def test_run_command_with_memory_limit(self, mock_docker):
        """Test memory limit is enforced."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig(memory_limit="1g")
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        runner.run_command("echo test")

        call_kwargs = mock_docker.from_env.return_value.containers.run.call_args
        assert call_kwargs[1].get("mem_limit") == "1g"

    @patch("bpsai_pair.security.sandbox.docker")
    def test_run_command_with_cpu_limit(self, mock_docker):
        """Test CPU limit is enforced."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig(cpu_limit=1.5)
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        runner.run_command("echo test")

        call_kwargs = mock_docker.from_env.return_value.containers.run.call_args
        # CPU is specified in nano CPUs (1 CPU = 1e9 nano CPUs)
        assert call_kwargs[1].get("nano_cpus") == int(1.5 * 1e9)

    @patch("bpsai_pair.security.sandbox.docker")
    def test_container_cleanup_on_success(self, mock_docker):
        """Test container is removed after successful execution."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        runner.run_command("echo test")

        mock_container.remove.assert_called_once()

    @patch("bpsai_pair.security.sandbox.docker")
    def test_container_cleanup_on_failure(self, mock_docker):
        """Test container is removed even after failure."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.side_effect = Exception("Container error")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)

        with pytest.raises(Exception):
            runner.run_command("echo test")

        mock_container.remove.assert_called_once()

    @patch("bpsai_pair.security.sandbox.docker")
    def test_workspace_mounted_correctly(self, mock_docker):
        """Test workspace is mounted as volume."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/my/workspace"), config=config)
        runner.run_command("ls")

        call_kwargs = mock_docker.from_env.return_value.containers.run.call_args
        volumes = call_kwargs[1].get("volumes", {})
        assert "/my/workspace" in volumes or str(Path("/my/workspace")) in volumes

    @patch("bpsai_pair.security.sandbox.docker")
    def test_env_passthrough(self, mock_docker):
        """Test environment variables are passed through."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig
        import os

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"}):
            config = SandboxConfig(env_passthrough=["GITHUB_TOKEN"])
            runner = SandboxRunner(workspace=Path("/workspace"), config=config)
            runner.run_command("echo $GITHUB_TOKEN")

            call_kwargs = mock_docker.from_env.return_value.containers.run.call_args
            env = call_kwargs[1].get("environment", {})
            assert env.get("GITHUB_TOKEN") == "test_token"


class TestSandboxRunnerDisabled:
    """Tests for SandboxRunner when sandbox is disabled."""

    @patch("bpsai_pair.security.sandbox.subprocess")
    def test_disabled_sandbox_runs_locally(self, mock_subprocess):
        """Test that disabled sandbox runs commands locally."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_subprocess.run.return_value = MagicMock(
            returncode=0,
            stdout="Hello",
            stderr=""
        )

        config = SandboxConfig(enabled=False)
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        result = runner.run_command("echo 'Hello'")

        assert result.exit_code == 0
        mock_subprocess.run.assert_called_once()


class TestSandboxDockerNotAvailable:
    """Tests for when Docker is not available."""

    def test_docker_not_installed_raises_error(self):
        """Test error when Docker is not installed."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        with patch("bpsai_pair.security.sandbox.docker") as mock_docker:
            mock_docker.from_env.side_effect = Exception("Docker not available")

            config = SandboxConfig()
            runner = SandboxRunner(workspace=Path("/workspace"), config=config)

            with pytest.raises(Exception) as exc_info:
                runner.run_command("echo test")
            assert "Docker" in str(exc_info.value) or "docker" in str(exc_info.value).lower()

    def test_check_docker_available(self):
        """Test checking if Docker is available."""
        from bpsai_pair.security.sandbox import SandboxRunner

        with patch("bpsai_pair.security.sandbox.docker") as mock_docker:
            mock_docker.from_env.return_value.ping.return_value = True
            assert SandboxRunner.is_docker_available() is True

        with patch("bpsai_pair.security.sandbox.docker") as mock_docker:
            mock_docker.from_env.side_effect = Exception("Not available")
            assert SandboxRunner.is_docker_available() is False


class TestChangeDetection:
    """Tests for file change detection in sandbox."""

    @patch("bpsai_pair.security.sandbox.docker")
    def test_detect_created_files(self, mock_docker):
        """Test detecting newly created files."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        # Mock diff to show created file
        mock_container.diff.return_value = [
            {"Path": "/workspace/new_file.txt", "Kind": 1}  # 1 = created
        ]
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        result = runner.run_command("touch new_file.txt")

        assert result.has_changes is True
        assert any(c.action == "created" for c in result.changes)

    @patch("bpsai_pair.security.sandbox.docker")
    def test_detect_modified_files(self, mock_docker):
        """Test detecting modified files."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_container.diff.return_value = [
            {"Path": "/workspace/existing.txt", "Kind": 0}  # 0 = modified
        ]
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        result = runner.run_command("echo 'new content' >> existing.txt")

        assert result.has_changes is True
        assert any(c.action == "modified" for c in result.changes)

    @patch("bpsai_pair.security.sandbox.docker")
    def test_detect_deleted_files(self, mock_docker):
        """Test detecting deleted files."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig

        mock_container = MagicMock()
        mock_container.exec_run.return_value = MagicMock(exit_code=0, output=b"")
        mock_container.diff.return_value = [
            {"Path": "/workspace/removed.txt", "Kind": 2}  # 2 = deleted
        ]
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)
        result = runner.run_command("rm removed.txt")

        assert result.has_changes is True
        assert any(c.action == "deleted" for c in result.changes)


class TestApplyOrDiscardChanges:
    """Tests for applying or discarding sandbox changes."""

    def test_apply_changes(self):
        """Test applying changes from sandbox to host."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig, SandboxResult, FileChange

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)

        changes = [FileChange(path="new_file.txt", action="created")]
        result = SandboxResult(exit_code=0, stdout="", stderr="", changes=changes)

        # With bind mounts, apply_changes is a no-op (changes are already on host)
        # This should complete without error
        runner.apply_changes(result)
        # No exception means success

    @patch("bpsai_pair.security.sandbox.docker")
    def test_discard_changes(self, mock_docker):
        """Test discarding changes (container removed, no copy)."""
        from bpsai_pair.security.sandbox import SandboxRunner, SandboxConfig, SandboxResult, FileChange

        mock_container = MagicMock()
        mock_docker.from_env.return_value.containers.run.return_value = mock_container

        config = SandboxConfig()
        runner = SandboxRunner(workspace=Path("/workspace"), config=config)

        changes = [FileChange(path="new_file.txt", action="created")]
        result = SandboxResult(exit_code=0, stdout="", stderr="", changes=changes)

        # discard_changes should just remove the container
        runner.discard_changes(result)
        # No copy should happen - changes just stay in the container which is removed
