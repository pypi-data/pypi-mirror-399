# Getting Started with VibeGate

**Get from zero to your first quality check in under 5 minutes.**

## Install

```bash
pip install vibegate
```

For all quality tools bundled:

```bash
pip install "vibegate[tools]"
```

## Quick Start

Run VibeGate on your Python project:

```bash
vibegate run .
```

This one command:
- Checks if you have required tools installed
- Runs all enabled quality checks
- Creates reports in plain English
- Shows you exactly what needs fixing

**Default behavior:**
- Works without config (uses balanced profile)
- Outputs go to `.vibegate/` directory
- Auto-opens web viewer in interactive mode

## View Results

VibeGate creates several outputs:

| File | What It Is |
|------|------------|
| `.vibegate/plain_report.md` | Friendly summary in plain English |
| `.vibegate/artifacts/vibegate_report.md` | Technical details with file paths and line numbers |
| `.vibegate/artifacts/fixpack.json` | Machine-readable action plan |
| `.vibegate/agent_prompt.md` | Instructions for AI coding assistants |
| `.vibegate/evidence/vibegate.jsonl` | Complete audit trail |

**To view results in the web UI:**

```bash
pip install "vibegate[ui]"
vibegate view .
```

Opens at `http://127.0.0.1:8787` with:
- Friendly and technical reports
- Run history and comparison
- Interactive findings browser

## Profiles

VibeGate includes built-in profiles for different scenarios:

**balanced** (default)
- Comprehensive checks without being overwhelming
- Outputs: `.vibegate/` directory
- Good for: Local development

**fast**
- Quick feedback, skips slow checks (tests, typecheck)
- Outputs: `.vibegate/` directory
- Good for: Pre-commit hooks

**strict**
- Maximum checks, including security scanning
- Outputs: `.vibegate/` directory
- Good for: Release validation

**ci**
- Optimized for continuous integration
- Outputs: `artifacts/` and `evidence/` (easier for CI artifact upload)
- Good for: GitHub Actions, GitLab CI, etc.

**Using a profile:**

```bash
vibegate run . --profile fast
vibegate run . --profile strict
vibegate run . --profile ci
```

## Using in CI

### GitHub Actions

```yaml
name: Quality Gate

on: [push, pull_request]

jobs:
  vibegate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install VibeGate
        run: pipx install "vibegate[tools]"

      - name: Run quality gate
        run: vibegate run . --profile ci

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: vibegate-reports
          path: |
            artifacts/
            evidence/
```

**Exit codes:**
- `0` = PASS (all checks passed)
- `1` = FAIL (blocking issues found)
- `2` = CONFIG ERROR (invalid configuration)

### Where Outputs Go

**Default profiles (balanced, fast, strict):**
- Reports: `.vibegate/artifacts/`
- Evidence: `.vibegate/evidence/`
- Plain report: `.vibegate/plain_report.md`

**CI profile:**
- Reports: `artifacts/`
- Evidence: `evidence/`
- Plain report: `artifacts/plain_report.md`

This makes CI artifact upload simpler since paths don't start with `.`

## Common Errors

### Missing Tools

**Error:**
```
Missing required tools:
- ruff
- pyright
- pytest
```

**Solution:**

```bash
# Install all tools at once
pip install "vibegate[tools]"

# Or install individually
pip install ruff pyright pytest

# For security tools
brew install gitleaks  # macOS
# See: https://github.com/gitleaks/gitleaks#installation
```

**Check what's missing:**

```bash
vibegate doctor .
```

Shows which tools are missing and how to install them.

### Config Validation Failed

**Error:**
```
Configuration error: Invalid vibegate.yaml
```

**Solution:**

```bash
# Overwrite with fresh defaults
vibegate init . --force

# Or delete and recreate
rm vibegate.yaml
vibegate init .
```

### No Findings But Still Failing

Check `.vibegate/suppressions.yaml` - you may have expired suppressions that need updating.

## Next Steps

- **Customize checks:** Edit `vibegate.yaml` (or create with `vibegate init .`)
- **Suppress findings:** Add to `.vibegate/suppressions.yaml`
- **Track false positives:** Use `vibegate label <fingerprint> --false-positive --reason <tag>`
- **Explore findings:** `vibegate view .` for the web UI
- **Read the docs:** `README.md` and `docs/` directory

## Quick Commands Reference

```bash
vibegate run .              # Run all checks (recommended)
vibegate run . --profile ci # Use CI profile
vibegate doctor .           # Check for missing tools
vibegate view .             # Open web UI
vibegate init .             # Create vibegate.yaml
vibegate clean . --dry-run  # Preview cleanup (safe)
vibegate --help             # Show all commands
```

## Need Help?

- **Documentation:** `README.md` and `docs/` directory
- **Issues:** https://github.com/maxadamsky/VibeGate/issues
- **Architecture:** `docs/ARCHITECTURE.md`
- **Plugin development:** `docs/PLUGINS.md`
