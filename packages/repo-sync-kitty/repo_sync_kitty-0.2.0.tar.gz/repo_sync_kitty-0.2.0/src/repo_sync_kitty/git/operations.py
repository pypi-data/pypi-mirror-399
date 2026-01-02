"""Git operations using GitPython."""

from pathlib import Path
from typing import TYPE_CHECKING

from git import GitCommandError, Repo
from git.remote import FetchInfo

if TYPE_CHECKING:
    from git.refs.head import HEAD, Head


class GitError(Exception):
    """Base exception for git operations."""


class CloneError(GitError):
    """Raised when clone fails."""


class FetchError(GitError):
    """Raised when fetch fails."""


class PullError(GitError):
    """Raised when pull fails."""


class PushError(GitError):
    """Raised when push fails."""


class RepoManager:
    """Manager for git repository operations."""

    def __init__(self, path: Path) -> None:
        """Initialize with repository path."""
        self.path = path
        self._repo: Repo | None = None

    @property
    def repo(self) -> Repo:
        """Get the GitPython Repo object, loading lazily."""
        if self._repo is None:
            if not self.exists():
                raise GitError(f"Not a git repository: {self.path}")
            self._repo = Repo(self.path)
        return self._repo

    def exists(self) -> bool:
        """Check if the repository exists."""
        return (self.path / ".git").is_dir()

    @classmethod
    def clone(cls, url: str, path: Path, branch: str | None = None) -> "RepoManager":
        """Clone a repository.

        Args:
            url: The repository URL to clone
            path: Local path to clone to
            branch: Branch to checkout (default: remote's default)

        Returns:
            RepoManager for the cloned repository

        Raises:
            CloneError: If clone fails
        """
        try:
            if branch:
                Repo.clone_from(url, path, branch=branch)
            else:
                Repo.clone_from(url, path)
            return cls(path)
        except GitCommandError as e:
            raise CloneError(f"Failed to clone {url}: {e}") from e

    def fetch(self, remote_name: str | None = None) -> list[FetchInfo]:
        """Fetch from remote(s).

        Args:
            remote_name: Specific remote to fetch, or None for all

        Returns:
            List of FetchInfo objects

        Raises:
            FetchError: If fetch fails
        """
        try:
            results: list[FetchInfo] = []
            if remote_name:
                remote = self.repo.remote(remote_name)
                results.extend(remote.fetch())
            else:
                for remote in self.repo.remotes:
                    results.extend(remote.fetch())
            return results
        except GitCommandError as e:
            raise FetchError(f"Failed to fetch: {e}") from e

    def pull(self, remote_name: str | None = None, branch: str | None = None) -> None:
        """Pull from remote.

        Args:
            remote_name: Remote to pull from (default: tracking remote or first available)
            branch: Branch to pull (default: current branch)

        Raises:
            PullError: If pull fails
        """
        try:
            # Determine which remote to use
            if remote_name:
                remote = self.repo.remote(remote_name)
            else:
                # Try to get tracking remote for current branch
                if not self.repo.head.is_detached:
                    tracking = self.repo.active_branch.tracking_branch()
                    if tracking:
                        remote = self.repo.remote(tracking.remote_name)
                    elif self.repo.remotes:
                        # Fall back to first remote
                        remote = self.repo.remotes[0]
                    else:
                        raise PullError("No remotes configured")
                elif self.repo.remotes:
                    remote = self.repo.remotes[0]
                else:
                    raise PullError("No remotes configured")

            if branch:
                remote.pull(branch)
            else:
                remote.pull()
        except GitCommandError as e:
            raise PullError(f"Failed to pull: {e}") from e

    def get_current_branch(self) -> str | None:
        """Get the current branch name, or None if detached."""
        if self.repo.head.is_detached:
            return None
        return self.repo.active_branch.name

    def get_remotes(self) -> list[str]:
        """Get list of remote names."""
        return [r.name for r in self.repo.remotes]

    def get_remote_urls(self) -> dict[str, str]:
        """Get mapping of remote names to their URLs."""
        return {r.name: r.url for r in self.repo.remotes}

    def is_clean(self) -> bool:
        """Check if working directory is clean (no changes)."""
        return not self.repo.is_dirty(untracked_files=True)

    def has_staged_changes(self) -> bool:
        """Check if there are staged changes."""
        return len(self.repo.index.diff("HEAD")) > 0

    def has_modified_files(self) -> bool:
        """Check if there are modified tracked files."""
        return len(self.repo.index.diff(None)) > 0

    def has_untracked_files(self) -> bool:
        """Check if there are untracked files."""
        return len(self.repo.untracked_files) > 0

    def is_rebasing(self) -> bool:
        """Check if a rebase is in progress."""
        git_dir = self.path / ".git"
        return (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists()

    def is_merging(self) -> bool:
        """Check if a merge is in progress."""
        return (self.path / ".git" / "MERGE_HEAD").exists()

    def is_cherry_picking(self) -> bool:
        """Check if a cherry-pick is in progress."""
        return (self.path / ".git" / "CHERRY_PICK_HEAD").exists()

    def is_detached(self) -> bool:
        """Check if HEAD is detached."""
        return self.repo.head.is_detached

    def get_head_commit(self) -> str:
        """Get the current HEAD commit hash."""
        return self.repo.head.commit.hexsha

    def get_ahead_behind(
        self, remote_name: str = "origin", branch: str | None = None
    ) -> tuple[int, int]:
        """Get commits ahead/behind remote.

        Args:
            remote_name: Remote to compare against
            branch: Branch to compare (default: current branch)

        Returns:
            Tuple of (ahead, behind) counts
        """
        if branch is None:
            branch = self.get_current_branch()
            if branch is None:
                return (0, 0)  # Detached HEAD

        try:
            remote_ref = f"{remote_name}/{branch}"
            # Check if remote ref exists
            if remote_ref not in [ref.name for ref in self.repo.refs]:
                return (0, 0)

            local_commits = list(
                self.repo.iter_commits(f"{remote_ref}..{branch}")
            )
            remote_commits = list(
                self.repo.iter_commits(f"{branch}..{remote_ref}")
            )
            return (len(local_commits), len(remote_commits))
        except GitCommandError:
            return (0, 0)

    def get_in_progress_operation(self) -> str | None:
        """Get the name of any in-progress operation."""
        if self.is_rebasing():
            return "rebase"
        if self.is_merging():
            return "merge"
        if self.is_cherry_picking():
            return "cherry-pick"
        return None

    def checkout(self, branch: str) -> "HEAD | Head":
        """Checkout a branch.

        Args:
            branch: Branch name to checkout

        Returns:
            The checked out branch head
        """
        return self.repo.heads[branch].checkout()

    def get_branches_at_head(self) -> list[str]:
        """Get list of local branches whose tip matches current HEAD commit.

        Returns:
            List of branch names pointing to HEAD commit
        """
        head_sha = self.get_head_commit()
        return [
            branch.name
            for branch in self.repo.heads
            if branch.commit.hexsha == head_sha
        ]

    def get_remote_branches_at_head(self) -> list[tuple[str, str]]:
        """Get list of remote branches whose tip matches current HEAD commit.

        Returns:
            List of (remote_name, branch_name) tuples for remotes at HEAD.
            E.g., [("origin", "master"), ("origin", "main")]
        """
        head_sha = self.get_head_commit()
        result: list[tuple[str, str]] = []
        for remote in self.repo.remotes:
            for ref in remote.refs:
                if ref.commit.hexsha == head_sha:
                    # ref.name is like "origin/master" - extract branch part
                    branch_name = ref.name.split("/", 1)[1] if "/" in ref.name else ref.name
                    result.append((remote.name, branch_name))
        return result

    def has_branch(self, branch: str) -> bool:
        """Check if a local branch exists.

        Args:
            branch: Branch name to check

        Returns:
            True if branch exists locally
        """
        return branch in [b.name for b in self.repo.heads]

    def create_tracking_branch(self, branch: str, remote: str = "origin") -> None:
        """Create a local branch that tracks a remote branch.

        Args:
            branch: Branch name to create
            remote: Remote name to track

        Raises:
            GitError: If branch creation fails
        """
        remote_ref = f"{remote}/{branch}"
        try:
            # Create local branch from remote ref
            self.repo.create_head(branch, remote_ref)
            # Set up tracking
            local_branch = self.repo.heads[branch]
            local_branch.set_tracking_branch(self.repo.refs[remote_ref])
        except Exception as e:
            raise GitError(f"Failed to create tracking branch {branch}: {e}") from e

    def has_remote(self, name: str) -> bool:
        """Check if a remote exists.

        Args:
            name: Remote name to check

        Returns:
            True if remote exists
        """
        return name in [r.name for r in self.repo.remotes]

    def add_remote(self, name: str, url: str) -> None:
        """Add a new remote.

        Args:
            name: Remote name
            url: Remote URL

        Raises:
            GitError: If remote already exists or creation fails
        """
        if self.has_remote(name):
            raise GitError(f"Remote '{name}' already exists")
        try:
            self.repo.create_remote(name, url)
        except GitCommandError as e:
            raise GitError(f"Failed to add remote '{name}': {e}") from e

    def set_remote_url(self, name: str, url: str) -> None:
        """Set the URL for an existing remote.

        Args:
            name: Remote name
            url: New remote URL

        Raises:
            GitError: If remote doesn't exist or update fails
        """
        if not self.has_remote(name):
            raise GitError(f"Remote '{name}' does not exist")
        try:
            remote = self.repo.remote(name)
            remote.set_url(url)
        except GitCommandError as e:
            raise GitError(f"Failed to set URL for remote '{name}': {e}") from e

    def push(
        self,
        remote_name: str = "origin",
        branch: str | None = None,
        set_upstream: bool = False,
        all_branches: bool = False,
    ) -> None:
        """Push to remote.

        Args:
            remote_name: Remote to push to
            branch: Branch to push (default: current branch)
            set_upstream: Set upstream tracking
            all_branches: Push all branches

        Raises:
            PushError: If push fails
        """
        try:
            remote = self.repo.remote(remote_name)

            if all_branches:
                # Push all branches
                remote.push(all=True)
            else:
                # Push specific branch or current
                if branch is None:
                    branch = self.get_current_branch()
                    if branch is None:
                        raise PushError("Cannot push: HEAD is detached")

                if set_upstream:
                    remote.push(refspec=f"{branch}:{branch}", set_upstream=True)
                else:
                    remote.push(refspec=f"{branch}:{branch}")
        except GitCommandError as e:
            raise PushError(f"Failed to push to {remote_name}: {e}") from e
