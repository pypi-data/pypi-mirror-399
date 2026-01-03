"""
Tests for MCP Task Tools

Tests basic task tool functionality.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestTaskToolsList:
    """Tests for task tool list functionality."""

    def test_list_tools_includes_task_tools(self):
        """list_tools includes all task management tools."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        tool_names = [t["name"] for t in tools]

        assert "paircoder_task_list" in tool_names
        assert "paircoder_task_next" in tool_names
        assert "paircoder_task_start" in tool_names
        assert "paircoder_task_complete" in tool_names

    def test_task_list_tool_has_correct_params(self):
        """paircoder_task_list has correct parameters."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        task_list = next(t for t in tools if t["name"] == "paircoder_task_list")

        assert "status" in task_list["parameters"]
        assert "plan" in task_list["parameters"]
        assert "sprint" in task_list["parameters"]

    def test_task_start_tool_has_correct_params(self):
        """paircoder_task_start has correct parameters."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        task_start = next(t for t in tools if t["name"] == "paircoder_task_start")

        assert "task_id" in task_start["parameters"]
        assert "agent" in task_start["parameters"]

    def test_task_complete_tool_has_correct_params(self):
        """paircoder_task_complete has correct parameters."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        task_complete = next(t for t in tools if t["name"] == "paircoder_task_complete")

        assert "task_id" in task_complete["parameters"]
        assert "summary" in task_complete["parameters"]


class TestTaskToolsFindPaircoder:
    """Tests for find_paircoder_dir helper."""

    def test_find_paircoder_dir_raises_when_not_found(self, tmp_path):
        """find_paircoder_dir raises FileNotFoundError when no .paircoder exists."""
        from bpsai_pair.mcp.tools.tasks import find_paircoder_dir
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(FileNotFoundError):
                find_paircoder_dir()
        finally:
            os.chdir(original_cwd)

    def test_find_paircoder_dir_finds_directory(self, tmp_path):
        """find_paircoder_dir finds .paircoder in current directory."""
        from bpsai_pair.mcp.tools.tasks import find_paircoder_dir
        import os

        # Create .paircoder directory
        (tmp_path / ".paircoder").mkdir()

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = find_paircoder_dir()
            assert result.name == ".paircoder"
        finally:
            os.chdir(original_cwd)
