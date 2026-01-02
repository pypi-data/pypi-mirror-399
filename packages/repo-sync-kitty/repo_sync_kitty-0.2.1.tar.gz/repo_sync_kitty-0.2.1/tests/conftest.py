"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def tmp_manifest(tmp_path: Path) -> Path:
    """Create a temporary manifest file."""
    manifest = tmp_path / "manifest.toml"
    manifest.write_text('''
[common]
root_path = "/tmp/test-repos"
branch = "main"
remote = "ghpub"
parallelism = 2

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[projects]]
slug = "octocat/Hello-World"
path = "hello-world"
''')
    return manifest


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a temporary directory for test repositories."""
    repo_dir = tmp_path / "repos"
    repo_dir.mkdir()
    return repo_dir


@pytest.fixture
def full_manifest(tmp_path: Path) -> Path:
    """Create a manifest with multiple remotes, inheritance, and varied statuses."""
    manifest = tmp_path / "manifest.toml"
    manifest.write_text('''
[common]
root_path = "~/Projects"
branch = "main"
remote = "ghpub"
parallelism = 4
timeout = 300

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[remotes]]
name = "mine"
base_url = "ssh://git@github.com/vladistan/"
branch = "develop"
parallelism = 2
timeout = 600

[[remotes]]
name = "gitlab"
base_url = "https://gitlab.com/"
branch = "master"

[[projects]]
slug = "linkml/linkml"
path = "libs/linkml"
remote = "ghpub"

[[projects]]
slug = "infra"
path = "infra/global"
remote = "mine"

[[projects]]
slug = "infra"
path = "infra/global-dev"
remote = "mine"
branch = "feature"

[[projects]]
slug = "old-tool"
path = "archive/old"
remote = "mine"
status = "archived"

[[projects]]
slug = "deprecated"
path = "libs/deprecated"
remote = "ghpub"
status = "deleted"
''')
    return manifest


@pytest.fixture
def invalid_remote_manifest(tmp_path: Path) -> Path:
    """Create a manifest with an invalid remote reference."""
    manifest = tmp_path / "manifest.toml"
    manifest.write_text('''
[common]
root_path = "/tmp"
branch = "main"
remote = "nonexistent"

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[projects]]
slug = "test/repo"
path = "test"
''')
    return manifest


@pytest.fixture
def duplicate_paths_manifest(tmp_path: Path) -> Path:
    """Create a manifest with duplicate project paths."""
    manifest = tmp_path / "manifest.toml"
    manifest.write_text('''
[common]
root_path = "/tmp"
branch = "main"
remote = "ghpub"

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[projects]]
slug = "owner/repo1"
path = "same/path"

[[projects]]
slug = "owner/repo2"
path = "same/path"
''')
    return manifest


@pytest.fixture
def invalid_toml_manifest(tmp_path: Path) -> Path:
    """Create a manifest with invalid TOML syntax."""
    manifest = tmp_path / "manifest.toml"
    manifest.write_text('''
[common
root_path = "/tmp"
''')
    return manifest


@pytest.fixture
def dict_format_manifest(tmp_path: Path) -> Path:
    """Create a manifest using dict format for add command tests."""
    manifest = tmp_path / "manifest.toml"
    manifest.write_text('''[common]
root_path = "/tmp/test-repos"
branch = "main"
remote = "origin"
parallelism = 2

[remotes]
origin = { base_url = "https://github.com/" }

[projects]
"hello-world" = { slug = "octocat/Hello-World" }
''')
    return manifest
