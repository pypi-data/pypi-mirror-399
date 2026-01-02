"""Move command: relocate a repository to a new path."""

import os
import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from repo_sync_kitty.config.loader import (
    ManifestError,
    load_manifest,
    resolve_all_projects,
)
from repo_sync_kitty.git.operations import RepoManager

console = Console()


def _find_project_by_path(manifest_path: Path, search_path: str) -> tuple[str, str] | None:
    """Find a project in manifest by its path.

    Args:
        manifest_path: Path to manifest file
        search_path: Path to search for (can be partial)

    Returns:
        Tuple of (full_path, slug) if found, None otherwise
    """
    mf = load_manifest(manifest_path)
    projects = resolve_all_projects(mf)

    # Try exact match first
    for p in projects:
        if str(p.path) == search_path:
            return (str(p.path), p.slug)

    # Try suffix match (e.g., "repo" matches "owner/repo")
    for p in projects:
        if str(p.path).endswith(f"/{search_path}") or str(p.path) == search_path:
            return (str(p.path), p.slug)

    return None


def _slug_derivable_from_path(path: str, slug: str) -> bool:
    """Check if slug can be derived from path (last component matches)."""
    path_last = path.rstrip("/").split("/")[-1]
    return path_last == slug


def _update_manifest_path(
    manifest_path: Path, old_path: str, new_path: str, slug: str
) -> bool:
    """Update a project's path in the manifest file.

    Handles slug attribute:
    - If slug derivable from old_path but not from new_path: add slug attribute
    - If slug not derivable from old_path but derivable from new_path: remove slug attribute

    Args:
        manifest_path: Path to manifest file
        old_path: Current path in manifest
        new_path: New path to set
        slug: The project's slug

    Returns:
        True if updated successfully
    """
    content = manifest_path.read_text()

    # Check if slug can be derived from path (last component matches slug)
    old_path_matched_slug = _slug_derivable_from_path(old_path, slug)
    new_path_matches_slug = _slug_derivable_from_path(new_path, slug)

    # Handle both array format [[projects]] and dict format [projects]
    # Array format: path = "old/path"
    # Dict format: "old/path" = { ... }

    # Try array format first
    old_entry = f'path = "{old_path}"'
    new_entry = f'path = "{new_path}"'

    if old_entry in content:
        content = content.replace(old_entry, new_entry, 1)

        # Handle slug attribute changes for array format
        if old_path_matched_slug and not new_path_matches_slug:
            # Need to add slug - insert after the path line
            content = content.replace(
                new_entry,
                f'{new_entry}\nslug = "{slug}"',
                1
            )
        elif not old_path_matched_slug and new_path_matches_slug:
            # Need to remove slug - find and remove the slug line near this entry
            # This is tricky for array format, try to find slug = "slug" nearby
            slug_line = f'slug = "{slug}"'
            content = content.replace(f"\n{slug_line}", "", 1)

        manifest_path.write_text(content)
        return True

    # Try dict format - the path is the key
    old_key = f'"{old_path}"'
    new_key = f'"{new_path}"'

    if old_key in content:
        content = content.replace(old_key, new_key, 1)

        # Handle slug attribute changes for dict format
        if old_path_matched_slug and not new_path_matches_slug:
            # Need to add slug attribute to the dict
            # Find the line and add slug
            import re
            # Match the new key followed by = {
            pattern = rf'"{re.escape(new_path)}"\s*=\s*\{{\s*'
            match = re.search(pattern, content)
            if match:
                # Insert slug after the opening brace
                insert_pos = match.end()
                content = content[:insert_pos] + f'slug = "{slug}", ' + content[insert_pos:]

        elif not old_path_matched_slug and new_path_matches_slug:
            # Need to remove slug attribute from the dict
            # Try various patterns for slug in dict format
            import re
            # Remove slug = "...", or slug="...",
            patterns = [
                rf'slug\s*=\s*"{re.escape(slug)}"\s*,\s*',
                rf',\s*slug\s*=\s*"{re.escape(slug)}"',
            ]
            for pat in patterns:
                content, count = re.subn(pat, "", content, count=1)
                if count > 0:
                    break

        manifest_path.write_text(content)
        return True

    return False


def move(
    ctx: typer.Context,
    repo_path: Annotated[
        str,
        typer.Argument(help="Current path of the repository (as shown in status)"),
    ],
    new_path: Annotated[
        str,
        typer.Argument(help="New path for the repository"),
    ],
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Show what would be done without making changes"),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Move even if repo has uncommitted changes"),
    ] = False,
) -> None:
    """Move a repository to a new path and update the manifest."""
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

    # Resolve root path
    root_path = Path(mf.common.root_path).expanduser()

    # Find the project in manifest
    project_info = _find_project_by_path(manifest_path, repo_path)
    if not project_info:
        console.print(f"[red]Error:[/red] Repository not found in manifest: {repo_path}")
        console.print("Use [bold]repo-sync-kitty status[/bold] to see available repositories.")
        raise typer.Exit(2)

    old_path, slug = project_info

    # Normalize new_path (remove trailing slashes, etc.)
    new_path = new_path.rstrip("/")

    # Handle paths starting with ./ as relative to current directory
    # Otherwise, treat as relative to root_path
    if new_path.startswith("./"):
        # Relative to current directory - resolve to absolute, then make relative to root
        abs_new_path = Path.cwd() / new_path[2:]
        try:
            new_path = str(abs_new_path.resolve().relative_to(root_path.resolve()))
        except ValueError:
            console.print(f"[red]Error:[/red] Path '{new_path}' is outside root_path: {root_path}")
            raise typer.Exit(2)

    # Safety check: same path
    if old_path == new_path:
        console.print("[yellow]Warning:[/yellow] Source and destination are the same. Nothing to do.")
        return

    # Compute actual filesystem paths
    old_fs_path = root_path / old_path
    new_fs_path = root_path / new_path

    # Safety check: source exists
    if not old_fs_path.exists():
        console.print(f"[red]Error:[/red] Source repository does not exist: {old_fs_path}")
        console.print("The repository may not be cloned yet. Use [bold]repo-sync-kitty sync[/bold] first.")
        raise typer.Exit(2)

    # Safety check: source is a git repo
    mgr = RepoManager(old_fs_path)
    if not mgr.exists():
        console.print(f"[red]Error:[/red] Source is not a git repository: {old_fs_path}")
        raise typer.Exit(2)

    # Safety check: destination doesn't exist
    if new_fs_path.exists():
        console.print(f"[red]Error:[/red] Destination already exists: {new_fs_path}")
        console.print("Cannot overwrite existing directory.")
        raise typer.Exit(2)

    # Safety check: destination parent exists or can be created
    new_parent = new_fs_path.parent
    if not new_parent.exists():
        if dry_run:
            console.print(f"[dim]Would create directory:[/dim] {new_parent}")
        # Parent will be created during move

    # Safety check: repo is clean (unless --force)
    if not force:
        if not mgr.is_clean():
            console.print("[red]Error:[/red] Repository has uncommitted changes.")
            console.print("Commit or stash changes first, or use [bold]--force[/bold] to move anyway.")
            raise typer.Exit(2)

        in_progress = mgr.get_in_progress_operation()
        if in_progress:
            console.print(f"[red]Error:[/red] Repository has {in_progress} in progress.")
            console.print(f"Complete or abort the {in_progress} first, or use [bold]--force[/bold] to move anyway.")
            raise typer.Exit(2)

    # Safety check: new path doesn't conflict with another project
    projects = resolve_all_projects(mf)
    for p in projects:
        if str(p.path) == new_path:
            console.print(f"[red]Error:[/red] New path conflicts with existing project: {p.slug}")
            raise typer.Exit(2)

    # Dry run - just show what would happen
    if dry_run:
        console.print("[bold]Dry run - no changes will be made[/bold]\n")
        console.print(f"Would move repository:")
        console.print(f"  From: {old_fs_path}")
        console.print(f"  To:   {new_fs_path}")
        console.print(f"\nWould update manifest:")
        console.print(f"  Old path: {old_path}")
        console.print(f"  New path: {new_path}")
        return

    # Perform the move
    console.print(f"Moving repository...")
    console.print(f"  From: [cyan]{old_fs_path}[/cyan]")
    console.print(f"  To:   [cyan]{new_fs_path}[/cyan]")

    try:
        # Create parent directory if needed
        new_parent.mkdir(parents=True, exist_ok=True)

        # Try os.rename first - it's atomic and preserves symlinks
        # But only works on the same filesystem
        try:
            os.rename(old_fs_path, new_fs_path)
        except OSError:
            # Cross-filesystem move - use copytree with symlinks=True
            # to preserve symlinks (like .git in git-repo setups)
            shutil.copytree(
                old_fs_path,
                new_fs_path,
                symlinks=True,  # Preserve symlinks instead of following them
                dirs_exist_ok=False,
            )
            # Verify the copy succeeded before removing original
            if new_fs_path.exists():
                shutil.rmtree(old_fs_path)
            else:
                raise OSError("Copy failed - destination does not exist")

    except OSError as e:
        console.print(f"[red]Error:[/red] Failed to move repository: {e}")
        # Clean up partial copy if it exists
        if new_fs_path.exists() and old_fs_path.exists():
            shutil.rmtree(new_fs_path, ignore_errors=True)
        raise typer.Exit(1) from e

    # Update the manifest
    console.print(f"\nUpdating manifest...")
    if _update_manifest_path(manifest_path, old_path, new_path, slug):
        console.print(f"  Updated path: [cyan]{old_path}[/cyan] → [cyan]{new_path}[/cyan]")
        # Report slug changes
        old_derivable = _slug_derivable_from_path(old_path, slug)
        new_derivable = _slug_derivable_from_path(new_path, slug)
        if old_derivable and not new_derivable:
            console.print(f"  Added slug: [cyan]{slug}[/cyan]")
        elif not old_derivable and new_derivable:
            console.print(f"  Removed slug (now derivable from path)")
    else:
        # Move succeeded but manifest update failed - try to move back
        console.print("[red]Error:[/red] Failed to update manifest.")
        console.print("Attempting to restore original location...")
        try:
            try:
                os.rename(new_fs_path, old_fs_path)
            except OSError:
                shutil.copytree(new_fs_path, old_fs_path, symlinks=True)
                shutil.rmtree(new_fs_path)
            console.print("[yellow]Repository restored to original location.[/yellow]")
        except OSError:
            console.print(f"[red]Critical:[/red] Could not restore! Repository is at: {new_fs_path}")
            console.print("Please manually update the manifest or move the repository back.")
        raise typer.Exit(1)

    # Clean up empty parent directories
    old_parent = old_fs_path.parent
    while old_parent != root_path:
        try:
            if old_parent.exists() and not any(old_parent.iterdir()):
                old_parent.rmdir()
                console.print(f"  Removed empty directory: [dim]{old_parent}[/dim]")
            else:
                break
        except OSError:
            break
        old_parent = old_parent.parent

    console.print(f"\n[green]✓[/green] Successfully moved [bold]{slug}[/bold] to [cyan]{new_path}[/cyan]")
