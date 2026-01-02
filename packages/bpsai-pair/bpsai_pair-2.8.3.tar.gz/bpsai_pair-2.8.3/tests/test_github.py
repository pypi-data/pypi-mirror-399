"""Tests for GitHub integration."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

from bpsai_pair.github.client import RepoInfo, GitHubClient, GitHubService
from bpsai_pair.github.pr import PRInfo, PRManager, PRWorkflow


class TestRepoInfo:
    """Tests for RepoInfo parsing."""

    def test_parse_ssh_url(self):
        """Test parsing SSH remote URL."""
        url = "git@github.com:owner/repo.git"
        info = RepoInfo.from_remote_url(url)

        assert info is not None
        assert info.owner == "owner"
        assert info.name == "repo"
        assert info.full_name == "owner/repo"
        assert info.url == "https://github.com/owner/repo"

    def test_parse_https_url(self):
        """Test parsing HTTPS remote URL."""
        url = "https://github.com/owner/repo.git"
        info = RepoInfo.from_remote_url(url)

        assert info is not None
        assert info.owner == "owner"
        assert info.name == "repo"
        assert info.full_name == "owner/repo"

    def test_parse_https_url_no_git_suffix(self):
        """Test parsing HTTPS URL without .git suffix."""
        url = "https://github.com/owner/repo"
        info = RepoInfo.from_remote_url(url)

        assert info is not None
        assert info.full_name == "owner/repo"

    def test_parse_invalid_url(self):
        """Test parsing invalid URL returns None."""
        url = "https://gitlab.com/owner/repo"
        info = RepoInfo.from_remote_url(url)

        assert info is None


class TestGitHubClient:
    """Tests for GitHubClient."""

    def test_init_with_token(self):
        """Test initializing with token."""
        client = GitHubClient(token="test-token")
        assert client.token == "test-token"

    def test_init_from_env(self):
        """Test initializing from environment."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "env-token"}):
            client = GitHubClient()
            assert client.token == "env-token"

    @patch("subprocess.run")
    def test_gh_cli_available_true(self, mock_run):
        """Test gh CLI detection when available."""
        mock_run.return_value = MagicMock(returncode=0)

        client = GitHubClient()
        assert client.gh_cli_available is True

    @patch("subprocess.run")
    def test_gh_cli_available_false(self, mock_run):
        """Test gh CLI detection when not available."""
        mock_run.return_value = MagicMock(returncode=1)

        client = GitHubClient()
        assert client.gh_cli_available is False

    @patch("subprocess.run")
    def test_gh_cli_not_installed(self, mock_run):
        """Test gh CLI detection when not installed."""
        mock_run.side_effect = FileNotFoundError

        client = GitHubClient()
        assert client.gh_cli_available is False

    @patch("subprocess.run")
    def test_get_repo_info(self, mock_run):
        """Test getting repo info from git remote."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="git@github.com:owner/repo.git\n"
        )

        client = GitHubClient()
        info = client.get_repo_info()

        assert info is not None
        assert info.full_name == "owner/repo"

    @patch("subprocess.run")
    def test_get_current_branch(self, mock_run):
        """Test getting current branch."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="feature/test\n"
        )

        client = GitHubClient()
        branch = client.get_current_branch()

        assert branch == "feature/test"

    @patch("subprocess.run")
    def test_create_pr_success(self, mock_run):
        """Test creating a PR."""
        # First call for gh auth status, second for pr create
        mock_run.side_effect = [
            MagicMock(returncode=0),  # gh auth status
            MagicMock(returncode=0, stdout="https://github.com/owner/repo/pull/123\n"),
        ]

        client = GitHubClient()
        result = client.create_pr(
            title="Test PR",
            body="Test body",
        )

        assert result is not None
        assert result["number"] == 123
        assert "123" in result["url"]


class TestGitHubService:
    """Tests for GitHubService."""

    @patch.object(GitHubClient, "get_repo_info")
    def test_is_github_repo_true(self, mock_get_repo):
        """Test is_github_repo when in a GitHub repo."""
        mock_get_repo.return_value = RepoInfo(
            owner="owner",
            name="repo",
            full_name="owner/repo"
        )

        service = GitHubService()
        assert service.is_github_repo() is True

    @patch.object(GitHubClient, "get_repo_info")
    def test_is_github_repo_false(self, mock_get_repo):
        """Test is_github_repo when not in a GitHub repo."""
        mock_get_repo.return_value = None

        service = GitHubService()
        assert service.is_github_repo() is False

    @patch.object(GitHubClient, "get_repo_info")
    @patch.object(GitHubClient, "gh_cli_available", new_callable=PropertyMock)
    def test_healthcheck(self, mock_gh_cli, mock_get_repo):
        """Test healthcheck."""
        mock_gh_cli.return_value = True
        mock_get_repo.return_value = RepoInfo(
            owner="owner",
            name="repo",
            full_name="owner/repo"
        )

        service = GitHubService()
        health = service.healthcheck()

        assert health["ok"] is True
        assert health["gh_cli"] is True
        assert health["repo"] == "owner/repo"


class TestPRInfo:
    """Tests for PRInfo."""

    def test_from_gh_json(self):
        """Test creating PRInfo from gh JSON."""
        data = {
            "number": 123,
            "title": "[TASK-001] Test PR",
            "url": "https://github.com/owner/repo/pull/123",
            "state": "OPEN",
            "reviewDecision": "APPROVED",
            "mergeable": "MERGEABLE",
        }

        pr = PRInfo.from_gh_json(data)

        assert pr.number == 123
        assert pr.task_id == "TASK-001"
        assert pr.state == "open"
        assert pr.is_approved() is True

    def test_task_id_extraction(self):
        """Test extracting task ID from title."""
        data = {
            "number": 1,
            "title": "TASK-042 Fix the bug",
            "url": "http://example.com",
            "state": "open",
        }

        pr = PRInfo.from_gh_json(data)
        assert pr.task_id == "TASK-042"

    def test_task_id_with_brackets(self):
        """Test task ID with brackets in title."""
        data = {
            "number": 1,
            "title": "[TASK-100] Add feature",
            "url": "http://example.com",
            "state": "open",
        }

        pr = PRInfo.from_gh_json(data)
        assert pr.task_id == "TASK-100"

    def test_no_task_id(self):
        """Test title without task ID."""
        data = {
            "number": 1,
            "title": "Regular PR without task",
            "url": "http://example.com",
            "state": "open",
        }

        pr = PRInfo.from_gh_json(data)
        assert pr.task_id is None

    def test_is_ready_to_merge(self):
        """Test ready to merge check."""
        pr = PRInfo(
            number=1,
            title="Test",
            url="http://example.com",
            state="open",
            draft=False,
            mergeable=True,
            review_decision="APPROVED",
        )

        assert pr.is_ready_to_merge() is True

    def test_not_ready_to_merge_draft(self):
        """Test draft PR is not ready."""
        pr = PRInfo(
            number=1,
            title="Test",
            url="http://example.com",
            state="open",
            draft=True,
            mergeable=True,
            review_decision="APPROVED",
        )

        assert pr.is_ready_to_merge() is False


class TestPRManager:
    """Tests for PRManager."""

    def test_create_pr_for_task(self, tmp_path):
        """Test creating PR for a task."""
        # Create .paircoder/tasks directory
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        # Create mock service and client
        mock_client = MagicMock()
        mock_client.create_pr.return_value = {
            "number": 42,
            "url": "https://github.com/owner/repo/pull/42",
        }

        mock_service = MagicMock()
        mock_service.client = mock_client

        manager = PRManager(
            service=mock_service,
            project_root=tmp_path,
            paircoder_dir=paircoder_dir,
        )

        pr = manager.create_pr_for_task(
            task_id="TASK-001",
            summary="Test summary",
        )

        assert pr is not None
        assert pr.number == 42
        assert pr.task_id == "TASK-001"

    def test_get_pr_for_task(self, tmp_path):
        """Test finding PR for a task."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        mock_client = MagicMock()
        mock_client.list_prs.return_value = [
            {"number": 1, "title": "Other PR"},
            {"number": 2, "title": "[TASK-001] Test PR"},
        ]
        mock_client.get_pr_status.return_value = {
            "number": 2,
            "title": "[TASK-001] Test PR",
            "url": "http://example.com/2",
            "state": "OPEN",
        }

        mock_service = MagicMock()
        mock_service.client = mock_client

        manager = PRManager(
            service=mock_service,
            project_root=tmp_path,
            paircoder_dir=paircoder_dir,
        )

        pr = manager.get_pr_for_task("TASK-001")

        assert pr is not None
        assert pr.number == 2
        assert pr.task_id == "TASK-001"


class TestPRWorkflow:
    """Tests for PRWorkflow."""

    def test_on_task_complete_creates_pr(self, tmp_path):
        """Test on_task_complete creates PR on feature branch."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()
        (paircoder_dir / "tasks").mkdir()

        mock_client = MagicMock()
        mock_client.get_default_branch.return_value = "main"
        mock_client.create_pr.return_value = {
            "number": 1,
            "url": "http://example.com/1",
        }

        mock_service = MagicMock()
        mock_service.client = mock_client
        mock_service.get_current_branch.return_value = "feature/test"

        manager = PRManager(
            service=mock_service,
            project_root=tmp_path,
            paircoder_dir=paircoder_dir,
        )

        # Mock get_pr_for_branch to return None (no existing PR)
        manager.get_pr_for_branch = MagicMock(return_value=None)

        workflow = PRWorkflow(manager)
        pr = workflow.on_task_complete("TASK-001")

        assert pr is not None
        assert pr.task_id == "TASK-001"

    def test_on_task_complete_skips_main(self, tmp_path):
        """Test on_task_complete skips main branch."""
        paircoder_dir = tmp_path / ".paircoder"
        paircoder_dir.mkdir()

        mock_client = MagicMock()
        mock_client.get_default_branch.return_value = "main"

        mock_service = MagicMock()
        mock_service.client = mock_client
        mock_service.get_current_branch.return_value = "main"

        manager = PRManager(
            service=mock_service,
            project_root=tmp_path,
            paircoder_dir=paircoder_dir,
        )
        manager.create_pr_for_task = MagicMock()

        workflow = PRWorkflow(manager)
        pr = workflow.on_task_complete("TASK-001")

        assert pr is None
        manager.create_pr_for_task.assert_not_called()
