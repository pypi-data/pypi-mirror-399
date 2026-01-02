"""Tests for forge clients."""

import pytest

from repo_sync_kitty.forge.bitbucket import BitbucketClient
from repo_sync_kitty.forge.github import GitHubClient
from repo_sync_kitty.forge.gitlab import GitLabClient


# Clients that support optional tokens (stub implementations)
OPTIONAL_TOKEN_CLIENTS = [GitLabClient, BitbucketClient]

# Clients that require tokens (full implementations)
REQUIRED_TOKEN_CLIENTS = [GitHubClient]


@pytest.mark.parametrize("client_class", OPTIONAL_TOKEN_CLIENTS)
class TestOptionalTokenClients:
    """Tests for forge clients with optional tokens."""

    def test_init_without_token(self, client_class: type) -> None:
        """Test client initialization without token sets None."""
        client = client_class()
        assert client.token is None

    def test_init_with_token(self, client_class: type) -> None:
        """Test client initialization with token stores it."""
        client = client_class(token="my-token")
        assert client.token == "my-token"


@pytest.mark.parametrize("client_class", REQUIRED_TOKEN_CLIENTS)
class TestRequiredTokenClients:
    """Tests for forge clients that require tokens."""

    def test_init_with_token(self, client_class: type) -> None:
        """Test client initialization with token stores it."""
        client = client_class(token="my-token")
        assert client.token == "my-token"


class TestGitHubClient:
    """Tests specific to GitHubClient."""

    def test_headers_includes_auth(self) -> None:
        """Test that headers include authorization."""
        client = GitHubClient(token="test-token")
        headers = client._headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["User-Agent"] == "repo-sync-kitty"

    def test_get_repo_web_url(self) -> None:
        """Test web URL construction."""
        client = GitHubClient(token="test-token")
        url = client.get_repo_web_url("owner", "repo")
        assert url == "https://github.com/owner/repo"
