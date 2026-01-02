"""Import command: import repositories from git-repo manifest."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

console = Console()


def _parse_repo_manifest(xml_path: Path) -> dict[str, Any]:
    """Parse a git-repo manifest XML file.

    Args:
        xml_path: Path to the manifest XML file

    Returns:
        Dict with remotes, default settings, and projects
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Parse remotes
    remotes: dict[str, str] = {}
    for remote in root.findall("remote"):
        name = remote.get("name")
        fetch = remote.get("fetch", "")
        if name:
            # Normalize URL - ensure trailing slash
            if fetch and not fetch.endswith("/"):
                fetch = fetch + "/"
            remotes[name] = fetch

    # Parse default settings
    default_elem = root.find("default")
    default_remote = default_elem.get("remote", "origin") if default_elem is not None else "origin"
    default_revision = default_elem.get("revision", "main") if default_elem is not None else "main"

    # Parse projects (skip commented out ones - they're not in ElementTree anyway)
    projects: list[dict[str, str | None]] = []
    for project in root.findall("project"):
        proj_name: str | None = project.get("name", "")
        proj_path: str | None = project.get("path", "")
        proj_remote: str | None = project.get("remote")  # None means use default
        proj_revision: str | None = project.get("revision")  # None means use default

        if not proj_name or not proj_path:
            continue

        # Clean up name - remove .git suffix if present
        if proj_name.endswith(".git"):
            proj_name = proj_name[:-4]

        projects.append({
            "slug": proj_name,
            "path": proj_path,
            "remote": proj_remote,
            "revision": proj_revision,
        })

    return {
        "remotes": remotes,
        "default_remote": default_remote,
        "default_revision": default_revision,
        "projects": projects,
    }


def _generate_toml(
    parsed: dict[str, Any],
    root_path: str,
) -> str:
    """Generate TOML manifest from parsed git-repo data.

    Args:
        parsed: Parsed manifest data
        root_path: Root path for the manifest

    Returns:
        TOML string
    """
    lines = [
        "[common]",
        f'root_path = "{root_path}"',
        f'branch = "{parsed["default_revision"]}"',
        f'remote = "{parsed["default_remote"]}"',
        "parallelism = 4",
        "timeout = 300",
        "",
        "[remotes]",
    ]

    # Add remotes
    for name, base_url in sorted(parsed["remotes"].items()):
        lines.append(f'{name} = {{ base_url = "{base_url}" }}')

    lines.append("")
    lines.append("[projects]")

    # Add projects
    for proj in sorted(parsed["projects"], key=lambda p: p["path"]):
        path = proj["path"]
        slug = proj["slug"]
        remote = proj["remote"]
        revision = proj["revision"]

        # Build inline table parts
        parts: list[str] = []

        # Only include slug if it differs from path's final component
        path_name = Path(path).name
        if slug != path_name:
            parts.append(f'slug = "{slug}"')

        # Only include remote if different from default
        if remote and remote != parsed["default_remote"]:
            parts.append(f'remote = "{remote}"')

        # Only include branch if different from default
        if revision and revision != parsed["default_revision"]:
            parts.append(f'branch = "{revision}"')

        if parts:
            lines.append(f'"{path}" = {{ {", ".join(parts)} }}')
        else:
            # Empty table - just the path with derived slug
            lines.append(f'"{path}" = {{ }}')

    return "\n".join(lines) + "\n"


def import_manifest(
    source: Annotated[
        Path,
        typer.Argument(help="Path to git-repo manifest XML file (e.g., default.xml)"),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output path for manifest.toml"),
    ] = Path("manifest.toml"),
    root_path: Annotated[
        str | None,
        typer.Option("--root", "-r", help="Root path for repos (default: parent of source file)"),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing manifest"),
    ] = False,
) -> None:
    """Import repositories from a git-repo manifest XML file.

    Converts a Google repo tool manifest (default.xml) to repo-sync-kitty format.
    """
    if not source.exists():
        console.print(f"[red]Error:[/red] Source file not found: {source}")
        raise typer.Exit(2)

    if output.exists() and not force:
        console.print(f"[red]Error:[/red] {output} already exists. Use --force to overwrite.")
        raise typer.Exit(1)

    # Parse the XML manifest
    try:
        parsed = _parse_repo_manifest(source)
    except ET.ParseError as e:
        console.print(f"[red]Error:[/red] Invalid XML: {e}")
        raise typer.Exit(2) from e

    # Determine root path
    if root_path is None:
        # Default to parent directory of the manifest
        root_path = str(source.parent.parent.resolve())

    console.print(f"Importing from [cyan]{source}[/cyan]...")
    console.print(f"  Remotes: {len(parsed['remotes'])}")
    console.print(f"  Projects: {len(parsed['projects'])}")
    console.print(f"  Default remote: {parsed['default_remote']}")
    console.print(f"  Default branch: {parsed['default_revision']}")

    # Generate TOML
    toml_content = _generate_toml(parsed, root_path)

    # Write output
    output.write_text(toml_content)
    console.print(f"\n[green]✓[/green] Created {output}")
    console.print(f"\nRoot path set to: {root_path}")
    console.print(f"Run [bold]repo-sync-kitty check -m {output}[/bold] to validate.")
