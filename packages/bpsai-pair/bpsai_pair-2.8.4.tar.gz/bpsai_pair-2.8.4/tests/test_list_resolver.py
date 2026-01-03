"""Tests for list_resolver module."""
import pytest
from unittest.mock import Mock, MagicMock

from bpsai_pair.trello.list_resolver import (
    normalize_list_name,
    STATUS_LIST_PATTERNS,
    LIST_STATUS_PATTERNS,
    ListResolver,
    create_list_status_map,
)


class TestNormalizeListName:
    """Tests for normalize_list_name function."""

    def test_removes_spaces_around_slash(self):
        """Test spaces around slashes are removed."""
        assert normalize_list_name("Deployed / Done") == "deployed/done"
        assert normalize_list_name("Intake / Backlog") == "intake/backlog"

    def test_handles_no_spaces(self):
        """Test names without spaces around slashes."""
        assert normalize_list_name("Deployed/Done") == "deployed/done"

    def test_lowercase(self):
        """Test names are lowercased."""
        assert normalize_list_name("IN PROGRESS") == "in progress"
        assert normalize_list_name("Done") == "done"

    def test_strips_whitespace(self):
        """Test leading/trailing whitespace is stripped."""
        assert normalize_list_name("  Done  ") == "done"
        assert normalize_list_name("\tBacklog\n") == "backlog"

    def test_multiple_slashes(self):
        """Test multiple slashes are handled."""
        assert normalize_list_name("A / B / C") == "a/b/c"


class TestStatusListPatterns:
    """Tests for STATUS_LIST_PATTERNS dictionary."""

    def test_pending_patterns(self):
        """Test pending status patterns."""
        patterns = STATUS_LIST_PATTERNS["pending"]
        assert "intake" in patterns
        assert "backlog" in patterns
        assert "planned" in patterns
        assert "ready" in patterns
        assert "todo" in patterns

    def test_in_progress_patterns(self):
        """Test in_progress status patterns."""
        patterns = STATUS_LIST_PATTERNS["in_progress"]
        assert "in progress" in patterns
        assert "doing" in patterns
        assert "working" in patterns

    def test_review_patterns(self):
        """Test review status patterns."""
        patterns = STATUS_LIST_PATTERNS["review"]
        assert "review" in patterns
        assert "testing" in patterns
        assert "qa" in patterns

    def test_done_patterns(self):
        """Test done status patterns."""
        patterns = STATUS_LIST_PATTERNS["done"]
        assert "done" in patterns
        assert "deployed" in patterns
        assert "complete" in patterns

    def test_blocked_patterns(self):
        """Test blocked status patterns."""
        patterns = STATUS_LIST_PATTERNS["blocked"]
        assert "blocked" in patterns
        assert "issues" in patterns
        assert "tech debt" in patterns


class TestListStatusPatterns:
    """Tests for LIST_STATUS_PATTERNS dictionary."""

    def test_pending_mappings(self):
        """Test pending status mappings."""
        assert LIST_STATUS_PATTERNS["intake"] == "pending"
        assert LIST_STATUS_PATTERNS["backlog"] == "pending"
        assert LIST_STATUS_PATTERNS["ready"] == "pending"

    def test_in_progress_mappings(self):
        """Test in_progress status mappings."""
        assert LIST_STATUS_PATTERNS["in progress"] == "in_progress"
        assert LIST_STATUS_PATTERNS["doing"] == "in_progress"

    def test_review_mappings(self):
        """Test review status mappings."""
        assert LIST_STATUS_PATTERNS["review"] == "review"
        assert LIST_STATUS_PATTERNS["testing"] == "review"
        assert LIST_STATUS_PATTERNS["qa"] == "review"

    def test_done_mappings(self):
        """Test done status mappings."""
        assert LIST_STATUS_PATTERNS["done"] == "done"
        assert LIST_STATUS_PATTERNS["deployed"] == "done"
        assert LIST_STATUS_PATTERNS["complete"] == "done"

    def test_blocked_mappings(self):
        """Test blocked status mappings."""
        assert LIST_STATUS_PATTERNS["blocked"] == "blocked"
        assert LIST_STATUS_PATTERNS["issues"] == "blocked"
        assert LIST_STATUS_PATTERNS["tech debt"] == "blocked"


class TestListResolver:
    """Tests for ListResolver class."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock()
        mock_board = Mock()

        # Create mock lists
        list1 = Mock()
        list1.id = "list1"
        list1.name = "Backlog"
        list1.closed = False

        list2 = Mock()
        list2.id = "list2"
        list2.name = "In Progress"
        list2.closed = False

        list3 = Mock()
        list3.id = "list3"
        list3.name = "Done"
        list3.closed = False

        mock_board.list_lists.return_value = [list1, list2, list3]
        service.board = mock_board
        return service

    def test_init(self, mock_service):
        """Test initialization."""
        resolver = ListResolver(mock_service)
        assert resolver.service == mock_service
        assert resolver._lists_cache is None

    def test_fetch_lists(self, mock_service):
        """Test fetching lists from board."""
        resolver = ListResolver(mock_service)
        lists = resolver._fetch_lists()

        assert len(lists) == 3
        assert lists[0]["name"] == "Backlog"
        assert lists[0]["id"] == "list1"

    def test_fetch_lists_cached(self, mock_service):
        """Test lists are cached after first fetch."""
        resolver = ListResolver(mock_service)
        resolver._fetch_lists()
        resolver._fetch_lists()

        # Only called once
        mock_service.board.list_lists.assert_called_once()

    def test_fetch_lists_skips_closed(self, mock_service):
        """Test archived lists are skipped."""
        archived = Mock()
        archived.id = "archived"
        archived.name = "Archived List"
        archived.closed = True

        mock_service.board.list_lists.return_value.append(archived)

        resolver = ListResolver(mock_service)
        lists = resolver._fetch_lists()

        assert len(lists) == 3
        assert all(lst["name"] != "Archived List" for lst in lists)

    def test_fetch_lists_error(self, mock_service):
        """Test fetch handles errors gracefully."""
        mock_service.board.list_lists.side_effect = Exception("API error")

        resolver = ListResolver(mock_service)
        lists = resolver._fetch_lists()

        assert lists == []

    def test_get_all_lists(self, mock_service):
        """Test get_all_lists returns all lists."""
        resolver = ListResolver(mock_service)
        lists = resolver.get_all_lists()

        assert len(lists) == 3

    def test_find_list_for_status_pending(self, mock_service):
        """Test finding list for pending status."""
        resolver = ListResolver(mock_service)
        result = resolver.find_list_for_status("pending")

        assert result is not None
        assert result["name"] == "Backlog"
        assert result["id"] == "list1"

    def test_find_list_for_status_in_progress(self, mock_service):
        """Test finding list for in_progress status."""
        resolver = ListResolver(mock_service)
        result = resolver.find_list_for_status("in_progress")

        assert result is not None
        assert result["name"] == "In Progress"

    def test_find_list_for_status_done(self, mock_service):
        """Test finding list for done status."""
        resolver = ListResolver(mock_service)
        result = resolver.find_list_for_status("done")

        assert result is not None
        assert result["name"] == "Done"

    def test_find_list_for_status_not_found(self, mock_service):
        """Test finding list for unknown status returns None."""
        resolver = ListResolver(mock_service)
        result = resolver.find_list_for_status("nonexistent")

        assert result is None

    def test_find_list_for_status_empty_lists(self, mock_service):
        """Test finding list when board has no lists."""
        mock_service.board.list_lists.return_value = []

        resolver = ListResolver(mock_service)
        result = resolver.find_list_for_status("pending")

        assert result is None

    def test_get_status_for_list_backlog(self, mock_service):
        """Test getting status for Backlog list."""
        resolver = ListResolver(mock_service)
        status = resolver.get_status_for_list("Backlog")

        assert status == "pending"

    def test_get_status_for_list_in_progress(self, mock_service):
        """Test getting status for In Progress list."""
        resolver = ListResolver(mock_service)
        status = resolver.get_status_for_list("In Progress")

        assert status == "in_progress"

    def test_get_status_for_list_done(self, mock_service):
        """Test getting status for Done list."""
        resolver = ListResolver(mock_service)
        status = resolver.get_status_for_list("Done")

        assert status == "done"

    def test_get_status_for_list_deployed_done(self, mock_service):
        """Test getting status for Deployed / Done list."""
        resolver = ListResolver(mock_service)
        status = resolver.get_status_for_list("Deployed / Done")

        assert status == "done"

    def test_get_status_for_list_unknown(self, mock_service):
        """Test getting status for unknown list."""
        resolver = ListResolver(mock_service)
        status = resolver.get_status_for_list("Unknown List Name")

        assert status is None

    def test_get_list_id_exact_match(self, mock_service):
        """Test getting list ID with exact match."""
        resolver = ListResolver(mock_service)
        list_id = resolver.get_list_id("Backlog")

        assert list_id == "list1"

    def test_get_list_id_normalized_match(self, mock_service):
        """Test getting list ID with normalized match."""
        resolver = ListResolver(mock_service)
        list_id = resolver.get_list_id("backlog")

        assert list_id == "list1"

    def test_get_list_id_partial_match(self, mock_service):
        """Test getting list ID with partial match."""
        resolver = ListResolver(mock_service)
        list_id = resolver.get_list_id("Progress")

        assert list_id == "list2"

    def test_get_list_id_not_found(self, mock_service):
        """Test getting list ID that doesn't exist."""
        resolver = ListResolver(mock_service)
        list_id = resolver.get_list_id("Nonexistent")

        assert list_id is None

    def test_get_list_id_empty_cache(self, mock_service):
        """Test getting list ID when no lists cached."""
        mock_service.board.list_lists.return_value = []

        resolver = ListResolver(mock_service)
        list_id = resolver.get_list_id("Backlog")

        assert list_id is None

    def test_get_list_name_exact_match(self, mock_service):
        """Test getting actual list name with exact match."""
        resolver = ListResolver(mock_service)
        name = resolver.get_list_name("Backlog")

        assert name == "Backlog"

    def test_get_list_name_normalized(self, mock_service):
        """Test getting list name with normalized input."""
        resolver = ListResolver(mock_service)
        name = resolver.get_list_name("in progress")

        assert name == "In Progress"

    def test_get_list_name_partial_match(self, mock_service):
        """Test getting list name with partial match."""
        resolver = ListResolver(mock_service)
        name = resolver.get_list_name("Progress")

        assert name == "In Progress"

    def test_get_list_name_not_found(self, mock_service):
        """Test getting list name that doesn't exist."""
        resolver = ListResolver(mock_service)
        name = resolver.get_list_name("Nonexistent")

        assert name is None

    def test_get_list_name_empty_cache(self, mock_service):
        """Test getting list name when no lists cached."""
        mock_service.board.list_lists.return_value = []

        resolver = ListResolver(mock_service)
        name = resolver.get_list_name("Backlog")

        assert name is None

    def test_clear_cache(self, mock_service):
        """Test clearing cache."""
        resolver = ListResolver(mock_service)
        resolver._fetch_lists()

        assert resolver._lists_cache is not None

        resolver.clear_cache()

        assert resolver._lists_cache is None
        assert resolver._list_map is None
        assert resolver._list_names is None


class TestCreateListStatusMap:
    """Tests for create_list_status_map function."""

    @pytest.fixture
    def mock_service(self):
        """Create mock TrelloService."""
        service = Mock()
        mock_board = Mock()

        list1 = Mock()
        list1.id = "list1"
        list1.name = "Intake / Backlog"
        list1.closed = False

        list2 = Mock()
        list2.id = "list2"
        list2.name = "In Progress"
        list2.closed = False

        list3 = Mock()
        list3.id = "list3"
        list3.name = "Deployed / Done"
        list3.closed = False

        mock_board.list_lists.return_value = [list1, list2, list3]
        service.board = mock_board
        return service

    def test_creates_map(self, mock_service):
        """Test creating list status map."""
        result = create_list_status_map(mock_service)

        assert "Intake / Backlog" in result
        assert result["Intake / Backlog"] == "pending"
        assert result["In Progress"] == "in_progress"
        assert result["Deployed / Done"] == "done"

    def test_empty_board(self, mock_service):
        """Test with empty board."""
        mock_service.board.list_lists.return_value = []

        result = create_list_status_map(mock_service)

        assert result == {}

    def test_unknown_lists_excluded(self, mock_service):
        """Test unknown list names are not in result."""
        unknown = Mock()
        unknown.id = "unknown"
        unknown.name = "Random List"
        unknown.closed = False

        mock_service.board.list_lists.return_value.append(unknown)

        result = create_list_status_map(mock_service)

        assert "Random List" not in result
