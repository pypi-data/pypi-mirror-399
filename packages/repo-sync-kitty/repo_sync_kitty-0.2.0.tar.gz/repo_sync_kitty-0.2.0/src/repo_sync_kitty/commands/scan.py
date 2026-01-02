"""Scan command: list repos from remote forge."""

import os
from pathlib import Path
from typing import Annotated, Any

import httpx
import typer
from rich.console import Console
from rich.table import Table

console = Console()


def _make_request_with_retry(
    url: str,
    headers: dict[str, str],
    params: dict[str, int | str],
    max_retries: int = 3,
    timeout: int = 60,
) -> httpx.Response:
    """Make HTTP request with retry for transient errors.

    Args:
        url: URL to request
        headers: Request headers
        params: Query parameters
        max_retries: Maximum retry attempts
        timeout: Request timeout in seconds

    Returns:
        Response object

    Raises:
        httpx.HTTPStatusError: If request fails after retries
    """
    import time

    last_error: Exception | None = None

    for attempt in range(max_retries):
        try:
            response = httpx.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout,
            )

            # Retry on 5xx server errors
            if response.status_code >= 500 and attempt < max_retries - 1:
                delay = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                time.sleep(delay)
                continue

            return response

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = 2 ** attempt
                time.sleep(delay)
                continue
            raise

    # Should not reach here, but handle edge case
    if last_error:
        raise last_error
    raise httpx.HTTPStatusError("Max retries exceeded", request=None, response=None)  # type: ignore[arg-type]


def _scan_github(org: str, token: str | None = None) -> list[dict[str, str]]:
    """Scan GitHub for repositories.

    Args:
        org: Organization or user name
        token: Optional GitHub token for private repos

    Returns:
        List of repo info dicts
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "repo-sync-kitty",  # GitHub requires User-Agent
    }
    if token:
        headers["Authorization"] = f"token {token}"

    repos: list[dict[str, str]] = []
    seen_slugs: set[str] = set()

    def add_repo(repo: dict[str, Any]) -> None:
        """Add repo if not already seen."""
        slug = repo["full_name"]
        if slug.lower() not in seen_slugs:
            seen_slugs.add(slug.lower())
            repos.append({
                "name": repo["name"],
                "slug": slug,
                "description": repo.get("description") or "",
                "default_branch": repo.get("default_branch", "main"),
                "private": "private" if repo.get("private") else "public",
                "url": repo["clone_url"],
            })

    # If authenticated, first try /user/repos to get private repos
    if token:
        url = "https://api.github.com/user/repos"
        page = 1

        while True:
            try:
                response = _make_request_with_retry(
                    url,
                    headers=headers,
                    params={"per_page": 100, "page": page, "affiliation": "owner"},
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for repo in data:
                    # Only include repos owned by the target org/user
                    if repo.get("owner", {}).get("login", "").lower() == org.lower():
                        add_repo(repo)

                page += 1
            except httpx.HTTPStatusError:
                break

    # Try as org first, then as user (for public repos or when not authenticated)
    for endpoint in [f"orgs/{org}/repos", f"users/{org}/repos"]:
        url = f"https://api.github.com/{endpoint}"
        page = 1

        while True:
            try:
                response = _make_request_with_retry(
                    url,
                    headers=headers,
                    params={"per_page": 100, "page": page},
                )

                if response.status_code == 404:
                    break  # Try next endpoint

                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for repo in data:
                    add_repo(repo)

                page += 1

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    break
                raise

        if repos:
            break  # Found repos, don't try other endpoint

    return repos


def _scan_gitlab(org: str, token: str | None = None) -> list[dict[str, str]]:
    """Scan GitLab for repositories.

    Args:
        org: Group or user name
        token: Optional GitLab token

    Returns:
        List of repo info dicts
    """
    headers = {"User-Agent": "repo-sync-kitty"}
    if token:
        headers["PRIVATE-TOKEN"] = token

    repos: list[dict[str, str]] = []

    # Try as group first, then as user
    for endpoint in [f"groups/{org}/projects", f"users/{org}/projects"]:
        url = f"https://gitlab.com/api/v4/{endpoint}"
        page = 1

        while True:
            try:
                response = _make_request_with_retry(
                    url,
                    headers=headers,
                    params={"per_page": 100, "page": page},
                )

                if response.status_code == 404:
                    break

                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for repo in data:
                    repos.append({
                        "name": repo["name"],
                        "slug": repo["path_with_namespace"],
                        "description": repo.get("description") or "",
                        "default_branch": repo.get("default_branch", "main"),
                        "private": "private" if repo.get("visibility") == "private" else "public",
                        "url": repo["http_url_to_repo"],
                    })

                page += 1

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    break
                raise

        if repos:
            break

    return repos


def _get_manifest_slugs(manifest_path: Path | None) -> set[str]:
    """Get set of slugs already in manifest.

    Args:
        manifest_path: Path to manifest file, or None

    Returns:
        Set of slugs (lowercase for comparison).
        Includes both full slugs (owner/repo) and repo names for flexible matching.
    """
    if manifest_path is None or not manifest_path.exists():
        return set()

    try:
        from repo_sync_kitty.config.loader import load_manifest

        mf = load_manifest(manifest_path)
        slugs: set[str] = set()
        for p in mf.projects:
            slug_lower = p.slug.lower()
            slugs.add(slug_lower)
            # Also add the repo name part if slug contains owner/repo
            if "/" in slug_lower:
                slugs.add(slug_lower.split("/")[-1])
        return slugs
    except Exception:
        return set()


def _is_in_manifest(repo_slug: str, manifest_slugs: set[str]) -> bool:
    """Check if a repo slug matches any slug in the manifest.

    Args:
        repo_slug: Full slug from forge (owner/repo)
        manifest_slugs: Set of slugs from manifest

    Returns:
        True if repo is in manifest (matches full slug or repo name)
    """
    slug_lower = repo_slug.lower()
    # Check full slug
    if slug_lower in manifest_slugs:
        return True
    # Check just the repo name part
    if "/" in slug_lower:
        repo_name = slug_lower.split("/")[-1]
        if repo_name in manifest_slugs:
            return True
    return False


def _extract_owner_from_base_url(base_url: str) -> str | None:
    """Extract owner from remote base_url if present.

    Args:
        base_url: Remote base URL like "https://github.com/" or "ssh://git@github.com/vladistan/"

    Returns:
        Owner string if base_url includes one, None otherwise
    """
    # Remove trailing slash for parsing
    url = base_url.rstrip("/")

    # SSH format: ssh://git@github.com/owner or git@github.com:owner
    # HTTPS format: https://github.com/owner

    # Check if URL ends with an owner (not just the domain)
    # e.g., "https://github.com/vladistan" or "ssh://git@github.com/vladistan"
    parts = url.split("/")
    if len(parts) >= 4:  # has path beyond domain
        # Last part could be owner
        potential_owner = parts[-1]
        # Make sure it's not empty and looks like an owner (no dots)
        if potential_owner and "." not in potential_owner:
            return potential_owner

    # SSH colon format: git@github.com:owner
    if "@" in url and ":" in url and "://" not in url:
        _, path = url.rsplit(":", 1)
        if path and "/" not in path and "." not in path:
            return path

    return None


def _add_repos_to_manifest(
    manifest_path: Path,
    repos: list[dict[str, str]],
    remote: str,
    remote_base_url: str,
    default_remote: str,
    default_branch: str,
) -> int:
    """Add repos to manifest file.

    Args:
        manifest_path: Path to manifest file
        repos: List of repo dicts to add
        remote: Remote name to use for these repos
        remote_base_url: Base URL of the remote (to extract owner prefix)
        default_remote: Default remote from manifest
        default_branch: Default branch from manifest

    Returns:
        Number of repos added
    """
    from repo_sync_kitty.commands.add import _add_project_to_manifest, _path_from_slug

    manifest_text = manifest_path.read_text()
    added = 0

    # Check if remote base_url includes an owner
    owner_prefix = _extract_owner_from_base_url(remote_base_url)

    for repo in repos:
        slug = repo["slug"]

        # Strip owner prefix from slug if it matches the remote's base_url owner
        if owner_prefix and slug.lower().startswith(owner_prefix.lower() + "/"):
            slug = slug[len(owner_prefix) + 1:]  # Remove "owner/" prefix

        path = _path_from_slug(repo["slug"])  # Use full slug for path
        repo_branch = repo["default_branch"]

        # Only include remote/branch if different from manifest defaults
        remote_to_use = remote if remote != default_remote else None
        branch = repo_branch if repo_branch != default_branch else None

        # Omit slug if it matches the path (can be derived)
        slug_to_use = slug if slug != path else None

        manifest_text = _add_project_to_manifest(
            manifest_text,
            path,
            slug_to_use,
            remote=remote_to_use,
            branch=branch,
        )
        added += 1

    manifest_path.write_text(manifest_text)
    return added


def scan(
    ctx: typer.Context,
    forge: Annotated[str, typer.Argument(help="Forge to scan (github, gitlab)")],
    org: Annotated[
        str | None,
        typer.Option("--org", "-o", help="Organization/user to scan"),
    ] = None,
    token: Annotated[
        str | None,
        typer.Option("--token", "-t", help="API token for authentication", envvar="GITHUB_TOKEN"),
    ] = None,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    remote: Annotated[
        str | None,
        typer.Option("--remote", "-r", help="Remote to use when adding repos"),
    ] = None,
    add: Annotated[
        bool,
        typer.Option("--add", help="Add scanned repos to manifest"),
    ] = False,
    missing: Annotated[
        bool,
        typer.Option("--missing", help="Only show repos not already in manifest"),
    ] = False,
) -> None:
    """Scan a forge for repositories."""
    if not org:
        console.print("[red]Error:[/red] --org is required")
        raise typer.Exit(2)

    # Resolve manifest path - fall back to manifest.toml in current dir
    global_manifest = ctx.obj.get("manifest") if ctx.obj else None
    resolved_manifest: Path | None = manifest or global_manifest or Path("manifest.toml")
    if resolved_manifest:
        resolved_manifest = Path(resolved_manifest)
        if not resolved_manifest.exists():
            resolved_manifest = None
    manifest_path = resolved_manifest

    # If adding, we need manifest and remote
    if add:
        if not manifest_path or not manifest_path.exists():
            console.print("[red]Error:[/red] --add requires a valid manifest file (-m)")
            raise typer.Exit(2)
        if not remote:
            console.print("[red]Error:[/red] --add requires --remote to specify which remote to use")
            raise typer.Exit(2)

        # Validate remote exists in manifest
        from repo_sync_kitty.config.loader import ManifestError, get_remote_by_name, load_manifest

        try:
            mf = load_manifest(manifest_path)
        except ManifestError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(2) from e

        remote_config = get_remote_by_name(mf, remote)
        if not remote_config:
            available = ", ".join(r.name for r in mf.remotes)
            console.print(f"[red]Error:[/red] Remote '{remote}' not found in manifest.")
            console.print(f"Available remotes: {available}")
            raise typer.Exit(2)

        remote_base_url = remote_config.base_url
        default_remote = mf.common.remote
        default_branch = mf.common.branch
    else:
        remote_base_url = ""  # Not used when not adding
        default_remote = "origin"  # Not used when not adding
        default_branch = "main"  # Not used when not adding

    forge = forge.lower()

    if forge == "github":
        # Also check GH_TOKEN and GITHUB_TOKEN env vars
        token = token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        console.print(f"Scanning GitHub for [cyan]{org}[/cyan]...")
        try:
            repos = _scan_github(org, token)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                console.print("[red]Error:[/red] Authentication failed. Check your token.")
            elif e.response.status_code == 403:
                console.print("[red]Error:[/red] Rate limited. Try again later or use a token.")
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e

    elif forge == "gitlab":
        token = token or os.getenv("GITLAB_TOKEN")
        console.print(f"Scanning GitLab for [cyan]{org}[/cyan]...")
        try:
            repos = _scan_gitlab(org, token)
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1) from e

    elif forge == "bitbucket":
        console.print("[yellow]Bitbucket scanning not yet implemented.[/yellow]")
        raise typer.Exit(1)

    else:
        console.print(f"[red]Error:[/red] Unknown forge: {forge}")
        console.print("Supported: github, gitlab")
        raise typer.Exit(2)

    if not repos:
        console.print(f"[yellow]No repositories found for {org}.[/yellow]")
        return

    # Get slugs already in manifest
    manifest_slugs = _get_manifest_slugs(manifest_path)
    have_manifest = bool(manifest_slugs) or (manifest_path and manifest_path.exists())

    # Filter to missing only if requested
    if missing:
        repos = [r for r in repos if not _is_in_manifest(r["slug"], manifest_slugs)]
        if not repos:
            console.print(f"[green]All repositories from {org} are already in manifest.[/green]")
            return

    # Display results
    total_found = len(repos)
    in_manifest_count = sum(1 for r in repos if _is_in_manifest(r["slug"], manifest_slugs))
    not_in_manifest_count = total_found - in_manifest_count

    table = Table(show_header=True, header_style="bold")
    if have_manifest:
        table.add_column("✓", justify="center", width=3)
    table.add_column("Name")
    table.add_column("Slug")
    table.add_column("Branch")
    table.add_column("Visibility")
    table.add_column("Description", max_width=40)

    for repo in sorted(repos, key=lambda r: r["name"]):
        vis_style = "dim" if repo["private"] == "private" else ""
        in_manifest = _is_in_manifest(repo["slug"], manifest_slugs)

        row = []
        if have_manifest:
            row.append("[green]✓[/green]" if in_manifest else "")
        row.extend([
            repo["name"],
            repo["slug"],
            repo["default_branch"],
            f"[{vis_style}]{repo['private']}[/{vis_style}]" if vis_style else repo["private"],
            repo["description"][:40] + "..." if len(repo["description"]) > 40 else repo["description"],
        ])
        table.add_row(*row)

    console.print(table)

    # Show summary after table
    console.print(f"\nFound [green]{total_found}[/green] repositories", end="")
    if have_manifest and not missing:
        console.print(f" ([cyan]{in_manifest_count}[/cyan] in manifest, [yellow]{not_in_manifest_count}[/yellow] missing)", end="")
    console.print()

    # Handle --add
    if add:
        repos_to_add = [r for r in repos if not _is_in_manifest(r["slug"], manifest_slugs)]
        if not repos_to_add:
            console.print("\n[yellow]No new repos to add (all already in manifest).[/yellow]")
            return

        # These are guaranteed non-None by validation at lines 395-400
        assert manifest_path is not None
        assert remote is not None
        added = _add_repos_to_manifest(
            manifest_path, repos_to_add, remote, remote_base_url, default_remote, default_branch
        )
        console.print(f"\n[green]✓[/green] Added {added} repositories to {manifest_path}")
    else:
        # Show example add commands with actual values if provided
        manifest_arg = str(manifest_path) if manifest_path else "manifest.toml"
        remote_arg = remote if remote else "<remote>"

        console.print("\nTo add repos to your manifest:")
        console.print(f"  repo-sync-kitty scan {forge} -o {org} --add -m {manifest_arg} -r {remote_arg}")
        if not_in_manifest_count > 0 and have_manifest:
            console.print("\nTo see only missing repos:")
            console.print(f"  repo-sync-kitty scan {forge} -o {org} --missing -m {manifest_arg}")
