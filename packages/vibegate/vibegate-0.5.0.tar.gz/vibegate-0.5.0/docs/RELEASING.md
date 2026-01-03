# Releasing VibeGate

This document describes how to release new versions of VibeGate.

## Overview

VibeGate uses **automated semantic versioning** for releases based on conventional commits:

1. **Use conventional commits** - All commits follow conventional commits format
2. **Merge to main** - When PRs are merged, commits are analyzed
3. **Automated release** - semantic-release determines version, updates CHANGELOG, creates tag, and publishes
4. **No manual version bumping** - Everything is automated based on commit history

## Quick Pre-Release Checklist

Before merging a PR that will trigger a release:

- [ ] All CI checks are passing (tests, lint, type check, vibegate)
- [ ] Commit messages follow conventional commits format (`feat:`, `fix:`, etc.)
- [ ] PyPI Trusted Publisher is configured (one-time setup, see below)
- [ ] GitHub environment `pypi` exists (one-time setup, see below)
- [ ] GitHub secret `RELEASE_PAT` is configured (one-time setup, required for branch protection bypass)

**That's it!** Merge the PR and semantic-release handles the rest automatically.

## Before You Merge the Release PR

Before merging a PR that will trigger a release, run the local pre-release verification:

```bash
make release-check
```

This single command runs both the pre-release checklist and the release candidate smoke test. For manual control, you can also run the individual scripts:

### 1. Pre-release Checklist

```bash
python scripts/pre_release_check.py
```

This script validates:
1. ✅ Git working tree is clean (no uncommitted changes)
2. ✅ Unit tests pass (`pytest`)
3. ✅ VibeGate run passes on itself (`vibegate run .`)
4. ✅ Package builds successfully (`python -m build`)
5. ✅ Package passes twine validation (`twine check dist/*`)

### 2. Release Candidate Smoke Test

```bash
make rc-smoke
# Or: python scripts/rc_smoke.py
```

This script validates profile behavior by:
1. 🧪 Creating a temporary test project with intentional issues
2. 🧪 Running `vibegate run` with `--profile fast`
3. 🧪 Running `vibegate run` with `--profile balanced` (validates `.vibegate/` output)
4. 🧪 Running `vibegate run` with `--profile ci` (validates `artifacts/` and `evidence/` output)
5. ✅ Ensuring all profiles exit with code 0 or 1 (never 2 for config errors)

**All checks must pass** before merging. The scripts will provide friendly error messages and next steps if any check fails.

Once both scripts pass and CI is green:
- Merge the PR with a conventional commit message
- `semantic-release.yml` will automatically publish to PyPI via Trusted Publisher

## Release Methods

### Method 1: Automated Semantic Release (Recommended)

The recommended way to release VibeGate is through the automated semantic-release workflow.

**How it works:**

- Every push to `main` triggers the semantic-release workflow
- Semantic-release analyzes commits since the last release
- If releasable commits exist (`feat`, `fix`, `perf`, `refactor`), it:
  - Determines the next version (major/minor/patch) based on commit types
  - Updates `pyproject.toml`, `CHANGELOG.md`, and commitizen version
  - Creates and pushes a git tag
  - Builds and publishes to PyPI
  - Creates a GitHub Release with changelog notes

**You do nothing!** Just merge PRs with conventional commit messages.

**Version determination:**

- `feat:` commits → minor version bump (0.1.0 → 0.2.0)
- `fix:`, `perf:`, `refactor:` commits → patch version bump (0.1.0 → 0.1.1)
- `feat!:` or `BREAKING CHANGE:` → major version bump (0.1.0 → 1.0.0)
- Other commits (`docs:`, `chore:`, `ci:`, `test:`) → no release

**Example workflow:**

```bash
# Contributors make changes with conventional commits
git commit -m "feat(cli): add verbose output option"
git commit -m "fix(checks): handle empty pyright output"

# Open PR, get it reviewed and merged to main
# → semantic-release automatically runs
# → Version bumped from 0.1.0a5 to 0.2.0a1
# → CHANGELOG updated
# → Tag v0.2.0a1 created
# → Published to PyPI
# → GitHub Release created
```

### Method 2: Manual Semantic Release

If you need to manually trigger a release:

```bash
# Preview what would be released
semantic-release version --print

# Create release locally (for testing)
semantic-release version --no-push --no-tag

# Or trigger the workflow manually from GitHub Actions
# Go to Actions → "semantic release" → Run workflow
```

### Method 3: Manual Tag Push (Not Recommended)

If absolutely necessary, you can manually create a version tag, but this bypasses all automated version management and is **not recommended**.

```bash
# Manually update version in pyproject.toml and CHANGELOG.md
git add pyproject.toml CHANGELOG.md
git commit -m "chore(release): 0.1.0a6"
git push origin main

# Create and push tag
git tag -a v0.1.0a6 -m "v0.1.0a6"
git push origin v0.1.0a6
```

**Warning:** This method bypasses semantic-release's version calculation and changelog generation. Use only in exceptional circumstances.

## Hotfix Releases

For emergency fixes to a released version:

1. Go to **Actions** → **"hotfix release"** → **Run workflow**
2. Enter the base tag to hotfix (e.g., `v0.1.0a5`)
3. Enter a description of the hotfix
4. The workflow will:
   - Create a hotfix branch from the base tag
   - Increment the version (0.1.0a5 → 0.1.0a6)
   - Update version and CHANGELOG
   - Create a PR for review
5. Review, test, and merge the PR
6. semantic-release will publish the hotfix

**Example:**

```bash
# Input to hotfix workflow:
Base tag: v0.1.0a5
Description: Fix critical bug in check runner

# Workflow creates:
Branch: hotfix/v0.1.0a6
Version: 0.1.0a6
PR: "hotfix: Fix critical bug in check runner (v0.1.0a6)"

# After merge:
→ semantic-release publishes v0.1.0a6
```

## Prerequisites

### Trusted Publishing Setup (One-Time)

VibeGate uses **trusted publishing** (OIDC) to securely publish to PyPI without storing API tokens. This is a one-time setup that enables automatic publishing when semantic-release runs.

**What is trusted publishing?**

Trusted publishing uses OpenID Connect (OIDC) to allow GitHub Actions to authenticate directly with PyPI. No secrets or API tokens are stored in GitHub - PyPI trusts the GitHub workflow based on repository and workflow configuration.

**Setup steps:**

1. **Go to your PyPI project page**: https://pypi.org/manage/project/vibegate/

2. **Navigate to Publishing settings**:
   - Click "Publishing" in the left sidebar
   - Scroll to "Add a new pending publisher"

3. **Configure the trusted publisher**:
   - PyPI Project Name: `vibegate`
   - Owner: `maxadamsky` (or your GitHub username/org)
   - Repository name: `VibeGate`
   - Workflow name: `semantic-release.yml`
   - Environment name: `pypi`

4. **Save the configuration**

5. **Create the GitHub environment** (if not already created):
   - Go to your GitHub repository → Settings → Environments
   - Click "New environment"
   - Name: `pypi`
   - (Optional) Add protection rules like required reviewers for extra safety

**That's it!** When the `semantic-release.yml` workflow runs after commits are merged to main, it will automatically authenticate with PyPI using OIDC and publish the package.

**Security benefits:**
- No API tokens to manage or rotate
- No secrets stored in GitHub
- Scoped to specific workflow and repository
- Automatic authentication per workflow run

### Local Tools

For manual semantic-release operations:

```bash
python -m pip install -e ".[dev]"
```

## CI Sanity Checks

Every pull request and push to main triggers automated CI workflows:

**Tests Job:**
- Runs on Python 3.10, 3.11, and 3.12 (matrix)
- Executes full pytest suite with `-q` (quiet) output
- Ensures cross-version compatibility

**VibeGate Job:**
- Runs `vibegate run .` on Python 3.11
- Generates quality reports and fix pack
- Uploads artifacts to workflow run:
  - `.vibegate/plain_report.md` - Plain text report
  - `.vibegate/agent_prompt.md` - Agent-ready prompt
  - `artifacts/vibegate_report.md` - Formatted markdown report
  - `artifacts/fixpack.json` - Deterministic fix pack
  - `evidence/vibegate.jsonl` - Full evidence ledger
- Displays friendly summary with PASS/FAIL status and issue count

**Viewing Artifacts:**
1. Go to the workflow run in the Actions tab
2. Scroll to the bottom to find "Artifacts"
3. Download `vibegate-artifacts.zip` to inspect reports locally

All CI checks must pass before PRs can be merged.

## Pre-Release Validation

Before any release (automated or manual), these checks run automatically:

```bash
ruff check .           # Linting
ruff format --check .  # Formatting
pyright                # Type checking
pytest                 # Tests
python -m vibegate run .  # Gate the repo with VibeGate
```

All checks must pass before publishing to PyPI.

### Local Build and Smoke Test

To manually validate a release before publishing:

```bash
# 1. Build distribution packages
python -m build

# 2. Check distribution packages
twine check dist/*

# 3. Local smoke test - install from wheel
python -m venv .venv-smoke
source .venv-smoke/bin/activate  # On Windows: .venv-smoke\Scripts\activate
pip install dist/*.whl

# 4. Verify basic functionality
vibegate --help
vibegate --version
vibegate ui --static  # Test UI with static files

# 5. Optional: Test with UI and LLM extras
pip install "dist/*.whl[ui,llm]"
vibegate ui --help

# 6. Cleanup
deactivate
rm -rf .venv-smoke
```

**Note:** OSS documentation and default configurations include local model providers only (Ollama, vLLM, SGLang, etc.). Cloud providers are not included in the open-source version.

## Testing Releases Locally

Before publishing, validate the build locally:

```bash
# Build the package
python -m build

# Install and test locally
python -m venv .venv-test
source .venv-test/bin/activate
pip install dist/*.whl
vibegate --help
vibegate run .
deactivate
rm -rf .venv-test
```

**Note:** TestPyPI publishing requires manual configuration and is not part of the automated workflow.

## Version Format

VibeGate follows [PEP 440](https://peps.python.org/pep-0440/) versioning:

| Format | Example | Use Case |
|--------|---------|----------|
| `X.Y.Z` | `1.0.0` | Stable release |
| `X.Y.ZaN` | `0.1.0a5` | Alpha pre-release |
| `X.Y.ZbN` | `0.1.0b1` | Beta pre-release |
| `X.Y.ZrcN` | `0.1.0rc1` | Release candidate |

## Changelog Format

CHANGELOG.md follows [Keep a Changelog](https://keepachangelog.com/) format and is **automatically updated** by semantic-release:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features (from feat: commits)

### Changed
- Changes to existing features

### Fixed
- Bug fixes (from fix: commits)

### Performance
- Performance improvements (from perf: commits)
```

## What Gets Published

When a release is created via semantic-release:

1. **Quality checks** run (ruff, pyright, pytest, vibegate)
2. **Build artifacts** created (sdist and wheel)
3. **Version verification** - tag matches `pyproject.toml` version
4. **PyPI publish** via Trusted Publisher (OIDC)
5. **GitHub Release** created with:
   - Changelog notes extracted automatically
   - Build artifacts attached
   - Pre-release flag set for alpha/beta/rc versions

**Workflow:**

- `semantic-release.yml` - Automatic version bump, changelog, tag creation, and publishing to PyPI

## Regular VibeGate Evolution

To keep rule quality sharp, run the full evolution loop regularly:

```bash
python -m vibegate evolve .
```

The scheduled **"vibegate evolve"** workflow runs weekly and uploads tuning artifacts.

## Release Drafter

The Release Drafter workflow automatically maintains a draft release with categorized changes from merged PRs. This provides a preview of the next release notes.

View draft releases at: `https://github.com/maxadamsky/VibeGate/releases`

## Troubleshooting

### "No release needed - no version bump"

This means no releasable commits (feat, fix, perf, refactor) were found since the last release. Only commits that don't trigger releases (docs, chore, ci, test) were added.

**Solution:** This is expected behavior. No release is needed.

### "Tag already exists"

You cannot re-release an existing version.

**Solution:**
- For automated releases, this shouldn't happen
- For manual releases, choose a different version number

### "Invalid version format"

Version must match PEP 440: `X.Y.Z` or `X.Y.Z{a|b|rc}N`

**Solution:** Use a valid version format

### "Protected branch update failed"

The workflow cannot push directly to protected branches.

**Solution:**
- Ensure the GitHub token has appropriate permissions
- Check branch protection rules allow the workflow to push

### PyPI publish fails

Common causes:
- Version already exists on PyPI
- Trusted Publisher not configured correctly
- Environment protection rules blocking publish

**Solution:**
- Verify Trusted Publisher configuration
- Check GitHub environment settings
- Ensure version is unique

### Commit message validation fails

PR commits don't follow conventional commits format.

**Solution:**
- Use conventional commit format: `<type>(<scope>): <subject>`
- Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
- Install pre-commit hooks to validate locally

## Rollback

If a bad release is published:

1. **PyPI**: [Yank the release](https://pypi.org/help/#yanked) from PyPI
   ```bash
   pip install twine
   twine upload --repository pypi --skip-existing dist/*
   ```

2. **GitHub**: Delete or edit the GitHub Release

3. **Hotfix**: Use the hotfix workflow to release a fixed version

**Note:** Yanking hides the version from default installs but doesn't delete it. Users can still install yanked versions explicitly.

## Best Practices

1. **Always use conventional commits** - Required for automated releases
2. **Keep commits focused** - One logical change per commit
3. **Write clear commit messages** - They become the changelog
4. **Test before merging** - All CI checks must pass
5. **Use draft releases** - Review the draft release before merging
6. **Hotfixes for emergencies only** - Prefer regular releases when possible
7. **Semantic versioning** - Breaking changes require major version bump

## Additional Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PEP 440 - Version Identification](https://peps.python.org/pep-0440/)
- [python-semantic-release](https://python-semantic-release.readthedocs.io/)
