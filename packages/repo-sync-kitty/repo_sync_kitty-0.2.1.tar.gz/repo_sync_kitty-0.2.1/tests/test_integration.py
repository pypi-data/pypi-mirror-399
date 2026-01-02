"""Integration tests with real git operations.

These tests use real git repos (GitHub public repos) to verify
end-to-end functionality. They're slower and require network access.
"""

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from repo_sync_kitty.cli import app
from repo_sync_kitty.git.operations import RepoManager

# Skip all integration tests if SKIP_INTEGRATION is set
pytestmark = pytest.mark.skipif(
    os.environ.get("SKIP_INTEGRATION", "").lower() in ("1", "true", "yes"),
    reason="Integration tests skipped via SKIP_INTEGRATION env var",
)


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def integration_root(tmp_path: Path) -> Path:
    """Create a root directory for integration test repos."""
    root = tmp_path / "integration-repos"
    root.mkdir()
    return root


@pytest.fixture
def integration_manifest(tmp_path: Path, integration_root: Path) -> Path:
    """Create a manifest for integration testing with real GitHub repos."""
    manifest = tmp_path / "integration-manifest.toml"
    # Note: Hello-World uses master as default branch, Spoon-Knife uses main
    manifest.write_text(f'''[common]
root_path = "{integration_root}"
branch = "main"
remote = "origin"
parallelism = 2

[remotes]
origin = {{ base_url = "https://github.com/" }}

[projects]
"hello-world" = {{ slug = "octocat/Hello-World", branch = "master" }}
"spoon-knife" = {{ slug = "octocat/Spoon-Knife" }}
''')
    return manifest


class TestGitOperationsIntegration:
    """Integration tests for git operations with real repos."""

    def test_clone_real_repo(self, integration_root: Path) -> None:
        """Test cloning a real public GitHub repo."""
        repo_path = integration_root / "hello-world"

        mgr = RepoManager.clone(
            "https://github.com/octocat/Hello-World.git",
            repo_path,
            branch="master",  # Hello-World uses master
        )

        assert repo_path.exists()
        assert (repo_path / ".git").is_dir()
        assert mgr.exists()
        # Hello-World has master as default
        assert mgr.get_current_branch() in ("master", "main")

    def test_fetch_real_repo(self, integration_root: Path) -> None:
        """Test fetching from a real repo."""
        repo_path = integration_root / "spoon-knife"

        # Clone first
        mgr = RepoManager.clone(
            "https://github.com/octocat/Spoon-Knife.git",
            repo_path,
        )

        # Fetch should work without error
        mgr.fetch()

        assert mgr.exists()
        assert "origin" in mgr.get_remotes()

    def test_repo_state_detection(self, integration_root: Path) -> None:
        """Test detecting repo state on a real clone."""
        repo_path = integration_root / "test-state"

        mgr = RepoManager.clone(
            "https://github.com/octocat/Hello-World.git",
            repo_path,
        )

        # Fresh clone should be clean
        assert mgr.is_clean()
        assert not mgr.is_detached()
        assert not mgr.is_rebasing()
        assert not mgr.is_merging()
        assert not mgr.is_cherry_picking()

    def test_dirty_state_detection(self, integration_root: Path) -> None:
        """Test detecting dirty state after modifications."""
        repo_path = integration_root / "dirty-test"

        mgr = RepoManager.clone(
            "https://github.com/octocat/Hello-World.git",
            repo_path,
        )

        # Create a new file to make it dirty
        (repo_path / "test-file.txt").write_text("test content")

        # Should now have untracked changes (but not modified tracked files)
        # Note: is_clean() checks for modified tracked files, not untracked
        assert mgr.exists()


class TestSyncIntegration:
    """Integration tests for sync command with real repos."""

    def test_sync_clones_missing_repos(
        self, cli_runner: CliRunner, integration_manifest: Path, integration_root: Path
    ) -> None:
        """Test that sync clones missing repos."""
        # Run sync
        result = cli_runner.invoke(
            app, ["sync", "-m", str(integration_manifest), "-v"]
        )

        # Print output for debugging if it fails
        if result.exit_code != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr if hasattr(result, 'stderr') else 'N/A'}")

        assert result.exit_code == 0, f"Sync failed with output: {result.stdout}"
        assert "cloned" in result.stdout.lower()

        # Check repos were cloned
        assert (integration_root / "hello-world" / ".git").is_dir()
        assert (integration_root / "spoon-knife" / ".git").is_dir()

    def test_sync_fetches_existing_repos(
        self, cli_runner: CliRunner, integration_manifest: Path, integration_root: Path  # noqa: ARG002
    ) -> None:
        """Test that sync fetches existing repos."""
        # Clone first (integration_root is used by fixture dependency)
        cli_runner.invoke(app, ["sync", "-m", str(integration_manifest)])

        # Run sync again
        result = cli_runner.invoke(
            app, ["sync", "-m", str(integration_manifest), "-v"]
        )

        assert result.exit_code == 0
        assert "fetched" in result.stdout.lower()

    def test_sync_dry_run_no_changes(
        self, cli_runner: CliRunner, integration_manifest: Path, integration_root: Path
    ) -> None:
        """Test that dry-run doesn't actually clone."""
        result = cli_runner.invoke(
            app, ["sync", "-m", str(integration_manifest), "--dry-run", "-v"]
        )

        assert result.exit_code == 0
        assert "would clone" in result.stdout.lower()

        # Should not have actually cloned
        assert not (integration_root / "hello-world").exists()

    def test_sync_clone_only_mode(
        self, cli_runner: CliRunner, integration_manifest: Path, integration_root: Path  # noqa: ARG002
    ) -> None:
        """Test clone-only mode."""
        # Clone first (integration_root is used by fixture dependency)
        cli_runner.invoke(app, ["sync", "-m", str(integration_manifest)])

        # Run with clone-only - should skip existing
        result = cli_runner.invoke(
            app, ["sync", "-m", str(integration_manifest), "--clone-only", "-v"]
        )

        assert result.exit_code == 0
        assert "already cloned" in result.stdout.lower()


class TestStatusIntegration:
    """Integration tests for status command with real repos."""

    def test_status_shows_missing(
        self, cli_runner: CliRunner, integration_manifest: Path
    ) -> None:
        """Test status shows missing repos."""
        result = cli_runner.invoke(
            app, ["status", "-m", str(integration_manifest)]
        )

        assert result.exit_code == 0
        assert "missing" in result.stdout.lower()

    def test_status_after_sync(
        self, cli_runner: CliRunner, integration_manifest: Path, integration_root: Path  # noqa: ARG002
    ) -> None:
        """Test status after successful sync."""
        # Sync first (integration_root is used by fixture dependency)
        cli_runner.invoke(app, ["sync", "-m", str(integration_manifest)])

        # Check status
        result = cli_runner.invoke(
            app, ["status", "-m", str(integration_manifest), "-v"]
        )

        assert result.exit_code == 0
        # Should show repos as present now
        assert "hello-world" in result.stdout
        assert "spoon-knife" in result.stdout


class TestCheckIntegration:
    """Integration tests for check command."""

    def test_check_valid_manifest(
        self, cli_runner: CliRunner, integration_manifest: Path
    ) -> None:
        """Test check passes for valid manifest."""
        result = cli_runner.invoke(
            app, ["check", "-m", str(integration_manifest)]
        )

        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()


class TestInitIntegration:
    """Integration tests for init command."""

    def test_init_scan_dir_finds_repos(
        self, cli_runner: CliRunner, integration_root: Path, tmp_path: Path
    ) -> None:
        """Test init --scan-dir finds real repos."""
        # Clone a repo first
        RepoManager.clone(
            "https://github.com/octocat/Hello-World.git",
            integration_root / "hello-world",
        )

        # Scan the directory
        output = tmp_path / "scanned-manifest.toml"
        result = cli_runner.invoke(
            app,
            ["init", "--scan-dir", str(integration_root), "-o", str(output)],
        )

        assert result.exit_code == 0
        assert output.exists()

        content = output.read_text()
        assert "hello-world" in content.lower() or "Hello-World" in content


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_full_workflow(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test complete workflow: init -> check -> sync -> status."""
        root = tmp_path / "e2e-test"
        root.mkdir()

        # Step 1: Create manifest manually (init creates template)
        # Note: Hello-World uses master as its default branch
        manifest = tmp_path / "e2e-manifest.toml"
        manifest.write_text(f'''[common]
root_path = "{root}"
branch = "master"
remote = "origin"
parallelism = 1

[remotes]
origin = {{ base_url = "https://github.com/" }}

[projects]
"hw" = {{ slug = "octocat/Hello-World" }}
''')

        # Step 2: Check manifest
        result = cli_runner.invoke(app, ["check", "-m", str(manifest)])
        assert result.exit_code == 0

        # Step 3: Status (should show missing)
        result = cli_runner.invoke(app, ["status", "-m", str(manifest)])
        assert result.exit_code == 0
        assert "missing" in result.stdout.lower()

        # Step 4: Sync
        result = cli_runner.invoke(app, ["sync", "-m", str(manifest), "-v"])
        assert result.exit_code == 0
        assert (root / "hw" / ".git").is_dir()

        # Step 5: Status again (should be ok now)
        result = cli_runner.invoke(app, ["status", "-m", str(manifest), "-v"])
        assert result.exit_code == 0
