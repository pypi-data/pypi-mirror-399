# VibeGate Architecture

## Overview

VibeGate is a **deterministic quality orchestrator** with an optional friendly translation layer. This document describes the technical architecture and pipeline.

## High-Level Architecture

```
User runs: vibegate run .
         ↓
┌────────────────────────────────────────────────────────────┐
│                  Configuration Loading                      │
│  - Read vibegate.yaml                                      │
│  - Validate against JSON schema                           │
│  - Apply profile overrides                                │
│  - Load suppressions.yaml                                  │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│              Deterministic Check Pipeline                   │
│                                                            │
│  1. Scan workspace (git ls-files or directory walk)       │
│  2. Run enabled checks in deterministic order             │
│  3. Collect findings from each check                      │
│  4. Apply fingerprinting (SHA256 of finding content)      │
│  5. Match suppressions                                     │
│  6. Decide PASS/FAIL                                       │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│                  Artifact Generation                        │
│                                                            │
│  - evidence.jsonl (proof log)                             │
│  - vibegate_report.md (technical report)                  │
│  - fixpack.json (remediation tasks)                       │
│  - plain_report.md (friendly report)                      │
│  - agent_prompt.md (AI assistant instructions)            │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│          Optional: LLM Enhancement (Local Only)            │
│                                                            │
│  IF llm.enabled:                                          │
│    - Enhance plain report with friendly explanations      │
│    - Generate context-aware fix prompts                   │
│    - Cache responses by finding fingerprint               │
│                                                            │
│  **Does NOT affect gate decision**                        │
└────────────────────────────────────────────────────────────┘
         ↓
    Exit with code:
    0 = PASS
    1 = FAIL
    2 = CONFIG ERROR
```

## The Determinism Boundary

**Everything above the LLM layer is deterministic.**

### Deterministic Components

These always produce the same output given the same input:

1. **Configuration loading** (vibegate.yaml + suppressions.yaml)
2. **File scanning** (git ls-files or sorted directory walk)
3. **Check execution** (tool invocations with fixed args)
4. **Finding collection** (parse tool output)
5. **Fingerprinting** (SHA256 of finding content)
6. **Suppression matching** (exact fingerprint or rule_id match)
7. **Gate decision** (PASS if no unsuppressed blocking findings, else FAIL)
8. **Evidence log** (JSONL with timestamps, but findings are deterministic)
9. **Fix pack generation** (sorted by category and severity)

### Non-Deterministic Components (Optional)

These may vary based on model state:

1. **LLM explanations** (uses local model, cached by fingerprint)
2. **LLM-generated fix prompts** (uses local model, cached by fingerprint)

**Key insight:** LLM components only enhance the **presentation** of results. They never affect the **gate decision**.

## Detailed Pipeline

### Phase 1: Configuration Loading

**Module:** `src/vibegate/config.py`

```python
def load_config(repo_root: Path) -> VibeGateConfig:
    1. Read vibegate.yaml
    2. Validate against schema/vibegate.schema.json
    3. If profile specified, apply profile overrides
    4. Load .vibegate/suppressions.yaml
    5. Return validated config object
```

**Determinism guarantee:** Given the same vibegate.yaml and suppressions.yaml, always produces the same config object.

### Phase 2: Workspace Scanning

**Module:** `src/vibegate/workspace.py`

```python
def scan_workspace(repo_root: Path) -> List[Path]:
    if is_git_repo(repo_root):
        # Use git ls-files (tracked files only)
        files = run("git ls-files").stdout.splitlines()
    else:
        # Walk directory with default excludes
        files = [f for f in repo_root.rglob("*") if not excluded(f)]

    # Always sort for determinism
    return sorted(files)
```

**Determinism guarantee:** Same repo state = same file list (sorted).

### Phase 3: Check Execution

**Module:** `src/vibegate/runner.py`

The runner orchestrates checks in deterministic order:

```python
def run_check(config: VibeGateConfig, repo_root: Path) -> tuple[List[ArtifactRecord], str]:
    evidence_writer = EvidenceWriter(config.outputs.evidence_jsonl)
    evidence_writer.run_start(...)

    # Run checks in fixed order
    check_order = [
        "formatting",
        "lint",
        "typecheck",
        "tests",
        "dependency_hygiene",
        "sast",
        "secrets",
        "vulnerability",
        "config_sanity",
        "error_handling",
        "defensive_coding",
        "complexity",
        "dead_code",
        "coverage",
        "runtime_smoke",
    ]

    findings: List[Finding] = []

    for check_key in check_order:
        if enabled(check_key):
            check_findings = run_single_check(check_key, config, repo_root)
            findings.extend(check_findings)

    # Apply fingerprinting
    for finding in findings:
        finding.fingerprint = generate_fingerprint(finding)

    # Match suppressions
    unsuppressed_findings = apply_suppressions(findings, config.suppressions)

    # Decide PASS/FAIL
    blocking_count = count_blocking(unsuppressed_findings)
    status = "PASS" if blocking_count == 0 else "FAIL"

    # Generate artifacts
    artifacts = generate_artifacts(findings, unsuppressed_findings, status)

    evidence_writer.run_summary(...)

    return (artifacts, status)
```

**Determinism guarantee:** Same config + same repo = same findings + same decision.

### Phase 4: Fingerprinting

**Module:** `src/vibegate/findings.py`

```python
def generate_fingerprint(finding: Finding) -> str:
    # Stable hash of finding content
    content = {
        "check_id": finding.check_id,
        "rule_id": finding.rule_id,
        "message": finding.message,
        "location": {
            "path": finding.location.path,
            "line": finding.location.line,
        },
    }

    # Sort keys for determinism
    canonical = json.dumps(content, sort_keys=True)
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"
```

**Determinism guarantee:** Same finding content = same fingerprint (always).

### Phase 5: Suppression Matching

**Module:** `src/vibegate/suppressions.py`

```python
def apply_suppressions(
    findings: List[Finding],
    suppressions: List[Suppression]
) -> List[Finding]:
    unsuppressed = []

    for finding in findings:
        suppressed = False

        for sup in suppressions:
            # Match by fingerprint (exact) or rule_id (pattern)
            if (sup.fingerprint and sup.fingerprint == finding.fingerprint) or \
               (sup.rule_id and sup.rule_id == finding.rule_id):
                # Check expiry
                if not expired(sup):
                    suppressed = True
                    evidence_writer.suppression_applied(finding, sup)
                    break

        if not suppressed:
            unsuppressed.append(finding)

    return unsuppressed
```

**Determinism guarantee:** Same findings + same suppressions = same unsuppressed findings.

### Phase 6: Artifact Generation

**Module:** `src/vibegate/artifacts.py`

#### 6.1: Technical Report

```python
def write_report(outputs: OutputsConfig, status: str, findings: List[Finding]) -> ArtifactRecord:
    lines = [
        "# VibeGate Report",
        f"Status: {status}",
        "## Findings",
    ]

    for finding in sorted(findings, key=severity_rank):
        lines.append(f"- [{finding.severity}] {finding.rule_id}: {finding.message}")

    outputs.report_markdown.write_text("\n".join(lines))
```

#### 6.2: Fix Pack

```python
def build_fixpack(findings: List[Finding]) -> dict:
    # Group by category (dependency_fix, security_fix, etc.)
    grouped = group_by_category(findings)

    groups = []
    for category in CATEGORY_ORDER:  # Fixed order
        if category in grouped:
            tasks = [
                {
                    "id": f"{category}-{i}",
                    "title": finding.message,
                    "file_targets": [finding.location.path],
                    "verification_commands": ["vibegate run"],
                }
                for i, finding in enumerate(sorted(grouped[category]))
            ]
            groups.append({"category": category, "tasks": tasks})

    return {
        "schema_version": "v1alpha1",
        "groups": groups,
    }
```

#### 6.3: Plain Report

```python
def write_plain_report(
    repo_root: Path,
    status: str,
    findings: List[Finding],
    detail_level: str,
) -> ArtifactRecord:
    lines = ["# Your Code Quality Report", "", "## What We Checked"]

    if status == "PASS":
        lines.append("## Good News!")
        lines.append("Your code passed all checks.")
    else:
        lines.append("## What Needs Attention")
        lines.append(f"We found {len(findings)} issues.")

        # Group by friendly category
        grouped = group_by_friendly_category(findings)

        for category, category_findings in grouped.items():
            lines.append(f"### {category} ({len(category_findings)} issues)")

            # Show examples (3 in simple mode, all in deep mode)
            examples = category_findings if detail_level == "deep" else category_findings[:3]

            for finding in examples:
                lines.append(f"- {finding.message}")

            if detail_level == "simple" and len(category_findings) > 3:
                lines.append(f"- ...and {len(category_findings) - 3} more")

            lines.append(f"**Why this matters:** {explain_category(category)}")

    plain_report_path = repo_root / ".vibegate" / "plain_report.md"
    plain_report_path.write_text("\n".join(lines))
```

#### 6.4: Agent Prompt Pack

```python
def write_agent_prompt(
    repo_root: Path,
    findings: List[Finding],
    fixpack_path: Path,
) -> tuple[ArtifactRecord, ArtifactRecord]:
    # Markdown version for humans
    md_lines = [
        "# AI Coding Agent: Fix VibeGate Issues",
        f"VibeGate found {len(findings)} issues that need fixing.",
        "## Key Principles",
        "1. Fix root causes, not symptoms",
        "2. Update tests when changing code",
        "3. Run VibeGate to verify fixes",
        "## Steps",
        f"1. Read the Fix Pack: {fixpack_path}",
        "2. Work through issues by priority",
        "3. Verify with: vibegate run .",
    ]

    # JSON version for machines
    json_data = {
        "version": "v1",
        "summary": f"Fix {len(findings)} issues",
        "steps": [...],
        "commands": ["vibegate run ."],
    }

    return (md_record, json_record)
```

#### 6.5: Evidence Log

```python
def write_evidence_jsonl(outputs: OutputsConfig) -> None:
    writer = EvidenceWriter(outputs.evidence_jsonl)

    writer.event({
        "event_type": "run_start",
        "run_id": generate_run_id(),
        "ts": now_iso(),
        "vibegate_version": __version__,
        ...
    })

    for check in checks:
        writer.event({"event_type": "check_start", ...})
        writer.event({"event_type": "tool_exec", ...})

        for finding in check_findings:
            writer.event({"event_type": "finding", ...})

        writer.event({"event_type": "check_end", ...})

    writer.event({
        "event_type": "run_summary",
        "result": status,
        "counts": {...},
        "decision": {...},
    })
```

**Determinism guarantee:** Evidence includes timestamps (non-deterministic), but the **findings and decision are deterministic**. The evidence log is an audit trail, not a decision input.

### Phase 7: Optional LLM Enhancement

**Module:** `src/vibegate/llm/enhancer.py`

```python
def enhance_plain_report_with_llm(
    plain_report: str,
    findings: List[Finding],
    llm_provider: LLMProvider,
) -> str:
    if not llm_provider:
        return plain_report  # Skip if LLM disabled

    enhanced_sections = []

    for finding in findings:
        # Check cache first
        cache_key = f"{finding.fingerprint}:{llm_provider.model}"
        cached = llm_cache.get(cache_key)

        if cached:
            explanation = cached
        else:
            # Generate explanation
            prompt = generate_explanation_prompt(finding)
            explanation = llm_provider.complete(prompt)
            llm_cache.set(cache_key, explanation)

        enhanced_sections.append(explanation)

    # Insert explanations into plain report
    return merge_explanations(plain_report, enhanced_sections)
```

**Non-determinism disclaimer:** LLM responses may vary slightly between runs (temperature > 0). However:
- Responses are **cached by fingerprint + model**
- Cache hits are deterministic
- LLM enhancement **never affects the gate decision**

## Evidence Log Format

The evidence log (`evidence/vibegate.jsonl`) is a sequence of JSON events:

```jsonl
{"event_type": "run_start", "run_id": "...", "ts": "...", ...}
{"event_type": "check_start", "check_id": "formatting", ...}
{"event_type": "tool_exec", "tool": "ruff", "command": [...], "exit_code": 0, ...}
{"event_type": "finding", "fingerprint": "sha256:...", "rule_id": "...", ...}
{"event_type": "check_end", "check_id": "formatting", "status": "completed", ...}
...
{"event_type": "run_summary", "result": "FAIL", "counts": {...}, ...}
```

**Use cases:**
- Compliance audits (proof that checks ran)
- Debugging (what happened and when)
- Trend analysis (compare runs over time)

## Check Implementations

Each check is a self-contained module that:

1. **Takes config + repo_root as input**
2. **Runs external tool or AST analysis**
3. **Returns list of findings**

**Example:** `src/vibegate/checks.py::run_ruff_check()`

```python
def run_ruff_check(config: VibeGateConfig, repo_root: Path) -> List[Finding]:
    # Run ruff with fixed args
    result = subprocess.run(
        ["ruff", "check", "--output-format", "json", "."],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    # Parse JSON output
    ruff_findings = json.loads(result.stdout)

    # Convert to VibeGate findings
    findings = []
    for rf in ruff_findings:
        findings.append(Finding(
            check_id="lint",
            rule_id=rf["code"],
            message=rf["message"],
            severity=map_severity(rf),
            location=Location(path=rf["filename"], line=rf["location"]["row"]),
        ))

    return findings
```

**Determinism guarantee:** Same code + same ruff version = same findings.

## Workspace Scope Rules

VibeGate only scans files in the workspace:

### In Git Repos

```python
def scan_git_workspace(repo_root: Path) -> List[Path]:
    # Use git ls-files (tracked files only)
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    files = [repo_root / line for line in result.stdout.splitlines()]
    return sorted(files)
```

### Outside Git

```python
def scan_directory_workspace(repo_root: Path) -> List[Path]:
    excluded_patterns = [
        ".venv/", "venv/", ".git/", "__pycache__/",
        "dist/", "build/", "*.egg-info/", "site-packages/",
    ]

    files = []
    for path in repo_root.rglob("*"):
        if path.is_file() and not matches_exclude(path, excluded_patterns):
            files.append(path)

    return sorted(files)
```

**Always excludes:**
- Virtual environment site-packages
- Build artifacts
- Cache directories

## Module Reference

| Module | Purpose |
|--------|---------|
| `cli.py` | Typer CLI commands |
| `runner.py` | Check orchestration |
| `checks.py` | Individual check implementations |
| `config.py` | Configuration dataclasses and loading |
| `findings.py` | Finding representation and fingerprinting |
| `evidence.py` | JSONL evidence writer |
| `artifacts.py` | Report and fixpack generation |
| `workspace.py` | File scanning and filtering |
| `suppressions.py` | Suppression matching logic |
| `tuning.py` | Evolution pipeline (label analysis, clustering) |
| `proposals.py` | Proposal generation from tuning clusters |
| `llm/providers.py` | LLM provider protocol |
| `llm/ollama.py` | Ollama provider implementation |
| `llm/prompts.py` | Prompt templates |
| `llm/cache.py` | LLM response caching |
| `llm/enhancer.py` | LLM integration helpers |
| `ui/server.py` | FastAPI web UI |

## Design Principles

1. **Determinism first**: Core pipeline must be reproducible
2. **Evidence always**: Every tool execution logged to evidence.jsonl
3. **Fail-safe**: Missing tools → skip gracefully, don't crash
4. **Local-first**: No network required for core functionality
5. **Privacy by design**: LLM helpers run locally, never send data to cloud
6. **Separation of concerns**: Gate decision (deterministic) vs presentation (LLM-enhanced)

## Future Architecture Extensions

### Planned: Plugin System

```python
# Entry point in pyproject.toml
[project.entry-points."vibegate.checks"]
my_custom_check = "my_plugin.checks:MyCheckPlugin"

# Plugin implementation
class MyCheckPlugin:
    def run(self, config, repo_root) -> List[Finding]:
        ...
```

### Planned: Observability Hooks

```python
# Entry point for emitters
[project.entry-points."vibegate.emitters"]
prometheus = "my_plugin.emitters:PrometheusEmitter"

# Emitter implementation
class PrometheusEmitter:
    def emit_run_summary(self, summary: dict) -> None:
        prometheus.gauge("vibegate_findings_total").set(summary["counts"]["findings_total"])
```

See `docs/OPEN_CORE_ROADMAP.md` for timeline.
