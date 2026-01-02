"""Tests for individual command execution."""

from pathlib import Path

from typer.testing import CliRunner

from repo_sync_kitty.cli import app


class TestSyncCommand:
    """Tests for sync command."""

    def test_sync_no_manifest_shows_error(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test sync command without manifest shows error."""
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = cli_runner.invoke(app, ["sync"])
            assert result.exit_code == 2
            assert "not found" in result.stdout.lower()
        finally:
            os.chdir(original_dir)

    def test_sync_with_manifest_dry_run(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test sync command with manifest in dry-run mode."""
        result = cli_runner.invoke(app, ["sync", "-m", str(tmp_manifest), "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout

    def test_sync_clone_only_flag(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test sync --clone-only flag is recognized."""
        result = cli_runner.invoke(
            app, ["sync", "-m", str(tmp_manifest), "--clone-only", "--dry-run"]
        )
        assert result.exit_code == 0

    def test_sync_fetch_only_flag(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test sync --fetch-only flag is recognized."""
        result = cli_runner.invoke(
            app, ["sync", "-m", str(tmp_manifest), "--fetch-only", "--dry-run"]
        )
        assert result.exit_code == 0

    def test_sync_pull_flag(self, cli_runner: CliRunner, tmp_manifest: Path) -> None:
        """Test sync --pull flag is recognized."""
        result = cli_runner.invoke(
            app, ["sync", "-m", str(tmp_manifest), "--pull", "--dry-run"]
        )
        assert result.exit_code == 0

    def test_sync_verbose_flag(self, cli_runner: CliRunner, tmp_manifest: Path) -> None:
        """Test sync --verbose flag shows detailed output."""
        result = cli_runner.invoke(
            app, ["sync", "-m", str(tmp_manifest), "--verbose", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "Syncing" in result.stdout
        assert "repositories" in result.stdout

    def test_sync_parallelism_flag(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test sync --parallelism flag overrides config."""
        result = cli_runner.invoke(
            app, ["sync", "-m", str(tmp_manifest), "-j", "2", "--verbose", "--dry-run"]
        )
        assert result.exit_code == 0
        assert "parallelism: 2" in result.stdout


class TestStatusCommand:
    """Tests for status command."""

    def test_status_no_manifest_shows_error(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test status command without manifest shows error."""
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = cli_runner.invoke(app, ["status"])
            assert result.exit_code == 2
            assert "not found" in result.stdout.lower()
        finally:
            os.chdir(original_dir)

    def test_status_with_manifest(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test status command with manifest shows table."""
        result = cli_runner.invoke(app, ["status", "-m", str(tmp_manifest)])
        # Exit code 0 even if repos are missing (just reporting status)
        assert result.exit_code == 0
        assert "Repository Status" in result.stdout

    def test_status_verbose_flag(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test status --verbose flag shows all repos."""
        result = cli_runner.invoke(
            app, ["status", "-m", str(tmp_manifest), "--verbose"]
        )
        assert result.exit_code == 0

    def test_status_show_deleted_flag(
        self, cli_runner: CliRunner, full_manifest: Path
    ) -> None:
        """Test status --show-deleted flag includes deleted repos."""
        result = cli_runner.invoke(
            app, ["status", "-m", str(full_manifest), "--show-deleted"]
        )
        assert result.exit_code == 0


class TestInitCommand:
    """Tests for init command."""

    def test_init_creates_manifest(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test init command creates manifest file."""
        output = tmp_path / "manifest.toml"
        result = cli_runner.invoke(app, ["init", "-o", str(output)])
        assert result.exit_code == 0
        assert output.exists()
        assert "Created" in result.stdout

    def test_init_refuses_overwrite(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test init refuses to overwrite existing manifest without --force."""
        output = tmp_path / "manifest.toml"
        output.write_text("[common]")
        result = cli_runner.invoke(app, ["init", "-o", str(output)])
        assert result.exit_code == 1
        assert "already exists" in result.stdout

    def test_init_force_overwrites(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test init --force overwrites existing manifest."""
        output = tmp_path / "manifest.toml"
        output.write_text("[common]")
        result = cli_runner.invoke(app, ["init", "-o", str(output), "--force"])
        assert result.exit_code == 0
        assert "Created" in result.stdout

    def test_init_with_scan_dir(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test init --scan-dir scans directory for repos."""
        output = tmp_path / "manifest.toml"
        result = cli_runner.invoke(
            app, ["init", "-o", str(output), "--scan-dir", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Scanning" in result.stdout

    def test_init_with_scan_forge_not_implemented(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test init --scan-forge shows not implemented message."""
        output = tmp_path / "manifest.toml"
        result = cli_runner.invoke(
            app, ["init", "-o", str(output), "--scan-forge", "github", "--org", "octocat"]
        )
        assert result.exit_code == 1
        assert "not yet implemented" in result.stdout.lower()


class TestCheckCommand:
    """Tests for check command."""

    def test_check_valid_manifest(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test check command with valid manifest shows success."""
        result = cli_runner.invoke(app, ["check", "-m", str(tmp_manifest)])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()

    def test_check_shows_common_config(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test check command displays common configuration."""
        result = cli_runner.invoke(app, ["check", "-m", str(tmp_manifest)])
        assert result.exit_code == 0
        assert "Root path" in result.stdout
        assert "Default remote" in result.stdout

    def test_check_shows_projects_table(
        self, cli_runner: CliRunner, tmp_manifest: Path
    ) -> None:
        """Test check command displays projects table."""
        result = cli_runner.invoke(app, ["check", "-m", str(tmp_manifest)])
        assert result.exit_code == 0
        assert "hello-world" in result.stdout
        assert "octocat/Hello-World" in result.stdout

    def test_check_file_not_found(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test check command with nonexistent manifest shows error."""
        result = cli_runner.invoke(
            app, ["check", "-m", str(tmp_path / "nonexistent.toml")]
        )
        assert result.exit_code == 2
        assert "not found" in result.stdout.lower()

    def test_check_invalid_toml(
        self, cli_runner: CliRunner, invalid_toml_manifest: Path
    ) -> None:
        """Test check command with invalid TOML shows error."""
        result = cli_runner.invoke(app, ["check", "-m", str(invalid_toml_manifest)])
        assert result.exit_code == 2
        assert "Invalid TOML" in result.stdout or "Error" in result.stdout

    def test_check_invalid_remote_reference(
        self, cli_runner: CliRunner, invalid_remote_manifest: Path
    ) -> None:
        """Test check command catches invalid remote references."""
        result = cli_runner.invoke(app, ["check", "-m", str(invalid_remote_manifest)])
        assert result.exit_code == 2
        assert "nonexistent" in result.stdout

    def test_check_full_manifest_shows_summary(
        self, cli_runner: CliRunner, full_manifest: Path
    ) -> None:
        """Test check command shows status summary for full manifest."""
        result = cli_runner.invoke(app, ["check", "-m", str(full_manifest)])
        assert result.exit_code == 0
        assert "active" in result.stdout.lower()
        assert "archived" in result.stdout.lower()
        assert "deleted" in result.stdout.lower()


class TestAddCommand:
    """Tests for add command."""

    def test_add_no_manifest_shows_error(self, cli_runner: CliRunner) -> None:
        """Test add command without manifest shows error."""
        result = cli_runner.invoke(app, ["add", "origin", "owner/repo"])
        assert result.exit_code == 2
        assert "not found" in result.stdout.lower()

    def test_add_invalid_remote_shows_error(
        self, cli_runner: CliRunner, dict_format_manifest: Path
    ) -> None:
        """Test add command with invalid remote shows error."""
        result = cli_runner.invoke(
            app, ["add", "nonexistent", "owner/repo", "-m", str(dict_format_manifest)]
        )
        assert result.exit_code == 2
        assert "not found" in result.stdout.lower()

    def test_add_creates_project_entry(
        self, cli_runner: CliRunner, dict_format_manifest: Path
    ) -> None:
        """Test add command creates project entry in manifest."""
        result = cli_runner.invoke(
            app, ["add", "origin", "octocat/Spoon-Knife", "-m", str(dict_format_manifest)]
        )
        assert result.exit_code == 0
        assert "Added" in result.stdout
        # Check manifest was updated
        content = dict_format_manifest.read_text()
        assert "Spoon-Knife" in content

    def test_add_with_path_and_branch(
        self, cli_runner: CliRunner, dict_format_manifest: Path
    ) -> None:
        """Test add command with --path and --branch options."""
        result = cli_runner.invoke(
            app,
            [
                "add", "origin", "octocat/test",
                "-m", str(dict_format_manifest),
                "--path", "my/path",
                "--branch", "develop",
            ],
        )
        assert result.exit_code == 0
        content = dict_format_manifest.read_text()
        assert "my/path" in content
        assert "develop" in content

    def test_add_duplicate_path_shows_error(
        self, cli_runner: CliRunner, dict_format_manifest: Path
    ) -> None:
        """Test add command rejects duplicate path."""
        result = cli_runner.invoke(
            app,
            ["add", "origin", "octocat/other", "-m", str(dict_format_manifest), "-p", "hello-world"],
        )
        assert result.exit_code == 1
        assert "already exists" in result.stdout.lower()


class TestScanCommand:
    """Tests for scan command."""

    def test_scan_requires_org(self, cli_runner: CliRunner) -> None:
        """Test scan command requires --org option."""
        result = cli_runner.invoke(app, ["scan", "github"])
        assert result.exit_code == 2
        assert "--org" in result.stdout.lower() or "required" in result.stdout.lower()

    def test_scan_unknown_forge_shows_error(self, cli_runner: CliRunner) -> None:
        """Test scan command with unknown forge shows error."""
        result = cli_runner.invoke(app, ["scan", "unknown", "--org", "test"])
        assert result.exit_code == 2
        assert "unknown forge" in result.stdout.lower()

    def test_scan_bitbucket_not_implemented(self, cli_runner: CliRunner) -> None:
        """Test scan bitbucket shows not implemented message."""
        result = cli_runner.invoke(app, ["scan", "bitbucket", "--org", "test"])
        assert result.exit_code == 1
        assert "not yet implemented" in result.stdout.lower()

    def test_scan_add_requires_manifest(self, cli_runner: CliRunner) -> None:
        """Test scan --add requires a valid manifest."""
        result = cli_runner.invoke(
            app, ["scan", "github", "--org", "test", "--add", "-r", "origin"]
        )
        assert result.exit_code == 2
        assert "manifest" in result.stdout.lower()

    def test_scan_add_requires_remote(
        self, cli_runner: CliRunner, dict_format_manifest: Path
    ) -> None:
        """Test scan --add requires --remote option."""
        result = cli_runner.invoke(
            app,
            ["scan", "github", "--org", "test", "--add", "-m", str(dict_format_manifest)],
        )
        assert result.exit_code == 2
        assert "remote" in result.stdout.lower()

    def test_scan_add_rejects_invalid_remote(
        self, cli_runner: CliRunner, dict_format_manifest: Path
    ) -> None:
        """Test scan --add rejects invalid remote name."""
        result = cli_runner.invoke(
            app,
            [
                "scan", "github", "--org", "test", "--add",
                "-m", str(dict_format_manifest), "-r", "nonexistent"
            ],
        )
        assert result.exit_code == 2
        assert "not found" in result.stdout.lower()
