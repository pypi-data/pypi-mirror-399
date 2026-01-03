"""Terminal summary rendering for VibeGate runs."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_fixpack(path: Path) -> dict[str, Any] | None:
    """Load fixpack JSON from path.

    Args:
        path: Path to fixpack.json

    Returns:
        Fixpack dict or None if not found/invalid
    """
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _count_findings_by_severity(fixpack: dict[str, Any]) -> dict[str, int]:
    """Count findings by severity from fixpack groups.

    Note: Fixpack tasks don't have severity, so we infer from task type.
    """
    severity_map = {
        "vulnerability_fix": "critical",
        "secret_removal": "critical",
        "security_fix": "high",
        "type_fix": "high",
        "test_fix": "high",
        "error_handling_fix": "medium",
        "defensive_coding_fix": "medium",
        "complexity_fix": "medium",
        "dead_code_fix": "low",
        "coverage_fix": "low",
        "lint_fix": "low",
        "formatting_fix": "info",
        "dependency_fix": "medium",
        "config_fix": "medium",
        "runtime_fix": "high",
        "tooling_fix": "high",
    }

    counts: dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
    }
    groups = fixpack.get("groups", [])
    for group in groups:
        tasks = group.get("tasks", [])
        for task in tasks:
            task_type = task.get("type", "")
            severity = severity_map.get(task_type, "low")
            counts[severity] = counts.get(severity, 0) + 1

    return counts


def _format_task_summary(task: dict[str, Any], max_title_len: int = 60) -> str:
    """Format a single task as a one-line summary.

    Args:
        task: Task dict from fixpack
        max_title_len: Max length for task title

    Returns:
        Formatted string like "  • Fix type errors in foo.py (3 findings)"
    """
    title = task.get("title", "Untitled task")
    if len(title) > max_title_len:
        title = title[: max_title_len - 3] + "..."

    # Count findings (references are fingerprints)
    refs = task.get("references", [])
    finding_count = len(refs)

    # Get verification command if present
    verification = task.get("verification_commands", [])
    cmd_hint = ""
    if verification:
        # Extract short command name
        first_cmd = verification[0]
        if "ruff" in first_cmd:
            cmd_hint = " [ruff]"
        elif "pyright" in first_cmd:
            cmd_hint = " [pyright]"
        elif "pytest" in first_cmd:
            cmd_hint = " [pytest]"

    finding_text = "finding" if finding_count == 1 else "findings"
    return f"  • {title} ({finding_count} {finding_text}){cmd_hint}"


def render_summary(
    fixpack: dict[str, Any],
    status: str,
    outputs: dict[str, str],
    detail: str,
    profile: str | None = None,
    max_tasks: int = 5,
) -> str:
    """Render a terminal-friendly summary of a VibeGate run.

    Args:
        fixpack: Fixpack payload dict
        status: PASS or FAIL
        outputs: Dict with output paths (evidence_jsonl, fixpack_json, etc.)
        detail: Detail level (simple or deep)
        profile: Profile name if used
        max_tasks: Maximum number of tasks to show per category

    Returns:
        Formatted summary string ready to print
    """
    lines = []

    # Header
    lines.append("")
    lines.append("=" * 60)
    lines.append("  VibeGate Run Summary")
    lines.append("=" * 60)
    lines.append("")

    # Status and metadata
    status_color = "PASS ✓" if status == "PASS" else "FAIL ✗"
    lines.append(f"Status:   {status_color}")

    if profile:
        lines.append(f"Profile:  {profile}")

    # Extract timestamp from fixpack
    generated_at = fixpack.get("generated_at", "")
    if generated_at:
        try:
            dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
            lines.append(f"Run at:   {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        except ValueError:
            pass

    lines.append("")

    # Counts
    groups = fixpack.get("groups", [])
    total_tasks = sum(len(group.get("tasks", [])) for group in groups)

    lines.append("Findings:")
    if total_tasks == 0:
        lines.append("  No issues found!")
    else:
        by_severity = _count_findings_by_severity(fixpack)
        lines.append(f"  Total tasks: {total_tasks}")

        # Show severity breakdown
        severity_order = ["critical", "high", "medium", "low", "info"]
        severity_symbols = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵",
            "info": "⚪",
        }
        for severity in severity_order:
            count = by_severity.get(severity, 0)
            if count > 0:
                symbol = severity_symbols.get(severity, "•")
                lines.append(f"  {symbol} {severity.capitalize()}: {count}")

    lines.append("")

    # Top tasks section
    if total_tasks > 0:
        lines.append("Top Tasks:")
        lines.append("")

        # Flatten all tasks with their group info
        all_tasks = []
        for group in groups:
            group_title = group.get("title", "")
            group_order = group.get("order", 0)
            for task in group.get("tasks", []):
                all_tasks.append(
                    {
                        "task": task,
                        "group_title": group_title,
                        "group_order": group_order,
                        "task_order": task.get("order", 0),
                    }
                )

        # Sort by group order, then task order
        all_tasks = sorted(all_tasks, key=lambda x: (x["group_order"], x["task_order"]))

        # Group by category and show top N per category
        current_group = None
        shown_in_group = 0

        for item in all_tasks:
            group_title = item["group_title"]
            task = item["task"]

            # Start new group if needed
            if group_title != current_group:
                current_group = group_title
                shown_in_group = 0
                lines.append(f"{group_title}:")

            # Show up to max_tasks per group
            if shown_in_group < max_tasks:
                lines.append(_format_task_summary(task))
                shown_in_group += 1

        # Show count of remaining tasks if any
        total_shown = sum(min(len(g.get("tasks", [])), max_tasks) for g in groups)
        if total_tasks > total_shown:
            lines.append("")
            lines.append(f"...and {total_tasks - total_shown} more tasks")

        lines.append("")

    # Next steps
    lines.append("Next Steps:")

    if status == "PASS":
        lines.append("  ✓ All checks passed! No action needed.")
        lines.append("  • Run regularly to catch issues early")
    else:
        lines.append("  1. Review fixpack for detailed remediation steps")
        lines.append("  2. Fix high-priority issues first (security, bugs)")
        lines.append("  3. Run VibeGate again to verify fixes")

    lines.append("")

    # Output files
    lines.append("Outputs:")
    fixpack_path = outputs.get("fixpack_json", ".vibegate/artifacts/fixpack.json")
    lines.append(f"  • Fix pack:  {fixpack_path}")

    report_path = outputs.get(
        "report_markdown", ".vibegate/artifacts/vibegate_report.md"
    )
    lines.append(f"  • Report:    {report_path}")

    evidence_path = outputs.get("evidence_jsonl", ".vibegate/evidence/vibegate.jsonl")
    lines.append(f"  • Evidence:  {evidence_path}")

    lines.append("")

    # Commands
    lines.append("Commands:")
    lines.append("  • View in UI:      vibegate view .")

    # Rerun command
    rerun_parts = ["vibegate run ."]
    if profile:
        rerun_parts.append(f"--profile {profile}")
    if detail != "simple":
        rerun_parts.append(f"--detail {detail}")
    rerun_parts.append("--no-view")
    lines.append(f"  • Rerun:           {' '.join(rerun_parts)}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)
