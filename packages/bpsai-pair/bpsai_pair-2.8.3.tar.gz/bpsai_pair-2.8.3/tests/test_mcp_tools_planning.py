"""
Tests for MCP Planning Tools

Tests basic planning tool functionality.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestPlanningToolsList:
    """Tests for planning tool list functionality."""

    def test_list_tools_includes_planning_tools(self):
        """list_tools includes all planning management tools."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        tool_names = [t["name"] for t in tools]

        assert "paircoder_plan_status" in tool_names
        assert "paircoder_plan_list" in tool_names

    def test_plan_status_tool_has_correct_params(self):
        """paircoder_plan_status has correct parameters."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        plan_status = next(t for t in tools if t["name"] == "paircoder_plan_status")

        assert "plan_id" in plan_status["parameters"]

    def test_plan_list_tool_has_empty_params(self):
        """paircoder_plan_list has no required parameters."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        plan_list = next(t for t in tools if t["name"] == "paircoder_plan_list")

        # plan_list has no required parameters
        assert isinstance(plan_list["parameters"], list)


class TestOrchestrateToolsList:
    """Tests for orchestration tool list functionality."""

    def test_list_tools_includes_orchestration_tools(self):
        """list_tools includes all orchestration tools."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        tool_names = [t["name"] for t in tools]

        assert "paircoder_orchestrate_analyze" in tool_names
        assert "paircoder_orchestrate_handoff" in tool_names

    def test_orchestrate_analyze_has_task_id_param(self):
        """paircoder_orchestrate_analyze has task_id parameter."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        analyze = next(t for t in tools if t["name"] == "paircoder_orchestrate_analyze")

        assert "task_id" in analyze["parameters"]


class TestMetricsToolsList:
    """Tests for metrics tool list functionality."""

    def test_list_tools_includes_metrics_tools(self):
        """list_tools includes all metrics tools."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        tool_names = [t["name"] for t in tools]

        assert "paircoder_metrics_record" in tool_names
        assert "paircoder_metrics_summary" in tool_names

    def test_metrics_record_has_required_params(self):
        """paircoder_metrics_record has required parameters."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        metrics_record = next(t for t in tools if t["name"] == "paircoder_metrics_record")

        assert "task_id" in metrics_record["parameters"]
        assert "agent" in metrics_record["parameters"]
        assert "model" in metrics_record["parameters"]


class TestTrelloToolsList:
    """Tests for Trello tool list functionality."""

    def test_list_tools_includes_trello_tools(self):
        """list_tools includes all Trello tools."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        tool_names = [t["name"] for t in tools]

        assert "paircoder_trello_sync_plan" in tool_names
        assert "paircoder_trello_update_card" in tool_names

    def test_trello_sync_plan_has_plan_id_param(self):
        """paircoder_trello_sync_plan has plan_id parameter."""
        from bpsai_pair.mcp.server import list_tools

        tools = list_tools()
        sync_plan = next(t for t in tools if t["name"] == "paircoder_trello_sync_plan")

        assert "plan_id" in sync_plan["parameters"]
        assert "board_id" in sync_plan["parameters"]
