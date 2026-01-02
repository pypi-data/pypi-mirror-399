"""TOML manifest loading with inheritance resolution."""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from repo_sync_kitty.config.models import (
    CommonConfig,
    Manifest,
    ProjectConfig,
    RemoteConfig,
)


class ManifestError(Exception):
    """Base exception for manifest errors."""


class ManifestNotFoundError(ManifestError):
    """Raised when manifest file is not found."""


class ManifestParseError(ManifestError):
    """Raised when manifest TOML is invalid."""


class ManifestValidationError(ManifestError):
    """Raised when manifest fails validation."""


@dataclass
class ResolvedProject:
    """A project with all inherited values resolved."""

    slug: str
    path: Path
    remote_name: str
    remote_url: str
    branch: str
    status: str
    parallelism: int
    timeout: int

    @property
    def clone_url(self) -> str:
        """Construct the full clone URL."""
        base = self.remote_url.rstrip("/")
        slug = self.slug
        if not slug.endswith(".git"):
            slug = f"{slug}.git"
        return f"{base}/{slug}"


def _parse_remotes(
    raw_remotes: dict[str, Any] | list[dict[str, Any]] | None,
) -> list[RemoteConfig]:
    """Parse remotes from either dict or list format.

    Supports:
    - Dict format: { "name": { base_url: "...", ... }, ... }
    - List format: [{ name: "...", base_url: "...", ... }, ...]
    """
    if raw_remotes is None:
        return []

    if isinstance(raw_remotes, list):
        # Array of tables format: [[remotes]]
        return [RemoteConfig(**r) for r in raw_remotes]

    # Dict format: [remotes] with name = { ... }
    remotes = []
    for name, config in raw_remotes.items():
        remotes.append(RemoteConfig(name=name, **config))
    return remotes


def _derive_slug_from_path(path: str) -> str:
    """Derive slug from path when not explicitly provided.

    The slug is the final component of the path.

    Args:
        path: Project path like "util/autorevision" or "myproject"

    Returns:
        Derived slug like "autorevision" or "myproject"
    """
    return Path(path).name


def _parse_projects(
    raw_projects: dict[str, Any] | list[dict[str, Any]] | None,
) -> list[ProjectConfig]:
    """Parse projects from either dict or list format.

    Supports:
    - Dict format: { "path": { slug: "...", ... }, ... }
    - List format: [{ slug: "...", path: "...", ... }, ...]

    If slug is not provided, it is derived from the path's final component.
    """
    if raw_projects is None:
        return []

    if isinstance(raw_projects, list):
        # Array of tables format: [[projects]]
        projects = []
        for p in raw_projects:
            # Derive slug from path if not provided
            if "slug" not in p and "path" in p:
                p = {**p, "slug": _derive_slug_from_path(str(p["path"]))}
            projects.append(ProjectConfig(**p))
        return projects

    # Dict format: [projects] with "path" = { ... }
    projects = []
    for path, config in raw_projects.items():
        # Derive slug from path if not provided
        if "slug" not in config:
            config = {**config, "slug": _derive_slug_from_path(path)}
        projects.append(ProjectConfig(path=Path(path), **config))
    return projects


def load_manifest(path: Path) -> Manifest:
    """Load and parse a manifest TOML file.

    Supports two formats for remotes and projects:
    - Dict format (compact): [remotes] / [projects] with keyed entries
    - Array format (explicit): [[remotes]] / [[projects]] tables

    Args:
        path: Path to the manifest.toml file

    Returns:
        Parsed Manifest object

    Raises:
        ManifestNotFoundError: If file doesn't exist
        ManifestParseError: If TOML is invalid
        ManifestValidationError: If validation fails
    """
    if not path.exists():
        raise ManifestNotFoundError(f"Manifest not found: {path}")

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ManifestParseError(f"Invalid TOML: {e}") from e

    try:
        return Manifest(
            common=CommonConfig(**data.get("common", {})),
            remotes=_parse_remotes(data.get("remotes")),
            projects=_parse_projects(data.get("projects")),
        )
    except ValidationError as e:
        raise ManifestValidationError(f"Validation failed: {e}") from e


def get_remote_by_name(manifest: Manifest, name: str) -> RemoteConfig | None:
    """Find a remote by name."""
    for remote in manifest.remotes:
        if remote.name == name:
            return remote
    return None


def resolve_project(manifest: Manifest, project: ProjectConfig) -> ResolvedProject:
    """Resolve all inherited values for a project.

    Inheritance chain: project -> remote -> common

    Args:
        manifest: The full manifest
        project: The project to resolve

    Returns:
        ResolvedProject with all values filled in

    Raises:
        ManifestValidationError: If referenced remote doesn't exist
    """
    # Determine remote name (project -> common)
    remote_name = project.remote or manifest.common.remote

    # Find the remote config
    remote = get_remote_by_name(manifest, remote_name)
    if remote is None:
        raise ManifestValidationError(
            f"Project '{project.slug}' references unknown remote '{remote_name}'"
        )

    # Resolve branch (project -> remote -> common)
    branch = project.branch or remote.branch or manifest.common.branch

    # Resolve parallelism (remote -> common)
    parallelism = remote.parallelism or manifest.common.parallelism

    # Resolve timeout (remote -> common)
    timeout = remote.timeout or manifest.common.timeout

    return ResolvedProject(
        slug=project.slug,
        path=project.path,
        remote_name=remote_name,
        remote_url=remote.base_url,
        branch=branch,
        status=project.status,
        parallelism=parallelism,
        timeout=timeout,
    )


def resolve_all_projects(manifest: Manifest) -> list[ResolvedProject]:
    """Resolve all projects in a manifest.

    Args:
        manifest: The manifest to process

    Returns:
        List of resolved projects
    """
    return [resolve_project(manifest, p) for p in manifest.projects]


def validate_manifest(manifest: Manifest) -> list[str]:
    """Validate manifest for semantic correctness.

    Checks:
    - All projects reference valid remotes
    - No duplicate project paths
    - Root path is valid

    Args:
        manifest: The manifest to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors: list[str] = []

    # Check common.remote exists
    if not get_remote_by_name(manifest, manifest.common.remote):
        errors.append(f"Default remote '{manifest.common.remote}' not defined in remotes")

    # Check all project remotes exist
    for project in manifest.projects:
        remote_name = project.remote or manifest.common.remote
        if not get_remote_by_name(manifest, remote_name):
            errors.append(
                f"Project '{project.slug}' references undefined remote '{remote_name}'"
            )

    # Check for duplicate paths
    paths = [str(p.path) for p in manifest.projects]
    seen: set[str] = set()
    for path in paths:
        if path in seen:
            errors.append(f"Duplicate project path: {path}")
        seen.add(path)

    # Note: Duplicate slugs within the same remote are allowed.
    # This supports the pattern of cloning the same repo to different paths
    # with different branches (e.g., main and develop checkouts).

    return errors


def extract_owner_from_base_url(base_url: str) -> str | None:
    """Extract owner/org from remote base_url.

    Parses various git URL formats to extract the owner component.

    Args:
        base_url: Remote base URL from config

    Returns:
        Owner name if found, None if base_url doesn't include owner

    Examples:
        >>> extract_owner_from_base_url("ssh://git@github.com/vladistan/")
        'vladistan'
        >>> extract_owner_from_base_url("https://github.com/vladistan/")
        'vladistan'
        >>> extract_owner_from_base_url("git@github.com:vladistan/")
        'vladistan'
        >>> extract_owner_from_base_url("https://github.com/")
        None
    """
    import re

    # Remove trailing slash for consistent parsing
    url = base_url.rstrip("/")

    # Pattern 1: SSH shorthand - git@host:owner
    # e.g., git@github.com:vladistan
    ssh_shorthand = re.match(r"^git@[^:]+:([^/]+)$", url)
    if ssh_shorthand:
        return ssh_shorthand.group(1)

    # Pattern 2: SSH URL - ssh://git@host/owner
    # e.g., ssh://git@github.com/vladistan
    ssh_url = re.match(r"^ssh://[^/]+/([^/]+)$", url)
    if ssh_url:
        return ssh_url.group(1)

    # Pattern 3: HTTPS/HTTP URL - https://host/owner
    # e.g., https://github.com/vladistan
    https_url = re.match(r"^https?://[^/]+/([^/]+)$", url)
    if https_url:
        return https_url.group(1)

    # No owner found in URL (e.g., https://github.com/)
    return None


def construct_clone_url(base_url: str, owner: str, repo_name: str) -> str:
    """Construct a clone URL from base_url, owner, and repo name.

    Args:
        base_url: Remote base URL (may or may not include owner)
        owner: Repository owner
        repo_name: Repository name

    Returns:
        Full clone URL
    """
    # Check if base_url already includes the owner
    url_owner = extract_owner_from_base_url(base_url)

    if url_owner:
        # Owner already in base_url, just append repo name
        base = base_url.rstrip("/")
        return f"{base}/{repo_name}.git"
    else:
        # Need to add owner
        base = base_url.rstrip("/")
        return f"{base}/{owner}/{repo_name}.git"
