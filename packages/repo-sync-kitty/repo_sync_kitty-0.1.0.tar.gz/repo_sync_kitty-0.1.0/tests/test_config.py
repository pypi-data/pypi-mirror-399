"""Tests for configuration models."""

from pathlib import Path

import pytest

from repo_sync_kitty.config.models import (
    CommonConfig,
    Manifest,
    ProjectConfig,
    RemoteConfig,
)


class TestRemoteConfig:
    """Tests for RemoteConfig model."""

    def test_init_with_required_fields_only(self) -> None:
        """Test RemoteConfig with only required fields."""
        remote = RemoteConfig(name="ghpub", base_url="https://github.com/")
        assert remote.name == "ghpub"
        assert remote.base_url == "https://github.com/"
        assert remote.branch is None
        assert remote.parallelism is None
        assert remote.timeout is None

    def test_init_with_all_optional_fields(self) -> None:
        """Test RemoteConfig with all optional fields."""
        remote = RemoteConfig(
            name="mine",
            base_url="ssh://git@github.com/",
            branch="develop",
            parallelism=2,
            timeout=600,
        )
        assert remote.branch == "develop"
        assert remote.parallelism == 2
        assert remote.timeout == 600


class TestProjectConfig:
    """Tests for ProjectConfig model."""

    def test_init_with_required_fields_only(self) -> None:
        """Test ProjectConfig with only required fields."""
        project = ProjectConfig(slug="owner/repo", path=Path("libs/repo"))
        assert project.slug == "owner/repo"
        assert project.path == Path("libs/repo")
        assert project.status == "active"
        assert project.remote is None
        assert project.branch is None

    @pytest.mark.parametrize("status", ["active", "archived", "deleted"])
    def test_init_with_valid_status(self, status: str) -> None:
        """Test ProjectConfig accepts valid status values."""
        project = ProjectConfig(
            slug="test/repo",
            path=Path("test"),
            status=status,  # type: ignore[arg-type]
        )
        assert project.status == status


class TestCommonConfig:
    """Tests for CommonConfig model."""

    def test_init_with_required_fields_only(self) -> None:
        """Test CommonConfig with only required fields uses defaults."""
        common = CommonConfig(
            root_path=Path("~/Projects"),
            remote="ghpub",
        )
        assert common.root_path == Path("~/Projects")
        assert common.remote == "ghpub"
        assert common.branch == "main"
        assert common.parallelism == 4
        assert common.log_level == "info"
        assert common.timeout == 300
        assert common.ignore_extra == []


class TestManifest:
    """Tests for Manifest model."""

    def test_init_with_all_sections(self) -> None:
        """Test Manifest with common, remotes, and projects."""
        manifest = Manifest(
            common=CommonConfig(root_path=Path("/tmp"), remote="ghpub"),
            remotes=[RemoteConfig(name="ghpub", base_url="https://github.com/")],
            projects=[ProjectConfig(slug="test/repo", path=Path("test"))],
        )
        assert len(manifest.remotes) == 1
        assert len(manifest.projects) == 1
        assert manifest.common.remote == "ghpub"
