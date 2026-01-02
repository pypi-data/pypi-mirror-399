# repo-sync-kitty

Git repository synchronization tool for teams. Keep multiple git repositories in sync across machines using a declarative TOML manifest.

## Features

- **Manifest-driven**: Define repositories in a single TOML file
- **Safe pulls**: Multiple precondition checks before pulling (dirty state, wrong branch, unpushed commits)
- **Parallel operations**: Configurable concurrency for faster syncs
- **Multiple remotes**: Support for GitHub, GitLab, Bitbucket, and custom git servers
- **Rich output**: Progress bars, colored status tables, and detailed summaries

## Installation

### Homebrew (macOS)

```bash
brew tap vladistan/gizmos
brew install repo-sync-kitty
```

### PyPI

```bash
pip install repo-sync-kitty
```

### From source

```bash
# Using uv (recommended)
cd tools/repo-sync-kitty
uv sync
uv run repo-sync-kitty --help

# Or install globally with pip
pip install .
```

## Quick Start

1. **Initialize a manifest** in your projects directory:

```bash
# Create an empty template
repo-sync-kitty init -o manifest.toml

# Or scan an existing directory for repos
repo-sync-kitty init --scan-dir ~/Projects -o manifest.toml
```

2. **Validate your manifest**:

```bash
repo-sync-kitty check -m manifest.toml
```

3. **Sync your repositories**:

```bash
# Dry run first
repo-sync-kitty sync -m manifest.toml --dry-run

# Actually sync
repo-sync-kitty sync -m manifest.toml
```

4. **Check status** anytime:

```bash
repo-sync-kitty status -m manifest.toml
```

## Commands

### `sync` - Clone and update repositories

```bash
repo-sync-kitty sync [OPTIONS]

Options:
  -m, --manifest PATH    Path to manifest.toml
  --fetch-only           Only fetch, don't clone or pull
  --clone-only           Only clone missing repos
  --pull                 Pull changes after fetch (if safe)
  -n, --dry-run          Show what would be done
  -v, --verbose          Show detailed output instead of progress bar
  -j, --parallelism INT  Override parallelism setting
```

**Examples:**
```bash
# Clone missing repos and fetch all
repo-sync-kitty sync -m manifest.toml

# Clone missing repos only
repo-sync-kitty sync -m manifest.toml --clone-only

# Fetch and pull (when safe)
repo-sync-kitty sync -m manifest.toml --pull

# Verbose output with 2 parallel workers
repo-sync-kitty sync -m manifest.toml -v -j 2
```

### `status` - Show repository status

```bash
repo-sync-kitty status [OPTIONS]

Options:
  -m, --manifest PATH   Path to manifest.toml
  -v, --verbose         Show all repos (not just issues)
  --show-deleted        Include deleted repos in output
```

**Output shows:**
- Missing repos (not cloned)
- Dirty repos (uncommitted changes)
- Wrong branch
- Ahead/behind remote
- Detached HEAD state

### `check` - Validate manifest

```bash
repo-sync-kitty check [OPTIONS]

Options:
  -m, --manifest PATH   Path to manifest.toml
```

Validates manifest syntax, checks that all referenced remotes exist, and displays a summary of configuration.

### `fix-detached` - Fix detached HEAD states

```bash
repo-sync-kitty fix-detached [OPTIONS]

Options:
  -m, --manifest PATH    Path to manifest.toml
  -n, --dry-run          Show what would be done without making changes
  -v, --verbose          Show detailed output instead of progress bar
  -j, --parallelism INT  Number of parallel workers
```

**Examples:**
```bash
# Dry run to see what would be fixed
repo-sync-kitty fix-detached -m manifest.toml --dry-run

# Fix detached HEADs
repo-sync-kitty fix-detached -m manifest.toml
```

Safely fixes detached HEAD states left by git-repo. For each detached repo:
1. **Checks for loose files** - aborts if there are untracked, modified, or staged files
2. **Finds branch at HEAD** - checks if HEAD points to a branch tip
3. **Checks out the branch** - only if HEAD is at a branch tip

This is safe for repos previously maintained by git-repo, which leaves repos in detached HEAD state pointing at branch tips.

### `init` - Create new manifest

```bash
repo-sync-kitty init [OPTIONS]

Options:
  -o, --output PATH     Output path for manifest.toml (default: manifest.toml)
  --scan-dir PATH       Scan directory for existing repos
  --scan-forge NAME     Scan forge for repos (not yet implemented)
  --org NAME            Organization/user to scan on forge
  -f, --force           Overwrite existing manifest
```

**Examples:**
```bash
# Create empty template
repo-sync-kitty init

# Scan ~/Projects for git repos and generate manifest
repo-sync-kitty init --scan-dir ~/Projects -o my-manifest.toml
```

### `add` - Add repository to manifest

```bash
repo-sync-kitty add REMOTE SLUG [OPTIONS]

Arguments:
  REMOTE               Remote name (must exist in manifest)
  SLUG                 Repository slug (e.g., 'owner/repo')

Options:
  -m, --manifest PATH  Path to manifest.toml
  -p, --path PATH      Local path (defaults to repo name from slug)
  -b, --branch NAME    Branch to track
```

**Examples:**
```bash
# Add repo with default path
repo-sync-kitty add origin octocat/Hello-World -m manifest.toml

# Add repo with custom path and branch
repo-sync-kitty add origin owner/repo -p libs/myrepo -b develop
```

### `import-repo` - Import from git-repo manifest

```bash
repo-sync-kitty import-repo SOURCE [OPTIONS]

Arguments:
  SOURCE               Path to git-repo manifest XML file (e.g., default.xml)

Options:
  -o, --output PATH    Output path for manifest.toml (default: manifest.toml)
  -r, --root PATH      Root path for repos (default: parent of source file)
  -f, --force          Overwrite existing manifest
```

**Examples:**
```bash
# Import from default.xml in current directory
repo-sync-kitty import-repo default.xml

# Import with custom output path
repo-sync-kitty import-repo ~/repo/default.xml -o my-manifest.toml

# Import and set custom root path
repo-sync-kitty import-repo default.xml -r ~/Projects/myteam -o manifest.toml
```

This command converts Google's [git-repo](https://gerrit.googlesource.com/git-repo/) manifest format (XML) to repo-sync-kitty's TOML format. The importer handles:
- Multiple remotes with different base URLs
- Default remote and branch settings
- Per-project remote and branch overrides
- Stripping `.git` suffix from project names

### `scan` - List repositories from forge

```bash
repo-sync-kitty scan FORGE [OPTIONS]

Arguments:
  FORGE                Forge to scan (github, gitlab)

Options:
  --org, -o NAME       Organization/user to scan (required)
  --token, -t TOKEN    API token for authentication
  -m, --manifest PATH  Path to manifest.toml (for comparison)
  -r, --remote NAME    Remote to use when adding repos
  --missing            Only show repos not already in manifest
  --add                Add scanned repos to manifest (requires -r)
```

**Examples:**
```bash
# Scan public GitHub repos
repo-sync-kitty scan github --org octocat

# Scan with token (required for private repos)
repo-sync-kitty scan github --org myorg --token $GH_TOKEN

# Compare against manifest (shows checkmarks for enrolled repos)
repo-sync-kitty scan github --org myorg -m manifest.toml

# Show only repos not in manifest
repo-sync-kitty scan github --org myorg -m manifest.toml --missing

# Add missing repos to manifest
repo-sync-kitty scan github --org myorg -m manifest.toml -r origin --add
```

**Note:** For GitHub, the token is checked in order: `-t` option → `GH_TOKEN` env var → `GITHUB_TOKEN` env var. A token is required to see private repositories.

## Manifest Format

### Basic Structure

```toml
[common]
root_path = "~/Projects/my-team"
branch = "main"
remote = "origin"
parallelism = 4
timeout = 300

[remotes]
origin = { base_url = "https://github.com/" }
gitlab = { base_url = "https://gitlab.com/", branch = "master" }

[projects]
"libs/repo1" = { slug = "owner/repo1" }
"libs/repo2" = { slug = "owner/repo2", branch = "develop" }
```

### Common Section

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `root_path` | string | required | Base directory for all repos |
| `branch` | string | `"main"` | Default branch to track |
| `remote` | string | required | Default remote name |
| `parallelism` | int | `4` | Max concurrent operations |
| `timeout` | int | `300` | Operation timeout in seconds |

### Remotes Section

Supports two formats:

**Compact (inline):**
```toml
[remotes]
ghpub = { base_url = "https://github.com/" }
mine = { base_url = "ssh://git@github.com/myuser/", branch = "develop" }
```

**Expanded (multi-line):**
```toml
[remotes.mine]
base_url = "ssh://git@github.com/myuser/"
branch = "develop"
parallelism = 2
timeout = 600
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | string | required | Base URL for clone URLs |
| `branch` | string | inherited | Default branch for this remote |
| `parallelism` | int | inherited | Max concurrent ops for this remote |
| `timeout` | int | inherited | Timeout for this remote's operations |

### Projects Section

**Compact:**
```toml
[projects]
"libs/linkml" = { slug = "linkml/linkml", remote = "ghpub" }
"infra" = { slug = "infra", branch = "develop" }
```

**Expanded:**
```toml
[projects."libs/linkml"]
slug = "linkml/linkml"
remote = "ghpub"
branch = "main"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `slug` | string | required | Repository slug (owner/repo) |
| `path` | string | key | Local path relative to root_path |
| `remote` | string | inherited | Remote to use |
| `branch` | string | inherited | Branch to track |
| `status` | string | `"active"` | One of: active, archived, deleted |

### Inheritance

Values inherit in this order: **project → remote → common**

```
branch: project.branch → remote.branch → common.branch
parallelism: remote.parallelism → common.parallelism
timeout: remote.timeout → common.timeout
```

### URL Construction

Clone URLs are constructed as: `{remote.base_url}{project.slug}.git`

Examples:
- `https://github.com/` + `linkml/linkml` → `https://github.com/linkml/linkml.git`
- `ssh://git@github.com/myuser/` + `infra` → `ssh://git@github.com/myuser/infra.git`

## Safety Checks

Before pulling, repo-sync-kitty checks:

1. **Correct branch**: Current branch matches expected
2. **Clean state**: No uncommitted changes
3. **No staged files**: Nothing in the index
4. **No in-progress operations**: Not rebasing, merging, or cherry-picking
5. **Not detached**: HEAD is attached to a branch
6. **Not ahead**: No unpushed commits

If any check fails, the repo is skipped with a warning.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GH_TOKEN` | GitHub API token for scan command (preferred) |
| `GITHUB_TOKEN` | GitHub API token for scan command (fallback) |
| `GITLAB_TOKEN` | GitLab API token for scan command |
| `SENTRY_DSN` | Optional Sentry DSN for error tracking |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | One or more operations failed |
| 2 | Invalid manifest or configuration |

## Development

```bash
# Install with dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## Troubleshooting

### "Not safe to pull" warnings

This means one of the safety checks failed. Run `status -v` to see details:

```bash
repo-sync-kitty status -m manifest.toml -v
```

Common causes:
- Uncommitted changes → commit or stash them
- Wrong branch → checkout the expected branch
- Unpushed commits → push your changes first
- In-progress rebase → complete or abort the rebase

### "Remote not found" errors

The remote referenced in a project doesn't exist in the `[remotes]` section. Add it or fix the reference.

### Slow syncs

Try increasing parallelism:

```bash
repo-sync-kitty sync -m manifest.toml -j 8
```

Or set it in your manifest:

```toml
[common]
parallelism = 8
```
