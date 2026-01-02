"""Safety checks for git operations."""

from dataclasses import dataclass, field

from repo_sync_kitty.git.operations import RepoManager


@dataclass
class SafetyReport:
    """Report from safety checks before pull."""

    safe_to_pull: bool = False
    reasons: list[str] = field(default_factory=list)
    current_branch: str | None = None
    expected_branch: str | None = None
    is_clean: bool = False
    is_ahead: bool = False
    in_progress_operation: str | None = None
    is_detached: bool = False


class SafetyChecker:
    """Check if a repository is safe to pull."""

    def __init__(self, repo: RepoManager) -> None:
        """Initialize with a RepoManager."""
        self.repo = repo

    def check(self, expected_branch: str | None = None) -> SafetyReport:
        """Run all safety checks.

        Args:
            expected_branch: The branch we expect to be on (optional)

        Returns:
            SafetyReport with all check results
        """
        reasons: list[str] = []

        # Get current state
        current_branch = self.repo.get_current_branch()
        is_detached = self.repo.is_detached()
        is_clean = self.repo.is_clean()
        in_progress = self.repo.get_in_progress_operation()

        # Check for detached HEAD
        if is_detached:
            reasons.append("HEAD is detached")

        # Check branch matches expected
        if expected_branch and current_branch != expected_branch:
            reasons.append(
                f"On branch '{current_branch}', expected '{expected_branch}'"
            )

        # Check for uncommitted changes
        if not is_clean:
            if self.repo.has_staged_changes():
                reasons.append("Has staged changes")
            if self.repo.has_modified_files():
                reasons.append("Has modified files")
            if self.repo.has_untracked_files():
                reasons.append("Has untracked files")

        # Check for in-progress operations
        if in_progress:
            reasons.append(f"Operation in progress: {in_progress}")

        # Check if ahead of remote (unpushed commits)
        ahead, _ = self.repo.get_ahead_behind()
        is_ahead = ahead > 0
        if is_ahead:
            reasons.append(f"Ahead of remote by {ahead} commit(s)")

        return SafetyReport(
            safe_to_pull=len(reasons) == 0,
            reasons=reasons,
            current_branch=current_branch,
            expected_branch=expected_branch,
            is_clean=is_clean,
            is_ahead=is_ahead,
            in_progress_operation=in_progress,
            is_detached=is_detached,
        )


def check_safe_to_pull(repo: RepoManager, expected_branch: str | None = None) -> SafetyReport:
    """Convenience function to check if a repo is safe to pull.

    Args:
        repo: The repository to check
        expected_branch: The branch we expect to be on (optional)

    Returns:
        SafetyReport with all check results
    """
    checker = SafetyChecker(repo)
    return checker.check(expected_branch)
