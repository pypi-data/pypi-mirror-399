"""Find orphan repos not tracked in manifest."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from repo_sync_kitty.config.loader import (
    ManifestError,
    load_manifest,
    resolve_all_projects,
)

console = Console()


def _is_git_repo(path: Path) -> bool:
    """Check if a directory is a git repository.

    Args:
        path: Directory path to check

    Returns:
        True if path contains a .git directory
    """
    return (path / ".git").is_dir()


def _find_git_repos(root: Path) -> list[Path]:
    """Recursively find all git repositories under a path.

    Algorithm:
    - If directory contains .git, it's a repo - add to list and don't recurse
    - Otherwise, recurse into subdirectories

    Args:
        root: Root directory to search

    Returns:
        List of paths to git repositories (relative to root)
    """
    repos: list[Path] = []

    def _scan_dir(current: Path) -> None:
        """Scan a directory for git repos."""
        if not current.is_dir():
            return

        if _is_git_repo(current):
            # Found a repo - add it and don't recurse further
            repos.append(current)
            return

        # Not a repo - recurse into subdirectories
        try:
            for child in sorted(current.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    _scan_dir(child)
        except PermissionError:
            # Skip directories we can't read
            pass

    _scan_dir(root)
    return repos


def _get_manifest_paths(manifest_path: Path) -> set[Path]:
    """Get all project paths from manifest as absolute paths.

    Args:
        manifest_path: Path to manifest file

    Returns:
        Set of absolute paths for all projects in manifest
    """
    mf = load_manifest(manifest_path)
    root_path = Path(mf.common.root_path).expanduser().resolve()
    projects = resolve_all_projects(mf)

    paths: set[Path] = set()
    for project in projects:
        full_path = (root_path / project.path).resolve()
        paths.add(full_path)

    return paths


def find_orphans(
    ctx: typer.Context,
    path: Annotated[
        Path | None,
        typer.Argument(help="Path to search for repos (default: manifest root_path)"),
    ] = None,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
) -> None:
    """Find git repositories not tracked in the manifest.

    Recursively scans a directory for git repos and reports any that
    aren't listed in the manifest (orphans).
    """
    # Find manifest
    global_manifest = ctx.obj.get("manifest") if ctx.obj else None
    manifest_path = manifest or global_manifest or Path("manifest.toml")
    if not manifest_path.exists():
        console.print(f"[red]Error:[/red] Manifest not found: {manifest_path}")
        raise typer.Exit(2)

    # Load manifest to get root_path
    try:
        mf = load_manifest(manifest_path)
    except ManifestError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(2) from e

    root_path = Path(mf.common.root_path).expanduser().resolve()

    # Determine search path
    search_path = path.resolve() if path else root_path
    if not search_path.exists():
        console.print(f"[red]Error:[/red] Path not found: {search_path}")
        raise typer.Exit(2)

    if not search_path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {search_path}")
        raise typer.Exit(2)

    console.print(f"Scanning [cyan]{search_path}[/cyan] for git repositories...")

    # Find all git repos
    found_repos = _find_git_repos(search_path)
    console.print(f"Found [green]{len(found_repos)}[/green] git repositories.\n")

    if not found_repos:
        return

    # Get manifest paths
    try:
        manifest_paths = _get_manifest_paths(manifest_path)
    except ManifestError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(2) from e

    # Find orphans (repos not in manifest)
    orphans: list[Path] = []
    tracked: list[Path] = []

    for repo_path in found_repos:
        abs_path = repo_path.resolve()
        if abs_path in manifest_paths:
            tracked.append(repo_path)
        else:
            orphans.append(repo_path)

    # Display results
    if orphans:
        console.print(f"[yellow]{len(orphans)} orphan(s)[/yellow] not in manifest:\n")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Path")

        for orphan in sorted(orphans):
            abs_path = orphan.resolve()
            try:
                rel_path = abs_path.relative_to(root_path)
            except ValueError:
                rel_path = abs_path

            table.add_row(str(rel_path))

        console.print(table)

        console.print(f"\n[dim]To add an orphan to manifest:[/dim]")
        console.print(f"  repo-sync-kitty add <slug> -p <path> -m {manifest_path}")
    else:
        console.print("[green]No orphans found.[/green] All repos are tracked in manifest.")

    # Summary
    console.print(f"\nSummary: {len(found_repos)} repos found, {len(tracked)} tracked, {len(orphans)} orphans")
