"""VibeGate UI server using FastAPI."""

from __future__ import annotations

import json
import logging
import re
import shutil
import threading
import time
import webbrowser
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class RunSession:
    """Track a UI-initiated check run."""

    run_id: str
    status: str  # "queued" | "running" | "done" | "error"
    started_at: str
    finished_at: str | None = None
    repo_root: Path = field(default_factory=lambda: Path("."))
    detail_level: str = "simple"
    static_mode: bool = False
    errors: list[str] = field(default_factory=list)
    result_status: str | None = None  # "PASS" | "FAIL"
    tailer_stop_event: threading.Event | None = None


class RunRequest(BaseModel):
    """Request body for starting a run."""

    detail_level: str = "simple"


@dataclass(frozen=True)
class IssueKey:
    """Stable key for tracking issues across runs."""

    fingerprint: str | None
    check_id: str
    file_path: str | None
    normalized_message: str
    severity: str  # Added for severity-based grouping

    def __hash__(self):
        if self.fingerprint:
            return hash(self.fingerprint)
        return hash((self.check_id, self.file_path or "", self.normalized_message))

    def __eq__(self, other):
        if not isinstance(other, IssueKey):
            return False
        if self.fingerprint and other.fingerprint:
            return self.fingerprint == other.fingerprint
        return (
            self.check_id == other.check_id
            and self.file_path == other.file_path
            and self.normalized_message == other.normalized_message
        )


@dataclass
class ComparisonResult:
    """Result of comparing two runs."""

    base_run_id: str
    target_run_id: str
    base_meta: dict
    target_meta: dict
    new_issues: list[dict]
    fixed_issues: list[dict]
    same_issues: list[dict]
    new_count: int
    fixed_count: int
    same_count: int
    new_by_category: dict[str, int]
    fixed_by_category: dict[str, int]
    new_by_severity: dict[str, int]  # Added for severity-based analytics
    fixed_by_severity: dict[str, int]  # Added for severity-based analytics
    base_errors: list[str]
    target_errors: list[str]


# Global in-memory registry for active runs
RUNS: Dict[str, RunSession] = {}
RUNS_LOCK = threading.Lock()


def _utc_now() -> str:
    """Return current UTC time as ISO8601 string."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _event_to_friendly_message(event: Dict[str, Any]) -> str:
    """Convert evidence event to user-friendly message."""
    event_type = event.get("event_type", "")

    if event_type == "run_start":
        return "Starting quality checks on your project..."

    if event_type == "check_start":
        check_key = event.get("check_key", "")
        friendly_names = {
            "formatting": "code formatting",
            "lint": "code quality",
            "typecheck": "type safety",
            "tests": "automated tests",
            "dependency_hygiene": "dependency health",
            "sast": "security analysis",
            "secrets": "secrets detection",
            "vulnerability": "vulnerability scan",
            "config_sanity": "configuration check",
            "runtime_smoke": "runtime validation",
            "error_handling": "error handling",
            "defensive_coding": "defensive programming",
            "complexity": "code complexity",
            "dead_code": "dead code detection",
            "coverage": "test coverage",
        }
        friendly = friendly_names.get(check_key, check_key)
        enabled = event.get("enabled", True)
        if enabled:
            return f"Checking {friendly}..."
        return f"Skipping {friendly} (disabled)"

    if event_type == "check_end":
        check_key = event.get("check_key", "")
        status = event.get("status", "")
        friendly_names = {
            "formatting": "code formatting",
            "lint": "code quality",
            "typecheck": "type safety",
            "tests": "automated tests",
            "dependency_hygiene": "dependency health",
            "sast": "security analysis",
            "secrets": "secrets detection",
            "vulnerability": "vulnerability scan",
            "config_sanity": "configuration check",
            "runtime_smoke": "runtime validation",
            "error_handling": "error handling",
            "defensive_coding": "defensive programming",
            "complexity": "code complexity",
            "dead_code": "dead code detection",
            "coverage": "test coverage",
        }
        friendly = friendly_names.get(check_key, check_key)
        friendly_cap = friendly.capitalize() if friendly else "Unknown"
        if status == "PASS":
            return f"✓ {friendly_cap} looks good"
        elif status == "FAIL":
            return f"✗ {friendly_cap} needs attention"
        elif status == "SKIPPED":
            return f"⊘ {friendly_cap} skipped"
        return f"Finished checking {friendly}"

    if event_type == "tool_exec":
        tool = event.get("tool", "")
        return f"Running tool: {tool}"

    if event_type == "finding":
        severity = event.get("severity", "low")
        return f"Found {severity} severity issue"

    if event_type == "run_summary":
        result = event.get("result", "")
        if result == "PASS":
            return "✓ All checks complete. Your project is ready!"
        elif result == "FAIL":
            return "✗ Checks complete. A few things need attention."
        return "Checks complete"

    return "Processing..."


def _write_run_meta(runs_dir: Path, run_id: str, session: RunSession) -> None:
    """Write run metadata to disk."""
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    meta_path = run_dir / "meta.json"
    meta_data = {
        "run_id": run_id,
        "status": session.status,
        "started_at": session.started_at,
        "finished_at": session.finished_at,
        "repo_root": str(session.repo_root),
        "detail_level": session.detail_level,
        "result_status": session.result_status,
        "errors": session.errors,
    }
    meta_path.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")


def _write_run_event(runs_dir: Path, run_id: str, event: Dict[str, Any]) -> None:
    """Append event to run events.jsonl."""
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    events_path = run_dir / "events.jsonl"
    with events_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def _write_run_summary(
    runs_dir: Path, run_id: str, counts: Dict[str, int], status: str
) -> None:
    """Write run summary to disk."""
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"
    summary_data = {
        "status": status,
        "counts": counts,
    }
    summary_path.write_text(json.dumps(summary_data, indent=2), encoding="utf-8")


def _write_run_meta_dict(runs_dir: Path, run_id: str, meta_data: dict) -> None:
    """Write run metadata from dict."""
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    meta_path = run_dir / "meta.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)


def _persist_run_outputs(
    run_id: str, repo_root: Path, runs_dir: Path
) -> dict[str, bool]:
    """
    Copy run outputs to runs_dir/<run_id>/outputs/ for comparison.

    Returns dict mapping output name to whether it was successfully copied.
    """
    outputs_dir = runs_dir / run_id / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Files to copy (relative to repo_root)
    output_files = {
        "plain_report": ".vibegate/plain_report.md",
        "vibegate_report": ".vibegate/artifacts/vibegate_report.md",
        "fixpack": ".vibegate/artifacts/fixpack.json",
        "agent_prompt": ".vibegate/agent_prompt.md",
    }

    copied = {}
    for output_key, rel_path in output_files.items():
        source = repo_root / rel_path
        if source.exists() and source.is_file():
            try:
                dest = outputs_dir / source.name
                shutil.copy2(source, dest)
                copied[output_key] = True
            except Exception as e:
                logger.warning(f"Failed to copy {output_key}: {e}")
                copied[output_key] = False
        else:
            copied[output_key] = False

    return copied


def _normalize_message(msg: str) -> str:
    """Normalize message for comparison (remove line numbers, trim whitespace)."""
    # Remove line/column references
    msg = re.sub(r"\bline\s+\d+\b", "line", msg, flags=re.IGNORECASE)
    msg = re.sub(r"\bcolumn\s+\d+\b", "column", msg, flags=re.IGNORECASE)
    msg = re.sub(r"\b\d+:\d+\b", "", msg)
    # Collapse whitespace
    msg = re.sub(r"\s+", " ", msg)
    return msg.strip().lower()


def _create_issue_key(issue: dict) -> IssueKey:
    """Create stable key from issue dict."""
    # Extract fingerprint from references
    fingerprint = None
    refs = issue.get("references", [])
    if refs and isinstance(refs, list):
        for ref in refs:
            if isinstance(ref, str) and ref.startswith("sha256:"):
                fingerprint = ref
                break

    # Extract file path
    file_path = None
    if "file_targets" in issue and issue["file_targets"]:
        file_path = (
            issue["file_targets"][0]
            if isinstance(issue["file_targets"], list)
            else None
        )
    elif "file_path" in issue:
        file_path = issue["file_path"]

    # Normalize message
    msg = issue.get("description") or issue.get("title") or ""
    normalized_msg = _normalize_message(msg)

    # Extract severity (default to "unknown")
    severity = issue.get("severity", "unknown")

    return IssueKey(
        fingerprint=fingerprint,
        check_id=issue.get("check_id") or issue.get("type", "unknown"),
        file_path=file_path,
        normalized_message=normalized_msg,
        severity=severity,
    )


def _extract_issues_from_fixpack(fixpack_path: Path) -> tuple[list[dict], list[str]]:
    """Extract all tasks from fixpack.json as issue dicts."""
    errors = []
    issues = []

    try:
        with open(fixpack_path) as f:
            fixpack = json.load(f)
    except FileNotFoundError:
        return [], [f"Fixpack not found: {fixpack_path.name}"]
    except json.JSONDecodeError as e:
        return [], [f"Invalid JSON: {e}"]

    for group in fixpack.get("groups", []):
        for task in group.get("tasks", []):
            issue = {
                **task,
                "group_id": group.get("id"),
                "group_title": group.get("title"),
                "category": task.get("type", "unknown").split("_")[0],
            }
            issues.append(issue)

    return issues, errors


def _extract_findings_from_evidence(
    evidence_path: Path,
) -> tuple[list[dict], list[str]]:
    """
    Extract findings from evidence.jsonl (or events.jsonl).

    Reads JSONL file and extracts all finding events, converting them to issue dict format
    compatible with fixpack tasks for comparison.

    Args:
        evidence_path: Path to evidence JSONL file

    Returns:
        Tuple of (findings_list, errors_list)
    """
    errors = []
    findings = []

    if not evidence_path.exists():
        return [], [f"Evidence file not found: {evidence_path.name}"]

    try:
        with evidence_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")
                    continue

                # Only process finding events
                if event.get("event_type") != "finding":
                    continue

                # Convert evidence finding to issue dict format
                # (compatible with fixpack task format)
                finding = {
                    "type": event.get("finding_type", "unknown"),
                    "check_id": event.get("check_id", "unknown"),
                    "severity": event.get("severity", "unknown"),
                    "title": event.get("message", ""),
                    "description": event.get("message", ""),
                    "file_path": None,
                    "file_targets": [],
                    "references": [event.get("fingerprint", "")],
                    "rule_id": event.get("rule_id", ""),
                    "tool": event.get("tool", ""),
                    "category": event.get("finding_type", "unknown").split("_")[0],
                }

                # Extract location if present
                if "location" in event and event["location"]:
                    loc = event["location"]
                    path = loc.get("path")
                    if path:
                        finding["file_path"] = path
                        finding["file_targets"] = [path]

                        # Add line info to description if available
                        if "line" in loc:
                            finding["description"] += f" (line {loc['line']})"

                findings.append(finding)

    except OSError as e:
        return [], [f"Failed to read evidence file: {e}"]

    return findings, errors


def _count_by_field(issues: list[dict], field: str) -> dict[str, int]:
    """Count issues by field value."""
    return dict(Counter(issue.get(field, "unknown") for issue in issues))


def _compare_runs(
    base_dir: Path,
    target_dir: Path,
    base_meta: dict,
    target_meta: dict,
) -> ComparisonResult:
    """
    Compare two runs using evidence JSONL if available, else fixpack.

    Prioritizes loading findings from evidence JSONL (richer data source with severity,
    rule_id, tool metadata) but falls back to fixpack.json for backward compatibility.

    Args:
        base_dir: Base run directory (.vibegate/ui/runs/{run_id})
        target_dir: Target run directory
        base_meta: Base run metadata
        target_meta: Target run metadata

    Returns:
        ComparisonResult with all comparison data including severity breakdowns
    """
    # Try evidence JSONL first (primary source)
    base_evidence = base_dir / "events.jsonl"  # UI run events
    target_evidence = target_dir / "events.jsonl"

    base_issues = []
    target_issues = []
    base_errors = []
    target_errors = []

    # Try loading from evidence first
    if base_evidence.exists():
        base_issues, base_errors = _extract_findings_from_evidence(base_evidence)

    if target_evidence.exists():
        target_issues, target_errors = _extract_findings_from_evidence(target_evidence)

    # Fallback to fixpack if evidence didn't yield findings
    if not base_issues:
        base_fixpack = base_dir / "outputs" / "fixpack.json"
        if base_fixpack.exists():
            base_issues, base_fixpack_errors = _extract_issues_from_fixpack(
                base_fixpack
            )
            base_errors.extend(base_fixpack_errors)
        else:
            base_errors.append("No evidence or fixpack found for base run")

    if not target_issues:
        target_fixpack = target_dir / "outputs" / "fixpack.json"
        if target_fixpack.exists():
            target_issues, target_fixpack_errors = _extract_issues_from_fixpack(
                target_fixpack
            )
            target_errors.extend(target_fixpack_errors)
        else:
            target_errors.append("No evidence or fixpack found for target run")

    # Build key → issue mappings (IssueKey now includes severity)
    base_map = {_create_issue_key(i): i for i in base_issues}
    target_map = {_create_issue_key(i): i for i in target_issues}

    # Compute diffs
    base_keys = set(base_map.keys())
    target_keys = set(target_map.keys())

    new_keys = target_keys - base_keys
    fixed_keys = base_keys - target_keys
    same_keys = base_keys & target_keys

    # Sort for determinism
    new_issues = [
        target_map[k]
        for k in sorted(new_keys, key=lambda k: (k.check_id, k.file_path or ""))
    ]
    fixed_issues = [
        base_map[k]
        for k in sorted(fixed_keys, key=lambda k: (k.check_id, k.file_path or ""))
    ]
    same_issues = [
        base_map[k]
        for k in sorted(same_keys, key=lambda k: (k.check_id, k.file_path or ""))
    ]

    return ComparisonResult(
        base_run_id=base_meta["run_id"],
        target_run_id=target_meta["run_id"],
        base_meta=base_meta,
        target_meta=target_meta,
        new_issues=new_issues,
        fixed_issues=fixed_issues,
        same_issues=same_issues,
        new_count=len(new_issues),
        fixed_count=len(fixed_issues),
        same_count=len(same_issues),
        new_by_category=_count_by_field(new_issues, "category"),
        fixed_by_category=_count_by_field(fixed_issues, "category"),
        new_by_severity=_count_by_field(new_issues, "severity"),
        fixed_by_severity=_count_by_field(fixed_issues, "severity"),
        base_errors=base_errors,
        target_errors=target_errors,
    )


def _compare_fixpacks(
    base_fixpack_path: Path,
    target_fixpack_path: Path,
    base_meta: dict,
    target_meta: dict,
) -> ComparisonResult:
    """
    Compare two fixpack.json files (legacy function for backward compatibility).

    Kept for existing tests and any external code that might call it directly.
    New code should use _compare_runs() instead.
    """
    # For backward compatibility, extract issues directly from fixpack paths
    base_issues, base_errors = _extract_issues_from_fixpack(base_fixpack_path)
    target_issues, target_errors = _extract_issues_from_fixpack(target_fixpack_path)

    # Build key → issue mappings
    base_map = {_create_issue_key(i): i for i in base_issues}
    target_map = {_create_issue_key(i): i for i in target_issues}

    # Compute diffs
    base_keys = set(base_map.keys())
    target_keys = set(target_map.keys())

    new_keys = target_keys - base_keys
    fixed_keys = base_keys - target_keys
    same_keys = base_keys & target_keys

    # Sort for determinism
    new_issues = [
        target_map[k]
        for k in sorted(new_keys, key=lambda k: (k.check_id, k.file_path or ""))
    ]
    fixed_issues = [
        base_map[k]
        for k in sorted(fixed_keys, key=lambda k: (k.check_id, k.file_path or ""))
    ]
    same_issues = [
        base_map[k]
        for k in sorted(same_keys, key=lambda k: (k.check_id, k.file_path or ""))
    ]

    return ComparisonResult(
        base_run_id=base_meta["run_id"],
        target_run_id=target_meta["run_id"],
        base_meta=base_meta,
        target_meta=target_meta,
        new_issues=new_issues,
        fixed_issues=fixed_issues,
        same_issues=same_issues,
        new_count=len(new_issues),
        fixed_count=len(fixed_issues),
        same_count=len(same_issues),
        new_by_category=_count_by_field(new_issues, "category"),
        fixed_by_category=_count_by_field(fixed_issues, "category"),
        new_by_severity=_count_by_field(new_issues, "severity"),
        fixed_by_severity=_count_by_field(fixed_issues, "severity"),
        base_errors=base_errors,
        target_errors=target_errors,
    )


def _tail_evidence_live(
    evidence_path: Path,
    run_id: str,
    runs_dir: Path,
    stop_event: threading.Event,
    start_offset: int = 0,
) -> None:
    """Tail evidence.jsonl in real-time and write events for this run_id.

    Args:
        evidence_path: Path to global evidence.jsonl
        run_id: Run ID to filter events for
        runs_dir: Directory containing run-specific events
        stop_event: Event to signal when to stop tailing
        start_offset: Byte offset to start reading from (default 0)
    """
    # Wait for evidence file to exist (up to 60 seconds)
    max_wait = 60
    start_wait = time.time()
    while not evidence_path.exists():
        if time.time() - start_wait > max_wait:
            logger.warning(
                f"Evidence file did not appear within {max_wait}s: {evidence_path}"
            )
            return
        if stop_event.is_set():
            return
        time.sleep(0.1)

    # Open file and seek to start_offset (to capture all new events)
    try:
        with evidence_path.open("r", encoding="utf-8") as f:
            # Seek to start_offset instead of EOF
            f.seek(start_offset)

            # Poll for new lines
            while True:
                line = f.readline()
                if line:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        if event.get("run_id") == run_id:
                            _write_run_event(runs_dir, run_id, event)
                    except json.JSONDecodeError as e:
                        logger.debug(f"Failed to parse evidence line: {e}")
                        continue
                else:
                    # No new data
                    if stop_event.is_set():
                        # Drain complete, exit
                        break
                    # Sleep briefly before checking again
                    time.sleep(0.3)
    except OSError as e:
        logger.warning(f"Error reading evidence file: {e}")


def _execute_run_in_background(
    run_id: str,
    repo_root: Path,
    detail_level: str,
    runs_dir: Path,
) -> None:
    """Execute check run in background thread."""
    from vibegate.config import load_config
    from vibegate.runner import run_check

    # Create stop event for tailer
    stop_event = threading.Event()

    with RUNS_LOCK:
        if run_id not in RUNS:
            return
        RUNS[run_id].status = "running"
        RUNS[run_id].tailer_stop_event = stop_event
        _write_run_meta(runs_dir, run_id, RUNS[run_id])

    tailer_thread = None

    try:
        # Load config
        config = load_config(repo_root)
        evidence_path = config.outputs.evidence_jsonl

        # Compute start offset to capture all new events (not just those after tailer starts)
        start_offset = evidence_path.stat().st_size if evidence_path.exists() else 0

        # Start concurrent tailer thread BEFORE run_check
        tailer_thread = threading.Thread(
            target=_tail_evidence_live,
            args=(evidence_path, run_id, runs_dir, stop_event, start_offset),
            daemon=True,
        )
        tailer_thread.start()

        # Run checks (tailer will stream events live)
        artifacts, status = run_check(
            config, repo_root, detail_level=detail_level, run_id=run_id
        )

        # Stop tailer
        stop_event.set()
        if tailer_thread:
            tailer_thread.join(timeout=2.0)

        # Write summary (read from already-written events)
        events_path = runs_dir / run_id / "events.jsonl"
        summary_event = None
        if events_path.exists():
            with events_path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                        if event.get("event_type") == "run_summary":
                            summary_event = event
                    except json.JSONDecodeError:
                        continue

        if summary_event:
            counts = summary_event.get("counts", {})
            _write_run_summary(runs_dir, run_id, counts, status)

        # Persist outputs for comparison
        outputs_copied = _persist_run_outputs(run_id, repo_root, runs_dir)

        # Update session and write meta with outputs info
        with RUNS_LOCK:
            if run_id in RUNS:
                RUNS[run_id].status = "done"
                RUNS[run_id].finished_at = _utc_now()
                RUNS[run_id].result_status = status
                # Write meta with outputs info
                meta_data = {
                    "run_id": run_id,
                    "status": "done",
                    "started_at": RUNS[run_id].started_at,
                    "finished_at": RUNS[run_id].finished_at,
                    "result_status": status,
                    "errors": RUNS[run_id].errors,
                    "outputs_available": outputs_copied,
                }
                _write_run_meta_dict(runs_dir, run_id, meta_data)

    except Exception as e:
        # Stop tailer on error
        stop_event.set()
        if tailer_thread:
            tailer_thread.join(timeout=2.0)

        # Record error
        error_msg = str(e)
        logger.exception(f"Run {run_id} failed with error: {error_msg}")
        with RUNS_LOCK:
            if run_id in RUNS:
                RUNS[run_id].status = "error"
                RUNS[run_id].finished_at = _utc_now()
                RUNS[run_id].errors.append(error_msg)
                _write_run_meta(runs_dir, run_id, RUNS[run_id])


class _AppRoutes:
    """Helper class to organize route handlers and reduce create_app complexity."""

    def __init__(self, repo_root: Path, static_mode: bool, runs_dir: Path):
        self.repo_root = repo_root
        self.static_mode = static_mode
        self.runs_dir = runs_dir

    async def home(self) -> str:
        """Home page with navigation."""
        state_path = self.repo_root / ".vibegate" / "state.json"
        last_run_info = None
        if state_path.exists():
            try:
                with state_path.open("r", encoding="utf-8") as f:
                    state_data = json.load(f)
                    last_run = state_data.get("last_run", {})
                    if last_run:
                        last_run_info = {
                            "timestamp": last_run.get("created_at", "Unknown"),
                            "status": last_run.get("status", "Unknown"),
                            "evidence_path": last_run.get("evidence_path"),
                        }
            except (json.JSONDecodeError, OSError) as e:
                logger.debug(f"Could not load state.json: {e}")

        # Check if fixpack exists to prioritize it
        fixpack_path = self.repo_root / ".vibegate" / "artifacts" / "fixpack.json"
        has_fixpack = fixpack_path.exists()

        return _render_home(last_run_info, self.static_mode, has_fixpack, self.runs_dir)

    async def plain_report(self) -> str:
        """View plain report (user-friendly)."""
        report_path = self.repo_root / ".vibegate" / "plain_report.md"
        if not report_path.exists():
            return _render_missing_artifact(
                "Plain Report",
                "plain_report.md",
                "Run 'vibegate run .' to generate the plain report, or view it with 'vibegate view .'",
            )
        content = report_path.read_text(encoding="utf-8")
        return _render_markdown_page("Plain Report", content, show_tech_toggle=True)

    async def technical_report(self) -> str:
        """View technical report."""
        report_path = self.repo_root / ".vibegate" / "artifacts" / "vibegate_report.md"
        if not report_path.exists():
            return _render_missing_artifact(
                "Technical Report",
                ".vibegate/artifacts/vibegate_report.md",
                "Run 'vibegate run .' to generate the technical report, or view it with 'vibegate view .'",
            )
        content = report_path.read_text(encoding="utf-8")
        return _render_markdown_page(
            "Technical Report", content, show_tech_toggle=False
        )

    async def fixpack(self) -> str:
        """View fixpack (interactive)."""
        fixpack_path = self.repo_root / ".vibegate" / "artifacts" / "fixpack.json"
        if not fixpack_path.exists():
            return _render_missing_artifact(
                "Fix Pack",
                ".vibegate/artifacts/fixpack.json",
                "Run 'vibegate run .' to generate the fix pack, or view it with 'vibegate view .'",
            )
        try:
            with fixpack_path.open("r", encoding="utf-8") as f:
                fixpack_data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            raise HTTPException(status_code=500, detail=f"Failed to load fix pack: {e}")
        return _render_fixpack(fixpack_data)

    async def agent_prompt(self) -> str:
        """View agent prompt (AI-ready)."""
        agent_prompt_path = self.repo_root / ".vibegate" / "agent_prompt.md"
        if not agent_prompt_path.exists():
            return _render_missing_artifact(
                "Agent Prompt",
                ".vibegate/agent_prompt.md",
                "Run 'vibegate run .' to generate the agent prompt, or view it with 'vibegate view .'",
            )
        content = agent_prompt_path.read_text(encoding="utf-8")
        return _render_markdown_page("Agent Prompt", content, show_tech_toggle=False)

    async def run_page(self) -> str:
        """Run page (trigger new check)."""
        return _render_run_page(self.static_mode)

    async def runs_list(self) -> str:
        """List all runs (history)."""
        # Load all runs from runs_dir
        all_runs = []
        if self.runs_dir.exists():
            for run_dir in self.runs_dir.iterdir():
                if not run_dir.is_dir():
                    continue
                meta_path = run_dir / "meta.json"
                if not meta_path.exists():
                    continue
                try:
                    meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
                    all_runs.append(meta_data)
                except (json.JSONDecodeError, OSError):
                    continue

        # Sort by started_at descending (most recent first)
        all_runs.sort(key=lambda x: x.get("started_at", ""), reverse=True)

        return _render_runs_list(all_runs, self.static_mode)

    async def run_detail(self, run_id: str) -> str:
        """View single run detail."""
        meta_path = self.runs_dir / run_id / "meta.json"
        if not meta_path.exists():
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

        try:
            meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            raise HTTPException(status_code=500, detail="Failed to load run metadata")

        summary_path = self.runs_dir / run_id / "summary.json"
        summary_data = None
        if summary_path.exists():
            try:
                summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                logger.debug(f"Failed to load summary for run {run_id}: {e}")

        return _render_run_detail(meta_data, summary_data)

    async def compare_selection_page(self) -> str:
        """Render run selection page for comparison."""
        runs = []
        if self.runs_dir.exists():
            for run_dir in self.runs_dir.iterdir():
                if not run_dir.is_dir():
                    continue
                meta_path = run_dir / "meta.json"
                if not meta_path.exists():
                    continue
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                    runs.append(meta)
                except Exception as e:
                    logger.warning(f"Failed to load meta for {run_dir.name}: {e}")

        # Sort newest first
        runs.sort(key=lambda r: r.get("started_at", ""), reverse=True)

        return _render_compare_selection_page(runs)

    async def compare_result_page(
        self, base: str, target: str, filter: str = ""
    ) -> str:
        """
        Render comparison result between two runs.

        Args:
            base: Base run ID
            target: Target run ID
            filter: Optional search filter for issue tables

        Returns:
            HTML string with comparison result page
        """
        base_dir = self.runs_dir / base
        target_dir = self.runs_dir / target

        if not base_dir.exists() or not target_dir.exists():
            raise HTTPException(status_code=404, detail="One or both runs not found")

        try:
            with open(base_dir / "meta.json") as f:
                base_meta = json.load(f)
            with open(target_dir / "meta.json") as f:
                target_meta = json.load(f)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to load run metadata: {e}"
            )

        # Use new comparison function (evidence-aware)
        comparison = _compare_runs(base_dir, target_dir, base_meta, target_meta)

        return _render_comparison_result(comparison, filter_query=filter)

    async def download(self, filename: str) -> FileResponse:
        """Download artifact file.

        Only allows whitelisted files for security.
        """
        # Whitelist of downloadable files
        allowed_files = {
            "plain_report.md": self.repo_root / ".vibegate" / "plain_report.md",
            "agent_prompt.md": self.repo_root / ".vibegate" / "agent_prompt.md",
            "vibegate_report.md": self.repo_root
            / ".vibegate"
            / "artifacts"
            / "vibegate_report.md",
            "fixpack.json": self.repo_root / ".vibegate" / "artifacts" / "fixpack.json",
            "fixpack.md": self.repo_root / ".vibegate" / "artifacts" / "fixpack.md",
            "vibegate.jsonl": self.repo_root
            / ".vibegate"
            / "evidence"
            / "vibegate.jsonl",
        }

        if filename not in allowed_files:
            raise HTTPException(status_code=404, detail="File not found or not allowed")

        file_path = allowed_files[filename]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream",
        )


def create_app(
    repo_root: Path, static_mode: bool = False, runs_dir: Path | None = None
) -> FastAPI:
    """Create FastAPI application for VibeGate UI.

    Args:
        repo_root: Repository root directory
        static_mode: If True, disable run triggers (read-only mode)
        runs_dir: Directory for storing UI run sessions (default: repo_root/.vibegate/ui/runs)

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(title="VibeGate UI", version="0.1.0")

    # Initialize runs_dir
    if runs_dir is None:
        runs_dir = repo_root / ".vibegate" / "ui" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    # Get absolute path to static directory
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Create route handlers with shared state
    routes = _AppRoutes(repo_root, static_mode, runs_dir)

    @app.get("/", response_class=HTMLResponse)
    async def home() -> str:
        return await routes.home()

    @app.get("/plain", response_class=HTMLResponse)
    async def plain_report() -> str:
        return await routes.plain_report()

    @app.get("/report", response_class=HTMLResponse)
    async def technical_report() -> str:
        return await routes.technical_report()

    @app.get("/fixpack", response_class=HTMLResponse)
    async def fixpack() -> str:
        return await routes.fixpack()

    @app.get("/agent", response_class=HTMLResponse)
    async def agent_prompt() -> str:
        return await routes.agent_prompt()

    # ===== Live Run Dashboard Routes =====

    @app.get("/run", response_class=HTMLResponse)
    async def run_page() -> str:
        return await routes.run_page()

    @app.post("/api/run")
    async def start_run(request: RunRequest) -> Dict[str, Any]:
        """Start a new check run."""
        if static_mode:
            raise HTTPException(
                status_code=403,
                detail="Read-only mode. Cannot start runs from UI. Use 'vibegate run .' from CLI.",
            )

        detail_level = request.detail_level

        # Check if any run is already active
        with RUNS_LOCK:
            for session in RUNS.values():
                if session.status in ("queued", "running"):
                    return {
                        "error": "A run is already in progress",
                        "active_run_id": session.run_id,
                        "run_url": f"/runs/{session.run_id}",
                    }

        # Create new run session
        run_id = uuid4().hex[:8]
        session = RunSession(
            run_id=run_id,
            status="queued",
            started_at=_utc_now(),
            repo_root=repo_root,
            detail_level=detail_level,
            static_mode=static_mode,
        )

        with RUNS_LOCK:
            RUNS[run_id] = session
            _write_run_meta(runs_dir, run_id, session)

        # Start run in background thread
        thread = threading.Thread(
            target=_execute_run_in_background,
            args=(run_id, repo_root, detail_level, runs_dir),
            daemon=True,
        )
        thread.start()

        return {
            "run_id": run_id,
            "run_url": f"/runs/{run_id}",
            "events_url": f"/api/runs/{run_id}/events",
            "status_url": f"/api/runs/{run_id}/status",
            "status": "queued",
        }

    @app.get("/api/runs/{run_id}/status")
    async def run_status(run_id: str) -> Dict[str, Any]:
        """Get status of a specific run."""
        with RUNS_LOCK:
            session = RUNS.get(run_id)

        if not session:
            # Try loading from disk
            meta_path = runs_dir / run_id / "meta.json"
            if not meta_path.exists():
                raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

            try:
                meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
                return meta_data
            except (json.JSONDecodeError, OSError):
                raise HTTPException(
                    status_code=500, detail="Failed to load run metadata"
                )

        response: Dict[str, Any] = {
            "run_id": session.run_id,
            "status": session.status,
            "started_at": session.started_at,
            "finished_at": session.finished_at,
            "result_status": session.result_status,
            "errors": session.errors,
        }

        if session.status == "done" and session.result_status:
            response["artifacts"] = {
                "plain_report": "/plain",
                "technical_report": "/report",
                "fixpack": "/fixpack",
                "agent_prompt": "/agent",
            }

        return response

    @app.get("/api/runs/{run_id}/events")
    async def run_events(run_id: str):
        """Stream run events via Server-Sent Events."""

        async def event_stream():
            """Generate SSE events."""
            events_path = runs_dir / run_id / "events.jsonl"
            file_handle = None
            last_heartbeat = time.time()
            heartbeat_interval = 15.0  # seconds

            try:
                # Initial connection message
                yield f"data: {json.dumps({'type': 'connected', 'run_id': run_id})}\n\n"

                # Stream existing and new events
                max_wait = 300  # 5 minutes timeout
                start_time = time.time()
                partial_line = ""

                while time.time() - start_time < max_wait:
                    # Open file if not already open
                    if file_handle is None and events_path.exists():
                        file_handle = events_path.open("r", encoding="utf-8")

                    # Read new lines
                    if file_handle:
                        while True:
                            line = file_handle.readline()
                            if not line:
                                break

                            # Combine with any partial line from previous iteration
                            full_line = partial_line + line
                            partial_line = ""

                            # Only process if line ends with newline (complete line)
                            if not full_line.endswith("\n"):
                                partial_line = full_line
                                break

                            line_content = full_line.strip()
                            if not line_content:
                                continue

                            try:
                                event = json.loads(line_content)
                                friendly_msg = _event_to_friendly_message(event)
                                yield f"data: {json.dumps({'type': 'event', 'event': event, 'message': friendly_msg})}\n\n"
                            except json.JSONDecodeError as e:
                                logger.debug(f"Failed to parse event line: {e}")
                                # Skip malformed line
                                continue

                    # Check if run is complete
                    is_complete = False
                    with RUNS_LOCK:
                        session = RUNS.get(run_id)
                        if session and session.status in ("done", "error"):
                            yield f"data: {json.dumps({'type': 'complete', 'status': session.status, 'result_status': session.result_status})}\n\n"
                            is_complete = True

                    if is_complete:
                        break

                    # If session not in memory, check meta.json from disk
                    if run_id not in RUNS:
                        meta_path = runs_dir / run_id / "meta.json"
                        if meta_path.exists():
                            try:
                                meta_data = json.loads(
                                    meta_path.read_text(encoding="utf-8")
                                )
                                status = meta_data.get("status", "")
                                if status in ("done", "error"):
                                    result_status = meta_data.get("result_status")
                                    yield f"data: {json.dumps({'type': 'complete', 'status': status, 'result_status': result_status})}\n\n"
                                    is_complete = True
                            except (json.JSONDecodeError, OSError) as e:
                                logger.debug(
                                    f"Failed to check completion status for run {run_id}: {e}"
                                )

                    if is_complete:
                        break

                    # Send heartbeat if needed
                    now = time.time()
                    if now - last_heartbeat > heartbeat_interval:
                        yield ": ping\n\n"
                        last_heartbeat = now

                    # Wait before checking again
                    await __import__("asyncio").sleep(0.4)

                # If loop exits due to timeout
                if time.time() - start_time >= max_wait:
                    yield 'data: {"type": "timeout"}\n\n'

            finally:
                # Clean up file handle
                if file_handle:
                    file_handle.close()

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    @app.get("/runs", response_class=HTMLResponse)
    async def runs_list() -> str:
        return await routes.runs_list()

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    async def run_detail(run_id: str) -> str:
        return await routes.run_detail(run_id)

    @app.get("/compare", response_class=HTMLResponse)
    async def compare_selection_page() -> str:
        return await routes.compare_selection_page()

    @app.get("/compare/result", response_class=HTMLResponse)
    async def compare_result_page(base: str, target: str) -> str:
        return await routes.compare_result_page(base, target)

    @app.get("/download/{filename}")
    async def download(filename: str) -> FileResponse:
        return await routes.download(filename)

    return app


def _render_home(
    last_run_info: Optional[Dict[str, Any]],
    static_mode: bool,
    has_fixpack: bool,
    runs_dir: Path,
) -> str:
    """Render home page HTML."""
    # Check if we have at least 2 runs for comparison link
    runs = []
    if runs_dir.exists():
        for run_dir in runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            meta_path = run_dir / "meta.json"
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                    runs.append(meta)
                except Exception:
                    continue

    # Sort newest first
    runs.sort(key=lambda r: r.get("started_at", ""), reverse=True)

    has_multiple_runs = len(runs) >= 2
    latest_run_id = runs[0]["run_id"] if runs else ""
    second_run_id = runs[1]["run_id"] if len(runs) >= 2 else ""

    last_run_html = ""
    if last_run_info:
        status = last_run_info.get("status", "Unknown")
        status_color = "green" if status == "PASS" else "red"
        last_run_html = f"""
        <div class="last-run">
            <h2>Last Run</h2>
            <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status}</span></p>
            <p><strong>Time:</strong> {last_run_info.get("timestamp", "Unknown")}</p>
        </div>
        """
    else:
        last_run_html = """
        <div class="last-run">
            <h2>No Recent Run</h2>
            <p>Run <code>vibegate run .</code> to generate artifacts.</p>
        </div>
        """

    mode_notice = ""
    if static_mode:
        mode_notice = """
        <div class="notice">
            <p><strong>Static Mode:</strong> Read-only viewer. Cannot run checks from UI.</p>
        </div>
        """

    # Prioritize Fix Pack if it exists
    primary_action = ""
    if has_fixpack:
        primary_action = """
        <div class="primary-action" style="margin: 2rem 0; padding: 1.5rem; background: #e7f5ff; border-left: 4px solid #007bff; border-radius: 4px;">
            <h2 style="margin-top: 0;">Fix Pack Ready</h2>
            <p style="margin: 0.5rem 0;">Your actionable to-do list for fixing issues.</p>
            <a href="/fixpack" class="primary-btn" style="display: inline-block; margin-top: 1rem; padding: 1rem 2rem; background: #007bff; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 1.1rem;">Open Fix Pack</a>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Home</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>VibeGate UI</h1>
            <p class="subtitle">Quality Gate for Your Python Project</p>
        </header>

        {mode_notice}
        {last_run_html}
        {primary_action}

        <nav class="main-nav">
            <h2>Actions</h2>
            <ul>
                <li>
                    <a href="/run" class="nav-link {
        "disabled" if static_mode else ""
    }" {'onclick="return false;"' if static_mode else ""}>
                        <strong>Run Checks Now</strong>
                        <span>{
        "Read-only mode (use CLI)" if static_mode else "Start a new quality check"
    }</span>
                    </a>
                </li>
                <li>
                    <a href="/runs" class="nav-link">
                        <strong>Run History</strong>
                        <span>View past check runs</span>
                    </a>
                </li>
                {
        ""
        if not has_multiple_runs
        else f'''
                <li>
                    <a href="/compare/result?base={second_run_id}&target={latest_run_id}" class="nav-link">
                        <strong>Compare Last 2 Runs</strong>
                        <span>See what changed in your latest run</span>
                    </a>
                </li>
                '''
    }
            </ul>

            <h2>View Results</h2>
            <ul>
                <li>
                    <a href="/plain" class="nav-link">
                        <strong>Friendly Report</strong>
                        <span>User-friendly overview of findings</span>
                    </a>
                </li>
                <li>
                    <a href="/report" class="nav-link">
                        <strong>Technical Report</strong>
                        <span>Detailed technical analysis</span>
                    </a>
                </li>
                <li>
                    <a href="/fixpack" class="nav-link">
                        <strong>Action Plan</strong>
                        <span>Step-by-step fixes to apply</span>
                    </a>
                </li>
                <li>
                    <a href="/agent" class="nav-link">
                        <strong>Agent Prompt</strong>
                        <span>Instructions for AI coding assistants</span>
                    </a>
                </li>
            </ul>
        </nav>

        <footer>
            <p>VibeGate - Deterministic Production Readiness Gate</p>
        </footer>
    </div>
</body>
</html>
"""


def _render_missing_artifact(title: str, filename: str, instruction: str) -> str:
    """Render page for missing artifact."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - {title}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; {title}
            </nav>
        </header>

        <div class="missing-artifact">
            <h2>Artifact Not Found</h2>
            <p>The file <code>{filename}</code> was not found.</p>
            <p><strong>Next step:</strong> {instruction}</p>
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _render_markdown_page(title: str, content: str, show_tech_toggle: bool) -> str:
    """Render markdown content as HTML page."""
    # Simple markdown rendering (headings, code blocks, lists, emphasis)
    html_content = _markdown_to_html(content)

    tech_toggle = ""
    if show_tech_toggle:
        tech_toggle = """
        <div class="toggle-container">
            <label>
                <input type="checkbox" id="tech-toggle" onchange="toggleTechnical()">
                Show Technical Details
            </label>
        </div>
        <script>
        function toggleTechnical() {
            const checkbox = document.getElementById('tech-toggle');
            const sections = document.querySelectorAll('.technical-section');
            sections.forEach(section => {
                section.style.display = checkbox.checked ? 'block' : 'none';
            });
        }
        // Hide technical sections by default
        document.addEventListener('DOMContentLoaded', function() {
            const sections = document.querySelectorAll('.technical-section');
            sections.forEach(section => {
                section.style.display = 'none';
            });
        });
        </script>
        """

    download_link = _get_download_filename(title)
    download_html = ""
    if download_link:
        download_html = (
            f'<a href="/download/{download_link}" class="download-btn">Download</a>'
        )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - {title}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; {title}
            </nav>
            {download_html}
        </header>

        {tech_toggle}

        <div class="markdown-content">
            {html_content}
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _render_fixpack(fixpack_data: Dict[str, Any]) -> str:
    """Render fix pack as interactive HTML."""
    groups = fixpack_data.get("groups", [])

    groups_html = ""
    for group in groups:
        category = group.get("category", "Unknown")
        description = group.get("description", "")
        tasks = group.get("tasks", [])

        tasks_html = ""
        for task in tasks:
            task_id = task.get("id", "")
            title = task.get("title", "")
            severity = task.get("severity", "unknown")
            remediation = task.get("remediation", "")

            # Simple markdown rendering for remediation
            remediation_html = _markdown_to_html(remediation)

            tasks_html += f"""
            <div class="task" data-severity="{severity}">
                <div class="task-header">
                    <span class="task-id">{task_id}</span>
                    <span class="severity-badge severity-{severity}">{severity}</span>
                </div>
                <h4>{title}</h4>
                <div class="task-remediation">
                    {remediation_html}
                </div>
            </div>
            """

        groups_html += f"""
        <div class="group">
            <h3>{category}</h3>
            <p class="group-description">{description}</p>
            <div class="tasks">
                {tasks_html}
            </div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Fix Pack</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Fix Pack</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; Fix Pack
            </nav>
            <a href="/download/fixpack.json" class="download-btn">Download JSON</a>
        </header>

        <div class="fixpack">
            {groups_html}
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _markdown_to_html(md: str) -> str:
    """Convert markdown to HTML (simple implementation).

    Supports:
    - Headings (# ## ###)
    - Code blocks (```)
    - Inline code (`)
    - Lists (- *)
    - Bold (**text**)
    - Italic (*text*)
    - Horizontal rules (---)
    """
    lines = md.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False
    code_lang = ""

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
                code_lang = ""
            else:
                code_lang = line.strip()[3:].strip()
                lang_class = f' class="language-{code_lang}"' if code_lang else ""
                html_lines.append(f"<pre{lang_class}><code>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(_escape_html(line))
            continue

        # Headings
        if line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{_inline_markdown(line[2:])}</h1>")
            continue
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            # Mark h2 with "Technical Details" as technical section
            heading_text = line[3:].strip()
            if "technical" in heading_text.lower():
                html_lines.append(
                    f'<h2 class="technical-section">{_inline_markdown(heading_text)}</h2>'
                )
            else:
                html_lines.append(f"<h2>{_inline_markdown(heading_text)}</h2>")
            continue
        if line.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{_inline_markdown(line[4:])}</h3>")
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr>")
            continue

        # Lists
        if line.strip().startswith(("- ", "* ")):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_inline_markdown(line.strip()[2:])}</li>")
            continue

        # End list if line doesn't start with list marker
        if in_list and not line.strip().startswith(("- ", "* ")):
            html_lines.append("</ul>")
            in_list = False

        # Empty line
        if not line.strip():
            html_lines.append("<br>")
            continue

        # Regular paragraph
        html_lines.append(f"<p>{_inline_markdown(line)}</p>")

    # Close any open tags
    if in_code_block:
        html_lines.append("</code></pre>")
    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def _inline_markdown(text: str) -> str:
    """Process inline markdown (code, bold, italic)."""
    import re

    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Bold
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

    # Italic (avoid matching ** from bold)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    return text


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _get_download_filename(title: str) -> Optional[str]:
    """Map page title to download filename."""
    mapping = {
        "Plain Report": "plain_report.md",
        "Technical Report": "vibegate_report.md",
        "Agent Prompt": "agent_prompt.md",
    }
    return mapping.get(title)


def _render_run_page(static_mode: bool) -> str:
    """Render the live run page."""
    if static_mode:
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Run Checks</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Run Checks</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; Run Checks
            </nav>
        </header>

        <div class="notice">
            <h2>Read-Only Mode</h2>
            <p>The UI is in read-only mode. You cannot start runs from the browser.</p>
            <p>To run checks, use the command line:</p>
            <pre><code>vibegate run .</code></pre>
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""

    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Run Checks</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        .detail-level-selector {
            margin: 20px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .detail-level-selector label {
            display: block;
            margin: 10px 0;
            cursor: pointer;
        }
        .detail-level-selector input[type="radio"] {
            margin-right: 10px;
        }
        .run-button {
            background: #28a745;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
            margin: 20px 0;
        }
        .run-button:hover { background: #218838; }
        .run-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        #progress { display: none; margin: 20px 0; }
        #progress.active { display: block; }
        #progress-messages {
            max-height: 400px;
            overflow-y: auto;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: monospace;
        }
        .progress-message { margin: 5px 0; }
        .progress-message.friendly { color: #333; }
        .progress-message.complete { color: #28a745; font-weight: bold; }
        .progress-message.error { color: #dc3545; font-weight: bold; }
        #links { display: none; margin: 20px 0; }
        #links.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Run Quality Checks</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; Run Checks
            </nav>
        </header>

        <div class="detail-level-selector">
            <h3>Detail Level</h3>
            <label>
                <input type="radio" name="detail-level" value="simple" checked>
                <strong>Simple (recommended)</strong> - Fast, essential checks only
            </label>
            <label>
                <input type="radio" name="detail-level" value="deep">
                <strong>More detail</strong> - Thorough analysis (slower)
            </label>
        </div>

        <div>
            <button id="start-button" class="run-button" onclick="startRun()">Start Checks</button>
        </div>

        <div id="progress">
            <h2>Progress</h2>
            <div id="progress-messages"></div>
        </div>

        <div id="links">
            <h2>Results Ready</h2>
            <ul>
                <li><a href="/plain">View Friendly Report</a></li>
                <li><a href="/report">View Technical Report</a></li>
                <li><a href="/fixpack">View Action Plan</a></li>
                <li><a href="/agent">View Agent Prompt</a></li>
            </ul>
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>

    <script>
        let eventSource = null;

        function addMessage(text, type = 'friendly') {
            const messagesDiv = document.getElementById('progress-messages');
            const msg = document.createElement('div');
            msg.className = `progress-message ${type}`;
            msg.textContent = text;
            messagesDiv.appendChild(msg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        async function startRun() {
            const button = document.getElementById('start-button');
            button.disabled = true;
            button.textContent = 'Running...';

            document.getElementById('progress').className = 'active';
            document.getElementById('progress-messages').innerHTML = '';

            // Get selected detail level
            const detailLevel = document.querySelector('input[name="detail-level"]:checked').value;

            try {
                const response = await fetch('/api/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ detail_level: detailLevel })
                });

                const data = await response.json();

                if (data.error) {
                    addMessage('Error: ' + data.error, 'error');
                    if (data.run_url) {
                        addMessage('Go to active run: ' + data.run_url, 'friendly');
                    }
                    button.disabled = false;
                    button.textContent = 'Start Checks';
                    return;
                }

                addMessage('Started run: ' + data.run_id + ' (' + detailLevel + ' mode)', 'friendly');

                // Connect to SSE stream
                eventSource = new EventSource(data.events_url);

                eventSource.onmessage = (event) => {
                    const payload = JSON.parse(event.data);

                    if (payload.type === 'connected') {
                        addMessage('Connected to run stream', 'friendly');
                    } else if (payload.type === 'event') {
                        addMessage(payload.message, 'friendly');
                    } else if (payload.type === 'complete') {
                        addMessage('Run complete: ' + (payload.result_status || payload.status), 'complete');
                        eventSource.close();
                        button.disabled = false;
                        button.textContent = 'Start Checks';
                        document.getElementById('links').className = 'active';
                    } else if (payload.type === 'timeout') {
                        addMessage('Stream timeout', 'error');
                        eventSource.close();
                        button.disabled = false;
                        button.textContent = 'Start Checks';
                    }
                };

                eventSource.onerror = () => {
                    addMessage('Stream error or disconnected', 'error');
                    eventSource.close();
                    button.disabled = false;
                    button.textContent = 'Start Checks';
                };

            } catch (error) {
                addMessage('Error: ' + error.message, 'error');
                button.disabled = false;
                button.textContent = 'Start Checks';
            }
        }
    </script>
</body>
</html>
"""


def _render_runs_list(runs: list[Dict[str, Any]], static_mode: bool) -> str:
    """Render the runs history list."""
    runs_html = ""
    if not runs:
        runs_html = "<p>No runs found. Run checks to create history.</p>"
    else:
        for idx, run in enumerate(runs):
            run_id = run.get("run_id", "unknown")
            status = run.get("status", "unknown")
            result_status = run.get("result_status", "")
            started_at = run.get("started_at", "")

            status_emoji = (
                "⏳"
                if status in ("queued", "running")
                else (
                    "✓"
                    if result_status == "PASS"
                    else "✗"
                    if result_status == "FAIL"
                    else "⊘"
                )
            )
            status_color = (
                "blue"
                if status in ("queued", "running")
                else (
                    "green"
                    if result_status == "PASS"
                    else "red"
                    if result_status == "FAIL"
                    else "gray"
                )
            )

            # Add "Compare to previous" link (except for oldest run)
            compare_link = ""
            if idx < len(runs) - 1:  # Not the last (oldest) run
                prev_run_id = runs[idx + 1]["run_id"]
                compare_link = f'<a href="/compare/result?base={prev_run_id}&target={run_id}" style="font-size: 0.9em; color: #007bff; text-decoration: none;">⚖️ Compare to previous</a>'

            runs_html += f"""
            <div class="run-card" style="border-left: 4px solid {status_color}; margin: 10px 0; padding: 15px; background: #f8f9fa;">
                <h3><a href="/runs/{run_id}">{status_emoji} Run {run_id}</a></h3>
                <p><strong>Status:</strong> {status} {f"({result_status})" if result_status else ""}</p>
                <p><strong>Started:</strong> {started_at}</p>
                {f"<p>{compare_link}</p>" if compare_link else ""}
            </div>
            """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Run History</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Run History</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; Run History
            </nav>
        </header>

        <div class="card" style="border-left: 4px solid #17a2b8; margin-bottom: 2rem; padding: 15px; background: #e7f5f7;">
            <h3>🔍 Compare Runs</h3>
            <p>Compare findings between two runs to track your progress.</p>
            <a href="/compare" style="display: inline-block; background: #17a2b8; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 4px; margin-top: 0.5rem;">Compare Runs</a>
        </div>

        <h2>Past Runs</h2>
        <div>
            {runs_html}
        </div>

        <footer>
            <a href="/">Back to Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _render_run_detail(meta: Dict[str, Any], summary: Optional[Dict[str, Any]]) -> str:
    """Render a single run detail page."""
    run_id = meta.get("run_id", "unknown")
    status = meta.get("status", "unknown")
    result_status = meta.get("result_status", "")
    started_at = meta.get("started_at", "")
    finished_at = meta.get("finished_at", "")
    errors = meta.get("errors", [])

    status_emoji = (
        "⏳"
        if status in ("queued", "running")
        else (
            "✓" if result_status == "PASS" else "✗" if result_status == "FAIL" else "⊘"
        )
    )
    status_color = (
        "blue"
        if status in ("queued", "running")
        else (
            "green"
            if result_status == "PASS"
            else "red"
            if result_status == "FAIL"
            else "gray"
        )
    )

    summary_html = ""
    if summary:
        counts = summary.get("counts", {})
        summary_html = f"""
        <div class="summary">
            <h2>Summary</h2>
            <ul>
                <li>Total findings: {counts.get("findings_total", 0)}</li>
                <li>Blocking: {counts.get("findings_blocking", 0)}</li>
                <li>Warnings: {counts.get("findings_warning", 0)}</li>
                <li>Suppressed: {counts.get("suppressed_total", 0)}</li>
            </ul>
        </div>
        """

    errors_html = ""
    if errors:
        errors_html = "<h2>Errors</h2><ul>"
        for error in errors:
            errors_html += f"<li>{_escape_html(error)}</li>"
        errors_html += "</ul>"

    links_html = ""
    if status == "done" and result_status:
        links_html = """
        <h2>View Results</h2>
        <ul>
            <li><a href="/plain">Friendly Report</a></li>
            <li><a href="/report">Technical Report</a></li>
            <li><a href="/fixpack">Action Plan</a></li>
            <li><a href="/agent">Agent Prompt</a></li>
        </ul>
        """

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VibeGate UI - Run {run_id}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{status_emoji} Run {run_id}</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; <a href="/runs">Run History</a> &gt; {run_id}
            </nav>
        </header>

        <div style="border-left: 4px solid {status_color}; padding-left: 15px; margin: 20px 0;">
            <p><strong>Status:</strong> {status} {f"({result_status})" if result_status else ""}</p>
            <p><strong>Started:</strong> {started_at}</p>
            <p><strong>Finished:</strong> {finished_at if finished_at else "In progress..."}</p>
        </div>

        {summary_html}
        {errors_html}
        {links_html}

        <footer>
            <a href="/runs">Back to Run History</a> | <a href="/">Home</a>
        </footer>
    </div>
</body>
</html>
"""


def _render_compare_selection_page(runs: list[dict]) -> str:
    """Render comparison selection page."""
    if not runs:
        options_html = '<option value="">No runs available</option>'
    else:
        options = []
        for run in runs:
            run_id = run["run_id"]
            status = run.get("result_status", run.get("status", "UNKNOWN"))
            timestamp = run.get("started_at", "Unknown time")[:19].replace("T", " ")
            label = f"{run_id} - {status} - {timestamp}"
            options.append(f'<option value="{run_id}">{_escape_html(label)}</option>')
        options_html = "\n".join(options)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compare Runs - VibeGate</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{ display: block; margin-bottom: 0.5rem; font-weight: bold; }}
        select {{ width: 100%; padding: 0.75rem; font-size: 1rem; border: 1px solid #ddd; border-radius: 4px; }}
        .compare-btn {{ background: #007bff; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; }}
        .compare-btn:hover {{ background: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Compare Runs</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; <a href="/runs">Runs</a> &gt; Compare
            </nav>
        </header>
        <p>Select two runs to compare their findings.</p>
        <form id="compare-form">
            <div class="form-group">
                <label for="base-run">Base Run (older):</label>
                <select id="base-run" name="base" required>
                    <option value="">Select base run...</option>
                    {options_html}
                </select>
            </div>
            <div class="form-group">
                <label for="target-run">Target Run (newer):</label>
                <select id="target-run" name="target" required>
                    <option value="">Select target run...</option>
                    {options_html}
                </select>
            </div>
            <button type="submit" class="compare-btn">Compare</button>
        </form>
        <footer><a href="/runs">Back to Runs</a></footer>
    </div>
    <script>
        document.getElementById('compare-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            const base = document.getElementById('base-run').value;
            const target = document.getElementById('target-run').value;
            if (!base || !target) {{ alert('Please select both runs'); return; }}
            if (base === target) {{ alert('Please select different runs'); return; }}
            window.location.href = `/compare/result?base=${{base}}&target=${{target}}`;
        }});
    </script>
</body>
</html>"""


def _render_comparison_result(result: ComparisonResult, filter_query: str = "") -> str:
    """
    Render comparison result page.

    Args:
        result: ComparisonResult with comparison data
        filter_query: Optional search filter for issue tables

    Returns:
        HTML string with complete comparison result page
    """
    base_time = result.base_meta.get("started_at", "Unknown")[:19].replace("T", " ")
    target_time = result.target_meta.get("started_at", "Unknown")[:19].replace("T", " ")

    errors_html = ""
    if result.base_errors or result.target_errors:
        error_items = []
        for err in result.base_errors:
            error_items.append(f"<li>Base: {_escape_html(err)}</li>")
        for err in result.target_errors:
            error_items.append(f"<li>Target: {_escape_html(err)}</li>")
        errors_html = f'<div class="card" style="border-left: 4px solid #ffc107; margin-bottom: 2rem;"><h3>⚠️ Warnings</h3><ul>{"".join(error_items)}</ul></div>'

    severity_html = _render_severity_breakdown(result)
    category_html = _render_category_breakdown(result)
    new_table = _render_issues_table(
        result.new_issues, limit=50, filter_query=filter_query
    )
    fixed_table = _render_issues_table(
        result.fixed_issues, limit=50, filter_query=filter_query
    )
    same_table = _render_issues_table(
        result.same_issues, limit=50, filter_query=filter_query
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparison Result - VibeGate</title>
    <link rel="stylesheet" href="/static/style.css">
    <style>
        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 2rem 0; }}
        .stat {{ font-size: 3rem; font-weight: bold; margin: 0.5rem 0; }}
        .run-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem; }}
        details {{ margin-top: 1rem; border: 1px solid #ddd; border-radius: 4px; padding: 1rem; }}
        summary {{ cursor: pointer; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Comparison Result</h1>
            <nav class="breadcrumb">
                <a href="/">Home</a> &gt; <a href="/runs">Runs</a> &gt; <a href="/compare">Compare</a> &gt; Result
            </nav>
        </header>
        <div class="run-info">
            <div class="card">
                <h3>Base Run</h3>
                <p><strong>ID:</strong> {result.base_run_id}</p>
                <p><strong>Status:</strong> {result.base_meta.get("result_status", "UNKNOWN")}</p>
                <p><strong>Time:</strong> {base_time}</p>
            </div>
            <div class="card">
                <h3>Target Run</h3>
                <p><strong>ID:</strong> {result.target_run_id}</p>
                <p><strong>Status:</strong> {result.target_meta.get("result_status", "UNKNOWN")}</p>
                <p><strong>Time:</strong> {target_time}</p>
            </div>
        </div>
        {errors_html}
        <h2>Summary</h2>
        <div class="summary-cards">
            <div class="card" style="border-left: 4px solid #dc3545;">
                <h3>🔴 New Issues</h3>
                <div class="stat">{result.new_count}</div>
                <p>Found in target, not in base</p>
            </div>
            <div class="card" style="border-left: 4px solid #28a745;">
                <h3>✅ Fixed Issues</h3>
                <div class="stat">{result.fixed_count}</div>
                <p>Found in base, resolved in target</p>
            </div>
            <div class="card" style="border-left: 4px solid #6c757d;">
                <h3>⚪ Unchanged Issues</h3>
                <div class="stat">{result.same_count}</div>
                <p>Present in both runs</p>
            </div>
        </div>
        {severity_html}
        {category_html}
        <details>
            <summary>Technical Details - New Issues ({result.new_count})</summary>
            {new_table}
        </details>
        <details>
            <summary>Technical Details - Fixed Issues ({result.fixed_count})</summary>
            {fixed_table}
        </details>
        <details>
            <summary>Persistent Issues ({result.same_count})</summary>
            {same_table}
        </details>
        <footer>
            <a href="/compare">Compare Other Runs</a> | <a href="/runs">Back to Runs</a>
        </footer>
    </div>
</body>
</html>"""


def _render_issues_table(
    issues: list[dict], limit: int = 50, filter_query: str = ""
) -> str:
    """
    Render table of issues with optional filtering and pagination.

    Args:
        issues: List of issue dicts
        limit: Maximum issues to show (default 50)
        filter_query: Optional search filter (file path or message contains)

    Returns:
        HTML string with issues table
    """
    if not issues:
        return "<p>No issues in this category.</p>"

    # Apply filter if provided
    filtered_issues = issues
    if filter_query:
        filter_lower = filter_query.lower()
        filtered_issues = [
            issue
            for issue in issues
            if (
                filter_lower in str(issue.get("file_path", "")).lower()
                or filter_lower
                in str(
                    issue.get("file_targets", [""])[0]
                    if issue.get("file_targets")
                    else ""
                ).lower()
                or filter_lower in str(issue.get("title", "")).lower()
                or filter_lower in str(issue.get("description", "")).lower()
            )
        ]

    total_count = len(filtered_issues)
    display_issues = filtered_issues[:limit]
    remaining = max(0, total_count - limit)

    # Severity badge helper
    def severity_badge(severity: str) -> str:
        colors = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#17a2b8",
            "info": "#6c757d",
        }
        color = colors.get(severity, "#6c757d")
        return f'<span style="background: {color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; font-weight: bold;">{severity.upper()}</span>'

    rows = []
    for issue in display_issues:
        file_path = ""
        if "file_targets" in issue and issue["file_targets"]:
            file_path = issue["file_targets"][0]
        elif "file_path" in issue:
            file_path = issue["file_path"]

        severity = issue.get("severity", "unknown")
        check_type = issue.get("type", "unknown")
        title = issue.get("title", "N/A")

        rows.append(
            f"<tr><td>{_escape_html(check_type)}</td><td>{severity_badge(severity)}</td><td>{_escape_html(file_path or 'N/A')}</td><td>{_escape_html(title)}</td></tr>"
        )

    pagination_notice = ""
    if remaining > 0:
        pagination_notice = f'<p style="color: #856404; background: #fff3cd; padding: 10px; border-radius: 4px; margin-top: 1rem;"><strong>Note:</strong> Showing top {limit} of {total_count} issues. {remaining} more not displayed. Use search/filter to narrow results.</p>'

    filter_hint = ""
    if filter_query:
        filter_hint = f'<p style="margin-bottom: 0.5rem;"><em>Filtered by: "{_escape_html(filter_query)}" ({total_count} matches)</em></p>'

    return f"""
        {filter_hint}
        <table>
            <thead>
                <tr>
                    <th>Check Type</th>
                    <th>Severity</th>
                    <th>File</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
        {pagination_notice}
    """


def _render_category_breakdown(result: ComparisonResult) -> str:
    """Render category breakdown."""
    if not result.new_by_category and not result.fixed_by_category:
        return ""

    new_rows = "".join(
        f"<tr><td>{cat}</td><td>{count}</td></tr>"
        for cat, count in sorted(result.new_by_category.items())
    )
    fixed_rows = "".join(
        f"<tr><td>{cat}</td><td>{count}</td></tr>"
        for cat, count in sorted(result.fixed_by_category.items())
    )

    return f"""<details>
        <summary>Category Breakdown</summary>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <h4>New Issues by Category</h4>
                <table><thead><tr><th>Category</th><th>Count</th></tr></thead><tbody>{new_rows or '<tr><td colspan="2">None</td></tr>'}</tbody></table>
            </div>
            <div>
                <h4>Fixed Issues by Category</h4>
                <table><thead><tr><th>Category</th><th>Count</th></tr></thead><tbody>{fixed_rows or '<tr><td colspan="2">None</td></tr>'}</tbody></table>
            </div>
        </div>
    </details>"""


def _render_severity_breakdown(result: ComparisonResult) -> str:
    """
    Render severity breakdown chart using plain HTML horizontal bars.

    Shows visual distribution of issues by severity level (critical, high, medium, low, info)
    using horizontal bar charts with color coding.

    Args:
        result: ComparisonResult with severity breakdown data

    Returns:
        HTML string with severity breakdown charts
    """
    if not result.new_by_severity and not result.fixed_by_severity:
        return ""

    # Severity order (most severe first)
    severity_order = ["critical", "high", "medium", "low", "info"]

    # Color mapping for severity levels
    severity_colors = {
        "critical": "#dc3545",  # red
        "high": "#fd7e14",  # orange
        "medium": "#ffc107",  # yellow
        "low": "#17a2b8",  # cyan
        "info": "#6c757d",  # gray
    }

    # Build new issues chart
    new_max = max(result.new_by_severity.values()) if result.new_by_severity else 1
    new_rows = []
    for sev in severity_order:
        count = result.new_by_severity.get(sev, 0)
        if count > 0:
            width_pct = (count / new_max) * 100 if new_max > 0 else 0
            color = severity_colors.get(sev, "#6c757d")
            new_rows.append(
                f"""
                <tr>
                    <td><strong>{sev.capitalize()}</strong></td>
                    <td style="width: 60%;">
                        <div style="background: {color}; width: {width_pct}%; padding: 4px 8px; border-radius: 3px; color: white; font-weight: bold;">
                            {count}
                        </div>
                    </td>
                </tr>
            """
            )

    # Build fixed issues chart
    fixed_max = (
        max(result.fixed_by_severity.values()) if result.fixed_by_severity else 1
    )
    fixed_rows = []
    for sev in severity_order:
        count = result.fixed_by_severity.get(sev, 0)
        if count > 0:
            width_pct = (count / fixed_max) * 100 if fixed_max > 0 else 0
            color = severity_colors.get(sev, "#6c757d")
            fixed_rows.append(
                f"""
                <tr>
                    <td><strong>{sev.capitalize()}</strong></td>
                    <td style="width: 60%;">
                        <div style="background: {color}; width: {width_pct}%; padding: 4px 8px; border-radius: 3px; color: white; font-weight: bold;">
                            {count}
                        </div>
                    </td>
                </tr>
            """
            )

    new_chart_html = (
        f"""
        <table style="width: 100%; margin-top: 1rem;">
            <tbody>
                {"".join(new_rows) if new_rows else '<tr><td colspan="2">No new issues</td></tr>'}
            </tbody>
        </table>
    """
        if new_rows
        else "<p>No new issues by severity.</p>"
    )

    fixed_chart_html = (
        f"""
        <table style="width: 100%; margin-top: 1rem;">
            <tbody>
                {"".join(fixed_rows) if fixed_rows else '<tr><td colspan="2">No fixed issues</td></tr>'}
            </tbody>
        </table>
    """
        if fixed_rows
        else "<p>No fixed issues by severity.</p>"
    )

    return f"""
    <details open>
        <summary>Severity Breakdown</summary>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <h4>New Issues by Severity</h4>
                {new_chart_html}
            </div>
            <div>
                <h4>Fixed Issues by Severity</h4>
                {fixed_chart_html}
            </div>
        </div>
    </details>
    """


def serve(
    repo_root: Path,
    host: str = "127.0.0.1",
    port: int = 8787,
    open_browser: bool = True,
    static_mode: bool = False,
    runs_dir: Optional[Path] = None,
) -> None:
    """Start the VibeGate UI server.

    Args:
        repo_root: Repository root directory
        host: Host to bind to
        port: Port to bind to
        open_browser: Whether to open browser automatically
        static_mode: If True, disable run triggers (read-only mode)
        runs_dir: Directory for storing UI run sessions (unused in static mode)

    Raises:
        ValueError: If repo_root is invalid
    """
    if not repo_root.exists():
        raise ValueError(f"Repository root does not exist: {repo_root}")

    if not repo_root.is_dir():
        raise ValueError(f"Repository root is not a directory: {repo_root}")

    app = create_app(repo_root, static_mode, runs_dir)

    # Open browser after server starts
    if open_browser:
        url = f"http://{host}:{port}"

        def open_browser_callback() -> None:
            webbrowser.open(url)

        # Schedule browser open after a brief delay
        import threading

        threading.Timer(1.0, open_browser_callback).start()

    # Run server
    uvicorn.run(app, host=host, port=port, log_level="info")
