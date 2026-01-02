"""Git operations layer."""

from repo_sync_kitty.git.operations import (
    CloneError,
    FetchError,
    GitError,
    PullError,
    RepoManager,
)
from repo_sync_kitty.git.retry import (
    RetryConfig,
    RetryManager,
    RetryResult,
    RetryState,
    with_retry,
)
from repo_sync_kitty.git.safety import (
    SafetyChecker,
    SafetyReport,
    check_safe_to_pull,
)

__all__ = [
    "CloneError",
    "FetchError",
    "GitError",
    "PullError",
    "RepoManager",
    "RetryConfig",
    "RetryManager",
    "RetryResult",
    "RetryState",
    "SafetyChecker",
    "SafetyReport",
    "check_safe_to_pull",
    "with_retry",
]
