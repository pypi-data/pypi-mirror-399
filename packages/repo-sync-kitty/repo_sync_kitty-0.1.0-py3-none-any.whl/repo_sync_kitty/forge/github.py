"""GitHub API client."""

import httpx


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""


class GitHubAuthError(GitHubAPIError):
    """Authentication failed."""


class GitHubRateLimitError(GitHubAPIError):
    """Rate limit exceeded."""


class GitHubRepoExistsError(GitHubAPIError):
    """Repository already exists."""


class GitHubClient:
    """Client for GitHub API."""

    BASE_URL = "https://api.github.com"
    TIMEOUT = 30

    def __init__(self, token: str) -> None:
        """Initialize with token (required for write operations)."""
        self.token = token

    def _headers(self) -> dict[str, str]:
        """Get request headers."""
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "repo-sync-kitty",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle API error responses."""
        if response.status_code == 401:
            raise GitHubAuthError("Authentication failed. Check your GITHUB_TOKEN.")
        if response.status_code == 403:
            if "rate limit" in response.text.lower():
                raise GitHubRateLimitError("GitHub API rate limit exceeded.")
            raise GitHubAPIError(f"Access forbidden: {response.text}")
        if response.status_code == 422:
            data = response.json()
            errors = data.get("errors", [])
            for error in errors:
                if error.get("message") == "name already exists on this account":
                    raise GitHubRepoExistsError("Repository already exists.")
            raise GitHubAPIError(f"Validation failed: {data}")
        if response.status_code >= 400:
            raise GitHubAPIError(f"API error {response.status_code}: {response.text}")

    def repo_exists(self, owner: str, repo: str) -> bool:
        """Check if a repository exists.

        Args:
            owner: Repository owner (user or org)
            repo: Repository name

        Returns:
            True if repo exists, False otherwise
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        response = httpx.get(url, headers=self._headers(), timeout=self.TIMEOUT)
        if response.status_code == 404:
            return False
        if response.status_code == 200:
            return True
        self._handle_error(response)
        return False  # Unreachable but satisfies type checker

    def get_authenticated_user(self) -> str:
        """Get the username of the authenticated user.

        Returns:
            Username of the authenticated user

        Raises:
            GitHubAuthError: If authentication fails
        """
        url = f"{self.BASE_URL}/user"
        response = httpx.get(url, headers=self._headers(), timeout=self.TIMEOUT)
        if response.status_code != 200:
            self._handle_error(response)
        return str(response.json()["login"])

    def is_organization(self, name: str) -> bool:
        """Check if a name is an organization (vs a user).

        Args:
            name: Owner name to check

        Returns:
            True if it's an organization, False if it's a user
        """
        url = f"{self.BASE_URL}/orgs/{name}"
        response = httpx.get(url, headers=self._headers(), timeout=self.TIMEOUT)
        return response.status_code == 200

    def create_repo(
        self,
        owner: str,
        name: str,
        description: str = "",
        private: bool = True,
        has_issues: bool = False,
        has_wiki: bool = False,
    ) -> dict[str, object]:
        """Create a new repository.

        Args:
            owner: Repository owner (user or org)
            name: Repository name
            description: Repository description
            private: Whether the repo should be private
            has_issues: Enable issues
            has_wiki: Enable wiki

        Returns:
            Created repository data from API

        Raises:
            GitHubRepoExistsError: If repo already exists
            GitHubAPIError: For other API errors
        """
        # Determine if owner is an org or the authenticated user
        if self.is_organization(owner):
            url = f"{self.BASE_URL}/orgs/{owner}/repos"
        else:
            url = f"{self.BASE_URL}/user/repos"

        payload = {
            "name": name,
            "description": description,
            "private": private,
            "has_issues": has_issues,
            "has_wiki": has_wiki,
            "auto_init": False,  # Don't create README, we're pushing existing content
        }

        response = httpx.post(
            url,
            headers=self._headers(),
            json=payload,
            timeout=self.TIMEOUT,
        )

        if response.status_code not in (200, 201):
            self._handle_error(response)

        return dict(response.json())

    def update_repo_settings(
        self,
        owner: str,
        repo: str,
        default_branch: str = "main",
        allow_rebase_merge: bool = True,
        allow_squash_merge: bool = True,
        allow_merge_commit: bool = True,
    ) -> None:
        """Update repository settings.

        Args:
            owner: Repository owner
            repo: Repository name
            default_branch: Default branch name
            allow_rebase_merge: Allow rebase merging
            allow_squash_merge: Allow squash merging
            allow_merge_commit: Allow merge commits
        """
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"

        payload = {
            "default_branch": default_branch,
            "allow_rebase_merge": allow_rebase_merge,
            "allow_squash_merge": allow_squash_merge,
            "allow_merge_commit": allow_merge_commit,
        }

        response = httpx.patch(
            url,
            headers=self._headers(),
            json=payload,
            timeout=self.TIMEOUT,
        )

        if response.status_code != 200:
            self._handle_error(response)

    def get_repo_web_url(self, owner: str, repo: str) -> str:
        """Get the web URL for a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Web URL for the repository
        """
        return f"https://github.com/{owner}/{repo}"
