# VibeGate Demo Check Pack

This is a demonstration check pack showing how to create bundled checks for VibeGate using the CheckPack API.

## What This Demonstrates

This pack shows three different check patterns:

1. **TodoFinderCheck** - Regex-based check
   - Scans for TODO/FIXME/XXX comments
   - Shows simple pattern matching
   - Demonstrates fingerprint generation

2. **PrintStatementCheck** - AST-based check
   - Parses Python AST to find print() calls
   - Shows how to walk the AST
   - Demonstrates error handling for parse failures

3. **LongLineCheck** - Configurable check
   - Finds lines exceeding max length
   - Shows parameterized checks
   - Demonstrates simple line-by-line scanning

## Installation

### For Development

```bash
# From this directory
pip install -e .
```

### For Production

```bash
pip install vibegate-demo-pack
```

## Usage

After installation, the pack is automatically discovered by VibeGate:

```bash
# List all available packs (should show demo-pack)
vibegate plugins list

# Verify the pack loads correctly
vibegate plugins doctor

# Run checks (demo pack will be included automatically)
vibegate run . --no-view
```

**Note**: Legacy hyphenated commands (`plugins-list`, `plugins-doctor`) are still supported for backward compatibility.

## Pack Structure

```
demo-pack/
├── pyproject.toml                # Package metadata and entry points
├── README.md                     # This file
└── src/
    └── vibegate_demo_pack/
        ├── __init__.py
        ├── pack.py               # CheckPack implementation
        └── checks/
            ├── __init__.py
            ├── todo_finder.py    # Regex-based check
            ├── print_statement.py # AST-based check
            └── long_line.py      # Configurable check
```

## Key Concepts

### CheckPack Protocol

The pack implements the `CheckPack` protocol by providing:

1. **metadata property** - Returns `CheckPackMetadata` with pack info
2. **register_checks() method** - Returns list of check plugin instances

```python
class DemoCheckPack:
    @property
    def metadata(self) -> CheckPackMetadata:
        return CheckPackMetadata(
            pack_id="demo-pack",
            pack_name="Demo Check Pack",
            description="...",
            version="1.0.0",
            author="VibeGate Team",
            tags=["demo", "example"],
        )

    def register_checks(self) -> Sequence[CheckPlugin]:
        return [
            TodoFinderCheck(),
            PrintStatementCheck(),
            LongLineCheck(max_length=120),
        ]
```

### Entry Point Registration

The pack is registered via setuptools entry point in `pyproject.toml`:

```toml
[project.entry-points."vibegate.checkpacks"]
demo = "vibegate_demo_pack.pack:DemoCheckPack"
```

The entry point group **must** be `vibegate.checkpacks` for check packs.

### Check Plugin Interface

Each check implements the `CheckPlugin` protocol:

```python
class MyCheck:
    def run(self, context: PluginContext) -> Sequence[Finding]:
        # Scan files, run tools, analyze code
        findings = []

        for file_path in context.workspace_files:
            # Check logic here
            pass

        return findings
```

## Extending This Pack

To add your own checks:

1. Create a new check file in `src/vibegate_demo_pack/checks/`
2. Implement the `CheckPlugin` protocol
3. Add the check to `register_checks()` in `pack.py`
4. Update version in `pyproject.toml`

## Example Output

When run on a Python project with TODOs and print statements:

```
Check Packs:
  • demo: Demo Check Pack v1.0.0 (3 checks)
    Demonstration check pack showing VibeGate plugin patterns
    Author: VibeGate Team
    Tags: demo, example, code-quality
```

And in the findings report:

```
[INFO] demo-pack.todo-finder: TODO(alice): Refactor this function
  Location: src/main.py:42

[INFO] demo-pack.print-statement: Use logging instead of print() for production code
  Location: src/debug.py:15

[INFO] demo-pack.long-line: Line exceeds 120 characters (currently 145)
  Location: src/utils.py:89
```

## Next Steps

- See `docs/PLUGINS.md` for comprehensive plugin development guide
- Check `examples/hello-plugin/` for simpler individual plugin example
- Review core checks in `src/vibegate/checks.py` for more patterns

## License

MIT - Same as VibeGate
