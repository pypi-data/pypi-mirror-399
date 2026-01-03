"""Tests for Trello auth module."""
import pytest
import json
from pathlib import Path
from unittest.mock import patch

from bpsai_pair.trello.auth import (
    store_token,
    load_token,
    clear_token,
    is_connected,
    TOKEN_STORE_VERSION,
)


class TestTrelloAuth:
    """Tests for Trello authentication functions."""

    def test_store_and_load_token(self, tmp_path):
        """Test storing and loading credentials."""
        tokens_dir = tmp_path / ".trello_codex_tokens"
        token_file = tokens_dir / "trello_token.json"

        with patch('bpsai_pair.trello.auth.TOKENS_FOLDER', tokens_dir):
            with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
                # Store
                store_token(token="my-token", api_key="my-api-key")

                # Verify file created
                assert token_file.exists()

                # Load
                data = load_token()
                assert data["token"] == "my-token"
                assert data["api_key"] == "my-api-key"
                assert data["version"] == TOKEN_STORE_VERSION

    def test_load_token_missing_file(self, tmp_path):
        """Test loading when no token file exists."""
        with patch('bpsai_pair.trello.auth.TOKEN_FILE', tmp_path / "nonexistent.json"):
            result = load_token()
            assert result is None

    def test_load_token_invalid_json(self, tmp_path):
        """Test loading when token file has invalid JSON."""
        token_file = tmp_path / "trello_token.json"
        token_file.write_text("not valid json")

        with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
            result = load_token()
            assert result is None

    def test_load_token_missing_fields(self, tmp_path):
        """Test loading when token file is missing required fields."""
        token_file = tmp_path / "trello_token.json"
        token_file.write_text(json.dumps({"token": "test"}))  # Missing api_key

        with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
            result = load_token()
            assert result is None

    def test_clear_token(self, tmp_path):
        """Test clearing credentials."""
        tokens_dir = tmp_path / ".trello_codex_tokens"
        tokens_dir.mkdir()
        token_file = tokens_dir / "trello_token.json"
        token_file.write_text('{"token": "test", "api_key": "key"}')

        with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
            clear_token()
            assert not token_file.exists()

    def test_clear_token_nonexistent(self, tmp_path):
        """Test clearing when no token file exists."""
        with patch('bpsai_pair.trello.auth.TOKEN_FILE', tmp_path / "nonexistent.json"):
            # Should not raise
            clear_token()

    def test_is_connected_true(self, tmp_path):
        """Test connection check when connected."""
        tokens_dir = tmp_path / ".trello_codex_tokens"
        tokens_dir.mkdir()
        token_file = tokens_dir / "trello_token.json"
        token_file.write_text(json.dumps({
            "token": "test-token",
            "api_key": "test-api-key",
            "version": 2
        }))

        with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
            assert is_connected() == True

    def test_is_connected_false(self, tmp_path):
        """Test connection check when not connected."""
        with patch('bpsai_pair.trello.auth.TOKEN_FILE', tmp_path / "nonexistent.json"):
            assert is_connected() == False


class TestTrelloAuthUnicode:
    """Tests for Unicode handling in Trello auth module."""

    def test_store_and_load_unicode_token(self, tmp_path):
        """Test storing and loading credentials with Unicode values."""
        tokens_dir = tmp_path / ".trello_codex_tokens"
        token_file = tokens_dir / "trello_token.json"

        with patch('bpsai_pair.trello.auth.TOKENS_FOLDER', tokens_dir):
            with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
                # Store token with Unicode chars (emojis, Japanese, accented)
                store_token(token="🚀-token-日本語", api_key="api-key-émoji")

                # Verify file created
                assert token_file.exists()

                # Verify raw file content contains actual Unicode (not escaped)
                raw_content = token_file.read_text(encoding="utf-8")
                assert "🚀" in raw_content
                assert "日本語" in raw_content
                assert "émoji" in raw_content

                # Load and verify
                data = load_token()
                assert data["token"] == "🚀-token-日本語"
                assert data["api_key"] == "api-key-émoji"
                assert data["version"] == TOKEN_STORE_VERSION

    def test_load_unicode_token_file(self, tmp_path):
        """Test loading token file with Unicode content."""
        token_file = tmp_path / "trello_token.json"
        token_file.write_text(
            '{"token": "🚀日本語", "api_key": "clé-émoji", "version": 2}',
            encoding="utf-8"
        )

        with patch('bpsai_pair.trello.auth.TOKEN_FILE', token_file):
            data = load_token()
            assert data["token"] == "🚀日本語"
            assert data["api_key"] == "clé-émoji"
