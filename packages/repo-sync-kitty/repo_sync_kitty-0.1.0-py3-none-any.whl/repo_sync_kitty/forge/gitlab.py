"""GitLab API client."""


class GitLabClient:
    """Client for GitLab API."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize with optional token."""
        self.token = token
