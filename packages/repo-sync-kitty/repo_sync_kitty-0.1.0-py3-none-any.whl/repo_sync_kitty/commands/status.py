"""Status command: show repository sync status."""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from repo_sync_kitty.config.loader import (
    ManifestError,
    ResolvedProject,
    load_manifest,
    resolve_all_projects,
)
from repo_sync_kitty.git.operations import RepoManager

console = Console()


def _normalize_git_url(url: str) -> str:
    """Normalize a git URL for comparison.

    Handles variations like:
    - https://github.com/owner/repo vs https://github.com/owner/repo.git
    - git@github.com:owner/repo vs ssh://git@github.com/owner/repo
    - Trailing slashes

    Args:
        url: Git URL to normalize

    Returns:
        Normalized URL for comparison
    """
    url = url.strip().rstrip("/")

    # Remove .git suffix
    if url.endswith(".git"):
        url = url[:-4]

    # Convert SSH shorthand (git@host:path) to ssh:// format
    ssh_shorthand = re.match(r"^(\w+)@([^:]+):(.+)$", url)
    if ssh_shorthand:
        user, host, path = ssh_shorthand.groups()
        url = f"ssh://{user}@{host}/{path}"

    # Normalize to lowercase for comparison
    return url.lower()


def _any_remote_matches(remote_urls: dict[str, str], expected_url: str) -> bool:
    """Check if any configured remote URL matches the expected URL.

    Args:
        remote_urls: Dict mapping remote names to URLs
        expected_url: Expected clone URL from manifest

    Returns:
        True if at least one remote matches
    """
    expected_normalized = _normalize_git_url(expected_url)

    for url in remote_urls.values():
        if _normalize_git_url(url) == expected_normalized:
            return True

    return False


@dataclass
class RepoStatus:
    """Status of a single repository."""

    project: ResolvedProject
    exists: bool
    current_branch: str | None = None
    expected_branch: str | None = None
    is_clean: bool = True
    is_detached: bool = False
    ahead: int = 0
    behind: int = 0
    in_progress_op: str | None = None
    issues: list[str] | None = None

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []

    @property
    def has_issues(self) -> bool:
        """Check if this repo has any issues."""
        return len(self.issues or []) > 0

    @property
    def status_label(self) -> str:
        """Get a short status label."""
        if not self.exists:
            return "missing"
        if self.is_detached:
            return "detached"
        if not self.is_clean:
            return "dirty"
        if self.ahead > 0:
            return "ahead"
        if self.behind > 0:
            return "behind"
        return "ok"


def get_repo_status(project: ResolvedProject, root_path: Path) -> RepoStatus:
    """Get the status of a single repository.

    Args:
        project: The resolved project configuration
        root_path: Root directory for all repos

    Returns:
        RepoStatus with current state
    """
    repo_path = root_path / project.path
    issues: list[str] = []

    # Check if repo exists
    mgr = RepoManager(repo_path)
    if not mgr.exists():
        # For deleted repos, not existing is the expected state (no issue)
        if project.status == "deleted":
            return RepoStatus(
                project=project,
                exists=False,
                expected_branch=project.branch,
                issues=[],  # No issues - this is expected
            )
        # For active/archived repos, not existing is an issue
        issues.append("not cloned")
        return RepoStatus(
            project=project,
            exists=False,
            expected_branch=project.branch,
            issues=issues,
        )

    # Get current state
    current_branch = mgr.get_current_branch()
    is_detached = mgr.is_detached()
    is_clean = mgr.is_clean()
    in_progress_op = mgr.get_in_progress_operation()

    # Get ahead/behind compared to the project's declared remote
    ahead, behind = mgr.get_ahead_behind(
        remote_name=project.remote_name, branch=project.branch
    )

    # Check for issues
    if is_detached:
        issues.append("HEAD detached")

    if current_branch and current_branch != project.branch:
        issues.append(f"on '{current_branch}' (expected '{project.branch}')")

    if not is_clean:
        # Get more details
        if mgr.has_staged_changes():
            issues.append("staged changes")
        if mgr.has_modified_files():
            issues.append("modified files")
        if mgr.has_untracked_files():
            issues.append("untracked files")

    if in_progress_op:
        issues.append(f"{in_progress_op} in progress")

    if ahead > 0:
        issues.append(f"{ahead} unpushed commit(s)")

    if behind > 0:
        issues.append(f"{behind} commit(s) behind")

    # Check if any configured remote matches the expected URL
    remote_urls = mgr.get_remote_urls()
    expected_url = project.clone_url
    if not _any_remote_matches(remote_urls, expected_url):
        issues.append(f"no remote matches expected URL")

    # Deleted repo still exists on disk - check if safe to delete
    if project.status == "deleted":
        if issues:
            # Has other issues - NOT safe to delete
            issues.insert(0, "NOT SAFE TO DELETE")
        else:
            # Clean state - safe to delete
            issues.append("marked deleted but still exists")

    return RepoStatus(
        project=project,
        exists=True,
        current_branch=current_branch,
        expected_branch=project.branch,
        is_clean=is_clean,
        is_detached=is_detached,
        ahead=ahead,
        behind=behind,
        in_progress_op=in_progress_op,
        issues=issues,
    )


def create_status_table(
    statuses: list[RepoStatus],
    show_all: bool = False,
    show_deleted: bool = False,
) -> Table:
    """Create a Rich table showing repository statuses.

    Args:
        statuses: List of repo statuses
        show_all: Show all repos, not just those with issues
        show_deleted: Include deleted repos

    Returns:
        Rich Table object
    """
    table = Table(title="Repository Status")
    table.add_column("Path", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Branch")
    table.add_column("Issues")

    for status in statuses:
        # Skip deleted repos without issues (properly cleaned up) unless --show-deleted
        # But show deleted repos that still exist (they have issues)
        if status.project.status == "deleted" and not status.has_issues and not show_deleted:
            continue

        # Skip repos without issues unless --all
        if not show_all and not status.has_issues:
            continue

        # Determine status color
        status_label = status.status_label
        if status_label == "ok":
            status_style = "[green]ok[/green]"
        elif status_label == "missing":
            status_style = "[red]missing[/red]"
        elif status_label in ("dirty", "detached"):
            status_style = f"[yellow]{status_label}[/yellow]"
        else:
            status_style = f"[blue]{status_label}[/blue]"

        # Format branch
        if status.exists and status.current_branch:
            branch = status.current_branch
            if status.current_branch != status.expected_branch:
                branch = f"[yellow]{branch}[/yellow]"
        else:
            branch = "-"

        # Format issues
        issues_str = ", ".join(status.issues or []) if status.issues else ""

        # Add archived indicator
        if status.project.status == "archived":
            status_style = f"{status_style} [dim](archived)[/dim]"

        table.add_row(
            str(status.project.path),
            status_style,
            branch,
            issues_str,
        )

    return table


def _collect_statuses_with_progress(
    projects: list[ResolvedProject],
    root_path: Path,
    parallelism: int,
) -> list[RepoStatus]:
    """Collect repo statuses with progress bar.

    Args:
        projects: List of resolved projects
        root_path: Root directory for all repos
        parallelism: Number of parallel workers

    Returns:
        List of RepoStatus objects
    """
    statuses: list[RepoStatus] = []

    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Collecting status...", total=len(projects))

        with ThreadPoolExecutor(max_workers=parallelism) as executor:
            futures = {
                executor.submit(get_repo_status, project, root_path): project
                for project in projects
            }

            for future in as_completed(futures):
                result = future.result()
                statuses.append(result)
                progress.update(task, advance=1, description=f"Checked {result.project.path}")

    # Sort by original project order
    project_order = {str(p.path): i for i, p in enumerate(projects)}
    statuses.sort(key=lambda s: project_order.get(str(s.project.path), 0))

    return statuses


def _collect_statuses_verbose(
    projects: list[ResolvedProject],
    root_path: Path,
) -> list[RepoStatus]:
    """Collect repo statuses with verbose output (no progress bar).

    Args:
        projects: List of resolved projects
        root_path: Root directory for all repos

    Returns:
        List of RepoStatus objects
    """
    statuses: list[RepoStatus] = []
    for project in projects:
        repo_status = get_repo_status(project, root_path)
        statuses.append(repo_status)
        # Show each repo as it's checked
        status_label = repo_status.status_label
        if status_label == "ok":
            console.print(f"  [green]✓[/green] {project.path}")
        elif status_label == "missing":
            console.print(f"  [red]✗[/red] {project.path} (missing)")
        else:
            issues_str = ", ".join(repo_status.issues or [])
            console.print(f"  [yellow]![/yellow] {project.path}: {issues_str}")
    return statuses


def status(
    ctx: typer.Context,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed output instead of progress bar"),
    ] = False,
    show_all: Annotated[
        bool,
        typer.Option("--all", "-a", help="Show all repos, not just those with issues"),
    ] = False,
    show_deleted: Annotated[
        bool,
        typer.Option("--show-deleted", help="Include deleted repos in output"),
    ] = False,
    parallelism: Annotated[
        int | None,
        typer.Option("--parallelism", "-j", help="Number of parallel workers"),
    ] = None,
) -> None:
    """Show repository sync status."""
    # Find manifest: command option > global option > default
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

    # Determine parallelism
    num_workers = parallelism or mf.common.parallelism

    # Resolve all projects
    projects = resolve_all_projects(mf)

    # Get status for each project
    if verbose:
        console.print(f"Checking {len(projects)} repositories...\n")
        statuses = _collect_statuses_verbose(projects, root_path)
        console.print()  # Blank line before table
    else:
        statuses = _collect_statuses_with_progress(projects, root_path, num_workers)

    # Create and display table
    table = create_status_table(statuses, show_all=show_all, show_deleted=show_deleted)
    console.print(table)

    # Summary
    total = len([s for s in statuses if s.project.status != "deleted" or show_deleted])
    issues = len([s for s in statuses if s.has_issues and (s.project.status != "deleted" or show_deleted)])
    missing = len([s for s in statuses if not s.exists and s.project.status == "active"])

    if issues > 0:
        console.print(f"\n[yellow]{issues} issue(s)[/yellow] found in {total} repositories.")
        if missing > 0:
            console.print(f"Run [bold]repo-sync-kitty sync[/bold] to clone {missing} missing repo(s).")
    elif verbose:
        console.print(f"\n[green]All {total} repositories are in sync.[/green]")
