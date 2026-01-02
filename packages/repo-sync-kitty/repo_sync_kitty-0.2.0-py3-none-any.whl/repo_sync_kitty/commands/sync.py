"""Sync command: clone missing repos, fetch/pull existing."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from repo_sync_kitty.config.loader import (
    ManifestError,
    ResolvedProject,
    load_manifest,
    resolve_all_projects,
)
from repo_sync_kitty.git.operations import (
    CloneError,
    FetchError,
    PullError,
    RepoManager,
)
from repo_sync_kitty.git.retry import RetryConfig, with_retry
from repo_sync_kitty.git.safety import SafetyChecker

console = Console()


@dataclass
class SyncResult:
    """Result of syncing a single repository."""

    project: ResolvedProject
    action: str  # "cloned", "fetched", "pulled", "skipped", "error"
    success: bool
    message: str = ""
    error: Exception | None = None


@dataclass
class SyncSummary:
    """Summary of all sync operations."""

    results: list[SyncResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def cloned(self) -> int:
        return len([r for r in self.results if r.action == "cloned" and r.success])

    @property
    def fetched(self) -> int:
        return len([r for r in self.results if r.action == "fetched" and r.success])

    @property
    def pulled(self) -> int:
        return len([r for r in self.results if r.action == "pulled" and r.success])

    @property
    def skipped(self) -> int:
        return len([r for r in self.results if r.action == "skipped"])

    @property
    def errors(self) -> list[SyncResult]:
        return [r for r in self.results if not r.success]


def sync_repo(
    project: ResolvedProject,
    root_path: Path,
    fetch_only: bool = False,
    clone_only: bool = False,
    pull: bool = False,
    dry_run: bool = False,
    retry_config: RetryConfig | None = None,
) -> SyncResult:
    """Sync a single repository.

    Args:
        project: The resolved project to sync
        root_path: Root directory for repos
        fetch_only: Only fetch, don't clone or pull
        clone_only: Only clone missing repos
        pull: Pull after fetch if safe
        dry_run: Just report what would be done
        retry_config: Retry configuration for network operations

    Returns:
        SyncResult with outcome
    """
    repo_path = root_path / project.path
    mgr = RepoManager(repo_path)

    # Skip deleted repos entirely
    if project.status == "deleted":
        return SyncResult(
            project=project,
            action="skipped",
            success=True,
            message="status is deleted",
        )

    # Check if repo exists
    if not mgr.exists():
        if fetch_only:
            return SyncResult(
                project=project,
                action="skipped",
                success=True,
                message="not cloned (fetch-only mode)",
            )

        # Clone the repository
        if dry_run:
            return SyncResult(
                project=project,
                action="cloned",
                success=True,
                message=f"would clone from {project.clone_url}",
            )

        try:
            # Ensure parent directory exists
            repo_path.parent.mkdir(parents=True, exist_ok=True)

            # Clone with retry
            def do_clone() -> RepoManager:
                return RepoManager.clone(
                    project.clone_url,
                    repo_path,
                    branch=project.branch,
                )

            result = with_retry(do_clone, config=retry_config)
            if not result.success:
                raise result.last_error or CloneError("Clone failed after retries")

            return SyncResult(
                project=project,
                action="cloned",
                success=True,
                message=f"cloned {project.branch}",
            )
        except CloneError as e:
            return SyncResult(
                project=project,
                action="error",
                success=False,
                message=str(e),
                error=e,
            )

    # Repo exists - fetch and optionally pull
    if clone_only:
        return SyncResult(
            project=project,
            action="skipped",
            success=True,
            message="already cloned (clone-only mode)",
        )

    # Archived repos: clone if missing (handled above), but don't fetch/pull
    if project.status == "archived":
        return SyncResult(
            project=project,
            action="skipped",
            success=True,
            message="archived (no fetch/pull)",
        )

    # Fetch
    if dry_run:
        msg = "would fetch"
        if pull:
            msg += " and pull if safe"
        return SyncResult(
            project=project,
            action="fetched",
            success=True,
            message=msg,
        )

    try:
        # Fetch with retry
        def do_fetch() -> None:
            mgr.fetch()

        result = with_retry(do_fetch, config=retry_config)
        if not result.success:
            raise result.last_error or FetchError("Fetch failed after retries")

    except FetchError as e:
        return SyncResult(
            project=project,
            action="error",
            success=False,
            message=f"fetch failed: {e}",
            error=e,
        )

    # Pull if requested and safe
    if not pull or fetch_only:
        return SyncResult(
            project=project,
            action="fetched",
            success=True,
            message="fetched",
        )

    # Check safety before pull
    checker = SafetyChecker(mgr)
    safety = checker.check(expected_branch=project.branch)

    if not safety.safe_to_pull:
        reasons = ", ".join(safety.reasons)
        return SyncResult(
            project=project,
            action="skipped",
            success=True,
            message=f"not safe to pull: {reasons}",
        )

    # Pull
    try:
        def do_pull() -> None:
            mgr.pull()

        result = with_retry(do_pull, config=retry_config)
        if not result.success:
            raise result.last_error or PullError("Pull failed after retries")

        return SyncResult(
            project=project,
            action="pulled",
            success=True,
            message="fetched and pulled",
        )
    except PullError as e:
        return SyncResult(
            project=project,
            action="error",
            success=False,
            message=f"pull failed: {e}",
            error=e,
        )


def _sync_verbose(
    projects: list[ResolvedProject],
    root_path: Path,
    summary: SyncSummary,
    num_workers: int,
    fetch_only: bool,
    clone_only: bool,
    pull: bool,
    dry_run: bool,
    retry_config: RetryConfig,
) -> None:
    """Sync repos with verbose output showing each operation."""
    console.print(f"[bold]Syncing {len(projects)} repositories (parallelism: {num_workers})[/bold]\n")

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {
            executor.submit(
                sync_repo,
                project,
                root_path,
                fetch_only=fetch_only,
                clone_only=clone_only,
                pull=pull,
                dry_run=dry_run,
                retry_config=retry_config,
            ): project
            for project in projects
        }

        for future in as_completed(futures):
            result = future.result()
            summary.results.append(result)

            # Print verbose output
            path = result.project.path
            if result.success:
                if result.action == "cloned":
                    console.print(f"[green]✓[/green] {path}: cloned ({result.message})")
                elif result.action == "fetched":
                    console.print(f"[blue]↓[/blue] {path}: fetched")
                elif result.action == "pulled":
                    console.print(f"[cyan]↓[/cyan] {path}: pulled")
                elif result.action == "skipped":
                    console.print(f"[dim]–[/dim] {path}: skipped ({result.message})")
            else:
                console.print(f"[red]✗[/red] {path}: {result.message}")


def _sync_with_progress(
    projects: list[ResolvedProject],
    root_path: Path,
    summary: SyncSummary,
    num_workers: int,
    fetch_only: bool,
    clone_only: bool,
    pull: bool,
    dry_run: bool,
    retry_config: RetryConfig,
) -> None:
    """Sync repos with progress bar."""
    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Syncing repositories...", total=len(projects))

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(
                    sync_repo,
                    project,
                    root_path,
                    fetch_only=fetch_only,
                    clone_only=clone_only,
                    pull=pull,
                    dry_run=dry_run,
                    retry_config=retry_config,
                ): project
                for project in projects
            }

            for future in as_completed(futures):
                result = future.result()
                summary.results.append(result)
                progress.update(task, advance=1, description=f"Synced {result.project.path}")


def print_summary(summary: SyncSummary, dry_run: bool = False, verbose: bool = False) -> None:
    """Print sync summary to console."""
    if dry_run:
        console.print("\n[bold]Dry run complete.[/bold] No changes made.")
    else:
        console.print("\n[bold]Sync complete.[/bold]")

    parts = []
    if summary.cloned > 0:
        parts.append(f"[green]{summary.cloned} cloned[/green]")
    if summary.fetched > 0:
        parts.append(f"[blue]{summary.fetched} fetched[/blue]")
    if summary.pulled > 0:
        parts.append(f"[cyan]{summary.pulled} pulled[/cyan]")
    if summary.skipped > 0:
        parts.append(f"[dim]{summary.skipped} skipped[/dim]")
    if summary.errors:
        parts.append(f"[red]{len(summary.errors)} failed[/red]")

    if parts:
        console.print("  " + ", ".join(parts))

    # Show skipped repos with reasons (only in verbose mode)
    if verbose:
        skipped = [r for r in summary.results if r.action == "skipped"]
        if skipped:
            console.print(f"\n[dim]Skipped ({len(skipped)}):[/dim]")
            for result in skipped:
                console.print(f"  [dim]–[/dim] {result.project.path}: {result.message}")

    # Show errors with details (always shown)
    if summary.errors:
        console.print(f"\n[red]Errors ({len(summary.errors)}):[/red]")
        for err in summary.errors:
            console.print(f"  [red]✗[/red] {err.project.path}: {err.message}")


def sync(
    ctx: typer.Context,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    fetch_only: Annotated[
        bool,
        typer.Option("--fetch-only", help="Only fetch, don't clone or pull"),
    ] = False,
    clone_only: Annotated[
        bool,
        typer.Option("--clone-only", help="Only clone missing repos"),
    ] = False,
    pull: Annotated[
        bool,
        typer.Option("--pull", help="Pull changes after fetch (if safe)"),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Show what would be done"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed output instead of progress bar"),
    ] = False,
    parallelism: Annotated[
        int | None,
        typer.Option("--parallelism", "-j", help="Number of parallel operations (overrides config)"),
    ] = None,
) -> None:
    """Clone missing repos, fetch updates, and optionally pull."""
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

    # Resolve all projects - include active and archived (but not deleted)
    projects = resolve_all_projects(mf)
    syncable_projects = [p for p in projects if p.status != "deleted"]

    if not syncable_projects:
        console.print("[yellow]No projects to sync.[/yellow]")
        return

    # Set up retry config
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
    )

    # Sync with progress
    summary = SyncSummary()
    # CLI parallelism overrides all config settings
    num_workers = parallelism if parallelism is not None else mf.common.parallelism

    if verbose:
        # Verbose mode: show detailed output
        _sync_verbose(
            syncable_projects,
            root_path,
            summary,
            num_workers,
            fetch_only,
            clone_only,
            pull,
            dry_run,
            retry_config,
        )
    else:
        # Progress bar mode
        _sync_with_progress(
            syncable_projects,
            root_path,
            summary,
            num_workers,
            fetch_only,
            clone_only,
            pull,
            dry_run,
            retry_config,
        )

    # Add deleted projects to summary as skipped
    for project in projects:
        if project.status == "deleted":
            summary.results.append(
                SyncResult(
                    project=project,
                    action="skipped",
                    success=True,
                    message="status is deleted",
                )
            )

    # Print summary
    print_summary(summary, dry_run=dry_run, verbose=verbose)

    # Exit with error if any failures
    if summary.errors:
        raise typer.Exit(1)
