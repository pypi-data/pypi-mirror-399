"""Bitbucket API client."""


class BitbucketClient:
    """Client for Bitbucket API."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize with optional token."""
        self.token = token
