"""Main CLI application using Typer."""

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from repo_sync_kitty import __version__
from repo_sync_kitty.commands import (
    add,
    check,
    enroll,
    find_orphans,
    fix_detached,
    import_manifest,
    init,
    move,
    scan,
    status,
    sync,
)
from repo_sync_kitty.commands import (
    open as open_cmd,
)

# Initialize Sentry if DSN is provided
if dsn := os.getenv("SENTRY_DSN"):
    try:
        import sentry_sdk

        sentry_sdk.init(dsn=dsn, release=f"repo-sync-kitty@{__version__}")
    except ImportError:
        pass  # sentry-sdk not installed, skip

console = Console()

app = typer.Typer(
    name="repo-sync-kitty",
    help="Git repository synchronization tool for teams.",
    add_completion=False,
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"repo-sync-kitty {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[  # noqa: ARG001
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
    manifest: Annotated[
        Path | None,
        typer.Option(
            "--manifest",
            "-m",
            help="Path to manifest.toml file.",
            envvar="REPO_SYNC_KITTY_MANIFEST",
        ),
    ] = None,
    root: Annotated[
        Path | None,
        typer.Option(
            "--root",
            "-r",
            help="Root directory for repositories.",
            envvar="REPO_SYNC_KITTY_ROOT",
        ),
    ] = None,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output."),
    ] = False,
) -> None:
    """Git repository synchronization tool for teams."""
    # Store global options in context for subcommands to access
    ctx.ensure_object(dict)
    ctx.obj["manifest"] = manifest
    ctx.obj["root"] = root
    ctx.obj["verbose"] = verbose
    if no_color:
        console.no_color = True


# Register commands
app.command(name="sync")(sync.sync)
app.command(name="status")(status.status)
app.command(name="init")(init.init)
app.command(name="add")(add.add)
app.command(name="check")(check.check)
app.command(name="scan")(scan.scan)
app.command(name="import-repo")(import_manifest.import_manifest)
app.command(name="fix-detached")(fix_detached.fix_detached)
app.command(name="find-orphans")(find_orphans.find_orphans)
app.command(name="move")(move.move)
app.command(name="open")(open_cmd.open_repo)
app.command(name="enroll")(enroll.enroll)


if __name__ == "__main__":
    app()
