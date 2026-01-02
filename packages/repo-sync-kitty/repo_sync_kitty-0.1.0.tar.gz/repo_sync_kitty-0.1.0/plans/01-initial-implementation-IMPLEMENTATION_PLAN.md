# repo-sync-kitty - Initial Implementation Plan

## Implementation Progress

- [x] Phase 1: Project Foundation & CLI Skeleton
- [x] Phase 2: Config & Manifest System
- [x] Phase 3: Git Operations Layer
- [x] Phase 4: Core Commands (sync, status)
- [x] Phase 5: Secondary Commands (init, add, scan)
- [x] Phase 6: Polish & Production Readiness
- [x] Phase 7: Extended Commands (bonus features beyond original scope)

## Summary of Deliverables

### Phase 1: Project Foundation
- [x] Project structure with uv
- [x] pyproject.toml with dependencies
- [x] CLI skeleton with Typer
- [x] pytest with coverage tracking
- [x] Sentry integration (optional, via env var)
- [x] ruff and mypy configuration

### Phase 2: Config & Manifest
- [x] Pydantic models for manifest.toml
- [x] TOML parsing with inheritance (dict and array formats)
- [x] Config validation
- [x] `check` command working

### Phase 3: Git Operations
- [x] GitPython wrapper module (RepoManager)
- [x] Clone, fetch, pull operations
- [x] Safety check detection (SafetyChecker)
- [x] Repo state inspection (in-progress ops, ahead/behind)
- [x] Retry logic with exponential backoff (RetryManager)
- [x] Unit tests for git operations

### Phase 4: Core Commands
- [x] `status` command (terse/verbose, --all flag)
- [x] `sync` command with progress bar
- [x] Parallel execution (ThreadPoolExecutor)
- [x] Retry with exponential backoff
- [x] Error collection and summary reporting

### Phase 5: Secondary Commands
- [x] `init` command (template, dir scan)
- [x] `add` command
- [x] `scan` command (GitHub with --add, --missing flags)

### Phase 6: Polish & Documentation
- [x] README.md complete with all commands documented
- [x] Integration tests (test_integration.py)
- [x] 210 tests passing

### Phase 7: Extended Commands (Bonus)
- [x] `import-repo` command (git-repo XML manifest conversion)
- [x] `fix-detached` command (fix detached HEADs from git-repo)
- [x] `find-orphans` command (find untracked repos)
- [x] `move` command (relocate repos and update manifest)
- [x] `open` command (open repo in browser)

## Remaining Work

- [ ] Increase test coverage from 54% to 75%+ (coverage gate currently failing)
- [ ] Add tests for new commands: move, open, find-orphans, fix-detached
- [ ] GitLab/Bitbucket forge support (stubs exist, not implemented)

---

## Overview

repo-sync-kitty is a Python CLI tool for synchronizing git repositories across team machines. It uses a TOML manifest file to declare which repositories should be present, their locations, and branches. The tool clones missing repos, fetches updates, and safely pulls changes when conditions allow.

**Key Features**:
- Manifest-driven repository management
- Safe pull with multiple precondition checks
- Parallel operations with configurable concurrency
- Support for multiple remotes and forges
- Rich terminal output with progress tracking

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    repo-sync-kitty CLI                          │
│                        (Typer)                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│  Config   │  │    Git    │  │   Forge   │  │  Output   │
│ (Pydantic)│  │(subprocess)│  │  (httpx)  │  │  (Rich)   │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
      │              │              │
      ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐
│manifest.  │  │ Local Git │  │  GitHub   │
│  toml     │  │   Repos   │  │  GitLab   │
└───────────┘  └───────────┘  │ Bitbucket │
                              └───────────┘
```

## Alternatives Evaluation

For detailed analysis of alternative approaches and technologies considered, see [ALTERNATIVES](01-initial-implementation-ALTERNATIVES.md).

**Selected Solutions**:
- **Git Interaction**: GitPython
- **Parallelism**: concurrent.futures ThreadPoolExecutor
- **CLI Framework**: Typer
- **Config Validation**: Pydantic Settings
- **Output**: Rich
- **HTTP Client**: httpx

**Key Decision Factors**: Mature OO API, maintainability, full git feature support, modern Python patterns

## Testing Approach

- **Unit Tests**: pytest with mocked GitPython objects
- **Integration Tests**: Real git operations against test repositories
- **Coverage Target**: 80%+ with pytest-cov (enforced from Phase 1)
- **Observability**: Sentry integration from Phase 1 (optional, via SENTRY_DSN env var)
- **CI**: ruff linting, mypy type checking, pytest with coverage gate

---

## Detailed Implementation Phases

### Phase 1: Project Foundation & CLI Skeleton

**Goal**: Establish project structure, dependencies, and basic CLI that responds to commands.

#### Step 1.1: Project Setup

**Implementation**:
1. Initialize uv project in `tools/repo-sync-kitty/`
2. Create `pyproject.toml` with dependencies
3. Set up `src/repo_sync_kitty/` package structure
4. Configure ruff and mypy

**Project Structure**:
```
tools/repo-sync-kitty/
├── pyproject.toml
├── README.md
├── plans/
│   ├── 01-initial-implementation-IMPLEMENTATION_PLAN.md
│   └── 01-initial-implementation-ALTERNATIVES.md
├── src/
│   └── repo_sync_kitty/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── sync.py
│       │   ├── status.py
│       │   ├── init.py
│       │   ├── add.py
│       │   ├── check.py
│       │   └── scan.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── models.py
│       ├── git/
│       │   ├── __init__.py
│       │   ├── operations.py
│       │   └── safety.py
│       ├── forge/
│       │   ├── __init__.py
│       │   ├── github.py
│       │   ├── gitlab.py
│       │   └── bitbucket.py
│       └── output/
│           ├── __init__.py
│           └── display.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_config.py
    ├── test_git.py
    └── test_commands.py
```

**Dependencies**:
```
- typer[all] >= 0.9.0
- pydantic-settings >= 2.0.0
- rich >= 13.0.0
- httpx >= 0.25.0
- gitpython >= 3.1.0
- sentry-sdk >= 1.0.0 (optional extra)
```

**Dev Dependencies**:
```
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- ruff >= 0.1.0
- mypy >= 1.0.0
```

#### Step 1.2: CLI Skeleton

**Implementation**:
1. Create main Typer app in `cli.py`
2. Add stub commands: init, sync, status, add, check, scan
3. Add global options: --manifest, --root, --no-color, --verbose
4. Set up entry point in pyproject.toml

**CLI Structure**:
```
repo-sync-kitty
├── init [--scan-dir] [--scan-forge]
├── sync [--fetch-only] [--clone-only] [--pull] [--dry-run]
├── status [--verbose] [--show-deleted]
├── add <remote> <slug> [--path] [--branch]
├── check
└── scan <remote> [--org] [--token]

Global Options:
├── --manifest, -m PATH
├── --root PATH
├── --no-color
└── --verbose, -v
```

#### Step 1.3: Sentry Integration

**Implementation**:
1. Initialize Sentry if `SENTRY_DSN` environment variable is set
2. Add to CLI startup in `cli.py`
3. Configure release version from package version
4. Capture unhandled exceptions automatically

**Sentry Setup**:
```python
# In cli.py or __init__.py
import sentry_sdk
import os

if dsn := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(dsn=dsn, release=__version__)
```

#### Step 1.4: Test Infrastructure

**Implementation**:
1. Set up pytest with coverage
2. Configure coverage to fail under 80%
3. Create initial test file with passing test
4. Add conftest.py with common fixtures

**Validation Checkpoint**:
```bash
# Install in dev mode
cd tools/repo-sync-kitty
uv sync
uv run repo-sync-kitty --help
uv run repo-sync-kitty sync --help
uv run pytest --cov=repo_sync_kitty --cov-fail-under=80
uv run ruff check .
uv run mypy src/
```

**Deliverables**:
- [x] pyproject.toml configured
- [x] Package structure created
- [x] CLI responds to --help for all commands
- [x] Sentry initializes when SENTRY_DSN set
- [x] pytest runs with coverage tracking (90% achieved)
- [x] ruff and mypy pass

**User Validated**: [x]

---

### Phase 2: Config & Manifest System

**Goal**: Parse and validate manifest.toml with full inheritance support.

#### Step 2.1: Pydantic Models

**Implementation**:
1. Create `RemoteConfig` model (name, base_url, branch, parallelism, timeout)
2. Create `ProjectConfig` model (slug, path, remote, branch, status)
3. Create `CommonConfig` model (root_path, branch, remote, parallelism, log_level, timeout)
4. Create `Manifest` model combining all sections
5. Implement inheritance resolution (common → remote → project)

**Config Schema**:
```
Manifest
├── common: CommonConfig
│   ├── root_path: Path
│   ├── branch: str = "main"
│   ├── remote: str
│   ├── parallelism: int = 4
│   ├── log_level: str = "info"
│   ├── timeout: int = 300
│   └── ignore_extra: list[str] = []
├── remotes: list[RemoteConfig]
│   ├── name: str
│   ├── base_url: str
│   ├── branch: str | None (inherits from common)
│   ├── parallelism: int | None (inherits from common)
│   └── timeout: int | None (inherits from common)
└── projects: list[ProjectConfig]
    ├── slug: str
    ├── path: Path
    ├── remote: str | None (inherits from common)
    ├── branch: str | None (inherits from remote → common)
    └── status: Literal["active", "archived", "deleted"] = "active"
```

#### Step 2.2: TOML Parsing

**Implementation**:
1. Use `tomllib` (Python 3.11+ stdlib) for parsing
2. Load and validate against Pydantic models
3. Resolve inheritance chain
4. Compute final URLs for each project

**URL Construction Logic**:
```
final_url = remote.base_url + project.slug + ".git"

Examples:
- base_url="https://github.com/" + slug="linkml/linkml" → "https://github.com/linkml/linkml.git"
- base_url="ssh://git@github.com/vladistan/" + slug="infra" → "ssh://git@github.com/vladistan/infra.git"
```

#### Step 2.3: Check Command

**Implementation**:
1. Load manifest
2. Validate all fields
3. Verify remotes referenced by projects exist
4. Report any validation errors
5. Show summary of manifest contents

**Validation Checkpoint**:
```bash
# Create test manifest
cat > test-manifest.toml << 'EOF'
[common]
root_path = "~/Projects/test"
branch = "main"
remote = "ghpub"
parallelism = 4

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

[[remotes]]
name = "mine"
base_url = "ssh://git@github.com/vladistan/"

projects = [
  { slug = "linkml/linkml", path = "libs/linkml", remote = "ghpub" },
  { slug = "infra", path = "infra/global", remote = "mine" },
]
EOF

uv run repo-sync-kitty check --manifest test-manifest.toml
```

**Deliverables**:
- [x] Pydantic models defined
- [x] TOML parsing works (dict and array formats)
- [x] Inheritance resolution works
- [x] URL construction correct
- [x] `check` command validates and reports
- [x] Unit tests for config parsing (80 tests, 94% coverage)

**User Validated**: [x]

---

### Phase 3: Git Operations Layer

**Goal**: Implement git operations via GitPython with safety checks.

#### Step 3.1: Git Wrapper

**Implementation**:
1. Create `RepoManager` class wrapping GitPython `Repo`
2. Implement `clone(url, path, branch)` using `Repo.clone_from()`
3. Implement `fetch(remotes=None)` - fetch all or specific remotes via `remote.fetch()`
4. Implement `pull()` with safety checks via `remote.pull()`
5. Handle errors and timeouts

**Git Operations** (leveraging GitPython):
```
RepoManager(path)
├── clone(url, branch) → Repo           # Repo.clone_from()
├── fetch(remote=None) → FetchInfo[]    # remote.fetch()
├── pull() → PullInfo | raises UnsafeError  # origin.pull()
├── get_current_branch() → str | None   # repo.active_branch.name
├── get_remotes() → list[str]           # [r.name for r in repo.remotes]
├── is_clean() → bool                   # not repo.is_dirty()
├── has_staged_changes() → bool         # len(repo.index.diff("HEAD")) > 0
├── has_modified_files() → bool         # len(repo.index.diff(None)) > 0
├── is_rebasing() → bool                # check .git/rebase-merge or rebase-apply
├── is_merging() → bool                 # repo.git.merge("--head")? or .git/MERGE_HEAD
├── is_cherry_picking() → bool          # check .git/CHERRY_PICK_HEAD
├── is_detached() → bool                # repo.head.is_detached
├── get_ahead_behind(remote, branch) → tuple[int, int]  # repo.iter_commits()
└── exists() → bool                     # path.exists() and Repo(path)
```

#### Step 3.2: Safety Checks

**Implementation**:
1. Create `SafetyChecker` class
2. Check all conditions before pull:
   - Current branch matches expected branch
   - No staged changes
   - No modified tracked files
   - Not in rebase/merge/cherry-pick
   - Not in detached HEAD
   - Not ahead of remote (unpushed commits)
3. Return detailed safety report

**Safety Check Results**:
```
SafetyReport
├── safe_to_pull: bool
├── reasons: list[str]  # Why not safe
├── current_branch: str
├── expected_branch: str
├── is_clean: bool
├── is_ahead: bool
├── in_progress_operation: str | None
└── is_detached: bool
```

#### Step 3.3: Retry Logic

**Implementation**:
1. Implement exponential backoff for network operations
2. Track per-remote error state
3. Reset backoff when errors stop
4. Configurable max retries and base delay

**Validation Checkpoint**:
```bash
# Test with a real repo
cd /tmp
git clone https://github.com/octocat/Hello-World.git
uv run python -c "
from repo_sync_kitty.git import RepoManager
mgr = RepoManager('/tmp/Hello-World')
print(f'Branch: {mgr.get_current_branch()}')
print(f'Clean: {mgr.is_clean()}')
print(f'Remotes: {mgr.get_remotes()}')
print(f'Detached: {mgr.is_detached()}')
"
```

**Deliverables**:
- [x] RepoManager class with all operations
- [x] Safety checks implemented
- [x] Retry with exponential backoff
- [x] Timeout handling
- [x] Unit tests with mocked GitPython (38 git tests)
- [x] Integration test with real repo

**User Validated**: [x]

---

### Phase 4: Core Commands (sync, status)

**Goal**: Implement the main sync and status commands with full functionality.

#### Step 4.1: Status Command

**Implementation**:
1. Load manifest and scan root directory
2. Compare manifest projects vs disk state
3. For each project, gather:
   - Present/missing status
   - Current branch vs expected
   - Clean/dirty state
   - Ahead/behind remote
4. Terse mode: only show repos with issues
5. Verbose mode: show all repos
6. Handle --show-deleted flag
7. Warn about extra repos not in manifest

**Status Output (Terse)**:
```
repo-sync-kitty status

 Repository Status
┌──────────────────┬──────────┬────────────┬─────────────┐
│ Path             │ Status   │ Branch     │ Issues      │
├──────────────────┼──────────┼────────────┼─────────────┤
│ libs/linkml      │ missing  │ -          │ not cloned  │
│ infra/global-dev │ dirty    │ develop    │ 2 modified  │
│ tools/old        │ extra    │ main       │ not in manifest │
└──────────────────┴──────────┴────────────┴─────────────┘

3 issues found. Run 'repo-sync-kitty sync' to resolve.
```

#### Step 4.2: Sync Command

**Implementation**:
1. Load manifest
2. Create thread pool with configured parallelism
3. For each active project:
   - If missing: clone
   - If present: fetch all remotes
   - If safe: pull
   - If not safe: warn
4. Show progress bar (% complete)
5. Handle --fetch-only, --clone-only, --pull flags
6. Handle --dry-run
7. Collect and report errors at end
8. Exit non-zero if any failures

**Sync Flow**:
```
For each project (parallel):
├── Check if directory exists
│   ├── No → Clone (if not --fetch-only)
│   └── Yes → Continue
├── Fetch all remotes
├── Check safety
│   ├── Safe → Pull (unless --fetch-only)
│   └── Unsafe → Warn, skip pull
└── Report result
```

#### Step 4.3: Parallel Execution

**Implementation**:
1. Use ThreadPoolExecutor with max_workers from config
2. Implement per-repo timeout
3. Ensure slow repos don't block others
4. Aggregate results after all complete

**Validation Checkpoint**:
```bash
# Create a test manifest with real repos
cat > ~/test-manifest.toml << 'EOF'
[common]
root_path = "~/Projects/sync-test"
branch = "main"
remote = "ghpub"
parallelism = 2

[[remotes]]
name = "ghpub"
base_url = "https://github.com/"

projects = [
  { slug = "octocat/Hello-World", path = "hello-world" },
  { slug = "octocat/Spoon-Knife", path = "spoon-knife" },
]
EOF

# Test status (repos don't exist yet)
uv run repo-sync-kitty status -m ~/test-manifest.toml

# Test sync dry-run
uv run repo-sync-kitty sync -m ~/test-manifest.toml --dry-run

# Test actual sync
uv run repo-sync-kitty sync -m ~/test-manifest.toml

# Test status again
uv run repo-sync-kitty status -m ~/test-manifest.toml
```

**Deliverables**:
- [x] `status` command working (terse/verbose)
- [x] `sync` command clones missing repos
- [x] `sync` command fetches existing repos
- [x] `sync` command pulls when safe
- [x] Progress bar shows during sync
- [x] Parallel execution works
- [x] Retry logic works
- [x] --dry-run works
- [x] Error summary at end
- [x] Tests for sync scenarios

**User Validated**: [x]

---

### Phase 5: Secondary Commands (init, add, check, scan)

**Goal**: Implement helper commands for manifest management.

#### Step 5.1: Init Command

**Implementation**:
1. Create empty manifest template
2. With --scan-dir: scan directory for existing repos, add to manifest
3. With --scan-forge: scan remote forge, list available repos
4. Write manifest.toml to current directory or specified path

**Init Modes**:
```
repo-sync-kitty init                    # Create empty template
repo-sync-kitty init --scan-dir ./      # Scan dir, generate manifest
repo-sync-kitty init --scan-forge github --org linkml  # Scan GitHub org
```

#### Step 5.2: Add Command

**Implementation**:
1. Load existing manifest
2. Add new project entry with specified remote and slug
3. Compute path from slug if not specified
4. Validate remote exists
5. Write updated manifest

**Add Usage**:
```
repo-sync-kitty add ghpub linkml/linkml                    # Uses slug as path
repo-sync-kitty add ghpub linkml/linkml --path libs/linkml # Custom path
repo-sync-kitty add mine infra --branch develop            # Custom branch
```

#### Step 5.3: Scan Command

**Implementation**:
1. Connect to forge API (GitHub, GitLab, Bitbucket)
2. List repos in org/user
3. Filter by visibility if token provided
4. Output list for user review
5. Optionally add to manifest with --add flag

**Forge Modules**:
```
forge/
├── base.py      # Abstract ForgeClient
├── github.py    # GitHub API (repos endpoint)
├── gitlab.py    # GitLab API
└── bitbucket.py # Bitbucket API
```

**Validation Checkpoint**:
```bash
# Test init
mkdir /tmp/init-test && cd /tmp/init-test
uv run repo-sync-kitty init
cat manifest.toml

# Test init with dir scan
cd ~/Projects/existing-repos
uv run repo-sync-kitty init --scan-dir .

# Test add
uv run repo-sync-kitty add ghpub octocat/Hello-World -m manifest.toml

# Test scan (public repos, no token needed)
uv run repo-sync-kitty scan ghpub --org octocat
```

**Deliverables**:
- [x] `init` creates template
- [x] `init --scan-dir` discovers repos
- [x] `init --scan-forge` lists remote repos (GitHub only)
- [x] `add` adds project to manifest
- [x] `scan` lists repos from forges
- [x] `scan --add` and `--missing` flags for manifest comparison
- [x] GitHub support (GitLab/Bitbucket stubs only)
- [x] Tests for each command

**User Validated**: [x]

---

### Phase 6: Polish & Production Readiness

**Goal**: Final documentation, integration tests, and production hardening.

#### Step 6.1: Documentation

**Implementation**:
1. Write comprehensive README.md
2. Document all commands and options
3. Provide example manifests
4. Add troubleshooting section

#### Step 6.2: Integration Tests

**Implementation**:
1. Add integration tests with real repos (GitHub public repos)
2. Test full sync workflow end-to-end
3. Test error scenarios (network failures, invalid repos)
4. Validate coverage still meets 80%+ threshold

#### Step 6.3: Final Validation

**Implementation**:
1. Add pre-commit hooks for project
2. Final linting and type checking pass
3. Test installation from clean environment

**Validation Checkpoint**:
```bash
# Run full test suite with integration tests
uv run pytest --cov=repo_sync_kitty --cov-report=term-missing

# Verify coverage threshold
uv run pytest --cov=repo_sync_kitty --cov-fail-under=80

# Run linters
uv run ruff check .
uv run mypy src/

# Test installation
uv pip install .
repo-sync-kitty --version
repo-sync-kitty --help
```

**Deliverables**:
- [x] README.md complete (448 lines, all commands documented)
- [x] Integration tests passing (test_integration.py - 13 tests)
- [ ] 75%+ test coverage maintained (currently at 54% - needs work)
- [x] All linters pass (ruff, mypy)
- [x] Tool installable and working

**User Validated**: [x] (except coverage)

---

### Phase 7: Extended Commands (Bonus Features)

**Goal**: Additional utility commands beyond original scope for enhanced workflow support.

These commands were added to support migration from git-repo and improve daily workflow:

#### Step 7.1: import-repo Command
- [x] Parse git-repo XML manifest format
- [x] Convert to repo-sync-kitty TOML format
- [x] Handle multiple remotes and branch overrides
- [x] Strip .git suffix from project names

#### Step 7.2: fix-detached Command
- [x] Detect detached HEAD states
- [x] Safely check out branch if HEAD is at branch tip
- [x] Abort if repo has loose files
- [x] Parallel execution with progress bar

#### Step 7.3: find-orphans Command
- [x] Scan directory for git repos
- [x] Compare against manifest
- [x] Report repos not in manifest

#### Step 7.4: move Command
- [x] Move repository to new path
- [x] Update manifest with new path
- [x] Preserve symlinks (.git in git-repo setups)
- [x] Handle slug attribute changes

#### Step 7.5: open Command
- [x] Construct web URL from remote base_url
- [x] Open repo in default browser
- [x] Work with repos not in manifest

**Deliverables**:
- [x] `import-repo` command working
- [x] `fix-detached` command working
- [x] `find-orphans` command working
- [x] `move` command working
- [x] `open` command working
- [ ] Tests for extended commands (low coverage: 5-10% for move, open, find-orphans, fix-detached)

**User Validated**: [x] (functionality works, tests needed)

---

## Example Manifest

```toml
[common]
root_path = "~/Projects/my-team"
branch = "main"
remote = "mine"
parallelism = 4
log_level = "info"
timeout = 300
ignore_extra = ["scratch", "tmp"]

# Compact one-line format for simple remotes
[remotes]
ghpub = { base_url = "https://github.com/" }
gitlab = { base_url = "https://gitlab.com/", branch = "master" }

# Expanded format for remotes with more options
[remotes.mine]
base_url = "ssh://git@github.com/vladistan/"
branch = "develop"
parallelism = 2
timeout = 600

# Compact one-line format for most projects
[projects]
"libs/linkml-runtime" = { slug = "linkml/linkml-runtime", remote = "ghpub" }
"infra/global" = { slug = "infra" }
"infra/global-dev" = { slug = "infra", branch = "feature" }
"archive/old-tool" = { slug = "old-tool", status = "archived" }
"libs/deprecated" = { slug = "deprecated-lib", status = "deleted" }

# Expanded format for projects with more options
[projects."libs/linkml"]
slug = "linkml/linkml"
remote = "ghpub"
branch = "main"
```

## Command Reference

| Command | Description |
|---------|-------------|
| `init` | Create new manifest (template, scan dir, scan forge) |
| `sync` | Clone missing, fetch/pull existing repos |
| `status` | Show repository sync status |
| `add` | Add repository to manifest |
| `check` | Validate manifest file |
| `scan` | List repos from remote forge |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | One or more operations failed |
| 2 | Invalid manifest or configuration |
| 3 | Network/authentication error |
