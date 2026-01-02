"""Fix detached HEAD states left by git-repo."""

from dataclasses import dataclass
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
from repo_sync_kitty.git.operations import RepoManager

console = Console()


@dataclass
class FixResult:
    """Result of attempting to fix a detached HEAD."""

    project: ResolvedProject
    action: str  # "fixed", "skipped", "error"
    message: str
    branch_checked_out: str | None = None


def _check_repo_clean(mgr: RepoManager) -> str | None:
    """Check if repo has any loose files.

    Args:
        mgr: RepoManager for the repo

    Returns:
        Error message if repo is not clean, None if clean
    """
    issues = []
    if mgr.has_untracked_files():
        issues.append("untracked files")
    if mgr.has_modified_files():
        issues.append("modified files")
    if mgr.has_staged_changes():
        issues.append("staged changes")
    if mgr.get_in_progress_operation():
        issues.append(f"{mgr.get_in_progress_operation()} in progress")

    if issues:
        return f"has {', '.join(issues)}"
    return None


def fix_detached_repo(
    project: ResolvedProject,
    root_path: Path,
    dry_run: bool = False,
) -> FixResult:
    """Attempt to fix detached HEAD for a single repo.

    Args:
        project: The resolved project configuration
        root_path: Root directory for all repos
        dry_run: If True, don't actually checkout

    Returns:
        FixResult with outcome
    """
    repo_path = root_path / project.path
    mgr = RepoManager(repo_path)

    # Check if repo exists
    if not mgr.exists():
        return FixResult(
            project=project,
            action="skipped",
            message="not cloned",
        )

    # Check if HEAD is detached
    if not mgr.is_detached():
        return FixResult(
            project=project,
            action="skipped",
            message="not detached",
        )

    # Check for loose files
    clean_error = _check_repo_clean(mgr)
    if clean_error:
        return FixResult(
            project=project,
            action="error",
            message=f"cannot fix: {clean_error}",
        )

    # Find which branches point to HEAD
    local_branches = mgr.get_branches_at_head()
    remote_branches = mgr.get_remote_branches_at_head()

    expected = project.branch

    # First, check local branches
    if local_branches:
        if expected in local_branches:
            target_branch = expected
        elif len(local_branches) == 1:
            target_branch = local_branches[0]
        else:
            return FixResult(
                project=project,
                action="error",
                message=f"ambiguous: HEAD at local branches {local_branches}, expected '{expected}'",
            )

        # Checkout the local branch
        if dry_run:
            return FixResult(
                project=project,
                action="fixed",
                message=f"would checkout '{target_branch}'",
                branch_checked_out=target_branch,
            )

        try:
            mgr.checkout(target_branch)
            return FixResult(
                project=project,
                action="fixed",
                message=f"checked out '{target_branch}'",
                branch_checked_out=target_branch,
            )
        except Exception as e:
            return FixResult(
                project=project,
                action="error",
                message=f"checkout failed: {e}",
            )

    # No local branches at HEAD - check remote branches
    if not remote_branches:
        head_sha = mgr.get_head_commit()[:8]
        return FixResult(
            project=project,
            action="error",
            message=f"HEAD ({head_sha}) is not at any branch tip",
        )

    # Find matching remote branch for expected branch
    matching_remotes = [(r, b) for r, b in remote_branches if b == expected]

    if matching_remotes:
        # Use the first matching remote (prefer origin if present)
        origin_match = [(r, b) for r, b in matching_remotes if r == "origin"]
        remote_name, branch_name = origin_match[0] if origin_match else matching_remotes[0]
    elif len(remote_branches) == 1:
        # Only one remote branch at HEAD, use it
        remote_name, branch_name = remote_branches[0]
    else:
        # Multiple remote branches, none match expected
        remote_list = [f"{r}/{b}" for r, b in remote_branches]
        return FixResult(
            project=project,
            action="error",
            message=f"ambiguous: HEAD at remote branches {remote_list}, expected '{expected}'",
        )

    # Create local tracking branch and checkout
    if dry_run:
        return FixResult(
            project=project,
            action="fixed",
            message=f"would create and checkout '{branch_name}' (tracking {remote_name}/{branch_name})",
            branch_checked_out=branch_name,
        )

    try:
        mgr.create_tracking_branch(branch_name, remote_name)
        mgr.checkout(branch_name)
        return FixResult(
            project=project,
            action="fixed",
            message=f"created and checked out '{branch_name}' (tracking {remote_name}/{branch_name})",
            branch_checked_out=branch_name,
        )
    except Exception as e:
        return FixResult(
            project=project,
            action="error",
            message=f"failed to create/checkout branch: {e}",
        )


def fix_detached(
    ctx: typer.Context,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", "-n", help="Show what would be done without making changes"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed output instead of progress bar"),
    ] = False,
    parallelism: Annotated[
        int | None,
        typer.Option("--parallelism", "-j", help="Number of parallel workers"),
    ] = None,
) -> None:
    """Fix detached HEAD states left by git-repo.

    Safely checks out branches for repos where HEAD is detached but pointing
    at a branch tip. Only fixes repos that are clean (no loose files).
    """
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

    # Resolve paths
    root_path = Path(mf.common.root_path).expanduser()
    num_workers = parallelism or mf.common.parallelism
    projects = resolve_all_projects(mf)

    # Filter out deleted projects (include active and archived)
    active_projects = [p for p in projects if p.status != "deleted"]

    if dry_run:
        console.print("[bold]Dry run mode[/bold] - no changes will be made.\n")

    # Collect results
    results: list[FixResult] = []

    if verbose:
        console.print(f"Checking {len(active_projects)} repositories...\n")
        for project in active_projects:
            result = fix_detached_repo(project, root_path, dry_run)
            results.append(result)

            if result.action == "fixed":
                console.print(f"  [green]✓[/green] {project.path}: {result.message}")
            elif result.action == "error":
                console.print(f"  [red]✗[/red] {project.path}: {result.message}")
            # Skip "skipped" in verbose - too noisy
    else:
        # Progress bar mode with parallelism
        from concurrent.futures import ThreadPoolExecutor, as_completed

        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fixing detached heads...", total=len(active_projects))

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {
                    executor.submit(fix_detached_repo, project, root_path, dry_run): project
                    for project in active_projects
                }

                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    progress.update(task, advance=1, description=f"Checked {result.project.path}")

    # Summary
    fixed = [r for r in results if r.action == "fixed"]
    errors = [r for r in results if r.action == "error"]
    skipped = [r for r in results if r.action == "skipped"]

    console.print()
    if fixed:
        console.print(f"[green]Fixed {len(fixed)} detached HEAD(s)[/green]")
        if not verbose:
            for r in fixed:
                console.print(f"  • {r.project.path}: {r.message}")

    if errors:
        console.print(f"\n[red]{len(errors)} repo(s) could not be fixed:[/red]")
        for r in errors:
            console.print(f"  • {r.project.path}: {r.message}")

    if not fixed and not errors:
        console.print("[green]No detached HEADs found that need fixing.[/green]")

    # Show counts
    detached_count = len(fixed) + len(errors)
    console.print(f"\nSummary: {detached_count} detached, {len(fixed)} fixed, {len(errors)} errors, {len(skipped)} already ok")

    if errors:
        raise typer.Exit(1)
