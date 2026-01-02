"""Enroll a local repository on GitHub."""

import os
import webbrowser
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from repo_sync_kitty.config.loader import (
    ManifestError,
    construct_clone_url,
    extract_owner_from_base_url,
    get_remote_by_name,
    load_manifest,
)
from repo_sync_kitty.forge.github import (
    GitHubAPIError,
    GitHubAuthError,
    GitHubClient,
    GitHubRepoExistsError,
)
from repo_sync_kitty.git.operations import GitError, PushError, RepoManager

console = Console()


def enroll(
    ctx: typer.Context,
    path: Annotated[
        str,
        typer.Argument(help="Path to local repository to enroll"),
    ],
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", "-m", help="Path to manifest.toml file"),
    ] = None,
    remote: Annotated[
        str | None,
        typer.Option("--remote", "-r", help="Remote name from manifest to use"),
    ] = None,
    name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="Repository name (default: directory name)"),
    ] = None,
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Repository description"),
    ] = "",
    private: Annotated[
        bool,
        typer.Option("--private/--public", help="Repository visibility"),
    ] = True,
    enable_issues: Annotated[
        bool,
        typer.Option("--issues/--no-issues", help="Enable issues"),
    ] = False,
    enable_wiki: Annotated[
        bool,
        typer.Option("--wiki/--no-wiki", help="Enable wiki"),
    ] = False,
    token: Annotated[
        str | None,
        typer.Option("--token", "-t", help="GitHub token", envvar="GITHUB_TOKEN"),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show what would be done without making changes"),
    ] = False,
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", help="Open repository in browser after creation"),
    ] = True,
) -> None:
    """Create a GitHub repository for a local repo and push contents.

    This command:
    1. Creates a new repository on GitHub
    2. Configures merge settings (rebase, squash enabled)
    3. Adds the remote to your local repo (or updates existing)
    4. Pushes the current branch
    5. Opens the repository in your browser

    The owner is determined from the remote's base_url in your manifest.

    Path resolution:
    - Paths starting with './' are relative to current directory
    - Other paths are relative to root_path from manifest
    """
    # Check for token
    if not token:
        token = os.environ.get("GH_TOKEN")
    if not token:
        console.print("[red]Error:[/red] GitHub token required.")
        console.print("Set GITHUB_TOKEN or GH_TOKEN environment variable, or use --token")
        raise typer.Exit(2)

    # Load manifest first to get root_path for path resolution
    global_manifest = ctx.obj.get("manifest") if ctx.obj else None
    manifest_path = manifest or global_manifest or Path("manifest.toml")

    if not manifest_path.exists():
        console.print(f"[red]Error:[/red] Manifest not found: {manifest_path}")
        console.print("Use --manifest to specify manifest path")
        raise typer.Exit(2)

    try:
        mf = load_manifest(manifest_path)
    except ManifestError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(2) from e

    # Resolve root path from manifest
    root_path = Path(mf.common.root_path).expanduser().resolve()

    # Resolve the local repo path
    # Paths starting with './' are relative to current directory
    # Other paths are relative to root_path from manifest
    if path.startswith("./"):
        # Relative to current directory
        repo_path = (Path.cwd() / path[2:]).resolve()
    elif path.startswith("/") or path.startswith("~"):
        # Absolute path
        repo_path = Path(path).expanduser().resolve()
    else:
        # Relative to root_path
        repo_path = (root_path / path).resolve()

    if not repo_path.exists():
        console.print(f"[red]Error:[/red] Path does not exist: {repo_path}")
        raise typer.Exit(2)

    # Check it's a git repo
    mgr = RepoManager(repo_path)
    if not mgr.exists():
        console.print(f"[red]Error:[/red] Not a git repository: {repo_path}")
        raise typer.Exit(2)

    # Determine repo name
    repo_name = name or repo_path.name
    if not repo_name:
        console.print("[red]Error:[/red] Could not determine repository name")
        raise typer.Exit(2)

    # Resolve remote
    remote_name = remote or mf.common.remote
    remote_config = get_remote_by_name(mf, remote_name)
    if not remote_config:
        console.print(f"[red]Error:[/red] Remote '{remote_name}' not found in manifest")
        raise typer.Exit(2)

    # Extract owner from base_url
    owner = extract_owner_from_base_url(remote_config.base_url)
    if not owner:
        console.print(f"[red]Error:[/red] Cannot determine owner from base_url: {remote_config.base_url}")
        console.print("The base_url should include the owner, e.g.:")
        console.print("  ssh://git@github.com/vladistan/")
        console.print("  https://github.com/vladistan/")
        raise typer.Exit(2)

    # Resolve default branch from remote config or common
    default_branch = remote_config.branch or mf.common.branch

    # Get current branch of local repo
    current_branch = mgr.get_current_branch()
    if current_branch is None:
        console.print("[red]Error:[/red] Repository is in detached HEAD state")
        console.print("Please checkout a branch before enrolling")
        raise typer.Exit(2)

    # Construct clone URL for adding remote
    clone_url = construct_clone_url(remote_config.base_url, owner, repo_name)

    # Summary
    visibility = "private" if private else "public"
    console.print(f"\n[bold]Enrolling repository:[/bold] {repo_name}")
    console.print(f"  Owner: {owner}")
    console.print(f"  Visibility: {visibility}")
    console.print(f"  Description: {description or '(none)'}")
    console.print(f"  Issues: {'enabled' if enable_issues else 'disabled'}")
    console.print(f"  Wiki: {'enabled' if enable_wiki else 'disabled'}")
    console.print(f"  Default branch: {default_branch}")
    console.print(f"  Current branch: {current_branch}")
    console.print(f"  Clone URL: {clone_url}")
    console.print()

    if dry_run:
        console.print("[yellow]Dry run mode[/yellow] - no changes will be made")
        console.print("\nWould perform:")
        console.print(f"  1. Create GitHub repo: {owner}/{repo_name}")
        console.print("  2. Configure merge settings")
        console.print(f"  3. Add/update remote '{remote_name}' -> {clone_url}")
        console.print(f"  4. Push branch '{current_branch}'")
        if open_browser:
            console.print(f"  5. Open in browser: https://github.com/{owner}/{repo_name}")
        return

    # Initialize GitHub client
    gh = GitHubClient(token)

    # Check if repo already exists
    console.print(f"Checking if {owner}/{repo_name} exists...", end=" ")
    if gh.repo_exists(owner, repo_name):
        console.print("[red]EXISTS[/red]")
        console.print(f"\n[red]Error:[/red] Repository {owner}/{repo_name} already exists on GitHub")
        console.print("Use a different name with --name, or delete the existing repo first")
        raise typer.Exit(1)
    console.print("[green]available[/green]")

    # Create the repository
    try:
        console.print(f"Creating repository {owner}/{repo_name}...", end=" ")
        gh.create_repo(
            owner=owner,
            name=repo_name,
            description=description,
            private=private,
            has_issues=enable_issues,
            has_wiki=enable_wiki,
        )
        console.print("[green]done[/green]")
    except GitHubRepoExistsError as e:
        console.print("[red]failed[/red]")
        console.print(f"\n[red]Error:[/red] Repository {owner}/{repo_name} already exists")
        raise typer.Exit(1) from e
    except GitHubAuthError as e:
        console.print("[red]failed[/red]")
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(2) from e
    except GitHubAPIError as e:
        console.print("[red]failed[/red]")
        console.print(f"\n[red]Error:[/red] GitHub API error: {e}")
        raise typer.Exit(1) from e

    # Update repository settings
    try:
        console.print("Configuring merge settings...", end=" ")
        gh.update_repo_settings(
            owner=owner,
            repo=repo_name,
            default_branch=default_branch,
            allow_rebase_merge=True,
            allow_squash_merge=True,
            allow_merge_commit=True,
        )
        console.print("[green]done[/green]")
    except GitHubAPIError as e:
        console.print("[yellow]skipped[/yellow]")
        console.print(f"  Warning: Could not update settings: {e}")

    # Add or update remote in local repo
    try:
        if mgr.has_remote(remote_name):
            console.print(f"Updating remote '{remote_name}'...", end=" ")
            mgr.set_remote_url(remote_name, clone_url)
        else:
            console.print(f"Adding remote '{remote_name}'...", end=" ")
            mgr.add_remote(remote_name, clone_url)
        console.print("[green]done[/green]")
    except GitError as e:
        console.print("[red]failed[/red]")
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1) from e

    # Push current branch
    try:
        console.print(f"Pushing branch '{current_branch}'...", end=" ")
        mgr.push(remote_name=remote_name, branch=current_branch, set_upstream=True)
        console.print("[green]done[/green]")
    except PushError as e:
        console.print("[red]failed[/red]")
        console.print(f"\n[red]Error:[/red] {e}")
        console.print("\nThe repository was created but push failed.")
        console.print(f"You can push manually: git push -u {remote_name} {current_branch}")
        raise typer.Exit(1) from e

    # Success!
    web_url = gh.get_repo_web_url(owner, repo_name)
    console.print(f"\n[green]Success![/green] Repository created: {web_url}")

    # Open in browser
    if open_browser:
        console.print("Opening in browser...")
        webbrowser.open(web_url)
