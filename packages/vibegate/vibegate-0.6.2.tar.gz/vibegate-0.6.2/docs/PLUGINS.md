# VibeGate Plugins and Check Packs

VibeGate supports a flexible plugin system that allows you to extend its functionality without modifying the core codebase. This guide explains how to create, package, and publish your own check packs and plugins.

## Overview

VibeGate supports three types of plugins:

1. **Check Packs** - Bundles of related checks that can be installed and used as a group
2. **Check Plugins** - Individual check implementations
3. **Emitter Plugins** - Custom report/artifact generators

This guide focuses primarily on **Check Packs**, as they provide the easiest way to add and distribute multiple related checks.

## Check Packs vs Individual Plugins

### When to Use Check Packs

Use check packs when you want to:
- Bundle multiple related checks together (e.g., "AWS Security Pack", "Django Best Practices Pack")
- Distribute a cohesive set of checks as a single installable package
- Provide versioned metadata and documentation for your checks
- Make it easy for users to enable/disable all related checks at once

### When to Use Individual Check Plugins

Use individual check plugins when you:
- Have a single, standalone check
- Want maximum flexibility in plugin registration
- Need to integrate with existing check infrastructure

## Creating a Check Pack

### 1. Basic Structure

A check pack is a Python class that implements the `CheckPack` protocol:

```python
from vibegate.plugins import CheckPack, CheckPackMetadata, CheckPlugin, PluginContext, Finding
from typing import Sequence

class MyAwesomePack:
    """My awesome check pack with related security checks."""

    @property
    def metadata(self) -> CheckPackMetadata:
        return CheckPackMetadata(
            pack_id="awesome-pack",
            pack_name="Awesome Security Pack",
            description="A collection of awesome security checks",
            version="1.0.0",
            author="Your Name",
            tags=["security", "best-practices"],
        )

    def register_checks(self) -> Sequence[CheckPlugin]:
        """Return all checks provided by this pack."""
        return [
            SecretLeakCheck(),
            InsecureConfigCheck(),
            DangerousImportCheck(),
        ]
```

### 2. Implementing Individual Checks

Each check in your pack should implement the `CheckPlugin` protocol:

```python
class SecretLeakCheck:
    """Check for hardcoded secrets in configuration files."""

    def run(self, context: PluginContext) -> Sequence[Finding]:
        findings = []

        # Scan workspace files for secrets
        for file_path in context.workspace_files:
            if file_path.suffix not in [".py", ".yaml", ".json"]:
                continue

            try:
                content = file_path.read_text()
            except Exception:
                continue

            # Look for patterns like API_KEY = "sk-..."
            import re
            pattern = r'(API_KEY|SECRET|PASSWORD)\s*=\s*["\']([^"\']+)["\']'

            for match in re.finditer(pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                findings.append(
                    Finding(
                        check_id="awesome-pack.secret-leak",
                        finding_type="security",
                        rule_id="HARDCODED_SECRET",
                        severity="critical",
                        message=f"Hardcoded secret found: {match.group(1)}",
                        fingerprint=self._compute_fingerprint(file_path, line_number),
                        confidence="high",
                        remediation_hint="Move secrets to environment variables or secret management system",
                        location=FindingLocation(
                            path=str(file_path.relative_to(context.repo_root)),
                            line=line_number,
                        ),
                    )
                )

        return findings

    def _compute_fingerprint(self, path, line):
        import hashlib
        key = f"{path}:{line}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
```

### 3. Using the PluginContext

The `PluginContext` provides access to:

```python
@dataclass(frozen=True)
class PluginContext:
    repo_root: Path              # Root of the repository being checked
    config: VibeGateConfig       # Full VibeGate configuration
    workspace_files: Sequence[Path]  # All files in scope (respects .gitignore)
    tool_runner: ToolRunner      # Helper to run external tools
    logger: logging.Logger       # Logger for diagnostic messages
    evidence: EvidenceWriter     # Evidence recording (optional)
```

**Example: Running external tools**

```python
def run(self, context: PluginContext) -> Sequence[Finding]:
    # Run an external tool (e.g., custom linter)
    result = context.tool_runner(
        tool="my-custom-linter",
        args=["--json", str(context.repo_root)],
        cwd=context.repo_root,
        timeout=60,
        env={},
    )

    if result.exit_code != 0:
        context.logger.warning(f"Tool failed: {result.stderr}")
        return []

    # Parse output and create findings
    import json
    issues = json.loads(result.stdout)
    return self._convert_to_findings(issues)
```

### 4. Package Structure

Create a standard Python package structure:

```
my-awesome-pack/
├── pyproject.toml
├── README.md
├── src/
│   └── vibegate_awesome_pack/
│       ├── __init__.py
│       ├── pack.py          # CheckPack implementation
│       └── checks/
│           ├── __init__.py
│           ├── secret_leak.py
│           ├── insecure_config.py
│           └── dangerous_import.py
└── tests/
    └── test_checks.py
```

### 5. Entry Point Registration

Register your check pack in `pyproject.toml`:

```toml
[project]
name = "vibegate-awesome-pack"
version = "1.0.0"
description = "Awesome security checks for VibeGate"
requires-python = ">=3.10"
dependencies = [
    "vibegate>=0.4.0",
]

[project.entry-points."vibegate.checkpacks"]
awesome = "vibegate_awesome_pack.pack:MyAwesomePack"
```

**Important**: The entry point group must be `vibegate.checkpacks` for check packs.

## Publishing Your Check Pack

### 1. Prepare for Release

Ensure your package includes:
- Clear README with usage instructions
- License file (MIT recommended for compatibility)
- Version number following semantic versioning
- Tests for your checks
- Example configuration snippets

### 2. Build the Package

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# This creates:
# - dist/vibegate_awesome_pack-1.0.0-py3-none-any.whl
# - dist/vibegate_awesome_pack-1.0.0.tar.gz
```

### 3. Publish to PyPI

```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Then publish to real PyPI
twine upload dist/*
```

### 4. Usage Instructions

After publishing, users can install your pack with:

```bash
pip install vibegate-awesome-pack
```

Then run:

```bash
# List available packs (should show your pack)
vibegate plugins list

# Verify it loads correctly
vibegate plugins doctor

# Run checks (your pack will be auto-discovered)
vibegate run .
```

**Note**: Legacy hyphenated commands (`plugins-list`, `plugins-doctor`) are still supported for backward compatibility.

## Advanced Features

### Configuration Support

Check packs can accept configuration via the pack metadata:

```python
class ConfigurablePack:
    def __init__(self, severity_threshold: str = "medium"):
        self.severity_threshold = severity_threshold

    @property
    def metadata(self) -> CheckPackMetadata:
        return CheckPackMetadata(
            pack_id="configurable-pack",
            pack_name="Configurable Pack",
            description=f"Pack with {self.severity_threshold} severity threshold",
            version="1.0.0",
        )

    def register_checks(self) -> Sequence[CheckPlugin]:
        return [
            SeverityAwareCheck(self.severity_threshold),
        ]
```

### AST-Based Checks

Use Python's `ast` module for sophisticated code analysis:

```python
import ast
from vibegate.plugins import Finding, FindingLocation

class DangerousImportCheck:
    """Detect imports of dangerous modules."""

    DANGEROUS_MODULES = {"pickle", "marshal", "shelve", "exec", "eval"}

    def run(self, context: PluginContext) -> Sequence[Finding]:
        findings = []

        for file_path in context.workspace_files:
            if file_path.suffix != ".py":
                continue

            try:
                tree = ast.parse(file_path.read_text(), filename=str(file_path))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.DANGEROUS_MODULES:
                            findings.append(self._create_finding(
                                file_path, node, alias.name, context
                            ))
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.DANGEROUS_MODULES:
                        findings.append(self._create_finding(
                            file_path, node, node.module, context
                        ))

        return findings

    def _create_finding(self, path, node, module_name, context):
        return Finding(
            check_id="awesome-pack.dangerous-import",
            finding_type="security",
            rule_id="DANGEROUS_IMPORT",
            severity="high",
            message=f"Import of dangerous module '{module_name}'",
            fingerprint=self._fingerprint(path, node.lineno),
            ast_node_type=type(node).__name__,
            location=FindingLocation(
                path=str(path.relative_to(context.repo_root)),
                line=node.lineno,
                col=node.col_offset,
            ),
        )
```

### Multi-File Analysis

Analyze relationships across multiple files:

```python
class ImportCycleCheck:
    """Detect circular imports."""

    def run(self, context: PluginContext) -> Sequence[Finding]:
        # Build import graph
        import_graph = self._build_import_graph(context.workspace_files)

        # Detect cycles
        cycles = self._find_cycles(import_graph)

        # Create findings for each cycle
        findings = []
        for cycle in cycles:
            findings.append(
                Finding(
                    check_id="awesome-pack.import-cycle",
                    finding_type="maintainability",
                    rule_id="CIRCULAR_IMPORT",
                    severity="medium",
                    message=f"Circular import detected: {' -> '.join(cycle)}",
                    fingerprint=self._fingerprint(cycle),
                )
            )

        return findings
```

## Testing Your Check Pack

### Unit Tests

```python
# tests/test_checks.py
from pathlib import Path
from vibegate.plugins import PluginContext
from vibegate_awesome_pack.checks.secret_leak import SecretLeakCheck

def test_secret_leak_detection(tmp_path):
    # Create test file with secret (example, not real)
    test_file = tmp_path / "config.py"
    test_file.write_text('API_KEY = "sk-test-fake-key-example"')  # gitleaks:allow

    # Mock context
    class MockConfig:
        pass

    context = PluginContext(
        repo_root=tmp_path,
        config=MockConfig(),
        workspace_files=[test_file],
        tool_runner=lambda *args, **kwargs: None,
        logger=logging.getLogger("test"),
        evidence=None,
    )

    # Run check
    check = SecretLeakCheck()
    findings = check.run(context)

    # Verify
    assert len(findings) == 1
    assert findings[0].rule_id == "HARDCODED_SECRET"
    assert findings[0].severity == "critical"
```

### Integration Tests

```bash
# Test with real VibeGate
cd test-project/
pip install -e /path/to/my-awesome-pack
vibegate plugins doctor
vibegate run .
```

## Best Practices

### 1. Naming Conventions

- **Pack ID**: Use kebab-case (e.g., `aws-security`, `django-best-practices`)
- **Check IDs**: Prefix with pack ID (e.g., `aws-security.s3-public-access`)
- **Rule IDs**: Use SCREAMING_SNAKE_CASE (e.g., `S3_PUBLIC_BUCKET`)

### 2. Fingerprinting

Always generate stable fingerprints for findings:

```python
import hashlib

def _fingerprint(self, file_path: Path, line: int, rule_id: str) -> str:
    """Generate stable fingerprint for finding."""
    # Use file path + line + rule to ensure uniqueness
    key = f"{file_path}:{line}:{rule_id}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]
```

### 3. Severity Guidelines

- **critical**: Security vulnerabilities, data leaks, critical bugs
- **high**: Major security issues, significant bugs, policy violations
- **medium**: Code quality issues, minor security concerns, deprecations
- **low**: Style issues, optimization opportunities, suggestions
- **info**: Informational notices, documentation suggestions

### 4. Remediation Hints

Always provide actionable remediation guidance:

```python
Finding(
    # ...
    remediation_hint=(
        "Move API keys to environment variables:\n"
        "1. Store in .env file (add to .gitignore)\n"
        "2. Load with python-dotenv: load_dotenv()\n"
        "3. Access with os.getenv('API_KEY')"
    ),
)
```

### 5. Performance

- Filter `workspace_files` early to avoid processing irrelevant files
- Use caching for expensive operations
- Set reasonable timeouts for external tools
- Log performance metrics for optimization

```python
def run(self, context: PluginContext) -> Sequence[Finding]:
    import time
    start = time.time()

    # Filter files early
    py_files = [f for f in context.workspace_files if f.suffix == ".py"]

    findings = self._analyze_files(py_files)

    elapsed = time.time() - start
    context.logger.info(f"Analyzed {len(py_files)} files in {elapsed:.2f}s")

    return findings
```

### 6. Error Handling

Handle errors gracefully - don't crash the entire check run:

```python
def run(self, context: PluginContext) -> Sequence[Finding]:
    findings = []

    for file_path in context.workspace_files:
        try:
            findings.extend(self._check_file(file_path))
        except Exception as exc:
            context.logger.warning(
                f"Failed to check {file_path}: {exc}"
            )
            # Continue with other files
            continue

    return findings
```

## Example: Complete Check Pack

See the full example in `examples/security-pack/`:

```bash
examples/security-pack/
├── pyproject.toml
├── README.md
├── src/
│   └── vibegate_security_pack/
│       ├── __init__.py
│       ├── pack.py
│       └── checks/
│           ├── __init__.py
│           ├── hardcoded_secrets.py
│           ├── sql_injection.py
│           └── insecure_crypto.py
└── tests/
    └── test_security_checks.py
```

## Troubleshooting

### Pack Not Showing in `plugins list`

1. Verify entry point is registered correctly in `pyproject.toml`
2. Check group name is exactly `vibegate.checkpacks`
3. Reinstall package: `pip install -e .` (for local dev)
4. Run `vibegate plugins doctor` to see detailed errors

### Pack Loads but No Checks Run

1. Verify `register_checks()` returns non-empty list
2. Check each check implements `run(context)` method
3. Look for errors in logs (run with `--verbose`)

### Findings Not Appearing in Report

1. Verify `Finding` objects have all required fields
2. Check fingerprints are being generated
3. Ensure `check_id` follows naming convention
4. Verify findings aren't being suppressed in `suppressions.yaml`

## Resources

- **VibeGate Plugin API**: `src/vibegate/plugins/api.py`
- **Example Plugins**: `examples/hello-plugin/`
- **Core Checks**: `src/vibegate/checks.py` (for patterns/reference)
- **Finding Schema**: `src/vibegate/findings.py`

## Contributing

If you create a useful check pack, consider:
1. Publishing to PyPI for community use
2. Adding to the [VibeGate ecosystem list](https://github.com/maxadamsky/VibeGate/wiki/Ecosystem)
3. Sharing on the discussion forum
4. Contributing back to core if widely applicable

---

**Questions?** Open an issue at https://github.com/maxadamsky/VibeGate/issues
