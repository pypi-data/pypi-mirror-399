"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner

from repo_sync_kitty import __version__
from repo_sync_kitty.cli import app


def test_cli_version_flag_shows_version(cli_runner: CliRunner) -> None:
    """Test --version flag displays version string."""
    result = cli_runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_help_flag_shows_usage(cli_runner: CliRunner) -> None:
    """Test --help flag displays usage information."""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "repo-sync-kitty" in result.stdout


@pytest.mark.parametrize(
    "command,expected_options",
    [
        ("sync", ["fetch-only", "clone-only", "dry-run"]),
        ("status", ["verbose", "show-deleted"]),
        ("init", ["scan-dir", "scan-forge"]),
        ("add", ["REMOTE", "SLUG"]),
        ("check", ["manifest"]),
        ("scan", ["FORGE", "org", "token"]),
    ],
)
def test_cli_command_help_shows_options(
    cli_runner: CliRunner, command: str, expected_options: list[str]
) -> None:
    """Test command --help shows expected options."""
    result = cli_runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0
    for option in expected_options:
        assert option in result.stdout
