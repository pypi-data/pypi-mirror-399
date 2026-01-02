"""Add command: add repository to manifest."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from repo_sync_kitty.config.loader import (
    ManifestError,
    get_remote_by_name,
    load_manifest,
)

console = Console()


def _path_from_slug(slug: str) -> str:
    """Generate a default path from a slug.

    Args:
        slug: Repository slug like "owner/repo"

    Returns:
        Path string like "repo"
    """
    # Use just the repo name as path
    if "/" in slug:
        return slug.split("/")[-1]
    return slug


def _read_manifest_text(path: Path) -> str:
    """Read manifest file as text."""
    return path.read_text()


def _add_project_to_manifest(
    manifest_text: str,
    path: str,
    slug: str | None,
    remote: str | None = None,
    branch: str | None = None,
) -> str:
    """Add a project entry to manifest TOML text.

    Args:
        manifest_text: Current manifest content
        path: Project path
        slug: Repository slug (None to derive from path)
        remote: Optional remote name
        branch: Optional branch name

    Returns:
        Updated manifest text
    """
    # Build the project entry parts
    parts: list[str] = []
    if slug:
        parts.append(f'slug = "{slug}"')
    if remote:
        parts.append(f'remote = "{remote}"')
    if branch:
        parts.append(f'branch = "{branch}"')

    entry = f'"{path}" = {{ {", ".join(parts)} }}'

    # Find [projects] section and add entry
    lines = manifest_text.split("\n")
    result_lines: list[str] = []
    in_projects = False
    added = False

    for line in lines:
        result_lines.append(line)

        # Detect [projects] section
        if line.strip() == "[projects]":
            in_projects = True
            continue

        # Detect next section (end of projects)
        if in_projects and line.strip().startswith("[") and not line.strip().startswith('["'):
            # Add before next section
            if not added:
                result_lines.insert(-1, entry)
                added = True
            in_projects = False

    # If still in projects at end (no next section), append
    if in_projects and not added:
        result_lines.append(entry)

    return "\n".join(result_lines)


def add(
    ctx: typer.Context,
    remote: Annotated[str, typer.Argument(help="Remote name (must exist in manifest)")],
    slug: Annotated[str, typer.Argument(help="Repository slug (e.g., 'owner/repo')")],
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    path: Annotated[
        Path | None,
        typer.Option("--path", "-p", help="Local path (defaults to repo name from slug)"),
    ] = None,
    branch: Annotated[
        str | None,
        typer.Option("--branch", "-b", help="Branch to track"),
    ] = None,
) -> None:
    """Add a repository to the manifest."""
    # Find manifest: command option > global option > default
    global_manifest = ctx.obj.get("manifest") if ctx.obj else None
    manifest_path = manifest or global_manifest or Path("manifest.toml")

    if not manifest_path.exists():
        console.print(f"[red]Error:[/red] Manifest not found: {manifest_path}")
        console.print("Run [bold]repo-sync-kitty init[/bold] to create one.")
        raise typer.Exit(2)

    # Load and validate manifest
    try:
        mf = load_manifest(manifest_path)
    except ManifestError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(2) from e

    # Check remote exists
    if not get_remote_by_name(mf, remote):
        available = ", ".join(r.name for r in mf.remotes)
        console.print(f"[red]Error:[/red] Remote '{remote}' not found in manifest.")
        console.print(f"Available remotes: {available}")
        raise typer.Exit(2)

    # Determine path
    project_path = str(path) if path else _path_from_slug(slug)

    # Check for duplicate path
    existing_paths = {str(p.path) for p in mf.projects}
    if project_path in existing_paths:
        console.print(f"[red]Error:[/red] Path '{project_path}' already exists in manifest.")
        raise typer.Exit(1)

    # Read current manifest text
    manifest_text = _read_manifest_text(manifest_path)

    # Determine if we need to include remote (only if different from default)
    include_remote = remote != mf.common.remote

    # Add project
    updated_text = _add_project_to_manifest(
        manifest_text,
        project_path,
        slug,
        remote=remote if include_remote else None,
        branch=branch,
    )

    # Write updated manifest
    manifest_path.write_text(updated_text)

    console.print(f"[green]✓[/green] Added {slug} at {project_path}")
    if branch:
        console.print(f"  Branch: {branch}")
    console.print(f"  Remote: {remote}")
