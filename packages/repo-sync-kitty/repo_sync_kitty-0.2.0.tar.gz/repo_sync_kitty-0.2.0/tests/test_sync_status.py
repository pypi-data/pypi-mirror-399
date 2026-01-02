"""Unit tests for sync and status command internals."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from repo_sync_kitty.commands.status import (
    RepoStatus,
    create_status_table,
    get_repo_status,
)
from repo_sync_kitty.commands.sync import (
    SyncResult,
    SyncSummary,
    print_summary,
    sync_repo,
)
from repo_sync_kitty.config.loader import ResolvedProject


@pytest.fixture
def sample_project() -> ResolvedProject:
    """Create a sample resolved project for testing."""
    return ResolvedProject(
        slug="owner/repo",
        path=Path("test/repo"),
        remote_name="origin",
        remote_url="https://github.com/",
        branch="main",
        status="active",
        parallelism=4,
        timeout=300,
    )


@pytest.fixture
def archived_project() -> ResolvedProject:
    """Create an archived project for testing."""
    return ResolvedProject(
        slug="owner/old",
        path=Path("test/old"),
        remote_name="origin",
        remote_url="https://github.com/",
        branch="main",
        status="archived",
        parallelism=4,
        timeout=300,
    )


class TestRepoStatus:
    """Tests for RepoStatus dataclass."""

    def test_has_issues_false_when_empty(self, sample_project: ResolvedProject) -> None:
        """Test has_issues is False when no issues."""
        status = RepoStatus(project=sample_project, exists=True, issues=[])
        assert not status.has_issues

    def test_has_issues_true_when_issues(self, sample_project: ResolvedProject) -> None:
        """Test has_issues is True when issues exist."""
        status = RepoStatus(
            project=sample_project, exists=True, issues=["uncommitted changes"]
        )
        assert status.has_issues

    def test_status_label_missing(self, sample_project: ResolvedProject) -> None:
        """Test status_label returns 'missing' when not exists."""
        status = RepoStatus(project=sample_project, exists=False)
        assert status.status_label == "missing"

    def test_status_label_detached(self, sample_project: ResolvedProject) -> None:
        """Test status_label returns 'detached' when HEAD detached."""
        status = RepoStatus(project=sample_project, exists=True, is_detached=True)
        assert status.status_label == "detached"

    def test_status_label_dirty(self, sample_project: ResolvedProject) -> None:
        """Test status_label returns 'dirty' when not clean."""
        status = RepoStatus(project=sample_project, exists=True, is_clean=False)
        assert status.status_label == "dirty"

    def test_status_label_ahead(self, sample_project: ResolvedProject) -> None:
        """Test status_label returns 'ahead' when ahead of remote."""
        status = RepoStatus(project=sample_project, exists=True, ahead=3)
        assert status.status_label == "ahead"

    def test_status_label_behind(self, sample_project: ResolvedProject) -> None:
        """Test status_label returns 'behind' when behind remote."""
        status = RepoStatus(project=sample_project, exists=True, behind=2)
        assert status.status_label == "behind"

    def test_status_label_ok(self, sample_project: ResolvedProject) -> None:
        """Test status_label returns 'ok' when all good."""
        status = RepoStatus(project=sample_project, exists=True)
        assert status.status_label == "ok"


class TestGetRepoStatus:
    """Tests for get_repo_status function."""

    def test_get_repo_status_not_exists(
        self, sample_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test get_repo_status when repo doesn't exist."""
        status = get_repo_status(sample_project, tmp_path)
        assert not status.exists
        assert "not cloned" in status.issues

    def test_get_repo_status_exists_clean(
        self, sample_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test get_repo_status for clean existing repo."""
        repo_path = tmp_path / sample_project.path
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()

        with patch("repo_sync_kitty.commands.status.RepoManager") as MockMgr:
            mock_mgr = MagicMock()
            mock_mgr.exists.return_value = True
            mock_mgr.get_current_branch.return_value = "main"
            mock_mgr.is_detached.return_value = False
            mock_mgr.is_clean.return_value = True
            mock_mgr.get_in_progress_operation.return_value = None
            mock_mgr.get_ahead_behind.return_value = (0, 0)
            mock_mgr.has_staged_changes.return_value = False
            mock_mgr.has_modified_files.return_value = False
            mock_mgr.has_untracked_files.return_value = False
            # Remote URL matches expected clone URL
            mock_mgr.get_remote_urls.return_value = {
                "origin": "https://github.com/owner/repo.git"
            }
            MockMgr.return_value = mock_mgr

            status = get_repo_status(sample_project, tmp_path)

        assert status.exists
        assert status.is_clean
        assert not status.has_issues

    def test_get_repo_status_wrong_branch(
        self, sample_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test get_repo_status detects wrong branch."""
        with patch("repo_sync_kitty.commands.status.RepoManager") as MockMgr:
            mock_mgr = MagicMock()
            mock_mgr.exists.return_value = True
            mock_mgr.get_current_branch.return_value = "develop"
            mock_mgr.is_detached.return_value = False
            mock_mgr.is_clean.return_value = True
            mock_mgr.get_in_progress_operation.return_value = None
            mock_mgr.get_ahead_behind.return_value = (0, 0)
            mock_mgr.get_remote_urls.return_value = {
                "origin": "https://github.com/owner/repo"
            }
            MockMgr.return_value = mock_mgr

            status = get_repo_status(sample_project, tmp_path)

        assert status.has_issues
        assert any("develop" in issue and "main" in issue for issue in status.issues)


class TestCreateStatusTable:
    """Tests for create_status_table function."""

    def test_creates_table_with_issues(
        self, sample_project: ResolvedProject
    ) -> None:
        """Test table includes repos with issues."""
        statuses = [
            RepoStatus(
                project=sample_project,
                exists=False,
                issues=["not cloned"],
            )
        ]
        table = create_status_table(statuses, show_all=False)
        assert table.title == "Repository Status"
        assert len(table.columns) == 4

    def test_show_all_includes_ok_repos(
        self, sample_project: ResolvedProject
    ) -> None:
        """Test --all option shows repos without issues."""
        statuses = [
            RepoStatus(project=sample_project, exists=True, issues=[])
        ]
        # Default should skip repos without issues
        table = create_status_table(statuses, show_all=False)
        assert table.row_count == 0

        # --all should include them
        table = create_status_table(statuses, show_all=True)
        assert table.row_count == 1


class TestSyncResult:
    """Tests for SyncResult dataclass."""

    def test_sync_result_success(self, sample_project: ResolvedProject) -> None:
        """Test SyncResult for successful operation."""
        result = SyncResult(
            project=sample_project,
            action="cloned",
            success=True,
            message="cloned main",
        )
        assert result.success
        assert result.action == "cloned"


class TestSyncSummary:
    """Tests for SyncSummary dataclass."""

    def test_summary_counts(self, sample_project: ResolvedProject) -> None:
        """Test SyncSummary counts operations correctly."""
        summary = SyncSummary(
            results=[
                SyncResult(project=sample_project, action="cloned", success=True),
                SyncResult(project=sample_project, action="fetched", success=True),
                SyncResult(project=sample_project, action="pulled", success=True),
                SyncResult(project=sample_project, action="skipped", success=True),
                SyncResult(project=sample_project, action="error", success=False, message="fail"),
            ]
        )
        assert summary.total == 5
        assert summary.cloned == 1
        assert summary.fetched == 1
        assert summary.pulled == 1
        assert summary.skipped == 1
        assert len(summary.errors) == 1


class TestSyncRepo:
    """Tests for sync_repo function."""

    def test_sync_repo_archived_existing_skips_fetch(
        self, archived_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test sync_repo skips fetch/pull for existing archived repos."""
        # Create repo directory so it "exists"
        repo_path = tmp_path / archived_project.path
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()

        with patch("repo_sync_kitty.commands.sync.RepoManager") as MockMgr:
            mock_mgr = MagicMock()
            mock_mgr.exists.return_value = True
            MockMgr.return_value = mock_mgr

            result = sync_repo(archived_project, tmp_path)
            assert result.action == "skipped"
            assert "archived" in result.message

    def test_sync_repo_archived_missing_clones(
        self, archived_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test sync_repo clones missing archived repos."""
        result = sync_repo(archived_project, tmp_path, dry_run=True)
        assert result.action == "cloned"
        assert result.success
        assert "would clone" in result.message

    def test_sync_repo_dry_run_clone(
        self, sample_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test sync_repo dry run for missing repo."""
        result = sync_repo(sample_project, tmp_path, dry_run=True)
        assert result.action == "cloned"
        assert result.success
        assert "would clone" in result.message

    def test_sync_repo_dry_run_fetch(
        self, sample_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test sync_repo dry run for existing repo."""
        repo_path = tmp_path / sample_project.path
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()

        with patch("repo_sync_kitty.commands.sync.RepoManager") as MockMgr:
            mock_mgr = MagicMock()
            mock_mgr.exists.return_value = True
            MockMgr.return_value = mock_mgr

            result = sync_repo(sample_project, tmp_path, dry_run=True)

        assert result.action == "fetched"
        assert "would fetch" in result.message

    def test_sync_repo_fetch_only_skips_missing(
        self, sample_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test sync_repo with fetch_only skips missing repos."""
        result = sync_repo(sample_project, tmp_path, fetch_only=True)
        assert result.action == "skipped"
        assert "fetch-only" in result.message

    def test_sync_repo_clone_only_skips_existing(
        self, sample_project: ResolvedProject, tmp_path: Path
    ) -> None:
        """Test sync_repo with clone_only skips existing repos."""
        repo_path = tmp_path / sample_project.path
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()

        with patch("repo_sync_kitty.commands.sync.RepoManager") as MockMgr:
            mock_mgr = MagicMock()
            mock_mgr.exists.return_value = True
            MockMgr.return_value = mock_mgr

            result = sync_repo(sample_project, tmp_path, clone_only=True)

        assert result.action == "skipped"
        assert "clone-only" in result.message


class TestPrintSummary:
    """Tests for print_summary function."""

    def test_print_summary_dry_run(
        self, sample_project: ResolvedProject, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_summary shows dry run message."""
        summary = SyncSummary(
            results=[
                SyncResult(project=sample_project, action="cloned", success=True),
            ]
        )
        print_summary(summary, dry_run=True)
        captured = capsys.readouterr()
        assert "Dry run" in captured.out

    def test_print_summary_with_errors(
        self, sample_project: ResolvedProject, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test print_summary shows error details."""
        summary = SyncSummary(
            results=[
                SyncResult(
                    project=sample_project,
                    action="error",
                    success=False,
                    message="clone failed",
                ),
            ]
        )
        print_summary(summary, dry_run=False)
        captured = capsys.readouterr()
        assert "error" in captured.out.lower()
        assert "clone failed" in captured.out
