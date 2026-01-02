"""Find zombie directories and files outside git repositories."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from repo_sync_kitty.config.loader import ManifestError, load_manifest

console = Console()

# Files/directories to always ignore (OS artifacts and common dev tools)
IGNORED_NAMES = {
    ".DS_Store",
    ".Spotlight-V100",
    ".Trashes",
    ".envrc",
    ".python-version",
    ".java-version",
    ".claude",
    ".repo",
    ".vscode",
    "Thumbs.db",
}


def _is_git_repo(path: Path) -> bool:
    """Check if directory is a git repo (.git can be dir, file, or symlink).

    Args:
        path: Directory path to check

    Returns:
        True if path contains a .git entry
    """
    return (path / ".git").exists()


def _find_zombies(
    directory: Path, verbose: bool = False
) -> tuple[bool, list[Path]]:
    """Recursively find zombie entries (dirs/files outside git repos).

    Algorithm:
    - If directory has .git, it's a valid repo - stop descending
    - If directory contains at least one git repo, it's a grouping folder
    - Files in grouping folders (outside repos) are zombies
    - Directories without any git repos inside are zombies

    Args:
        directory: Directory to scan
        verbose: Whether to print verbose output

    Returns:
        Tuple of (contains_git, zombies) where:
        - contains_git: True if this dir or any child contains a git repo
        - zombies: List of zombie paths found
    """
    if _is_git_repo(directory):
        return (True, [])

    zombies: list[Path] = []
    contains_git = False

    try:
        children = sorted(directory.iterdir())
    except PermissionError:
        if verbose:
            console.print(f"[dim]Skipping (permission denied): {directory}[/dim]")
        return (False, [])

    for child in children:
        # Skip OS artifacts
        if child.name in IGNORED_NAMES:
            continue

        if child.is_file() or (child.is_symlink() and not child.is_dir()):
            # Loose file outside any repo = zombie
            zombies.append(child)
        elif child.is_dir():
            child_has_git, inner_zombies = _find_zombies(child, verbose)
            if child_has_git:
                # Child is a repo or grouping folder - propagate inner zombies
                contains_git = True
                zombies.extend(inner_zombies)
            else:
                # Child has no git repos - entire directory is zombie
                zombies.append(child)

    return (contains_git, zombies)


def scrub(
    ctx: typer.Context,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    path: Annotated[
        Path | None,
        typer.Option("--path", "-p", help="Override root path to scan"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show additional information"),
    ] = False,
) -> None:
    """Find zombie directories and files outside git repositories.

    Scans the project tree to discover abandoned entries:
    - Directories that aren't git repositories and don't contain any
    - Loose files that exist outside of any git repository

    These are "zombies" - orphaned files/dirs that can't be committed anywhere.
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

    # Determine root path
    root_path = path or Path(mf.common.root_path).expanduser().resolve()

    if not root_path.exists():
        console.print(f"[red]Error:[/red] Root path does not exist: {root_path}")
        raise typer.Exit(2)

    if not root_path.is_dir():
        console.print(f"[red]Error:[/red] Not a directory: {root_path}")
        raise typer.Exit(2)

    if verbose:
        console.print(f"Scanning [cyan]{root_path}[/cyan] for zombies...")

    # Find zombies
    _, zombies = _find_zombies(root_path, verbose)

    # Display results
    if not zombies:
        console.print("[green]No zombies found.[/green]")
        raise typer.Exit(0)

    for zombie in sorted(zombies):
        try:
            rel_path = zombie.relative_to(root_path)
        except ValueError:
            rel_path = zombie

        if zombie.is_dir():
            console.print(f"  [cyan]{rel_path}/[/cyan]")
        else:
            console.print(f"  {rel_path}")

    console.print()
    console.print(f"[yellow]Found {len(zombies)} zombie(s).[/yellow]")

    raise typer.Exit(1)
