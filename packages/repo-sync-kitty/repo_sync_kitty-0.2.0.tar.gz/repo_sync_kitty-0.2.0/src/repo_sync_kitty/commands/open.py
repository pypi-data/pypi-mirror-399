"""Open command: open repository in browser."""

import re
import webbrowser
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from repo_sync_kitty.config.loader import (
    ManifestError,
    ResolvedProject,
    get_remote_by_name,
    load_manifest,
    resolve_all_projects,
)
from repo_sync_kitty.git.operations import RepoManager

console = Console()


def _git_url_to_web_url(git_url: str) -> str | None:
    """Convert a git remote URL to a web browser URL.

    Handles common patterns for GitHub, GitLab, and Bitbucket.

    Args:
        git_url: Git remote URL (ssh or https)

    Returns:
        Web URL or None if pattern not recognized
    """
    url = git_url.strip()

    # Remove .git suffix
    if url.endswith(".git"):
        url = url[:-4]

    # SSH shorthand: git@github.com:owner/repo
    ssh_shorthand = re.match(r"^git@([^:]+):(.+)$", url)
    if ssh_shorthand:
        host, path = ssh_shorthand.groups()
        return f"https://{host}/{path}"

    # SSH URL: ssh://git@github.com/owner/repo
    ssh_url = re.match(r"^ssh://[^@]+@([^/]+)/(.+)$", url)
    if ssh_url:
        host, path = ssh_url.groups()
        return f"https://{host}/{path}"

    # HTTPS URL: already web-compatible
    if url.startswith("https://"):
        return url

    # HTTP URL
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)

    return None


def _find_matching_projects(
    projects: list[ResolvedProject],
    search: str,
) -> list[ResolvedProject]:
    """Find projects matching a search term.

    Args:
        projects: List of resolved projects
        search: Search term (slug, path, or partial match)

    Returns:
        List of matching projects
    """
    search_lower = search.lower()
    matches = []

    for p in projects:
        # Exact slug match
        if p.slug.lower() == search_lower:
            matches.append(p)
            continue

        # Exact path match
        if str(p.path).lower() == search_lower:
            matches.append(p)
            continue

        # Partial path match (end of path)
        path_str = str(p.path).lower()
        if path_str.endswith(f"/{search_lower}") or path_str == search_lower:
            matches.append(p)
            continue

        # Slug ends with search term
        if p.slug.lower().endswith(f"/{search_lower}"):
            matches.append(p)
            continue

        # Repo name part of slug matches
        slug_parts = p.slug.lower().split("/")
        if slug_parts[-1] == search_lower:
            matches.append(p)
            continue

    return matches


def _prompt_select_project(projects: list[ResolvedProject]) -> ResolvedProject | None:
    """Prompt user to select from multiple projects.

    Args:
        projects: List of projects to choose from

    Returns:
        Selected project or None if cancelled
    """
    console.print("\nMultiple projects match. Please select one:\n")
    for i, p in enumerate(projects, 1):
        console.print(f"  {i}. {p.path} ({p.slug})")

    console.print(f"  0. Cancel\n")

    try:
        choice = typer.prompt("Enter number", type=int)
        if choice == 0:
            return None
        if 1 <= choice <= len(projects):
            return projects[choice - 1]
        console.print("[red]Invalid choice[/red]")
        return None
    except (ValueError, typer.Abort):
        return None


def _prompt_select_remote(remotes: dict[str, str]) -> tuple[str, str] | None:
    """Prompt user to select from multiple remotes.

    Args:
        remotes: Dict mapping remote names to URLs

    Returns:
        Tuple of (name, url) or None if cancelled
    """
    console.print("\nMultiple remotes found. Please select one:\n")
    items = list(remotes.items())
    for i, (name, url) in enumerate(items, 1):
        web_url = _git_url_to_web_url(url)
        display_url = web_url or url
        console.print(f"  {i}. {name}: {display_url}")

    console.print(f"  0. Cancel\n")

    try:
        choice = typer.prompt("Enter number", type=int)
        if choice == 0:
            return None
        if 1 <= choice <= len(items):
            return items[choice - 1]
        console.print("[red]Invalid choice[/red]")
        return None
    except (ValueError, typer.Abort):
        return None


def open_repo(
    ctx: typer.Context,
    name: Annotated[
        str,
        typer.Argument(help="Repository name, slug, or path"),
    ],
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    remote: Annotated[
        str | None,
        typer.Option("--remote", "-r", help="Prefer this remote name"),
    ] = None,
    org: Annotated[
        str | None,
        typer.Option("--org", "-o", help="Prefer remotes matching this org/owner"),
    ] = None,
) -> None:
    """Open a repository in the web browser."""
    # Find manifest
    global_manifest = ctx.obj.get("manifest") if ctx.obj else None
    manifest_path = manifest or global_manifest or Path("manifest.toml")
    if not manifest_path.exists():
        console.print(f"[red]Error:[/red] Manifest not found: {manifest_path}")
        raise typer.Exit(2)

    # Load manifest
    try:
        mf = load_manifest(manifest_path)
    except ManifestError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(2) from e

    # Resolve root path and projects
    root_path = Path(mf.common.root_path).expanduser()
    projects = resolve_all_projects(mf)

    # Find matching projects
    matches = _find_matching_projects(projects, name)

    if not matches:
        # No project in manifest - but if remote is specified, try to open directly
        if remote:
            remote_config = get_remote_by_name(mf, remote)
            if remote_config:
                # Construct URL from remote base_url + name
                base_url = remote_config.base_url.rstrip("/")
                clone_url = f"{base_url}/{name}"
                web_url = _git_url_to_web_url(clone_url)
                if web_url:
                    console.print(f"Opening [cyan]{web_url}[/cyan]")
                    webbrowser.open(web_url)
                    return
                else:
                    console.print(f"[red]Error:[/red] Cannot determine web URL for: {clone_url}")
                    raise typer.Exit(1)
            else:
                console.print(f"[red]Error:[/red] Remote '{remote}' not found in manifest")
                raise typer.Exit(2)

        console.print(f"[red]Error:[/red] No project found matching '{name}'")
        console.print("Tip: Use [bold]-r <remote>[/bold] to open a repo not in manifest")
        raise typer.Exit(2)

    # Select project
    if len(matches) == 1:
        project = matches[0]
    else:
        # Try to narrow down by org if provided
        if org:
            org_matches = [p for p in matches if org.lower() in p.slug.lower()]
            if len(org_matches) == 1:
                project = org_matches[0]
            elif org_matches:
                project = _prompt_select_project(org_matches)
            else:
                project = _prompt_select_project(matches)
        else:
            project = _prompt_select_project(matches)

    if project is None:
        console.print("Cancelled.")
        return

    # Get the repo path
    repo_path = root_path / project.path

    # Check if repo exists
    mgr = RepoManager(repo_path)
    if not mgr.exists():
        # Repo not cloned - use manifest URL
        web_url = _git_url_to_web_url(project.clone_url)
        if web_url:
            console.print(f"Opening [cyan]{web_url}[/cyan]")
            webbrowser.open(web_url)
            return
        else:
            console.print(f"[red]Error:[/red] Cannot determine web URL for: {project.clone_url}")
            raise typer.Exit(1)

    # Get remotes from the actual repo
    remote_urls = mgr.get_remote_urls()

    if not remote_urls:
        console.print(f"[red]Error:[/red] No remotes configured in {repo_path}")
        raise typer.Exit(1)

    # Select remote
    selected_url = None

    if len(remote_urls) == 1:
        # Only one remote
        selected_url = list(remote_urls.values())[0]
    elif remote and remote in remote_urls:
        # User specified remote by name
        selected_url = remote_urls[remote]
    elif org:
        # Try to find remote matching org
        for url in remote_urls.values():
            if org.lower() in url.lower():
                selected_url = url
                break
        if not selected_url:
            # No match, prompt
            result = _prompt_select_remote(remote_urls)
            if result:
                selected_url = result[1]
    else:
        # Multiple remotes, no preference - prompt
        result = _prompt_select_remote(remote_urls)
        if result:
            selected_url = result[1]

    if not selected_url:
        console.print("Cancelled.")
        return

    # Convert to web URL
    web_url = _git_url_to_web_url(selected_url)
    if not web_url:
        console.print(f"[red]Error:[/red] Cannot determine web URL for: {selected_url}")
        raise typer.Exit(1)

    console.print(f"Opening [cyan]{web_url}[/cyan]")
    webbrowser.open(web_url)
