"""Check command: validate manifest file."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from repo_sync_kitty.config import (
    ManifestError,
    load_manifest,
    resolve_all_projects,
    validate_manifest,
)

console = Console()


def check(
    ctx: typer.Context,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
) -> None:
    """Validate the manifest file."""
    # Determine manifest path: command option > global option > default
    global_manifest = ctx.obj.get("manifest") if ctx.obj else None
    manifest_path = manifest or global_manifest or Path("manifest.toml")

    try:
        m = load_manifest(manifest_path)
    except ManifestError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2) from None

    # Run semantic validation
    errors = validate_manifest(m)

    if errors:
        console.print(f"[red]Manifest validation failed with {len(errors)} error(s):[/red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(code=2)

    # Success - show summary
    console.print(f"[green]✓[/green] Manifest is valid: {manifest_path}")
    console.print()

    # Show common config
    console.print("[bold]Common Configuration:[/bold]")
    console.print(f"  Root path:    {m.common.root_path}")
    console.print(f"  Default remote: {m.common.remote}")
    console.print(f"  Default branch: {m.common.branch}")
    console.print(f"  Parallelism:  {m.common.parallelism}")
    console.print(f"  Timeout:      {m.common.timeout}s")
    console.print()

    # Show remotes
    console.print(f"[bold]Remotes ({len(m.remotes)}):[/bold]")
    for remote in m.remotes:
        branch_info = f" (branch: {remote.branch})" if remote.branch else ""
        console.print(f"  • {remote.name}: {remote.base_url}{branch_info}")
    console.print()

    # Show projects table
    console.print(f"[bold]Projects ({len(m.projects)}):[/bold]")

    # Resolve all projects to show effective values
    resolved = resolve_all_projects(m)

    table = Table(show_header=True, header_style="bold")
    table.add_column("Path")
    table.add_column("Remote")
    table.add_column("Slug")
    table.add_column("Branch")
    table.add_column("Status")

    for proj in resolved:
        status_style = {
            "active": "green",
            "archived": "yellow",
            "deleted": "red",
        }.get(proj.status, "")
        table.add_row(
            str(proj.path),
            proj.remote_name,
            proj.slug,
            proj.branch,
            f"[{status_style}]{proj.status}[/{status_style}]" if status_style else proj.status,
        )

    console.print(table)

    # Summary counts
    active = sum(1 for p in resolved if p.status == "active")
    archived = sum(1 for p in resolved if p.status == "archived")
    deleted = sum(1 for p in resolved if p.status == "deleted")

    console.print()
    console.print(
        f"Summary: {active} active, {archived} archived, {deleted} deleted"
    )
