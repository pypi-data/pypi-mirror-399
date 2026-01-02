"""Tests for git operations."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from repo_sync_kitty.git.operations import (
    GitError,
    RepoManager,
)
from repo_sync_kitty.git.retry import RetryConfig, RetryManager, with_retry
from repo_sync_kitty.git.safety import SafetyChecker, SafetyReport, check_safe_to_pull


class TestRepoManager:
    """Tests for RepoManager class."""

    def test_exists_returns_false_for_nonexistent_path(self, tmp_path: Path) -> None:
        """Test exists() returns False when path doesn't exist."""
        mgr = RepoManager(tmp_path / "nonexistent")
        assert not mgr.exists()

    def test_exists_returns_false_for_non_git_directory(self, tmp_path: Path) -> None:
        """Test exists() returns False for directory without .git."""
        repo_path = tmp_path / "not-a-repo"
        repo_path.mkdir()
        mgr = RepoManager(repo_path)
        assert not mgr.exists()

    def test_exists_returns_true_for_git_directory(self, tmp_path: Path) -> None:
        """Test exists() returns True when .git directory present."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)
        assert mgr.exists()

    def test_repo_property_raises_for_non_repo(self, tmp_path: Path) -> None:
        """Test repo property raises GitError for non-repo path."""
        mgr = RepoManager(tmp_path / "nonexistent")
        with pytest.raises(GitError):
            _ = mgr.repo

    def test_is_rebasing_false_when_no_rebase(self, tmp_path: Path) -> None:
        """Test is_rebasing() returns False when no rebase in progress."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)
        assert not mgr.is_rebasing()

    def test_is_rebasing_true_when_rebase_merge_exists(self, tmp_path: Path) -> None:
        """Test is_rebasing() returns True when rebase-merge exists."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "rebase-merge").mkdir()
        mgr = RepoManager(repo_path)
        assert mgr.is_rebasing()

    def test_is_rebasing_true_when_rebase_apply_exists(self, tmp_path: Path) -> None:
        """Test is_rebasing() returns True when rebase-apply exists."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "rebase-apply").mkdir()
        mgr = RepoManager(repo_path)
        assert mgr.is_rebasing()

    def test_is_merging_false_when_no_merge(self, tmp_path: Path) -> None:
        """Test is_merging() returns False when no merge in progress."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)
        assert not mgr.is_merging()

    def test_is_merging_true_when_merge_head_exists(self, tmp_path: Path) -> None:
        """Test is_merging() returns True when MERGE_HEAD exists."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "MERGE_HEAD").touch()
        mgr = RepoManager(repo_path)
        assert mgr.is_merging()

    def test_is_cherry_picking_false_when_no_cherry_pick(self, tmp_path: Path) -> None:
        """Test is_cherry_picking() returns False when no cherry-pick."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)
        assert not mgr.is_cherry_picking()

    def test_is_cherry_picking_true_when_cherry_pick_head_exists(
        self, tmp_path: Path
    ) -> None:
        """Test is_cherry_picking() returns True when CHERRY_PICK_HEAD exists."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "CHERRY_PICK_HEAD").touch()
        mgr = RepoManager(repo_path)
        assert mgr.is_cherry_picking()

    def test_get_in_progress_operation_none(self, tmp_path: Path) -> None:
        """Test get_in_progress_operation() returns None when clean."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)
        assert mgr.get_in_progress_operation() is None

    @pytest.mark.parametrize(
        "marker,expected",
        [
            ("rebase-merge", "rebase"),
            ("rebase-apply", "rebase"),
        ],
    )
    def test_get_in_progress_operation_rebase(
        self, tmp_path: Path, marker: str, expected: str
    ) -> None:
        """Test get_in_progress_operation() detects rebase."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / marker).mkdir()
        mgr = RepoManager(repo_path)
        assert mgr.get_in_progress_operation() == expected

    def test_get_in_progress_operation_merge(self, tmp_path: Path) -> None:
        """Test get_in_progress_operation() detects merge."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "MERGE_HEAD").touch()
        mgr = RepoManager(repo_path)
        assert mgr.get_in_progress_operation() == "merge"

    def test_get_in_progress_operation_cherry_pick(self, tmp_path: Path) -> None:
        """Test get_in_progress_operation() detects cherry-pick."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        git_dir = repo_path / ".git"
        git_dir.mkdir()
        (git_dir / "CHERRY_PICK_HEAD").touch()
        mgr = RepoManager(repo_path)
        assert mgr.get_in_progress_operation() == "cherry-pick"


class TestRepoManagerWithMockedRepo:
    """Tests for RepoManager using mocked GitPython."""

    def test_get_current_branch_returns_name(self, tmp_path: Path) -> None:
        """Test get_current_branch() returns branch name."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"
        mgr._repo = mock_repo

        assert mgr.get_current_branch() == "main"

    def test_get_current_branch_returns_none_when_detached(
        self, tmp_path: Path
    ) -> None:
        """Test get_current_branch() returns None when detached."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.head.is_detached = True
        mgr._repo = mock_repo

        assert mgr.get_current_branch() is None

    def test_get_remotes_returns_list(self, tmp_path: Path) -> None:
        """Test get_remotes() returns list of remote names."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_origin = MagicMock()
        mock_origin.name = "origin"
        mock_upstream = MagicMock()
        mock_upstream.name = "upstream"
        mock_repo = MagicMock()
        mock_repo.remotes = [mock_origin, mock_upstream]
        mgr._repo = mock_repo

        assert mgr.get_remotes() == ["origin", "upstream"]

    def test_is_clean_returns_true_when_clean(self, tmp_path: Path) -> None:
        """Test is_clean() returns True when no changes."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.is_dirty.return_value = False
        mgr._repo = mock_repo

        assert mgr.is_clean()
        mock_repo.is_dirty.assert_called_once_with(untracked_files=True)

    def test_is_clean_returns_false_when_dirty(self, tmp_path: Path) -> None:
        """Test is_clean() returns False when changes exist."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.is_dirty.return_value = True
        mgr._repo = mock_repo

        assert not mgr.is_clean()

    def test_is_detached_returns_true(self, tmp_path: Path) -> None:
        """Test is_detached() returns True when HEAD is detached."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.head.is_detached = True
        mgr._repo = mock_repo

        assert mgr.is_detached()


class TestSafetyReport:
    """Tests for SafetyReport dataclass."""

    def test_init_with_defaults(self) -> None:
        """Test SafetyReport default values are safe defaults."""
        report = SafetyReport()
        assert not report.safe_to_pull
        assert report.reasons == []
        assert report.current_branch is None
        assert report.expected_branch is None
        assert not report.is_clean
        assert not report.is_ahead
        assert report.in_progress_operation is None
        assert not report.is_detached

    def test_init_with_unsafe_conditions(self) -> None:
        """Test SafetyReport with multiple unsafe conditions."""
        report = SafetyReport(
            safe_to_pull=False,
            reasons=["uncommitted changes", "ahead of remote"],
            current_branch="main",
            is_ahead=True,
        )
        assert not report.safe_to_pull
        assert len(report.reasons) == 2
        assert "uncommitted changes" in report.reasons
        assert "ahead of remote" in report.reasons


class TestSafetyChecker:
    """Tests for SafetyChecker class."""

    def test_check_safe_when_clean(self, tmp_path: Path) -> None:
        """Test check returns safe when repo is clean."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        # Mock the repo
        mock_repo = MagicMock()
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"
        mock_repo.is_dirty.return_value = False
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = []
        mock_repo.refs = []
        mgr._repo = mock_repo

        checker = SafetyChecker(mgr)
        report = checker.check()

        assert report.safe_to_pull
        assert report.reasons == []
        assert report.is_clean

    def test_check_unsafe_when_detached(self, tmp_path: Path) -> None:
        """Test check returns unsafe when HEAD is detached."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.head.is_detached = True
        mock_repo.is_dirty.return_value = False
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = []
        mock_repo.refs = []
        mgr._repo = mock_repo

        checker = SafetyChecker(mgr)
        report = checker.check()

        assert not report.safe_to_pull
        assert "HEAD is detached" in report.reasons
        assert report.is_detached

    def test_check_unsafe_when_wrong_branch(self, tmp_path: Path) -> None:
        """Test check returns unsafe when on wrong branch."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "develop"
        mock_repo.is_dirty.return_value = False
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = []
        mock_repo.refs = []
        mgr._repo = mock_repo

        checker = SafetyChecker(mgr)
        report = checker.check(expected_branch="main")

        assert not report.safe_to_pull
        assert any("expected 'main'" in r for r in report.reasons)

    def test_check_unsafe_when_dirty(self, tmp_path: Path) -> None:
        """Test check returns unsafe when repo is dirty."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"
        mock_repo.is_dirty.return_value = True
        mock_repo.index.diff.side_effect = [["staged"], ["modified"]]
        mock_repo.untracked_files = ["untracked.txt"]
        mock_repo.refs = []
        mgr._repo = mock_repo

        checker = SafetyChecker(mgr)
        report = checker.check()

        assert not report.safe_to_pull
        assert not report.is_clean

    def test_check_safe_to_pull_convenience_function(self, tmp_path: Path) -> None:
        """Test check_safe_to_pull convenience function."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()
        mgr = RepoManager(repo_path)

        mock_repo = MagicMock()
        mock_repo.head.is_detached = False
        mock_repo.active_branch.name = "main"
        mock_repo.is_dirty.return_value = False
        mock_repo.index.diff.return_value = []
        mock_repo.untracked_files = []
        mock_repo.refs = []
        mgr._repo = mock_repo

        report = check_safe_to_pull(mgr)
        assert report.safe_to_pull


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_default_values(self) -> None:
        """Test RetryConfig default values."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True

    def test_custom_values(self) -> None:
        """Test RetryConfig with custom values."""
        config = RetryConfig(
            max_retries=5,
            base_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
            jitter=False,
        )
        assert config.max_retries == 5
        assert config.base_delay == 0.5


class TestRetryManager:
    """Tests for RetryManager class."""

    def test_get_delay_exponential(self) -> None:
        """Test get_delay calculates exponential backoff."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)
        manager = RetryManager(config)

        assert manager.get_delay(0) == 1.0
        assert manager.get_delay(1) == 2.0
        assert manager.get_delay(2) == 4.0
        assert manager.get_delay(3) == 8.0

    def test_get_delay_respects_max(self) -> None:
        """Test get_delay respects max_delay."""
        config = RetryConfig(
            base_delay=1.0, max_delay=5.0, exponential_base=2.0, jitter=False
        )
        manager = RetryManager(config)

        assert manager.get_delay(10) == 5.0  # Would be 1024 without max

    def test_execute_success_first_try(self) -> None:
        """Test execute succeeds on first try."""
        config = RetryConfig(max_retries=3)
        manager = RetryManager(config)

        result = manager.execute(lambda: "success")

        assert result.success
        assert result.value == "success"
        assert result.attempts == 1
        assert result.total_delay == 0.0

    def test_execute_retries_on_git_error(self) -> None:
        """Test execute retries on GitError."""
        config = RetryConfig(max_retries=2, base_delay=0.01, jitter=False)
        manager = RetryManager(config)

        call_count = 0

        def failing_then_success() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise GitError("temporary failure")
            return "success"

        result = manager.execute(failing_then_success)

        assert result.success
        assert result.value == "success"
        assert result.attempts == 2

    def test_execute_fails_after_max_retries(self) -> None:
        """Test execute fails after max retries exhausted."""
        config = RetryConfig(max_retries=2, base_delay=0.01, jitter=False)
        manager = RetryManager(config)

        def always_fails() -> str:
            raise GitError("permanent failure")

        result = manager.execute(always_fails)

        assert not result.success
        assert result.attempts == 3  # Initial + 2 retries
        assert isinstance(result.last_error, GitError)


class TestWithRetry:
    """Tests for with_retry convenience function."""

    def test_with_retry_success(self) -> None:
        """Test with_retry returns success."""
        result = with_retry(lambda: 42)
        assert result.success
        assert result.value == 42

    def test_with_retry_with_custom_config(self) -> None:
        """Test with_retry uses custom config."""
        config = RetryConfig(max_retries=1, base_delay=0.01, jitter=False)
        call_count = 0

        def count_calls() -> int:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise GitError("fail")
            return call_count

        result = with_retry(count_calls, config=config)
        assert result.success
        assert call_count == 2
