"""Init command: create new manifest file."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from repo_sync_kitty.git.operations import RepoManager

console = Console()

MANIFEST_TEMPLATE = '''\
[common]
root_path = "{root_path}"
branch = "main"
remote = "origin"
parallelism = 4
timeout = 300

[remotes]
origin = {{ base_url = "https://github.com/" }}

[projects]
# Short form (inline table):
# "path/to/repo" = {{ slug = "owner/repo" }}
# "libs/mylib" = {{ slug = "owner/mylib", branch = "develop" }}

# Long form (expanded table):
# [projects."tools/mytool"]
# slug = "owner/mytool"
# branch = "main"
# remote = "origin"
# status = "active"
'''


def _scan_directory(directory: Path) -> list[dict[str, str]]:
    """Scan a directory for git repositories.

    Args:
        directory: Directory to scan

    Returns:
        List of dicts with path and remote info
    """
    repos: list[dict[str, str]] = []

    for item in directory.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith("."):
            continue

        mgr = RepoManager(item)
        if not mgr.exists():
            # Check subdirectories one level deep
            for subitem in item.iterdir():
                if subitem.is_dir() and not subitem.name.startswith("."):
                    sub_mgr = RepoManager(subitem)
                    if sub_mgr.exists():
                        repo_info = _get_repo_info(sub_mgr, subitem, directory)
                        if repo_info:
                            repos.append(repo_info)
        else:
            repo_info = _get_repo_info(mgr, item, directory)
            if repo_info:
                repos.append(repo_info)

    return repos


def _get_repo_info(mgr: RepoManager, repo_path: Path, root: Path) -> dict[str, str] | None:
    """Extract repository info from a RepoManager.

    Args:
        mgr: RepoManager instance
        repo_path: Path to the repository
        root: Root directory for relative path calculation

    Returns:
        Dict with repo info or None if no origin remote
    """
    try:
        remotes = mgr.get_remotes()
        if "origin" not in remotes:
            return None

        # Get origin URL
        origin = mgr.repo.remote("origin")
        url = origin.url

        # Parse slug from URL
        slug = _parse_slug_from_url(url)
        if not slug:
            return None

        # Get relative path
        rel_path = repo_path.relative_to(root)

        # Get current branch
        branch = mgr.get_current_branch() or "main"

        return {
            "path": str(rel_path),
            "slug": slug,
            "branch": branch,
            "url": url,
        }
    except Exception:
        return None


def _parse_slug_from_url(url: str) -> str | None:
    """Parse owner/repo slug from git URL.

    Args:
        url: Git remote URL

    Returns:
        Slug like "owner/repo" or None
    """
    # Handle various URL formats:
    # https://github.com/owner/repo.git
    # git@github.com:owner/repo.git
    # ssh://git@github.com/owner/repo.git

    url = url.rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    # SSH format with colon: git@github.com:owner/repo
    # But NOT ssh:// URLs which use slashes
    if "@" in url and ":" in url and not url.startswith("ssh://"):
        _, path = url.rsplit(":", 1)
        return path

    # HTTPS/SSH format: .../owner/repo
    parts = url.split("/")
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"

    return None


def _generate_manifest_from_scan(repos: list[dict[str, str]], root_path: Path) -> str:
    """Generate manifest TOML from scanned repos.

    Args:
        repos: List of repo info dicts
        root_path: Root path for the manifest

    Returns:
        TOML string
    """
    lines = [
        "[common]",
        f'root_path = "{root_path}"',
        'branch = "main"',
        'remote = "origin"',
        "parallelism = 4",
        "timeout = 300",
        "",
        "[remotes]",
        'origin = { base_url = "https://github.com/" }',
        "",
        "[projects]",
    ]

    for repo in sorted(repos, key=lambda r: r["path"]):
        path = repo["path"]
        slug = repo["slug"]
        branch = repo.get("branch", "main")

        if branch != "main":
            lines.append(f'"{path}" = {{ slug = "{slug}", branch = "{branch}" }}')
        else:
            lines.append(f'"{path}" = {{ slug = "{slug}" }}')

    return "\n".join(lines) + "\n"


def init(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output path for manifest.toml"),
    ] = Path("manifest.toml"),
    scan_dir: Annotated[
        Path | None,
        typer.Option("--scan-dir", help="Scan directory for existing repos"),
    ] = None,
    scan_forge: Annotated[
        str | None,
        typer.Option("--scan-forge", help="Scan forge for repos (github, gitlab, bitbucket)"),
    ] = None,
    org: Annotated[  # noqa: ARG001
        str | None,
        typer.Option("--org", help="Organization/user to scan on forge"),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing manifest"),
    ] = False,
) -> None:
    """Create a new manifest.toml file."""
    # Check if output exists
    if output.exists() and not force:
        console.print(f"[red]Error:[/red] {output} already exists. Use --force to overwrite.")
        raise typer.Exit(1)

    # Handle forge scanning (not yet implemented)
    if scan_forge:
        console.print("[yellow]Forge scanning not yet implemented.[/yellow]")
        console.print("Use 'repo-sync-kitty scan' to list repos from a forge.")
        raise typer.Exit(1)

    # Scan directory for repos
    if scan_dir:
        scan_path = scan_dir.expanduser().resolve()
        if not scan_path.is_dir():
            console.print(f"[red]Error:[/red] {scan_dir} is not a directory")
            raise typer.Exit(2)

        console.print(f"Scanning [cyan]{scan_path}[/cyan] for git repositories...")
        repos = _scan_directory(scan_path)

        if not repos:
            console.print("[yellow]No git repositories found.[/yellow]")
            console.print("Creating empty template instead.")
            content = MANIFEST_TEMPLATE.format(root_path=scan_path)
        else:
            console.print(f"Found [green]{len(repos)}[/green] repositories:")
            for repo in sorted(repos, key=lambda r: r["path"]):
                console.print(f"  • {repo['path']} ({repo['slug']})")
            content = _generate_manifest_from_scan(repos, scan_path)
    else:
        # Create template with current directory as root
        root_path = Path.cwd()
        content = MANIFEST_TEMPLATE.format(root_path=root_path)

    # Write manifest
    output.write_text(content)
    console.print(f"\n[green]✓[/green] Created {output}")

    if not scan_dir:
        console.print("\nEdit the manifest to add your remotes and projects.")
        console.print("Then run [bold]repo-sync-kitty check[/bold] to validate.")
