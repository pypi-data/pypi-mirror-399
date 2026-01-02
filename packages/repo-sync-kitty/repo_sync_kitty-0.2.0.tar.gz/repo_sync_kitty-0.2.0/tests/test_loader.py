"""Tests for manifest loading and resolution."""

from pathlib import Path

import pytest

from repo_sync_kitty.config import (
    ManifestNotFoundError,
    ManifestParseError,
    ManifestValidationError,
    ResolvedProject,
    load_manifest,
    resolve_all_projects,
    resolve_project,
    validate_manifest,
)
from repo_sync_kitty.config.loader import _parse_projects, _parse_remotes, get_remote_by_name

# Path to the example fixture
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseRemotes:
    """Tests for _parse_remotes function."""

    def test_parse_remotes_none(self) -> None:
        """Test parsing None returns empty list."""
        assert _parse_remotes(None) == []

    def test_parse_remotes_list_format(self) -> None:
        """Test parsing array-of-tables format."""
        raw = [
            {"name": "ghpub", "base_url": "https://github.com/"},
            {"name": "mine", "base_url": "ssh://git@github.com/vladistan/"},
        ]
        remotes = _parse_remotes(raw)
        assert len(remotes) == 2
        assert remotes[0].name == "ghpub"
        assert remotes[1].name == "mine"

    def test_parse_remotes_dict_format(self) -> None:
        """Test parsing dict format with name as key."""
        raw = {
            "ghpub": {"base_url": "https://github.com/"},
            "mine": {"base_url": "ssh://git@github.com/vladistan/", "branch": "develop"},
        }
        remotes = _parse_remotes(raw)
        assert len(remotes) == 2
        names = {r.name for r in remotes}
        assert names == {"ghpub", "mine"}
        mine = next(r for r in remotes if r.name == "mine")
        assert mine.branch == "develop"


class TestParseProjects:
    """Tests for _parse_projects function."""

    def test_parse_projects_none(self) -> None:
        """Test parsing None returns empty list."""
        assert _parse_projects(None) == []

    def test_parse_projects_list_format(self) -> None:
        """Test parsing array-of-tables format."""
        raw = [
            {"slug": "owner/repo", "path": "libs/repo"},
            {"slug": "infra", "path": "infra/global"},
        ]
        projects = _parse_projects(raw)
        assert len(projects) == 2
        assert projects[0].slug == "owner/repo"
        assert projects[0].path == Path("libs/repo")

    def test_parse_projects_dict_format(self) -> None:
        """Test parsing dict format with path as key."""
        raw = {
            "libs/repo": {"slug": "owner/repo"},
            "infra/global": {"slug": "infra", "remote": "mine"},
        }
        projects = _parse_projects(raw)
        assert len(projects) == 2
        paths = {str(p.path) for p in projects}
        assert paths == {"libs/repo", "infra/global"}
        infra = next(p for p in projects if str(p.path) == "infra/global")
        assert infra.remote == "mine"

    def test_parse_projects_derives_slug_from_path_dict_format(self) -> None:
        """Test slug is derived from path when not provided (dict format)."""
        raw = {
            "util/autorevision": {"branch": "master"},
            "libs/mylib": {},
        }
        projects = _parse_projects(raw)
        assert len(projects) == 2
        autorev = next(p for p in projects if str(p.path) == "util/autorevision")
        assert autorev.slug == "autorevision"
        mylib = next(p for p in projects if str(p.path) == "libs/mylib")
        assert mylib.slug == "mylib"

    def test_parse_projects_derives_slug_from_path_list_format(self) -> None:
        """Test slug is derived from path when not provided (list format)."""
        raw = [
            {"path": "tools/mytool", "branch": "develop"},
            {"path": "simple"},
        ]
        projects = _parse_projects(raw)
        assert len(projects) == 2
        assert projects[0].slug == "mytool"
        assert projects[1].slug == "simple"

    def test_parse_projects_explicit_slug_overrides_derived(self) -> None:
        """Test explicit slug is used even when path could derive one."""
        raw = {
            "util/autorevision": {"slug": "custom-slug", "branch": "master"},
        }
        projects = _parse_projects(raw)
        assert projects[0].slug == "custom-slug"


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_load_manifest_file_not_found(self, tmp_path: Path) -> None:
        """Test loading a nonexistent manifest raises ManifestNotFoundError."""
        with pytest.raises(ManifestNotFoundError) as exc_info:
            load_manifest(tmp_path / "nonexistent.toml")
        assert "not found" in str(exc_info.value)

    def test_load_manifest_invalid_toml(self, invalid_toml_manifest: Path) -> None:
        """Test loading invalid TOML raises ManifestParseError."""
        with pytest.raises(ManifestParseError) as exc_info:
            load_manifest(invalid_toml_manifest)
        assert "Invalid TOML" in str(exc_info.value)

    def test_load_manifest_valid(self, tmp_manifest: Path) -> None:
        """Test loading a valid manifest succeeds."""
        manifest = load_manifest(tmp_manifest)
        assert manifest.common.remote == "ghpub"
        assert len(manifest.remotes) == 1
        assert len(manifest.projects) == 1

    def test_load_manifest_full(self, full_manifest: Path) -> None:
        """Test loading a full manifest with multiple remotes and projects."""
        manifest = load_manifest(full_manifest)
        assert manifest.common.root_path == Path("~/Projects")
        assert manifest.common.branch == "main"
        assert manifest.common.parallelism == 4
        assert len(manifest.remotes) == 3
        assert len(manifest.projects) == 5

    def test_load_manifest_missing_required_field(self, tmp_path: Path) -> None:
        """Test loading manifest missing required fields raises ManifestValidationError."""
        manifest = tmp_path / "bad.toml"
        manifest.write_text("""
[common]
root_path = "/tmp"
# missing required 'remote' field
""")
        with pytest.raises(ManifestValidationError):
            load_manifest(manifest)

    def test_load_manifest_dict_format_fixture(self) -> None:
        """Test loading the example manifest with dict format."""
        manifest = load_manifest(FIXTURES_DIR / "example-manifest.toml")

        # Check common
        assert manifest.common.remote == "mine"
        assert manifest.common.parallelism == 4

        # Check remotes (3 total: ghpub, gitlab, mine)
        assert len(manifest.remotes) == 3
        remote_names = {r.name for r in manifest.remotes}
        assert remote_names == {"ghpub", "gitlab", "mine"}

        # Check mine remote has expanded values
        mine = next(r for r in manifest.remotes if r.name == "mine")
        assert mine.branch == "develop"
        assert mine.parallelism == 2
        assert mine.timeout == 600

        # Check projects (5 total)
        assert len(manifest.projects) == 5
        project_paths = {str(p.path) for p in manifest.projects}
        assert "libs/linkml" in project_paths
        assert "infra/global-dev" in project_paths

        # Check expanded project has correct values
        linkml = next(p for p in manifest.projects if str(p.path) == "libs/linkml")
        assert linkml.slug == "linkml/linkml"
        assert linkml.remote == "ghpub"
        assert linkml.branch == "main"

    def test_load_manifest_dict_format_resolves_correctly(self) -> None:
        """Test dict format manifest resolves inheritance correctly."""
        manifest = load_manifest(FIXTURES_DIR / "example-manifest.toml")
        resolved = resolve_all_projects(manifest)

        # infra/global should inherit from mine remote
        infra = next(r for r in resolved if str(r.path) == "infra/global")
        assert infra.remote_name == "mine"
        assert infra.branch == "develop"  # From mine remote
        assert infra.parallelism == 2  # From mine remote
        assert infra.timeout == 600  # From mine remote

        # infra/global-dev has explicit branch override
        infra_dev = next(r for r in resolved if str(r.path) == "infra/global-dev")
        assert infra_dev.branch == "feature"  # Explicit override

        # libs/linkml uses ghpub remote
        linkml = next(r for r in resolved if str(r.path) == "libs/linkml")
        assert linkml.remote_name == "ghpub"
        assert linkml.branch == "main"  # Explicit in project


class TestGetRemoteByName:
    """Tests for get_remote_by_name function."""

    def test_get_remote_by_name_found(self, full_manifest: Path) -> None:
        """Test finding an existing remote by name."""
        manifest = load_manifest(full_manifest)
        remote = get_remote_by_name(manifest, "mine")
        assert remote is not None
        assert remote.name == "mine"
        assert remote.base_url == "ssh://git@github.com/vladistan/"

    def test_get_remote_by_name_not_found(self, full_manifest: Path) -> None:
        """Test looking up nonexistent remote returns None."""
        manifest = load_manifest(full_manifest)
        remote = get_remote_by_name(manifest, "nonexistent")
        assert remote is None


class TestResolveProject:
    """Tests for resolve_project function."""

    def test_resolve_project_uses_project_values(self, full_manifest: Path) -> None:
        """Test project-level values take precedence."""
        manifest = load_manifest(full_manifest)
        # Project with explicit branch="feature"
        project = manifest.projects[2]  # infra/global-dev
        resolved = resolve_project(manifest, project)
        assert resolved.branch == "feature"
        assert resolved.remote_name == "mine"

    def test_resolve_project_inherits_from_remote(self, full_manifest: Path) -> None:
        """Test project inherits branch from remote when not specified."""
        manifest = load_manifest(full_manifest)
        # Project using remote "mine" which has branch="develop"
        project = manifest.projects[1]  # infra/global
        resolved = resolve_project(manifest, project)
        assert resolved.branch == "develop"  # From remote
        assert resolved.parallelism == 2  # From remote
        assert resolved.timeout == 600  # From remote

    def test_resolve_project_inherits_from_common(self, full_manifest: Path) -> None:
        """Test project inherits from common when remote has no override."""
        manifest = load_manifest(full_manifest)
        # Project using remote "ghpub" which has no branch override
        project = manifest.projects[0]  # libs/linkml
        resolved = resolve_project(manifest, project)
        assert resolved.branch == "main"  # From common
        assert resolved.parallelism == 4  # From common (ghpub has no override)
        assert resolved.timeout == 300  # From common

    def test_resolve_project_unknown_remote(self, tmp_path: Path) -> None:
        """Test resolving project with unknown remote raises error."""
        manifest_path = tmp_path / "bad.toml"
        manifest_path.write_text("""
[common]
root_path = "/tmp"
branch = "main"
remote = "ghpub"

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[projects]]
slug = "test/repo"
path = "test"
remote = "nonexistent"
""")
        manifest = load_manifest(manifest_path)
        with pytest.raises(ManifestValidationError) as exc_info:
            resolve_project(manifest, manifest.projects[0])
        assert "unknown remote" in str(exc_info.value)


class TestResolvedProject:
    """Tests for ResolvedProject dataclass."""

    def test_clone_url_https(self) -> None:
        """Test clone URL construction for HTTPS remote."""
        resolved = ResolvedProject(
            slug="owner/repo",
            path=Path("some/path"),
            remote_name="ghpub",
            remote_url="https://github.com/",
            branch="main",
            status="active",
            parallelism=4,
            timeout=300,
        )
        assert resolved.clone_url == "https://github.com/owner/repo.git"

    def test_clone_url_ssh(self) -> None:
        """Test clone URL construction for SSH remote."""
        resolved = ResolvedProject(
            slug="infra",
            path=Path("infra/global"),
            remote_name="mine",
            remote_url="ssh://git@github.com/vladistan/",
            branch="develop",
            status="active",
            parallelism=2,
            timeout=600,
        )
        assert resolved.clone_url == "ssh://git@github.com/vladistan/infra.git"

    def test_clone_url_trailing_slash_handled(self) -> None:
        """Test clone URL handles base URL with or without trailing slash."""
        resolved = ResolvedProject(
            slug="test/repo",
            path=Path("test"),
            remote_name="test",
            remote_url="https://github.com",  # No trailing slash
            branch="main",
            status="active",
            parallelism=4,
            timeout=300,
        )
        assert resolved.clone_url == "https://github.com/test/repo.git"

    def test_clone_url_already_has_git_suffix(self) -> None:
        """Test clone URL doesn't double .git suffix."""
        resolved = ResolvedProject(
            slug="owner/repo.git",
            path=Path("test"),
            remote_name="test",
            remote_url="https://github.com/",
            branch="main",
            status="active",
            parallelism=4,
            timeout=300,
        )
        assert resolved.clone_url == "https://github.com/owner/repo.git"


class TestResolveAllProjects:
    """Tests for resolve_all_projects function."""

    def test_resolve_all_projects(self, full_manifest: Path) -> None:
        """Test resolving all projects in a manifest."""
        manifest = load_manifest(full_manifest)
        resolved = resolve_all_projects(manifest)
        assert len(resolved) == 5
        assert all(isinstance(p, ResolvedProject) for p in resolved)

    def test_resolve_all_projects_preserves_order(self, full_manifest: Path) -> None:
        """Test resolved projects maintain original order."""
        manifest = load_manifest(full_manifest)
        resolved = resolve_all_projects(manifest)
        assert resolved[0].slug == "linkml/linkml"
        assert resolved[1].slug == "infra"
        assert resolved[4].slug == "deprecated"


class TestValidateManifest:
    """Tests for validate_manifest function."""

    def test_validate_manifest_valid(self, full_manifest: Path) -> None:
        """Test validating a valid manifest returns no errors."""
        manifest = load_manifest(full_manifest)
        errors = validate_manifest(manifest)
        assert errors == []

    def test_validate_manifest_invalid_default_remote(
        self, invalid_remote_manifest: Path
    ) -> None:
        """Test validation catches invalid default remote."""
        manifest = load_manifest(invalid_remote_manifest)
        errors = validate_manifest(manifest)
        assert len(errors) >= 1
        assert any("nonexistent" in e for e in errors)

    def test_validate_manifest_duplicate_paths(
        self, duplicate_paths_manifest: Path
    ) -> None:
        """Test validation catches duplicate project paths."""
        manifest = load_manifest(duplicate_paths_manifest)
        errors = validate_manifest(manifest)
        assert any("Duplicate project path" in e for e in errors)

    def test_validate_manifest_duplicate_slugs_same_remote_allowed(
        self, tmp_path: Path
    ) -> None:
        """Test duplicate slugs for same remote are allowed (multi-branch checkout)."""
        manifest_path = tmp_path / "dup.toml"
        manifest_path.write_text("""
[common]
root_path = "/tmp"
branch = "main"
remote = "ghpub"

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[projects]]
slug = "owner/repo"
path = "repo-main"
branch = "main"

[[projects]]
slug = "owner/repo"
path = "repo-develop"
branch = "develop"
""")
        manifest = load_manifest(manifest_path)
        errors = validate_manifest(manifest)
        assert errors == []  # Duplicate slugs with different paths/branches are OK

    def test_validate_manifest_same_slug_different_remotes_ok(
        self, tmp_path: Path
    ) -> None:
        """Test same slug on different remotes is allowed."""
        manifest_path = tmp_path / "ok.toml"
        manifest_path.write_text("""
[common]
root_path = "/tmp"
branch = "main"
remote = "ghpub"

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[remotes]]
name = "gitlab"
base_url = "https://gitlab.com/"

[[projects]]
slug = "same/repo"
path = "from-github"
remote = "ghpub"

[[projects]]
slug = "same/repo"
path = "from-gitlab"
remote = "gitlab"
""")
        manifest = load_manifest(manifest_path)
        errors = validate_manifest(manifest)
        assert errors == []
