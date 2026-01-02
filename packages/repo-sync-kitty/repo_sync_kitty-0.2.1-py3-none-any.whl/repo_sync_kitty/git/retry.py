"""Retry logic with exponential backoff for git operations."""

import random
import time
from collections.abc import Callable
from dataclasses import dataclass

from repo_sync_kitty.git.operations import GitError


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd


@dataclass
class RetryState:
    """Tracks retry state for a specific operation."""

    attempts: int = 0
    last_error: Exception | None = None
    total_delay: float = 0.0
    success: bool = False


@dataclass
class RetryResult:
    """Result of a retried operation."""

    success: bool
    value: object | None = None
    attempts: int = 0
    total_delay: float = 0.0
    last_error: Exception | None = None


class RetryManager:
    """Manages retry logic with exponential backoff."""

    def __init__(self, config: RetryConfig | None = None) -> None:
        """Initialize with optional config."""
        self.config = config or RetryConfig()
        self._remote_states: dict[str, RetryState] = {}

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number.

        Args:
            attempt: The attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            # Add up to 25% jitter
            jitter = delay * 0.25 * random.random()
            delay += jitter

        return delay

    def execute(
        self,
        operation: Callable[[], object],
        operation_name: str = "operation",  # noqa: ARG002
    ) -> RetryResult:
        """Execute an operation with retry logic.

        Args:
            operation: The callable to execute
            operation_name: Name for logging/error messages

        Returns:
            RetryResult with success status and value or error
        """
        state = RetryState()

        for attempt in range(self.config.max_retries + 1):
            state.attempts = attempt + 1
            try:
                result = operation()
                state.success = True
                return RetryResult(
                    success=True,
                    value=result,
                    attempts=state.attempts,
                    total_delay=state.total_delay,
                )
            except GitError as e:
                state.last_error = e
                if attempt < self.config.max_retries:
                    delay = self.get_delay(attempt)
                    state.total_delay += delay
                    time.sleep(delay)

        return RetryResult(
            success=False,
            attempts=state.attempts,
            total_delay=state.total_delay,
            last_error=state.last_error,
        )

    def reset_remote_state(self, remote: str) -> None:
        """Reset retry state for a remote after successful operation."""
        if remote in self._remote_states:
            del self._remote_states[remote]

    def get_remote_state(self, remote: str) -> RetryState:
        """Get or create retry state for a remote."""
        if remote not in self._remote_states:
            self._remote_states[remote] = RetryState()
        return self._remote_states[remote]


def with_retry(
    operation: Callable[[], object],
    config: RetryConfig | None = None,
    operation_name: str = "operation",
) -> RetryResult:
    """Execute an operation with retry logic.

    Convenience function for one-off retried operations.

    Args:
        operation: The callable to execute
        config: Optional retry configuration
        operation_name: Name for logging/error messages

    Returns:
        RetryResult with success status and value or error
    """
    manager = RetryManager(config)
    return manager.execute(operation, operation_name)
