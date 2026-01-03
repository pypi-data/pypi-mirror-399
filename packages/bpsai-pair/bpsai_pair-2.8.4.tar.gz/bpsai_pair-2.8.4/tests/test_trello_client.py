"""Tests for Trello client module."""
import pytest
from unittest.mock import MagicMock, patch


class TestTrelloService:
    """Tests for TrelloService class."""

    @pytest.fixture
    def mock_trello_module(self):
        """Mock the py-trello module."""
        mock_client_class = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        with patch.dict('sys.modules', {'trello': MagicMock(TrelloClient=mock_client_class)}):
            yield mock_client_class, mock_client_instance

    def test_init_creates_client(self, mock_trello_module):
        """Test that initialization creates a Trello client."""
        mock_client_class, _ = mock_trello_module

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="test-key", token="test-token")

        mock_client_class.assert_called_once_with(api_key="test-key", token="test-token")
        assert service.board is None
        assert service.lists == {}

    def test_init_raises_without_pytrello(self):
        """Test that init raises ImportError if py-trello not installed."""
        with patch.dict('sys.modules', {'trello': None}):
            # Force reimport to trigger the ImportError
            import importlib
            import bpsai_pair.trello.client as client_module

            with pytest.raises(ImportError, match="py-trello is required"):
                # We need to reload to test the import behavior
                importlib.reload(client_module)
                from bpsai_pair.trello.client import TrelloService
                TrelloService(api_key="test", token="test")

    def test_healthcheck_success(self, mock_trello_module):
        """Test healthcheck returns True on success."""
        _, mock_client = mock_trello_module
        mock_client.list_boards.return_value = []

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        assert service.healthcheck() == True
        mock_client.list_boards.assert_called_once()

    def test_healthcheck_failure(self, mock_trello_module):
        """Test healthcheck returns False on error."""
        _, mock_client = mock_trello_module
        mock_client.list_boards.side_effect = Exception("API error")

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        assert service.healthcheck() == False

    def test_set_board(self, mock_trello_module):
        """Test setting the active board."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()
        mock_board.name = "Test Board"

        mock_list1 = MagicMock()
        mock_list1.name = "Sprint"
        mock_list2 = MagicMock()
        mock_list2.name = "Done"
        mock_board.all_lists.return_value = [mock_list1, mock_list2]

        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        result = service.set_board("board-123")

        assert result == mock_board
        assert service.board == mock_board
        assert "Sprint" in service.lists
        assert "Done" in service.lists

    def test_get_board_lists_raises_without_board(self, mock_trello_module):
        """Test that get_board_lists raises if board not set."""
        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        with pytest.raises(ValueError, match="Board not set"):
            service.get_board_lists()

    def test_get_cards_in_list(self, mock_trello_module):
        """Test getting cards from a list."""
        _, mock_client = mock_trello_module

        mock_card = MagicMock()
        mock_card.name = "Test Card"

        mock_list = MagicMock()
        mock_list.name = "Sprint"
        mock_list.list_cards.return_value = [mock_card]

        mock_board = MagicMock()
        mock_board.all_lists.return_value = [mock_list]
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        cards = service.get_cards_in_list("Sprint")
        assert len(cards) == 1
        assert cards[0].name == "Test Card"

    def test_get_cards_empty_list(self, mock_trello_module):
        """Test getting cards from non-existent list returns empty."""
        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.lists = {"Sprint": MagicMock()}

        cards = service.get_cards_in_list("NonExistent")
        assert cards == []

    def test_is_card_blocked(self, mock_trello_module):
        """Test checking if card is blocked."""
        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        # Card with unchecked dependency
        mock_checklist = MagicMock()
        mock_checklist.name = "card dependencies"
        mock_checklist.items = [{"name": "Other task", "checked": False}]

        mock_card = MagicMock()
        mock_card.checklists = [mock_checklist]

        assert service.is_card_blocked(mock_card) == True

    def test_is_card_not_blocked(self, mock_trello_module):
        """Test card is not blocked when dependencies are checked."""
        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        mock_checklist = MagicMock()
        mock_checklist.name = "card dependencies"
        mock_checklist.items = [{"name": "Other task", "checked": True}]

        mock_card = MagicMock()
        mock_card.checklists = [mock_checklist]

        assert service.is_card_blocked(mock_card) == False

    def test_find_card_by_short_id(self, mock_trello_module):
        """Test finding card by short ID."""
        _, mock_client = mock_trello_module

        mock_card = MagicMock()
        mock_card.id = "card-full-id"
        mock_card.short_id = 123

        mock_list = MagicMock()
        mock_list.list_cards.return_value = [mock_card]

        mock_board = MagicMock()
        mock_board.all_lists.return_value = [mock_list]
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        card, lst = service.find_card("123")
        assert card == mock_card

    def test_find_card_with_prefix(self, mock_trello_module):
        """Test finding card with TRELLO- prefix."""
        _, mock_client = mock_trello_module

        mock_card = MagicMock()
        mock_card.id = "card-full-id"
        mock_card.short_id = 456

        mock_list = MagicMock()
        mock_list.list_cards.return_value = [mock_card]

        mock_board = MagicMock()
        mock_board.all_lists.return_value = [mock_list]
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        card, lst = service.find_card("TRELLO-456")
        assert card == mock_card

    def test_find_card_not_found(self, mock_trello_module):
        """Test finding non-existent card."""
        _, mock_client = mock_trello_module

        mock_list = MagicMock()
        mock_list.list_cards.return_value = []

        mock_board = MagicMock()
        mock_board.all_lists.return_value = [mock_list]
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        card, lst = service.find_card("999")
        assert card is None
        assert lst is None


class TestBoardStructure:
    """Tests for get_board_structure method."""

    @pytest.fixture
    def mock_trello_module(self):
        """Mock the py-trello module."""
        mock_client_class = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        with patch.dict('sys.modules', {'trello': MagicMock(TrelloClient=mock_client_class)}):
            yield mock_client_class, mock_client_instance

    def test_get_board_structure(self, mock_trello_module):
        """Test getting complete board structure."""
        _, mock_client = mock_trello_module

        # Setup mock board
        mock_board = MagicMock()

        # Mock lists
        mock_list1 = MagicMock()
        mock_list1.name = "Backlog"
        mock_list1.id = "list-1"
        mock_list2 = MagicMock()
        mock_list2.name = "In Progress"
        mock_list2.id = "list-2"
        mock_board.all_lists.return_value = [mock_list1, mock_list2]

        # Mock custom fields
        mock_field = MagicMock()
        mock_field.id = "field-1"
        mock_field.name = "Status"
        mock_field.field_type = "list"
        mock_field.list_options = {"opt1": "Enqueued", "opt2": "In Progress"}
        mock_board.get_custom_field_definitions.return_value = [mock_field]

        # Mock labels
        mock_label = MagicMock()
        mock_label.id = "label-1"
        mock_label.name = "Backend"
        mock_label.color = "blue"
        mock_board.get_labels.return_value = [mock_label]

        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        structure = service.get_board_structure()

        assert "lists" in structure
        assert "custom_fields" in structure
        assert "labels" in structure
        assert structure["lists"]["Backlog"] == "list-1"
        assert structure["lists"]["In Progress"] == "list-2"
        assert structure["custom_fields"]["Status"]["id"] == "field-1"
        assert structure["custom_fields"]["Status"]["type"] == "list"
        assert structure["labels"]["Backend"] == "label-1"

    def test_get_board_structure_raises_without_board(self, mock_trello_module):
        """Test get_board_structure raises if board not set."""
        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        with pytest.raises(ValueError, match="Board not set"):
            service.get_board_structure()

    def test_get_board_structure_skips_unnamed_labels(self, mock_trello_module):
        """Test get_board_structure skips labels without names."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()
        mock_board.all_lists.return_value = []
        mock_board.get_custom_field_definitions.return_value = []

        # Mock labels - one named, one unnamed
        mock_label1 = MagicMock()
        mock_label1.id = "label-1"
        mock_label1.name = "Backend"
        mock_label1.color = "blue"
        mock_label2 = MagicMock()
        mock_label2.id = "label-2"
        mock_label2.name = None  # Unnamed label
        mock_label2.color = "red"
        mock_board.get_labels.return_value = [mock_label1, mock_label2]

        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        structure = service.get_board_structure()

        assert len(structure["labels"]) == 1
        assert "Backend" in structure["labels"]


class TestSetCardStatus:
    """Tests for set_card_status method."""

    @pytest.fixture
    def mock_trello_module(self):
        """Mock the py-trello module."""
        mock_client_class = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        with patch.dict('sys.modules', {'trello': MagicMock(TrelloClient=mock_client_class)}):
            yield mock_client_class, mock_client_instance

    def test_set_card_status_success(self, mock_trello_module):
        """Test setting card status successfully."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()

        # Mock Status custom field
        mock_field = MagicMock()
        mock_field.id = "status-field-id"
        mock_field.name = "Status"
        mock_field.field_type = "list"
        mock_field.list_options = {"opt1": "Enqueued", "opt2": "In Progress", "opt3": "Done"}
        mock_board.get_custom_field_definitions.return_value = [mock_field]
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        mock_card = MagicMock()
        mock_card.id = "card-123"

        result = service.set_card_status(mock_card, "Done")

        assert result is True
        mock_client.fetch_json.assert_called_once()

    def test_set_card_status_field_not_found(self, mock_trello_module):
        """Test set_card_status when Status field doesn't exist."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()
        mock_board.get_custom_field_definitions.return_value = []
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        mock_card = MagicMock()
        result = service.set_card_status(mock_card, "Done")

        assert result is False

    def test_set_card_status_wrong_field_type(self, mock_trello_module):
        """Test set_card_status when Status field is not a list type."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()

        # Mock Status field as text type (wrong)
        mock_field = MagicMock()
        mock_field.id = "status-field-id"
        mock_field.name = "Status"
        mock_field.field_type = "text"  # Should be 'list'
        mock_field.list_options = {}
        mock_board.get_custom_field_definitions.return_value = [mock_field]
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        mock_card = MagicMock()
        result = service.set_card_status(mock_card, "Done")

        assert result is False

    def test_set_card_status_custom_field_name(self, mock_trello_module):
        """Test set_card_status with custom field name."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()

        # Mock custom status field with different name
        mock_field = MagicMock()
        mock_field.id = "custom-status-field"
        mock_field.name = "TaskStatus"
        mock_field.field_type = "list"
        mock_field.list_options = {"opt1": "Open", "opt2": "Closed"}
        mock_board.get_custom_field_definitions.return_value = [mock_field]
        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")
        service.set_board("board-123")

        mock_card = MagicMock()
        mock_card.id = "card-123"

        result = service.set_card_status(mock_card, "Closed", status_field_name="TaskStatus")

        assert result is True


class TestBoardTemplates:
    """Tests for board template copy functionality."""

    @pytest.fixture
    def mock_trello_module(self):
        """Mock the py-trello module."""
        mock_client_class = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        with patch.dict('sys.modules', {'trello': MagicMock(TrelloClient=mock_client_class)}):
            yield mock_client_class, mock_client_instance

    def test_find_board_by_name_found(self, mock_trello_module):
        """Test finding a board by name."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()
        mock_board.name = "BPS AI Project Template"
        mock_board.closed = False

        mock_client.list_boards.return_value = [mock_board]

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.find_board_by_name("BPS AI Project Template")

        assert result == mock_board

    def test_find_board_by_name_case_insensitive(self, mock_trello_module):
        """Test finding a board by name is case-insensitive."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()
        mock_board.name = "BPS AI Project Template"
        mock_board.closed = False

        mock_client.list_boards.return_value = [mock_board]

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.find_board_by_name("bps ai project template")

        assert result == mock_board

    def test_find_board_by_name_not_found(self, mock_trello_module):
        """Test finding a non-existent board returns None."""
        _, mock_client = mock_trello_module

        mock_client.list_boards.return_value = []

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.find_board_by_name("Non-existent Board")

        assert result is None

    def test_find_board_by_name_skips_closed(self, mock_trello_module):
        """Test that closed boards are not found."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()
        mock_board.name = "Archived Template"
        mock_board.closed = True  # Closed/archived

        mock_client.list_boards.return_value = [mock_board]

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.find_board_by_name("Archived Template")

        assert result is None

    def test_copy_board_from_template_success(self, mock_trello_module):
        """Test successfully copying a board from template."""
        _, mock_client = mock_trello_module

        # Setup template board
        mock_template = MagicMock()
        mock_template.id = "template-123"
        mock_template.name = "BPS AI Project Template"
        mock_template.closed = False

        # Setup new board
        mock_new_board = MagicMock()
        mock_new_board.id = "new-board-456"
        mock_new_board.name = "My New Project"
        mock_new_board.url = "https://trello.com/b/new-board"

        mock_client.list_boards.return_value = [mock_template]
        mock_client.fetch_json.return_value = {'id': 'new-board-456'}
        mock_client.get_board.return_value = mock_new_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.copy_board_from_template(
            template_name="BPS AI Project Template",
            new_board_name="My New Project"
        )

        assert result == mock_new_board
        mock_client.fetch_json.assert_called_once()
        call_args = mock_client.fetch_json.call_args
        assert call_args[0][0] == '/boards'
        assert call_args[1]['post_args']['name'] == 'My New Project'
        assert call_args[1]['post_args']['idBoardSource'] == 'template-123'
        assert 'customFields' in call_args[1]['post_args']['keepFromSource']
        assert 'labels' in call_args[1]['post_args']['keepFromSource']

    def test_copy_board_from_template_with_cards(self, mock_trello_module):
        """Test copying a board with cards preserved."""
        _, mock_client = mock_trello_module

        mock_template = MagicMock()
        mock_template.id = "template-123"
        mock_template.name = "Template"
        mock_template.closed = False

        mock_new_board = MagicMock()
        mock_new_board.id = "new-board-456"

        mock_client.list_boards.return_value = [mock_template]
        mock_client.fetch_json.return_value = {'id': 'new-board-456'}
        mock_client.get_board.return_value = mock_new_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.copy_board_from_template(
            template_name="Template",
            new_board_name="New Board",
            keep_cards=True
        )

        assert result == mock_new_board
        call_args = mock_client.fetch_json.call_args
        keep_from_source = call_args[1]['post_args']['keepFromSource']
        assert 'cards' in keep_from_source
        assert 'checklists' in keep_from_source

    def test_copy_board_from_template_not_found(self, mock_trello_module):
        """Test copying from non-existent template raises error."""
        _, mock_client = mock_trello_module

        mock_client.list_boards.return_value = []

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        with pytest.raises(ValueError, match="Template board .* not found"):
            service.copy_board_from_template(
                template_name="Non-existent Template",
                new_board_name="New Board"
            )

    def test_copy_board_from_template_api_error(self, mock_trello_module):
        """Test handling API error when copying board."""
        _, mock_client = mock_trello_module

        mock_template = MagicMock()
        mock_template.id = "template-123"
        mock_template.name = "Template"
        mock_template.closed = False

        mock_client.list_boards.return_value = [mock_template]
        mock_client.fetch_json.side_effect = Exception("API Error")

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.copy_board_from_template(
            template_name="Template",
            new_board_name="New Board"
        )

        assert result is None

    def test_get_board_info(self, mock_trello_module):
        """Test getting board info."""
        _, mock_client = mock_trello_module

        mock_board = MagicMock()
        mock_board.id = "board-123"
        mock_board.name = "Test Board"
        mock_board.url = "https://trello.com/b/board-123"

        # Mock lists
        mock_list = MagicMock()
        mock_list.name = "Backlog"
        mock_list.id = "list-1"
        mock_board.all_lists.return_value = [mock_list]

        # Mock custom fields
        mock_field = MagicMock()
        mock_field.id = "field-1"
        mock_field.name = "Status"
        mock_field.field_type = "list"
        mock_field.list_options = {}
        mock_board.get_custom_field_definitions.return_value = [mock_field]

        # Mock labels
        mock_label = MagicMock()
        mock_label.id = "label-1"
        mock_label.name = "Bug"
        mock_label.color = "red"
        mock_board.get_labels.return_value = [mock_label]

        mock_client.get_board.return_value = mock_board

        from bpsai_pair.trello.client import TrelloService
        service = TrelloService(api_key="key", token="token")

        result = service.get_board_info(mock_board)

        assert result['id'] == "board-123"
        assert result['name'] == "Test Board"
        assert result['lists'] == ["Backlog"]
        assert result['custom_fields'] == ["Status"]
        assert result['labels'] == ["Bug"]
        assert result['list_count'] == 1
        assert result['custom_field_count'] == 1
        assert result['label_count'] == 1
