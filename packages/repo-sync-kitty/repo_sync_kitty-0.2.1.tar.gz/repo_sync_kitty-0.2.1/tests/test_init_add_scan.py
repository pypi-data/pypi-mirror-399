"""Unit tests for init, add, and scan commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from repo_sync_kitty.commands.add import (
    _add_project_to_manifest,
    _path_from_slug,
)
from repo_sync_kitty.commands.import_manifest import (
    _generate_toml,
    _parse_repo_manifest,
)
from repo_sync_kitty.commands.init import (
    _generate_manifest_from_scan,
    _get_repo_info,
    _parse_slug_from_url,
    _scan_directory,
)
from repo_sync_kitty.commands.scan import (
    _extract_owner_from_base_url,
    _scan_github,
    _scan_gitlab,
)


class TestPathFromSlug:
    """Tests for _path_from_slug helper."""

    def test_extracts_repo_name_from_slug(self) -> None:
        """Test extracting repo name from owner/repo slug."""
        assert _path_from_slug("owner/repo") == "repo"

    def test_returns_slug_if_no_slash(self) -> None:
        """Test returning slug as-is if no slash."""
        assert _path_from_slug("repo") == "repo"

    def test_handles_nested_paths(self) -> None:
        """Test handling nested paths like group/subgroup/repo."""
        assert _path_from_slug("group/subgroup/repo") == "repo"


class TestAddProjectToManifest:
    """Tests for _add_project_to_manifest helper."""

    def test_adds_project_to_empty_projects_section(self) -> None:
        """Test adding project to manifest with empty projects section."""
        manifest = '''[common]
root_path = "/tmp"
remote = "origin"

[remotes]
origin = { base_url = "https://github.com/" }

[projects]
'''
        result = _add_project_to_manifest(manifest, "new-repo", "owner/new-repo")
        assert '"new-repo" = { slug = "owner/new-repo" }' in result

    def test_adds_project_with_remote(self) -> None:
        """Test adding project with explicit remote."""
        manifest = '''[common]
remote = "origin"

[projects]
'''
        result = _add_project_to_manifest(
            manifest, "path", "slug", remote="other"
        )
        assert 'remote = "other"' in result

    def test_adds_project_with_branch(self) -> None:
        """Test adding project with explicit branch."""
        manifest = '''[common]
remote = "origin"

[projects]
'''
        result = _add_project_to_manifest(
            manifest, "path", "slug", branch="develop"
        )
        assert 'branch = "develop"' in result

    def test_adds_before_next_section(self) -> None:
        """Test project is added before next section."""
        manifest = '''[projects]
"existing" = { slug = "a/b" }

[other]
key = "value"
'''
        result = _add_project_to_manifest(manifest, "new", "c/d")
        # New project should appear after existing but before [other]
        assert result.index('"new"') < result.index("[other]")


class TestParseSlugFromUrl:
    """Tests for _parse_slug_from_url helper."""

    def test_https_url_with_git_extension(self) -> None:
        """Test parsing HTTPS URL with .git extension."""
        url = "https://github.com/owner/repo.git"
        assert _parse_slug_from_url(url) == "owner/repo"

    def test_https_url_without_git_extension(self) -> None:
        """Test parsing HTTPS URL without .git extension."""
        url = "https://github.com/owner/repo"
        assert _parse_slug_from_url(url) == "owner/repo"

    def test_ssh_url_colon_format(self) -> None:
        """Test parsing SSH URL with colon format."""
        url = "git@github.com:owner/repo.git"
        assert _parse_slug_from_url(url) == "owner/repo"

    def test_ssh_url_slash_format(self) -> None:
        """Test parsing SSH URL with slash format (ssh://)."""
        url = "ssh://git@github.com/owner/repo.git"
        assert _parse_slug_from_url(url) == "owner/repo"

    def test_url_with_trailing_slash(self) -> None:
        """Test handling URL with trailing slash."""
        url = "https://github.com/owner/repo/"
        assert _parse_slug_from_url(url) == "owner/repo"


class TestGetRepoInfo:
    """Tests for _get_repo_info helper."""

    def test_returns_none_when_no_origin(self) -> None:
        """Test returns None when repo has no origin remote."""
        mgr = MagicMock()
        mgr.get_remotes.return_value = ["upstream"]

        result = _get_repo_info(mgr, Path("/repo"), Path("/"))
        assert result is None

    def test_returns_info_with_origin(self) -> None:
        """Test returns info dict when origin exists."""
        mgr = MagicMock()
        mgr.get_remotes.return_value = ["origin"]
        mgr.repo.remote.return_value.url = "https://github.com/owner/repo.git"
        mgr.get_current_branch.return_value = "main"

        result = _get_repo_info(mgr, Path("/root/myrepo"), Path("/root"))
        assert result is not None
        assert result["path"] == "myrepo"
        assert result["slug"] == "owner/repo"
        assert result["branch"] == "main"

    def test_returns_none_on_exception(self) -> None:
        """Test returns None when exception occurs."""
        mgr = MagicMock()
        mgr.get_remotes.side_effect = Exception("git error")

        result = _get_repo_info(mgr, Path("/repo"), Path("/"))
        assert result is None


class TestScanDirectory:
    """Tests for _scan_directory helper."""

    def test_returns_empty_for_empty_dir(self, tmp_path: Path) -> None:
        """Test returns empty list for empty directory."""
        result = _scan_directory(tmp_path)
        assert result == []

    def test_skips_hidden_directories(self, tmp_path: Path) -> None:
        """Test skips directories starting with dot."""
        (tmp_path / ".hidden").mkdir()
        result = _scan_directory(tmp_path)
        assert result == []

    def test_skips_non_directories(self, tmp_path: Path) -> None:
        """Test skips regular files."""
        (tmp_path / "file.txt").write_text("content")
        result = _scan_directory(tmp_path)
        assert result == []


class TestGenerateManifestFromScan:
    """Tests for _generate_manifest_from_scan helper."""

    def test_generates_manifest_with_repos(self) -> None:
        """Test generates valid manifest TOML."""
        repos = [
            {"path": "repo1", "slug": "owner/repo1", "branch": "main"},
            {"path": "repo2", "slug": "owner/repo2", "branch": "develop"},
        ]
        result = _generate_manifest_from_scan(repos, Path("/root"))

        assert "[common]" in result
        assert 'root_path = "/root"' in result
        assert "[remotes]" in result
        assert "[projects]" in result
        assert '"repo1" = { slug = "owner/repo1" }' in result
        # Non-main branch should include branch
        assert '"repo2" = { slug = "owner/repo2", branch = "develop" }' in result

    def test_sorts_repos_by_path(self) -> None:
        """Test repos are sorted by path."""
        repos = [
            {"path": "z-repo", "slug": "a/z", "branch": "main"},
            {"path": "a-repo", "slug": "a/a", "branch": "main"},
        ]
        result = _generate_manifest_from_scan(repos, Path("/root"))

        # a-repo should appear before z-repo
        assert result.index("a-repo") < result.index("z-repo")


class TestScanGitHub:
    """Tests for _scan_github helper."""

    @patch("repo_sync_kitty.commands.scan.httpx.get")
    def test_returns_repos_from_org(self, mock_get: MagicMock) -> None:
        """Test scanning GitHub org returns repos."""
        # First call returns data, second call returns empty (end pagination)
        mock_response_with_data = MagicMock()
        mock_response_with_data.status_code = 200
        mock_response_with_data.json.return_value = [
            {
                "name": "repo1",
                "full_name": "org/repo1",
                "description": "A test repo",
                "default_branch": "main",
                "private": False,
                "clone_url": "https://github.com/org/repo1.git",
            }
        ]

        mock_response_empty = MagicMock()
        mock_response_empty.status_code = 200
        mock_response_empty.json.return_value = []

        mock_get.side_effect = [mock_response_with_data, mock_response_empty]

        result = _scan_github("org")

        assert len(result) == 1
        assert result[0]["name"] == "repo1"
        assert result[0]["slug"] == "org/repo1"

    @patch("repo_sync_kitty.commands.scan.httpx.get")
    def test_handles_empty_response(self, mock_get: MagicMock) -> None:
        """Test handling empty response from GitHub."""
        # Org endpoint returns empty, then user endpoint also returns empty
        mock_empty = MagicMock()
        mock_empty.status_code = 200
        mock_empty.json.return_value = []
        mock_get.return_value = mock_empty

        result = _scan_github("empty-org")
        assert result == []

    @patch("repo_sync_kitty.commands.scan.httpx.get")
    def test_tries_user_endpoint_after_org_404(self, mock_get: MagicMock) -> None:
        """Test falls back to user endpoint on org 404."""
        # First call (org) returns 404, second call (user) returns data, third empty
        mock_404 = MagicMock()
        mock_404.status_code = 404

        mock_200 = MagicMock()
        mock_200.status_code = 200
        mock_200.json.return_value = [
            {
                "name": "user-repo",
                "full_name": "user/user-repo",
                "description": "",
                "default_branch": "main",
                "private": True,
                "clone_url": "https://github.com/user/user-repo.git",
            }
        ]

        mock_empty = MagicMock()
        mock_empty.status_code = 200
        mock_empty.json.return_value = []

        mock_get.side_effect = [mock_404, mock_200, mock_empty]

        result = _scan_github("user")
        assert len(result) == 1
        assert result[0]["private"] == "private"

    @patch("repo_sync_kitty.commands.scan.httpx.get")
    def test_uses_token_in_header(self, mock_get: MagicMock) -> None:
        """Test token is used in Authorization header."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        _scan_github("org", token="my-token")

        call_headers = mock_get.call_args_list[0][1]["headers"]
        assert call_headers["Authorization"] == "token my-token"


class TestScanGitLab:
    """Tests for _scan_gitlab helper."""

    @patch("repo_sync_kitty.commands.scan.httpx.get")
    def test_returns_repos_from_group(self, mock_get: MagicMock) -> None:
        """Test scanning GitLab group returns repos."""
        mock_response_with_data = MagicMock()
        mock_response_with_data.status_code = 200
        mock_response_with_data.json.return_value = [
            {
                "name": "project1",
                "path_with_namespace": "group/project1",
                "description": "A test project",
                "default_branch": "main",
                "visibility": "public",
                "http_url_to_repo": "https://gitlab.com/group/project1.git",
            }
        ]

        mock_response_empty = MagicMock()
        mock_response_empty.status_code = 200
        mock_response_empty.json.return_value = []

        mock_get.side_effect = [mock_response_with_data, mock_response_empty]

        result = _scan_gitlab("group")

        assert len(result) == 1
        assert result[0]["name"] == "project1"
        assert result[0]["slug"] == "group/project1"
        assert result[0]["private"] == "public"

    @patch("repo_sync_kitty.commands.scan.httpx.get")
    def test_uses_private_token_header(self, mock_get: MagicMock) -> None:
        """Test GitLab token is sent in PRIVATE-TOKEN header."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        _scan_gitlab("group", token="gl-token")

        call_headers = mock_get.call_args_list[0][1]["headers"]
        assert call_headers["PRIVATE-TOKEN"] == "gl-token"

    @patch("repo_sync_kitty.commands.scan.httpx.get")
    def test_handles_private_visibility(self, mock_get: MagicMock) -> None:
        """Test private visibility is correctly mapped."""
        mock_response_with_data = MagicMock()
        mock_response_with_data.status_code = 200
        mock_response_with_data.json.return_value = [
            {
                "name": "private-proj",
                "path_with_namespace": "group/private-proj",
                "description": None,
                "default_branch": "master",
                "visibility": "private",
                "http_url_to_repo": "https://gitlab.com/group/private-proj.git",
            }
        ]

        mock_response_empty = MagicMock()
        mock_response_empty.status_code = 200
        mock_response_empty.json.return_value = []

        mock_get.side_effect = [mock_response_with_data, mock_response_empty]

        result = _scan_gitlab("group")
        assert result[0]["private"] == "private"


class TestExtractOwnerFromBaseUrl:
    """Tests for _extract_owner_from_base_url helper."""

    def test_extracts_owner_from_https_url(self) -> None:
        """Test extracting owner from HTTPS URL with owner."""
        assert _extract_owner_from_base_url("https://github.com/vladistan/") == "vladistan"

    def test_extracts_owner_from_ssh_url(self) -> None:
        """Test extracting owner from SSH URL with owner."""
        assert _extract_owner_from_base_url("ssh://git@github.com/vladistan/") == "vladistan"

    def test_extracts_owner_from_git_colon_url(self) -> None:
        """Test extracting owner from git@host:owner format."""
        assert _extract_owner_from_base_url("git@github.com:vladistan") == "vladistan"

    def test_returns_none_for_base_url_without_owner(self) -> None:
        """Test returning None for URL without owner."""
        assert _extract_owner_from_base_url("https://github.com/") is None

    def test_returns_none_for_gitlab_base(self) -> None:
        """Test returning None for GitLab base URL."""
        assert _extract_owner_from_base_url("https://gitlab.com/") is None

    def test_handles_url_without_trailing_slash(self) -> None:
        """Test handling URL without trailing slash."""
        assert _extract_owner_from_base_url("https://github.com/myorg") == "myorg"


class TestParseRepoManifest:
    """Tests for _parse_repo_manifest helper."""

    def test_parses_remotes(self, tmp_path: Path) -> None:
        """Test parsing remotes from manifest."""
        xml = tmp_path / "manifest.xml"
        xml.write_text('''<?xml version="1.0"?>
<manifest>
  <remote name="origin" fetch="ssh://git@github.com/vladistan"/>
  <remote name="ghpub" fetch="https://github.com/"/>
  <default remote="origin" revision="master"/>
</manifest>
''')
        result = _parse_repo_manifest(xml)
        assert len(result["remotes"]) == 2
        assert result["remotes"]["origin"] == "ssh://git@github.com/vladistan/"
        assert result["remotes"]["ghpub"] == "https://github.com/"

    def test_parses_default_settings(self, tmp_path: Path) -> None:
        """Test parsing default remote and revision."""
        xml = tmp_path / "manifest.xml"
        xml.write_text('''<?xml version="1.0"?>
<manifest>
  <remote name="origin" fetch="https://github.com/"/>
  <default remote="origin" revision="main"/>
</manifest>
''')
        result = _parse_repo_manifest(xml)
        assert result["default_remote"] == "origin"
        assert result["default_revision"] == "main"

    def test_parses_projects(self, tmp_path: Path) -> None:
        """Test parsing projects from manifest."""
        xml = tmp_path / "manifest.xml"
        xml.write_text('''<?xml version="1.0"?>
<manifest>
  <remote name="origin" fetch="https://github.com/"/>
  <default remote="origin" revision="master"/>
  <project name="repo1.git" path="libs/repo1"/>
  <project name="repo2.git" path="tools/repo2" remote="ghpub"/>
  <project name="repo3.git" path="repo3" revision="develop"/>
</manifest>
''')
        result = _parse_repo_manifest(xml)
        assert len(result["projects"]) == 3
        # Check .git suffix is stripped
        assert result["projects"][0]["slug"] == "repo1"
        assert result["projects"][0]["path"] == "libs/repo1"
        # Check explicit remote
        assert result["projects"][1]["remote"] == "ghpub"
        # Check explicit revision
        assert result["projects"][2]["revision"] == "develop"

    def test_strips_git_suffix(self, tmp_path: Path) -> None:
        """Test .git suffix is stripped from project names."""
        xml = tmp_path / "manifest.xml"
        xml.write_text('''<?xml version="1.0"?>
<manifest>
  <remote name="origin" fetch="https://github.com/"/>
  <default remote="origin" revision="master"/>
  <project name="my-repo.git" path="my-repo"/>
</manifest>
''')
        result = _parse_repo_manifest(xml)
        assert result["projects"][0]["slug"] == "my-repo"

    def test_handles_missing_default(self, tmp_path: Path) -> None:
        """Test fallback when default element is missing."""
        xml = tmp_path / "manifest.xml"
        xml.write_text('''<?xml version="1.0"?>
<manifest>
  <remote name="origin" fetch="https://github.com/"/>
  <project name="repo.git" path="repo"/>
</manifest>
''')
        result = _parse_repo_manifest(xml)
        assert result["default_remote"] == "origin"
        assert result["default_revision"] == "main"


class TestGenerateToml:
    """Tests for _generate_toml helper."""

    def test_generates_common_section(self) -> None:
        """Test TOML includes common section with defaults."""
        parsed = {
            "remotes": {"origin": "https://github.com/"},
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [],
        }
        result = _generate_toml(parsed, "/root")
        assert "[common]" in result
        assert 'root_path = "/root"' in result
        assert 'branch = "main"' in result
        assert 'remote = "origin"' in result
        assert "parallelism = 4" in result
        assert "timeout = 300" in result

    def test_generates_remotes_section(self) -> None:
        """Test TOML includes remotes section."""
        parsed = {
            "remotes": {
                "ghpub": "https://github.com/",
                "origin": "ssh://git@github.com/user/",
            },
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [],
        }
        result = _generate_toml(parsed, "/root")
        assert "[remotes]" in result
        assert 'ghpub = { base_url = "https://github.com/" }' in result
        assert 'origin = { base_url = "ssh://git@github.com/user/" }' in result

    def test_generates_projects_section(self) -> None:
        """Test TOML includes projects section."""
        parsed = {
            "remotes": {"origin": "https://github.com/"},
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [
                {"slug": "repo1", "path": "repo1", "remote": None, "revision": None},
            ],
        }
        result = _generate_toml(parsed, "/root")
        assert "[projects]" in result
        assert '"repo1" = { }' in result

    def test_omits_default_remote_and_branch(self) -> None:
        """Test remote and branch are omitted if same as default."""
        parsed = {
            "remotes": {"origin": "https://github.com/"},
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [
                {"slug": "repo", "path": "libs/repo", "remote": "origin", "revision": "main"},
            ],
        }
        result = _generate_toml(parsed, "/root")
        # Should not include remote or branch since they match defaults
        # Also slug is omitted because it matches the path's final component
        assert '"libs/repo" = { }' in result

    def test_includes_non_default_remote_and_branch(self) -> None:
        """Test non-default remote and branch are included."""
        parsed = {
            "remotes": {"origin": "https://github.com/", "other": "https://other.com/"},
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [
                {"slug": "repo", "path": "repo", "remote": "other", "revision": "develop"},
            ],
        }
        result = _generate_toml(parsed, "/root")
        assert 'remote = "other"' in result
        assert 'branch = "develop"' in result

    def test_omits_slug_when_matches_path_name(self) -> None:
        """Test slug is omitted when it matches the path's final component."""
        parsed = {
            "remotes": {"origin": "https://github.com/"},
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [
                {"slug": "myrepo", "path": "libs/myrepo", "remote": None, "revision": None},
            ],
        }
        result = _generate_toml(parsed, "/root")
        # Slug matches path name, so should be omitted
        assert '"libs/myrepo" = { }' in result

    def test_includes_slug_when_differs_from_path(self) -> None:
        """Test slug is included when different from path's final component."""
        parsed = {
            "remotes": {"origin": "https://github.com/"},
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [
                {"slug": "owner/repo", "path": "libs/myrepo", "remote": None, "revision": None},
            ],
        }
        result = _generate_toml(parsed, "/root")
        assert 'slug = "owner/repo"' in result

    def test_sorts_projects_by_path(self) -> None:
        """Test projects are sorted by path."""
        parsed = {
            "remotes": {"origin": "https://github.com/"},
            "default_remote": "origin",
            "default_revision": "main",
            "projects": [
                {"slug": "z", "path": "z-path", "remote": None, "revision": None},
                {"slug": "a", "path": "a-path", "remote": None, "revision": None},
            ],
        }
        result = _generate_toml(parsed, "/root")
        # a-path should appear before z-path
        assert result.index("a-path") < result.index("z-path")
