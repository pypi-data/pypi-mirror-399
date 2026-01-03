"""Tests for MCP tools modules."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio

from bpsai_pair.mcp.tools import context, metrics, orchestration, tasks


class TestFindPaircoderDir:
    """Tests for find_paircoder_dir function across modules."""

    def test_context_finds_dir(self, tmp_path, monkeypatch):
        """Test context.find_paircoder_dir finds directory."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        result = context.find_paircoder_dir()
        assert result == paircoder_dir

    def test_context_finds_parent_dir(self, tmp_path, monkeypatch):
        """Test context.find_paircoder_dir finds parent directory."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        result = context.find_paircoder_dir()
        assert result == paircoder_dir

    def test_context_not_found(self, tmp_path, monkeypatch):
        """Test context.find_paircoder_dir raises when not found."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError):
            context.find_paircoder_dir()

    def test_metrics_finds_dir(self, tmp_path, monkeypatch):
        """Test metrics.find_paircoder_dir finds directory."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        result = metrics.find_paircoder_dir()
        assert result == paircoder_dir

    def test_orchestration_finds_dir(self, tmp_path, monkeypatch):
        """Test orchestration.find_paircoder_dir finds directory."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        result = orchestration.find_paircoder_dir()
        assert result == paircoder_dir

    def test_orchestration_get_project_root(self, tmp_path, monkeypatch):
        """Test orchestration.get_project_root returns parent."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        result = orchestration.get_project_root()
        assert result == tmp_path

    def test_tasks_finds_dir(self, tmp_path, monkeypatch):
        """Test tasks.find_paircoder_dir finds directory."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        result = tasks.find_paircoder_dir()
        assert result == paircoder_dir


class TestRegisterContextTools:
    """Tests for context tools registration."""

    def test_register_creates_tool(self):
        """Test register_context_tools registers tool."""
        mock_server = Mock()
        mock_server.tool = Mock(return_value=lambda f: f)

        context.register_context_tools(mock_server)

        mock_server.tool.assert_called()


class TestRegisterMetricsTools:
    """Tests for metrics tools registration."""

    def test_register_creates_tools(self):
        """Test register_metrics_tools registers tools."""
        mock_server = Mock()
        mock_server.tool = Mock(return_value=lambda f: f)

        metrics.register_metrics_tools(mock_server)

        assert mock_server.tool.call_count >= 2


class TestRegisterOrchestrationTools:
    """Tests for orchestration tools registration."""

    def test_register_creates_tools(self):
        """Test register_orchestration_tools registers tools."""
        mock_server = Mock()
        mock_server.tool = Mock(return_value=lambda f: f)

        orchestration.register_orchestration_tools(mock_server)

        assert mock_server.tool.call_count >= 2


class TestRegisterTaskTools:
    """Tests for task tools registration."""

    def test_register_creates_tools(self):
        """Test register_task_tools registers tools."""
        mock_server = Mock()
        mock_server.tool = Mock(return_value=lambda f: f)

        tasks.register_task_tools(mock_server)

        assert mock_server.tool.call_count >= 4


class TestContextTools:
    """Tests for context tool functions."""

    @pytest.fixture
    def setup_context(self, tmp_path, monkeypatch):
        """Setup paircoder directory with context files."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        context_dir = paircoder_dir / "context"
        context_dir.mkdir()

        (context_dir / "state.md").write_text("# State\nCurrent state")
        (context_dir / "project.md").write_text("# Project\nProject info")
        (paircoder_dir / "config.yaml").write_text("test: true")

        monkeypatch.chdir(tmp_path)
        return paircoder_dir

    def test_context_read_tool_wrapper(self, setup_context):
        """Test we can create the context read tool."""
        captured_func = None

        def capture_tool():
            def decorator(func):
                nonlocal captured_func
                captured_func = func
                return func
            return decorator

        mock_server = Mock()
        mock_server.tool = capture_tool

        context.register_context_tools(mock_server)
        assert captured_func is not None


class TestMetricsTools:
    """Tests for metrics tool functions."""

    def test_metrics_tool_wrapper(self, tmp_path, monkeypatch):
        """Test we can create the metrics tools."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        captured_funcs = []

        def capture_tool():
            def decorator(func):
                captured_funcs.append(func)
                return func
            return decorator

        mock_server = Mock()
        mock_server.tool = capture_tool

        metrics.register_metrics_tools(mock_server)
        assert len(captured_funcs) == 2  # record and summary


class TestOrchestrationTools:
    """Tests for orchestration tool functions."""

    def test_orchestration_tool_wrapper(self, tmp_path, monkeypatch):
        """Test we can create the orchestration tools."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        captured_funcs = []

        def capture_tool():
            def decorator(func):
                captured_funcs.append(func)
                return func
            return decorator

        mock_server = Mock()
        mock_server.tool = capture_tool

        orchestration.register_orchestration_tools(mock_server)
        assert len(captured_funcs) == 4  # analyze, handoff, plan, and review


class TestTaskTools:
    """Tests for task tool functions."""

    def test_task_tool_wrapper(self, tmp_path, monkeypatch):
        """Test we can create the task tools."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        captured_funcs = []

        def capture_tool():
            def decorator(func):
                captured_funcs.append(func)
                return func
            return decorator

        mock_server = Mock()
        mock_server.tool = capture_tool

        tasks.register_task_tools(mock_server)
        assert len(captured_funcs) == 4  # list, next, start, complete
