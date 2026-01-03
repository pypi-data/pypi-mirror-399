from __future__ import annotations

import importlib
import importlib.util
import json
import logging
from pathlib import Path
from typing import List, Optional, Set, Tuple

import typer
import yaml

from vibegate import __version__
from vibegate.checks import tool_exists, tool_version
from vibegate.config import ConfigError, VibeGateConfig, load_config
from vibegate.evidence import load_run_summary
from vibegate.runner import run_check, run_fixpack
from vibegate.ux.summary import load_fixpack, render_summary

app = typer.Typer(help="VibeGate CLI")
logger = logging.getLogger(__name__)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the VibeGate version and exit.",
    ),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command(hidden=True)
def check(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    detail: str = typer.Option(
        "simple",
        "--detail",
        help="Detail level for plain report: simple or deep",
    ),
) -> None:
    """Run VibeGate checks and create proof files (low-level command)."""
    repo_root = repo_root.resolve()

    # Validate detail level
    if detail not in ("simple", "deep"):
        typer.secho(
            f"Invalid detail level: {detail}. Must be 'simple' or 'deep'.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)

    # Load config (works with or without vibegate.yaml)
    try:
        config = load_config(repo_root)
    except ConfigError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=2) from exc

    # Enable UI comparison for CLI runs
    runs_dir = repo_root / ".vibegate" / "ui" / "runs"
    artifacts, status = run_check(
        config, repo_root, detail_level=detail, runs_dir=runs_dir
    )
    _print_outputs(config, artifacts)
    _print_summary(status, config)
    if status == "FAIL":
        raise typer.Exit(code=1)


@app.command()
def run(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    detail: str = typer.Option(
        "simple",
        "--detail",
        help="Detail level for plain report: simple or deep",
    ),
    skip_doctor: bool = typer.Option(
        False,
        "--skip-doctor",
        help="Skip tool verification check",
    ),
    view: Optional[bool] = typer.Option(
        None,
        "--view/--no-view",
        help="Auto-open UI after run (default: auto-detect TTY/CI)",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        help="Select profile from vibegate.yaml",
    ),
    summary: str = typer.Option(
        "short",
        "--summary",
        help="Summary mode: none, short, or full",
    ),
    max_tasks: int = typer.Option(
        5,
        "--max-tasks",
        help="Maximum tasks to show per category in summary",
    ),
) -> None:
    """Run VibeGate checks (primary command).

    This is the recommended entry point for running quality checks.
    Works without vibegate.yaml (uses sensible defaults).
    Runs tool verification first, then executes all enabled checks.
    """
    import os
    import sys

    repo_root = repo_root.resolve()

    # Validate detail level
    if detail not in ("simple", "deep"):
        typer.secho(
            f"Invalid detail level: {detail}. Must be 'simple' or 'deep'.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)

    # Validate summary mode
    if summary not in ("none", "short", "full"):
        typer.secho(
            f"Invalid summary mode: {summary}. Must be 'none', 'short', or 'full'.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)

    # Run doctor first (unless skipped)
    if not skip_doctor:
        typer.echo("Verifying tools...")
        try:
            # Load config to check which tools are required
            cli_overrides = {}
            if profile:
                cli_overrides["profile"] = profile

            config = load_config(repo_root, cli_overrides=cli_overrides)

            required_tools = _required_tools(config)
            missing = [tool for tool in sorted(required_tools) if not tool_exists(tool)]

            if missing:
                typer.secho("Missing required tools:", fg=typer.colors.RED)
                for tool in sorted(set(missing)):
                    typer.echo(f"- {tool}")
                typer.echo("\nInstall missing tools and try again.")
                typer.echo('Run: pip install "vibegate[tools]" or see vibegate doctor')
                raise typer.Exit(code=2)

            typer.secho("✓ All required tools available", fg=typer.colors.GREEN)
        except ConfigError as exc:
            typer.secho(f"Configuration error: {exc}", fg=typer.colors.RED)
            raise typer.Exit(code=2) from exc

    # Load config (works with or without vibegate.yaml)
    typer.echo("\nRunning checks...")
    try:
        cli_overrides = {}
        if profile:
            cli_overrides["profile"] = profile
        config = load_config(repo_root, cli_overrides=cli_overrides)
    except ConfigError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=2) from exc

    # Enable UI comparison for CLI runs
    runs_dir = repo_root / ".vibegate" / "ui" / "runs"
    artifacts, status = run_check(
        config, repo_root, detail_level=detail, runs_dir=runs_dir
    )
    _print_outputs(config, artifacts)
    _print_summary(status, config)

    # Print terminal summary if requested
    if summary != "none":
        fixpack_path = repo_root / config.outputs.fixpack_json
        fixpack_data = load_fixpack(fixpack_path)
        if fixpack_data:
            # Prepare outputs dict for summary
            outputs = {
                "fixpack_json": str(config.outputs.fixpack_json),
                "report_markdown": str(config.outputs.report_markdown),
                "evidence_jsonl": str(config.outputs.evidence_jsonl),
            }
            # Adjust max_tasks for summary mode
            tasks_to_show = max_tasks if summary == "short" else 999
            summary_text = render_summary(
                fixpack=fixpack_data,
                status=status,
                outputs=outputs,
                detail=detail,
                profile=profile,
                max_tasks=tasks_to_show,
            )
            typer.echo(summary_text)

    # Auto-open UI if appropriate
    should_view = view
    if should_view is None:
        # Auto-detect: view if TTY and not CI
        is_tty = sys.stdin.isatty()
        is_ci = os.environ.get("CI", "").lower() in ("true", "1", "yes")
        should_view = is_tty and not is_ci

    if should_view:
        typer.echo("\n" + "=" * 60)
        typer.secho("Opening UI viewer...", fg=typer.colors.CYAN, bold=True)
        typer.echo("=" * 60)
        typer.echo("Press Ctrl+C to stop the server and return to shell.\n")
        try:
            # Check UI deps
            ok, message = _check_ui_deps()
            if not ok:
                typer.secho(f"UI not available: {message}", fg=typer.colors.YELLOW)
                typer.echo(f"\nTo view results later: vibegate view {repo_root}")
            else:
                from vibegate.ui.server import serve

                # Open UI in static mode
                serve(
                    repo_root=repo_root,
                    host="127.0.0.1",
                    port=8787,
                    open_browser=True,
                    static_mode=True,
                    runs_dir=runs_dir,
                )
        except KeyboardInterrupt:
            typer.echo("\nUI server stopped.")
        except Exception as e:
            logger.debug(f"UI server error: {e}")
            typer.secho(
                f"\nUI server error. View results with: vibegate view {repo_root}",
                fg=typer.colors.YELLOW,
            )

    if status == "FAIL":
        raise typer.Exit(code=1)


@app.command(hidden=True)
def verify(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    detail: str = typer.Option(
        "simple",
        "--detail",
        help="Detail level for plain report: simple or deep",
    ),
) -> None:
    """Deprecated: Use 'vibegate run' instead."""
    typer.secho(
        "⚠️  WARNING: 'vibegate verify' is deprecated. Use 'vibegate run' instead.",
        fg=typer.colors.YELLOW,
        bold=True,
    )
    typer.echo("")
    run(
        repo_root,
        detail,
        skip_doctor=False,
        view=None,
        profile=None,
        summary="short",
        max_tasks=5,
    )


@app.command()
def view(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind to"),
    port: int = typer.Option(8787, "--port", help="Port to bind to"),
    runs_dir: Path = typer.Option(
        Path(".vibegate/ui/runs"),
        "--runs-dir",
        help="Where to store UI run sessions",
    ),
) -> None:
    """Open the web UI viewer in read-only mode.

    Launches the VibeGate web interface to browse check results,
    view reports, and explore findings. Read-only - cannot trigger
    new runs from the UI (use 'vibegate run' from CLI instead).
    """
    repo_root = repo_root.resolve()

    # Check UI deps
    ok, message = _check_ui_deps()
    if not ok:
        typer.secho(message, fg=typer.colors.RED)
        raise typer.Exit(code=2)

    try:
        from vibegate.ui.server import serve

        # Launch UI in static mode with browser
        serve(
            repo_root=repo_root,
            host=host,
            port=port,
            open_browser=True,
            static_mode=True,
            runs_dir=runs_dir if runs_dir.is_absolute() else repo_root / runs_dir,
        )
    except KeyboardInterrupt:
        typer.echo("\nUI server stopped.")
    except Exception as e:
        typer.secho(f"Failed to start UI: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=2) from e


@app.command(hidden=True)
def fixpack(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Emit placeholder fix pack artifacts."""
    repo_root = repo_root.resolve()
    try:
        config = load_config(repo_root)
    except ConfigError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=2) from exc

    artifacts, status = run_fixpack(config, repo_root)
    _print_outputs(config, artifacts)
    if status == "FAIL":
        raise typer.Exit(code=1)


@app.command("fixpack-list", hidden=True)
def fixpack_list(
    path: Path = typer.Option(
        Path(".vibegate/artifacts/fixpack.json"),
        "--path",
        help="Path to the fixpack JSON file.",
    ),
) -> None:
    """Print a TSV summary of fixpack tasks."""
    if not path.exists():
        typer.secho(f"Fixpack not found at {path}", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    with path.open("r", encoding="utf-8") as handle:
        fixpack = json.load(handle)
    groups = fixpack.get("groups", [])
    if not isinstance(groups, list):
        typer.secho("Fixpack groups are invalid.", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    rows: List[Tuple[int, int, str, str, str]] = []
    for group in groups:
        group_order = group.get("order")
        if not isinstance(group_order, int):
            group_order = 0
        tasks = group.get("tasks", [])
        if not isinstance(tasks, list):
            continue
        for task in tasks:
            task_id = task.get("id", "")
            title = task.get("title", "")
            severity = task.get("severity", "unknown")
            task_order = task.get("order")
            if not isinstance(task_order, int):
                task_order = 0
            rows.append(
                (
                    group_order,
                    task_order,
                    str(task_id),
                    str(title),
                    str(severity),
                )
            )
    for _, _, task_id, title, severity in sorted(
        rows, key=lambda item: (item[0], item[1], item[2])
    ):
        typer.echo(f"{task_id}\t{title}\t{severity}")


def _check_ui_deps() -> tuple[bool, str]:
    missing = []
    for name in ("typing_extensions", "fastapi", "uvicorn"):
        if importlib.util.find_spec(name) is None:
            missing.append(name)
    if missing:
        return (
            False,
            "Missing UI dependency modules: "
            + ", ".join(missing)
            + '. Run: pip install "vibegate[ui]"',
        )
    try:
        import typing_extensions  # noqa: F401
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        return (
            False,
            "UI dependencies import failed. "
            f"{type(exc).__name__}: {exc}. "
            'Reinstall with: pip install --force-reinstall "vibegate[ui]"',
        )
    return True, ""


@app.command(hidden=True)
def ui(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8787, "--port"),
    open_browser: bool = typer.Option(True, "--open/--no-open"),
    static: bool = typer.Option(
        False, "--static", help="Read-only mode; do not run checks from UI"
    ),
    runs_dir: Path = typer.Option(
        Path(".vibegate/ui/runs"),
        "--runs-dir",
        help="Where to store UI run sessions",
    ),
) -> None:
    """Start the local VibeGate UI server."""
    repo_root = repo_root.resolve()
    ok, message = _check_ui_deps()
    if not ok:
        typer.secho(message, fg=typer.colors.RED)
        raise typer.Exit(code=2)
    try:
        from vibegate.ui.server import serve
    except ModuleNotFoundError as exc:
        if exc.name in {
            "fastapi",
            "uvicorn",
            "starlette",
            "typing_extensions",
            "pydantic",
            "pydantic_core",
        }:
            typer.secho(
                'UI dependencies not installed. Run: pip install "vibegate[ui]"',
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=2) from exc
        raise

    try:
        serve(
            repo_root=repo_root,
            host=host,
            port=port,
            open_browser=open_browser,
            static_mode=static,
            runs_dir=runs_dir,
        )
    except ValueError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=2) from exc


@app.command()
def init(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite vibegate.yaml if it already exists.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip interactive prompts and use recommended defaults.",
    ),
    profile: str = typer.Option(
        "balanced",
        "--profile",
        help="Builtin profile to use (fast, balanced, strict, ci).",
    ),
    no_labels: bool = typer.Option(
        False,
        "--no-labels",
        help="Skip creating labels.yaml.",
    ),
) -> None:
    """Generate a minimal vibegate.yaml and supporting directories."""
    import sys

    repo_root = repo_root.resolve()
    if not isinstance(force, bool):
        force = False
    created: List[Path] = []

    # Interactive prompts (only if not --yes and running in TTY)
    use_interactive = not yes and sys.stdin.isatty()
    create_labels = not no_labels  # default to True unless --no-labels
    llm_config = None  # LLM configuration from wizard

    if use_interactive:
        typer.echo("Initializing VibeGate configuration...\n")
        if not no_labels:
            create_labels_input = typer.prompt(
                "Create labels.yaml for tracking false positives?",
                default="yes",
                type=str,
            )
            create_labels = create_labels_input.lower() in ("y", "yes", "")

        # Run LLM setup wizard
        try:
            from vibegate.llm.setup import run_llm_setup_wizard

            llm_config = run_llm_setup_wizard()
        except ImportError:
            # LLM module not available (ollama not installed)
            typer.echo(
                "\nNote: Install with 'pip install vibegate[llm]' for AI assistant features"
            )
        except Exception as e:
            typer.secho(f"\nLLM setup failed: {e}", fg=typer.colors.YELLOW)

    contract_path = repo_root / "vibegate.yaml"
    if contract_path.exists() and not force:
        typer.secho(
            "vibegate.yaml already exists. Use --force to overwrite.",
            fg=typer.colors.YELLOW,
        )
    else:
        # Write minimal config using selected profile
        contract = {
            "schema_version": "v1alpha1",
            "project": {
                "name": repo_root.name,
                "language": "python",
            },
            "profile": profile,
        }

        # Add LLM config if wizard completed
        if llm_config:
            contract["llm"] = {
                "enabled": llm_config.get("enabled", True),
                "provider": llm_config.get("provider", "ollama"),
                "cache_dir": ".vibegate/llm_cache",
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "model": llm_config.get("model", "codellama:7b"),
                    "temperature": 0.3,
                },
                "features": {
                    "explain_findings": True,
                    "generate_prompts": True,
                },
            }

        contract_path.write_text(
            yaml.safe_dump(contract, sort_keys=False), encoding="utf-8"
        )
        created.append(contract_path)

    # Create .vibegate directory structure
    for dirname in (".vibegate", ".vibegate/artifacts", ".vibegate/evidence"):
        directory = repo_root / dirname
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory)

    # Create LLM cache directory if LLM is configured
    if llm_config:
        llm_cache_dir = repo_root / ".vibegate" / "llm_cache"
        if not llm_cache_dir.exists():
            llm_cache_dir.mkdir(parents=True, exist_ok=True)
            created.append(llm_cache_dir)

    suppressions_path = repo_root / ".vibegate" / "suppressions.yaml"
    if not suppressions_path.exists() or force:
        suppressions_path.parent.mkdir(parents=True, exist_ok=True)
        suppressions_path.write_text(_suppressions_template(), encoding="utf-8")
        if suppressions_path not in created:
            created.append(suppressions_path)

    if create_labels:
        labels_path = repo_root / ".vibegate" / "labels.yaml"
        if not labels_path.exists() or force:
            labels_path.parent.mkdir(parents=True, exist_ok=True)
            labels_path.write_text(_labels_template(), encoding="utf-8")
            if labels_path not in created:
                created.append(labels_path)

    typer.echo("\nCreated:")
    if created:
        for path in created:
            typer.echo(f"  - {path.relative_to(repo_root)}")
    else:
        typer.echo("  - (nothing)")

    typer.echo("\nNext steps:")
    typer.echo("  1. vibegate doctor .")
    typer.echo("  2. vibegate run .")


@app.command()
def doctor(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Verify required tools and versions for enabled checks."""
    repo_root = repo_root.resolve()
    try:
        config = load_config(repo_root)
    except ConfigError as exc:
        typer.secho(str(exc), fg=typer.colors.RED)
        raise typer.Exit(code=2) from exc

    required_tools = _required_tools(config)
    missing = [tool for tool in sorted(required_tools) if not tool_exists(tool)]

    mismatches: List[Tuple[str, str, str]] = []
    for tool, expected in config.determinism.tool_versions.items():
        if not tool_exists(tool):
            if tool not in missing:
                missing.append(tool)
            continue
        observed_raw = tool_version(tool)
        observed = _extract_version(observed_raw) or observed_raw
        if observed != expected:
            mismatches.append((tool, expected, observed_raw))

    if missing:
        typer.secho("Missing required tools:", fg=typer.colors.RED)
        for tool in sorted(set(missing)):
            typer.echo(f"- {tool}")

    if mismatches:
        typer.secho("Version mismatches:", fg=typer.colors.RED)
        for tool, expected, observed in mismatches:
            typer.echo(f"- {tool}: expected {expected}, observed {observed}")

    if not missing and not mismatches:
        typer.secho("All required tools are available.", fg=typer.colors.GREEN)

    if missing or mismatches:
        typer.echo("\nInstall guidance:")
        typer.echo(
            '- All tools at once: pip install "vibegate[tools]" '
            '(or: pipx install "vibegate[tools]")'
        )
        typer.echo("\nIndividual tool installation:")
        guidance_tools = sorted(set(missing + [tool for tool, _, _ in mismatches]))
        for tool in guidance_tools:
            expected = config.determinism.tool_versions.get(tool)
            typer.echo(f"  {tool}: {_install_guidance(tool, expected)}")
        raise typer.Exit(code=1)


@app.command(hidden=True)
def prompt() -> None:
    """Stub command for future prompt-based workflows."""
    typer.echo("not implemented")


@app.command(hidden=True)
def label(
    fingerprint: str = typer.Argument(..., help="Finding fingerprint to label"),
    false_positive: bool = typer.Option(
        False, "--false-positive", help="Mark as false positive"
    ),
    true_positive: bool = typer.Option(
        False, "--true-positive", help="Mark as true positive"
    ),
    acceptable_risk: bool = typer.Option(
        False, "--acceptable-risk", help="Mark as acceptable risk"
    ),
    reason: str = typer.Option(..., "--reason", help="Short reason tag"),
    note: str = typer.Option("", "--note", help="Optional detailed note"),
    repo_root: Path = typer.Option(
        Path("."),
        "--repo",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Repository root directory",
    ),
) -> None:
    """Label a finding for false positive tracking.

    Labels help track finding quality but do NOT affect CI/CD behavior.
    Use suppressions.yaml to actually suppress findings in CI/CD.
    """
    from datetime import datetime, timezone

    repo_root = repo_root.resolve()

    # Validate exactly one label type
    label_flags = [false_positive, true_positive, acceptable_risk]
    if sum(label_flags) != 1:
        typer.secho(
            "Error: Specify exactly one of --false-positive, --true-positive, or --acceptable-risk",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=2)

    if false_positive:
        label_type = "false_positive"
    elif true_positive:
        label_type = "true_positive"
    else:
        label_type = "acceptable_risk"

    labels_path = repo_root / ".vibegate" / "labels.yaml"

    # Load existing labels or create new structure
    if labels_path.exists():
        with labels_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {"version": 1, "labels": []}

    labels_list = data.get("labels", [])
    if not isinstance(labels_list, list):
        labels_list = []

    # Find or create entry for this fingerprint
    existing_entry = None
    for entry in labels_list:
        if entry.get("fingerprint") == fingerprint:
            existing_entry = entry
            break

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if existing_entry:
        # Update existing entry
        existing_entry["label"] = label_type
        existing_entry["reason"] = reason
        existing_entry["note"] = note
        existing_entry["created_at"] = now_iso
        typer.echo(f"Updated label for fingerprint: {fingerprint[:12]}...")
    else:
        # Create new entry
        new_entry = {
            "fingerprint": fingerprint,
            "rule_id": "",  # Could be populated from evidence if available
            "label": label_type,
            "reason": reason,
            "note": note,
            "created_at": now_iso,
        }
        labels_list.append(new_entry)
        typer.echo(f"Added label for fingerprint: {fingerprint[:12]}...")

    data["labels"] = labels_list

    # Write back to file
    labels_path.parent.mkdir(parents=True, exist_ok=True)
    with labels_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)

    typer.secho(f"Label '{label_type}' saved to {labels_path}", fg=typer.colors.GREEN)
    typer.echo(f"Reason: {reason}")
    if note:
        typer.echo(f"Note: {note}")


@app.command(hidden=True)
def tune(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Repository root directory",
    ),
    evidence: Optional[Path] = typer.Option(
        None, "--evidence", help="Path to evidence JSONL file"
    ),
    labels: Optional[Path] = typer.Option(
        None, "--labels", help="Path to labels.yaml file"
    ),
    out: Path = typer.Option(
        Path(".vibegate/artifacts/tuning"),
        "--out",
        help="Output directory for tuning pack",
    ),
    max_examples: int = typer.Option(
        5, "--max-examples", help="Maximum examples per cluster"
    ),
    include_acceptable: bool = typer.Option(
        False, "--include-acceptable", help="Include acceptable_risk in analysis"
    ),
    format_type: str = typer.Option(
        "both", "--format", help="Output format: md, json, or both"
    ),
) -> None:
    """Analyze labeled findings and generate tuning recommendations.

    This command loads evidence from the last run and joins it with labels to:
    - Compute false positive rates by rule
    - Cluster similar false positives
    - Generate actionable tuning hints

    Output is deterministic and suitable for version control.
    """
    from vibegate import tuning as tuning_module

    repo_root = repo_root.resolve()

    # Resolve evidence path
    if evidence is None:
        # Try to load from state.json
        state_path = repo_root / ".vibegate" / "state.json"
        if state_path.exists():
            try:
                state_data = json.load(state_path.open("r", encoding="utf-8"))
                evidence_rel = state_data.get("last_run", {}).get("evidence_path")
                if evidence_rel:
                    evidence = repo_root / evidence_rel
            except (json.JSONDecodeError, KeyError, OSError) as exc:
                # State file malformed or missing - will use default evidence path
                # Fallback to default is handled below
                logger.debug(
                    "Could not load evidence path from state file: %s (using defaults)",
                    exc,
                )

        # Fall back to default
        if evidence is None:
            evidence = repo_root / ".vibegate" / "evidence" / "vibegate.jsonl"

    if not evidence.exists():
        typer.secho(
            f"Evidence file not found: {evidence}",
            fg=typer.colors.RED,
        )
        typer.echo("\nRun 'vibegate run .' first to generate evidence.")
        raise typer.Exit(code=2)

    # Resolve labels path
    if labels is None:
        labels = repo_root / ".vibegate" / "labels.yaml"

    if not labels.exists():
        typer.secho(
            f"Labels file not found: {labels}",
            fg=typer.colors.YELLOW,
        )
        typer.echo("\nNo labels found. Use 'vibegate label' to label findings.")
        typer.echo(
            "Example: vibegate label <fingerprint> --false-positive --reason <reason>"
        )
        raise typer.Exit(code=2)

    # Load evidence and labels
    typer.echo("Loading evidence and labels...")
    findings = tuning_module.load_evidence_findings(evidence)
    labels_map = tuning_module.load_labels(labels)

    if not findings:
        typer.secho("No findings in evidence file.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    # Join findings with labels
    labeled, unlabeled = tuning_module.join_findings_with_labels(findings, labels_map)

    if not labeled:
        typer.secho(
            "No labeled findings found. Label some findings first.",
            fg=typer.colors.YELLOW,
        )
        typer.echo(
            "\nExample: vibegate label <fingerprint> --false-positive --reason <reason>"
        )
        raise typer.Exit(code=0)

    # Compute metrics
    metrics = tuning_module.compute_metrics(labeled, unlabeled)

    # Check if there are any FPs to analyze
    if metrics.false_positive_count == 0 and not include_acceptable:
        typer.secho(
            "No false positives to analyze. All labeled findings are true positives.",
            fg=typer.colors.GREEN,
        )
        typer.echo("\nNothing to tune!")
        raise typer.Exit(code=0)

    if metrics.false_positive_count == 0 and metrics.acceptable_risk_count == 0:
        typer.secho(
            "No false positives or acceptable risks to analyze.",
            fg=typer.colors.GREEN,
        )
        typer.echo("\nNothing to tune!")
        raise typer.Exit(code=0)

    # Cluster findings
    typer.echo("Clustering findings...")
    clusters = tuning_module.cluster_findings(labeled, include_acceptable)

    if not clusters:
        typer.secho(
            "No clusters generated (this shouldn't happen with FPs).",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=0)

    # Write tuning pack
    typer.echo(f"Writing tuning pack to {out}...")
    out_resolved = repo_root / out if not out.is_absolute() else out
    report_path, clusters_json_path, examples_dir = tuning_module.write_tuning_pack(
        out_resolved, repo_root, metrics, clusters, max_examples
    )

    # Update state.json with tune metadata
    from vibegate.runner import write_tune_state

    write_tune_state(
        repo_root, out_resolved, report_path, clusters_json_path, examples_dir
    )

    # Print summary
    typer.echo("\nTuning Pack Created:")
    typer.echo(f"  - Report: {report_path}")
    typer.echo(f"  - Clusters JSON: {clusters_json_path}")
    typer.echo(f"  - Examples: {examples_dir}/")
    typer.echo("")
    typer.secho("Summary:", fg=typer.colors.GREEN)
    typer.echo(f"  - Total findings: {metrics.total_findings}")
    typer.echo(f"  - Labeled: {metrics.labeled_count}")
    typer.echo(f"  - False positives: {metrics.false_positive_count}")
    typer.echo(f"  - Clusters found: {len(clusters)}")
    typer.echo("")
    typer.echo("Review tuning_report.md for actionable insights.")


@app.command(hidden=True)
def propose(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Repository root directory",
    ),
    clusters: Optional[Path] = typer.Option(
        None, "--clusters", help="Path to tuning_clusters.json file"
    ),
    tuning_dir: Optional[Path] = typer.Option(
        None, "--tuning-dir", help="Tuning directory (alternative to --clusters)"
    ),
    out: Path = typer.Option(
        Path(".vibegate/artifacts/proposals"),
        "--out",
        help="Output directory for proposal pack",
    ),
    top: int = typer.Option(
        10, "--top", help="Number of top clusters to generate proposals for"
    ),
    format_type: str = typer.Option(
        "both", "--format", help="Output format: md, json, or both"
    ),
    include_acceptable: bool = typer.Option(
        False, "--include-acceptable", help="Include acceptable_risk clusters"
    ),
) -> None:
    """Generate Proposed Patch Pack from tuning clusters.

    This command takes tuning cluster analysis and generates actionable proposals:
    - Rule refinement suggestions
    - Suppression snippets (copy-pasteable)
    - Regression test snippets

    Output is deterministic and ready for PR review.
    """
    from vibegate import proposals as proposals_module
    from vibegate.runner import write_propose_state

    repo_root = repo_root.resolve()

    # Resolve clusters path
    if clusters is None and tuning_dir is None:
        # Try to load from state.json
        state_path = repo_root / ".vibegate" / "state.json"
        if state_path.exists():
            try:
                state_data = json.load(state_path.open("r", encoding="utf-8"))
                clusters_rel = state_data.get("last_tune", {}).get("clusters_path")
                if clusters_rel:
                    clusters = repo_root / clusters_rel
            except (json.JSONDecodeError, KeyError, OSError) as exc:
                # State file malformed or missing - will use default clusters path
                # Fallback to default is handled below
                logger.debug(
                    "Could not load clusters path from state file: %s (using defaults)",
                    exc,
                )

        # Fall back to default
        if clusters is None:
            clusters = (
                repo_root
                / ".vibegate"
                / "artifacts"
                / "tuning"
                / "tuning_clusters.json"
            )

    elif tuning_dir is not None:
        clusters = tuning_dir / "tuning_clusters.json"

    # Type assertion: clusters is always a Path after resolution logic
    assert clusters is not None, "clusters path should be resolved at this point"

    if not clusters.exists():
        typer.secho(
            f"Tuning clusters file not found: {clusters}",
            fg=typer.colors.RED,
        )
        typer.echo("\nRun 'vibegate tune .' first to generate tuning clusters.")
        raise typer.Exit(code=2)

    # Load clusters
    typer.echo("Loading tuning clusters...")
    clusters_data = proposals_module.load_tuning_clusters(clusters)

    if not clusters_data:
        typer.secho(
            "No clusters found in tuning data.",
            fg=typer.colors.YELLOW,
        )
        typer.echo("\nThis means either:")
        typer.echo("  - No false positives were identified during tuning")
        typer.echo("  - The tuning clusters file is empty or invalid")
        typer.echo("\nCreating empty proposal pack...")

        # Still create output directory and report
        out_dir = out if out.is_absolute() else repo_root / out
        out_dir.mkdir(parents=True, exist_ok=True)

        report_path = out_dir / "proposal_report.md"
        proposals_json_path = out_dir / "proposals.json"

        # Write empty reports
        report_path.write_text(
            "# VibeGate Proposed Patch Pack\n\n"
            "## No Proposals\n\n"
            "No clusters found. This could mean:\n"
            "- All checks are performing well\n"
            "- No false positives identified during tuning\n"
            "- More labeling needed\n",
            encoding="utf-8",
        )

        proposals_json_path.write_text(
            json.dumps({"proposals": []}, indent=2),
            encoding="utf-8",
        )

        # Update state.json
        write_propose_state(repo_root, out_dir, report_path, proposals_json_path)

        typer.echo(f"\nEmpty proposal pack created at {out_dir}")
        raise typer.Exit(code=0)

    # Load LLM provider if configured
    llm_provider = None
    try:
        from vibegate.config import load_config
        from vibegate.llm.enhancer import create_llm_provider_from_config

        config = load_config(repo_root)
        if config.llm and config.llm.enabled:
            typer.echo("🤖 LLM enabled - enhancing proposals with AI explanations...")
            llm_provider = create_llm_provider_from_config(config.llm)
            if llm_provider is None:
                typer.secho(
                    "⚠️  LLM configured but not available. Proposals will not include AI content.",
                    fg=typer.colors.YELLOW,
                )
    except Exception as e:
        typer.secho(
            f"⚠️  Failed to load LLM provider: {e}",
            fg=typer.colors.YELLOW,
        )

    # Generate proposals
    typer.echo(f"Generating proposals for top {top} clusters...")
    proposals = proposals_module.generate_proposals(
        clusters_data,
        repo_root,
        top_n=top,
        include_acceptable=include_acceptable,
        llm_provider=llm_provider,
    )

    if not proposals:
        typer.secho(
            "No proposals generated (this shouldn't happen with clusters).",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=0)

    # Write proposal pack
    out_dir = out if out.is_absolute() else repo_root / out
    typer.echo(f"Writing proposal pack to {out_dir}...")
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "proposal_report.md"
    proposals_json_path = out_dir / "proposals.json"
    copy_paste_dir = out_dir / "copy_paste_snippets"

    if format_type in ("md", "both"):
        proposals_module.write_proposals_markdown(proposals, report_path)

    if format_type in ("json", "both"):
        proposals_module.write_proposals_json(proposals, proposals_json_path)

    proposals_module.write_copy_paste_snippets(proposals, copy_paste_dir)

    # Update state.json
    write_propose_state(repo_root, out_dir, report_path, proposals_json_path)

    # Print summary
    typer.echo("\n" + "=" * 60)
    typer.secho("Proposed Patch Pack Created", fg=typer.colors.GREEN, bold=True)
    typer.echo("=" * 60)
    typer.echo(f"\n  - Report: {report_path.relative_to(repo_root)}")
    typer.echo(f"  - Proposals JSON: {proposals_json_path.relative_to(repo_root)}")
    typer.echo(
        f"  - Regression Snippets: {out_dir.relative_to(repo_root)}/regression_snippets/"
    )
    typer.echo(f"  - Copy-Paste Snippets: {copy_paste_dir.relative_to(repo_root)}/")

    typer.echo("\nSummary:")
    typer.echo(f"  - Total proposals: {len(proposals)}")

    # Show top 5 proposals
    typer.echo("\nTop 5 Proposals:")
    for proposal in proposals[:5]:
        hint_short = (
            proposal.primary_hint[:60] + "..."
            if len(proposal.primary_hint) > 60
            else proposal.primary_hint
        )
        typer.echo(
            f"  - {proposal.cluster_id}: {proposal.rule_id} ({proposal.count} findings)"
        )
        typer.echo(f"    Hint: {hint_short}")

    typer.echo(f"\nReview {report_path.relative_to(repo_root)} for detailed proposals.")
    typer.echo(
        "Remember: These are suggestions only. Review carefully before applying!"
    )


@app.command(hidden=True)
def start(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Deprecated: Use 'vibegate run' instead.

    The 'start' command has been replaced by the simpler 'run' command.
    """
    typer.secho(
        "⚠️  WARNING: 'vibegate start' is deprecated. Use 'vibegate run' instead.",
        fg=typer.colors.YELLOW,
        bold=True,
    )
    run(
        repo_root,
        detail="simple",
        skip_doctor=False,
        view=None,
        profile=None,
        summary="short",
        max_tasks=5,
    )


@app.command(hidden=True)
def triage(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
) -> None:
    """Interactive labeling workflow for findings.

    Allows you to mark findings as false_positive, true_positive, or acceptable_risk.
    This helps improve check tuning and track finding quality.

    Requires a TTY. For non-interactive labeling, use: vibegate label <fingerprint>
    """
    import sys
    from datetime import datetime, timezone

    repo_root = repo_root.resolve()

    # Check if running in TTY
    if not sys.stdin.isatty():
        typer.secho(
            "Triage is an interactive command and requires a TTY.",
            fg=typer.colors.YELLOW,
        )
        typer.echo("\nFor non-interactive labeling, use:")
        typer.echo("  vibegate label <fingerprint> --false-positive --reason <reason>")
        raise typer.Exit(code=1)

    # Load evidence from state.json or default path
    evidence_path = None
    state_path = repo_root / ".vibegate" / "state.json"
    if state_path.exists():
        try:
            state_data = json.load(state_path.open("r", encoding="utf-8"))
            evidence_rel = state_data.get("last_run", {}).get("evidence_path")
            if evidence_rel:
                evidence_path = repo_root / evidence_rel
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            # State file malformed or missing - will use default evidence path
            # Fallback to default is handled below
            logger.debug(
                "Could not load evidence path from state file: %s (using defaults)", exc
            )

    if evidence_path is None:
        evidence_path = repo_root / ".vibegate" / "evidence" / "vibegate.jsonl"

    if not evidence_path.exists():
        typer.secho(
            f"Evidence file not found: {evidence_path}",
            fg=typer.colors.RED,
        )
        typer.echo("\nRun 'vibegate run .' first to generate evidence.")
        raise typer.Exit(code=1)

    # Load findings from evidence
    findings_list = []
    with evidence_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                if event.get("event_type") == "finding":
                    findings_list.append(event)
            except json.JSONDecodeError:
                continue

    if not findings_list:
        typer.secho("No findings to triage!", fg=typer.colors.GREEN)
        raise typer.Exit(code=0)

    # Sort findings by severity (desc), confidence (desc), file path, line
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    confidence_order = {"high": 0, "medium": 1, "low": 2}

    def finding_sort_key(finding):
        severity = finding.get("severity", "info")
        confidence = finding.get("confidence", "low")
        location = finding.get("location") or {}
        path = location.get("path", "")
        line = location.get("line", 0)
        return (
            severity_order.get(severity, 99),
            confidence_order.get(confidence, 99),
            path,
            line,
        )

    findings_list = sorted(findings_list, key=finding_sort_key)

    # Load existing labels
    labels_path = repo_root / ".vibegate" / "labels.yaml"
    if labels_path.exists():
        with labels_path.open("r", encoding="utf-8") as f:
            labels_data = yaml.safe_load(f) or {}
    else:
        labels_data = {"version": 1, "labels": []}

    labels_list = labels_data.get("labels", [])
    if not isinstance(labels_list, list):
        labels_list = []

    # Track session stats
    session_stats = {"fp": 0, "tp": 0, "acceptable": 0}

    # Interactive loop
    typer.echo(f"\nFound {len(findings_list)} findings to triage.")
    typer.echo(
        "Commands: f=false_positive, t=true_positive, a=acceptable_risk, s=skip, q=quit\n"
    )

    idx = 0
    while idx < len(findings_list):
        finding = findings_list[idx]
        fingerprint = finding.get("fingerprint", "")
        rule_id = finding.get("rule_id", "")
        severity = finding.get("severity", "")
        confidence = finding.get("confidence", "")
        message = finding.get("message", "")
        location = finding.get("location") or {}
        path = location.get("path", "")
        line = location.get("line", "")

        typer.echo(f"[{idx + 1}/{len(findings_list)}] ", nl=False)
        typer.secho(f"{rule_id}", fg=typer.colors.CYAN, bold=True, nl=False)
        typer.echo(f" ({severity}/{confidence})")
        typer.echo(f"  File: {path}:{line}")
        typer.echo(f"  Message: {message}")
        typer.echo(f"  Fingerprint: {fingerprint[:16]}...")

        action = typer.prompt(
            "\nAction",
            default="s",
            type=str,
        ).lower()

        if action == "q":
            break
        elif action == "s":
            idx += 1
            typer.echo("")
            continue
        elif action in ("f", "t", "a"):
            # Prompt for reason
            reason = typer.prompt("Reason tag", type=str)
            note = typer.prompt("Note (optional)", default="", type=str)

            label_type = {
                "f": "false_positive",
                "t": "true_positive",
                "a": "acceptable_risk",
            }[action]

            # Update or create label
            existing = None
            for entry in labels_list:
                if entry.get("fingerprint") == fingerprint:
                    existing = entry
                    break

            now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            if existing:
                existing["label"] = label_type
                existing["reason"] = reason
                existing["note"] = note
                existing["created_at"] = now_iso
            else:
                labels_list.append(
                    {
                        "fingerprint": fingerprint,
                        "rule_id": rule_id,
                        "label": label_type,
                        "reason": reason,
                        "note": note,
                        "created_at": now_iso,
                    }
                )

            # Write labels immediately
            labels_data["labels"] = labels_list
            labels_path.parent.mkdir(parents=True, exist_ok=True)
            with labels_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    labels_data, f, sort_keys=False, default_flow_style=False
                )

            # Update session stats
            if label_type == "false_positive":
                session_stats["fp"] += 1
            elif label_type == "true_positive":
                session_stats["tp"] += 1
            elif label_type == "acceptable_risk":
                session_stats["acceptable"] += 1

            typer.secho(f"Saved: {label_type}", fg=typer.colors.GREEN)
            typer.echo(
                f"Session: FP={session_stats['fp']} TP={session_stats['tp']} Acceptable={session_stats['acceptable']}\n"
            )

            idx += 1
        else:
            typer.echo("Invalid action. Use f/t/a/s/q.\n")

    typer.echo("\nTriage session complete!")
    typer.echo(
        f"Labeled in this session: FP={session_stats['fp']} TP={session_stats['tp']} Acceptable={session_stats['acceptable']}"
    )
    typer.echo(f"Labels saved to: {labels_path}")


@app.command(hidden=True)
def evolve(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
    no_propose: bool = typer.Option(False, "--no-propose", help="Skip propose step"),
) -> None:
    """Full evolution loop: start + triage (optional) + tune + propose.

    This command runs the complete workflow:
    1. Initialize config (if needed), verify tools, and run checks
    2. Optionally triage findings interactively (if TTY)
    3. Generate tuning recommendations based on labels
    4. Generate actionable proposal pack for rule refinement

    Recommended for maintainers evolving check quality over time.
    """
    import sys

    repo_root = repo_root.resolve()

    # Step 1: Run start (init + doctor + check)
    typer.secho(
        "\n=== Phase 1: Running checks ===", fg=typer.colors.BRIGHT_CYAN, bold=True
    )
    start_failed = False
    try:
        start(repo_root)
    except typer.Exit as exc:
        if exc.exit_code == 1:
            # Check run failed (blocking findings), but we continue to tune
            start_failed = True
            typer.echo(
                "\nChecks found blocking issues, but continuing to tuning phase..."
            )
        else:
            # Config error or doctor failure - bail out
            raise

    # Step 2: Offer triage if TTY
    if sys.stdin.isatty():
        typer.secho(
            "\n=== Phase 2: Triage (optional) ===",
            fg=typer.colors.BRIGHT_CYAN,
            bold=True,
        )
        response = typer.prompt(
            "Open interactive triage to label findings?",
            default="Y",
            type=str,
        )
        if response.lower() in ("y", "yes", ""):
            try:
                triage(repo_root)
            except typer.Exit as exc:
                # Triage may exit early - continue to tune phase
                # User labels (if any) will still be available
                logger.debug(
                    "Triage command exited with code %s, continuing to tune phase",
                    getattr(exc, "exit_code", None),
                )
    else:
        typer.echo(
            "\nSkipping triage (non-TTY). Use 'vibegate triage .' for interactive labeling."
        )

    # Step 3: Run tune
    typer.secho("\n=== Phase 3: Tuning ===", fg=typer.colors.BRIGHT_CYAN, bold=True)

    # Check if labels exist
    labels_path = repo_root / ".vibegate" / "labels.yaml"
    if not labels_path.exists():
        typer.secho(
            "No labels found. Skipping tuning phase.",
            fg=typer.colors.YELLOW,
        )
        typer.echo(
            "\nLabel some findings first with 'vibegate triage .' or 'vibegate label'"
        )
        if start_failed:
            raise typer.Exit(code=1)
        raise typer.Exit(code=0)

    # Run tune
    try:
        # Load evidence and labels
        from vibegate import tuning as tuning_module

        evidence_path = None
        state_path = repo_root / ".vibegate" / "state.json"
        if state_path.exists():
            try:
                state_data = json.load(state_path.open("r", encoding="utf-8"))
                evidence_rel = state_data.get("last_run", {}).get("evidence_path")
                if evidence_rel:
                    evidence_path = repo_root / evidence_rel
            except (json.JSONDecodeError, KeyError, OSError) as exc:
                # State file malformed or missing - will use default evidence path
                # Fallback to default is handled below
                logger.debug(
                    "Could not load evidence path from state file: %s (using defaults)",
                    exc,
                )

        if evidence_path is None:
            evidence_path = repo_root / ".vibegate" / "evidence" / "vibegate.jsonl"

        if not evidence_path.exists():
            typer.secho(
                f"Evidence file not found: {evidence_path}",
                fg=typer.colors.RED,
            )
            if start_failed:
                raise typer.Exit(code=1)
            raise typer.Exit(code=2)

        typer.echo("Loading evidence and labels...")
        findings = tuning_module.load_evidence_findings(evidence_path)
        labels_map = tuning_module.load_labels(labels_path)

        if not findings:
            typer.secho("No findings in evidence file.", fg=typer.colors.YELLOW)
            if start_failed:
                raise typer.Exit(code=1)
            raise typer.Exit(code=0)

        labeled, unlabeled = tuning_module.join_findings_with_labels(
            findings, labels_map
        )

        if not labeled:
            typer.secho(
                "No labeled findings found. Label some findings first.",
                fg=typer.colors.YELLOW,
            )
            if start_failed:
                raise typer.Exit(code=1)
            raise typer.Exit(code=0)

        metrics = tuning_module.compute_metrics(labeled, unlabeled)

        if metrics.false_positive_count == 0:
            typer.secho(
                "No false positives to analyze. All labeled findings are true positives.",
                fg=typer.colors.GREEN,
            )
            typer.echo("\nNothing to tune!")
            if start_failed:
                raise typer.Exit(code=1)
            raise typer.Exit(code=0)

        typer.echo("Clustering findings...")
        clusters = tuning_module.cluster_findings(labeled, include_acceptable=False)

        if not clusters:
            typer.secho(
                "No clusters generated.",
                fg=typer.colors.YELLOW,
            )
            if start_failed:
                raise typer.Exit(code=1)
            raise typer.Exit(code=0)

        # Write tuning pack
        out_dir = repo_root / ".vibegate" / "artifacts" / "tuning"
        typer.echo(f"Writing tuning pack to {out_dir}...")
        report_path, clusters_json_path, examples_dir = tuning_module.write_tuning_pack(
            out_dir, repo_root, metrics, clusters, max_examples=5
        )

        # Update state.json with tune metadata
        from vibegate.runner import write_tune_state

        write_tune_state(
            repo_root, out_dir, report_path, clusters_json_path, examples_dir
        )

        # Print summary
        typer.echo("\n" + "=" * 60)
        typer.secho("Tuning Pack Created", fg=typer.colors.GREEN, bold=True)
        typer.echo("=" * 60)
        typer.echo(f"\n  - Report: {report_path.relative_to(repo_root)}")
        typer.echo(f"  - Clusters JSON: {clusters_json_path.relative_to(repo_root)}")
        typer.echo(f"  - Examples: {examples_dir.relative_to(repo_root)}/")

        typer.echo("\nSummary:")
        typer.echo(f"  - Total findings: {metrics.total_findings}")
        typer.echo(f"  - Labeled: {metrics.labeled_count}")
        typer.echo(f"  - False positives: {metrics.false_positive_count}")
        typer.echo(f"  - Clusters found: {len(clusters)}")

        # Print top N clusters
        typer.echo("\nTop 5 Clusters by FP count:")
        for cluster in clusters[:5]:
            typer.echo(
                f"  - {cluster.cluster_id}: {cluster.rule_id} ({cluster.count} findings)"
            )
            if cluster.action_hints:
                typer.echo(f"    Hint: {cluster.action_hints[0]}")

        typer.echo(
            f"\nReview {report_path.relative_to(repo_root)} for detailed analysis."
        )

        # Step 4: Run propose (unless --no-propose)
        if not no_propose:
            typer.secho(
                "\n=== Phase 4: Proposals ===", fg=typer.colors.BRIGHT_CYAN, bold=True
            )
            typer.echo("Generating actionable proposal pack...")

            from vibegate import proposals as proposals_module
            from vibegate.runner import write_propose_state

            # Generate proposals from the tuning clusters we just created
            proposals = proposals_module.generate_proposals(
                proposals_module.load_tuning_clusters(clusters_json_path),
                repo_root,
                top_n=10,
                include_acceptable=False,
            )

            if proposals:
                # Write proposal pack
                proposals_out = repo_root / ".vibegate" / "artifacts" / "proposals"
                proposals_out.mkdir(parents=True, exist_ok=True)

                proposals_report_path = proposals_out / "proposal_report.md"
                proposals_json_path = proposals_out / "proposals.json"
                copy_paste_dir = proposals_out / "copy_paste_snippets"

                proposals_module.write_proposals_markdown(
                    proposals, proposals_report_path
                )
                proposals_module.write_proposals_json(proposals, proposals_json_path)
                proposals_module.write_copy_paste_snippets(proposals, copy_paste_dir)

                # Update state.json
                write_propose_state(
                    repo_root, proposals_out, proposals_report_path, proposals_json_path
                )

                # Print summary
                typer.echo("\n" + "=" * 60)
                typer.secho(
                    "Proposed Patch Pack Created", fg=typer.colors.GREEN, bold=True
                )
                typer.echo("=" * 60)
                typer.echo(
                    f"\n  - Report: {proposals_report_path.relative_to(repo_root)}"
                )
                typer.echo(
                    f"  - Proposals JSON: {proposals_json_path.relative_to(repo_root)}"
                )
                typer.echo(
                    f"  - Copy-Paste Snippets: {copy_paste_dir.relative_to(repo_root)}/"
                )

                typer.echo("\nTop 5 Proposals:")
                for proposal in proposals[:5]:
                    hint_short = (
                        proposal.primary_hint[:60] + "..."
                        if len(proposal.primary_hint) > 60
                        else proposal.primary_hint
                    )
                    typer.echo(
                        f"  - {proposal.cluster_id}: {proposal.rule_id} ({proposal.count} findings)"
                    )
                    typer.echo(f"    Hint: {hint_short}")

                typer.echo(
                    f"\nReview {proposals_report_path.relative_to(repo_root)} for actionable proposals."
                )
            else:
                typer.secho("No proposals generated.", fg=typer.colors.YELLOW)

    except typer.Exit:
        if start_failed:
            raise typer.Exit(code=1)
        raise

    if start_failed:
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Print the VibeGate version."""
    typer.echo(__version__)


@app.command()
def clean(
    repo_root: Path = typer.Argument(
        Path("."),
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Repository root directory",
    ),
    all_caches: bool = typer.Option(
        False,
        "--all",
        help="Include UI runs and LLM cache in cleanup",
    ),
    venv: bool = typer.Option(
        False,
        "--venv",
        help="Also delete virtual environments (.venv, .venv-*)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be deleted without actually deleting",
    ),
) -> None:
    """Clean up cache directories and build artifacts.

    By default, removes common Python caches while preserving:
    - vibegate.yaml
    - .vibegate/suppressions.yaml
    - .vibegate/labels.yaml
    - .vibegate/llm_cache (unless --all is specified)
    - .vibegate/ui/runs (unless --all is specified)

    Use --dry-run to preview what would be deleted.
    """
    import shutil

    repo_root = repo_root.resolve()

    # Define cleanup targets
    # Standard cache directories to always clean
    standard_targets = [
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "__pycache__",
        "htmlcov",
        ".coverage",
        ".tox",
        ".nox",
        "dist",
        "build",
    ]

    # Glob patterns for .egg-info directories
    egg_info_pattern = "*.egg-info"

    # Additional targets based on flags
    additional_targets = []
    if all_caches:
        additional_targets.extend(
            [
                ".vibegate/ui/runs",
                ".vibegate/llm_cache",
            ]
        )

    venv_targets = []
    if venv:
        venv_targets.append(".venv")
        # Also match .venv-* directories

    # Collect all paths to delete
    to_delete: List[Path] = []

    # Standard targets
    for target in standard_targets:
        path = repo_root / target
        if path.exists():
            to_delete.append(path)

    # Find egg-info directories
    egg_info_dirs = list(repo_root.glob(egg_info_pattern))
    to_delete.extend(egg_info_dirs)

    # Additional targets
    for target in additional_targets:
        path = repo_root / target
        if path.exists():
            to_delete.append(path)

    # Virtual environments
    for target in venv_targets:
        path = repo_root / target
        if path.exists():
            to_delete.append(path)

    # Find .venv-* directories if --venv is enabled
    if venv:
        venv_pattern_dirs = list(repo_root.glob(".venv-*"))
        to_delete.extend(venv_pattern_dirs)

    # Recursively find all __pycache__ directories
    pycache_dirs = list(repo_root.rglob("__pycache__"))
    # Only add if not already in to_delete
    for pycache_dir in pycache_dirs:
        if pycache_dir not in to_delete:
            to_delete.append(pycache_dir)

    # Sort for deterministic output
    to_delete = sorted(set(to_delete))

    if not to_delete:
        typer.secho("No cache directories found to clean.", fg=typer.colors.GREEN)
        return

    # Display what will be/would be deleted
    if dry_run:
        typer.secho(
            "DRY RUN - The following would be deleted:",
            fg=typer.colors.YELLOW,
            bold=True,
        )
    else:
        typer.echo("Cleaning up cache directories:")

    for path in to_delete:
        rel_path = (
            path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
        )
        if path.is_file():
            size_str = f"({path.stat().st_size} bytes)"
        elif path.is_dir():
            size_str = "(directory)"
        else:
            size_str = ""

        typer.echo(f"  - {rel_path} {size_str}")

    if dry_run:
        typer.echo(
            f"\nWould delete {len(to_delete)} item(s). Run without --dry-run to actually delete."
        )
        return

    # Perform deletion
    deleted_count = 0
    error_count = 0

    for path in to_delete:
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            deleted_count += 1
        except Exception as e:
            error_count += 1
            rel_path = (
                path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
            )
            typer.secho(f"  ✗ Failed to delete {rel_path}: {e}", fg=typer.colors.RED)

    typer.echo("")
    if error_count == 0:
        typer.secho(
            f"✓ Successfully cleaned {deleted_count} item(s).",
            fg=typer.colors.GREEN,
            bold=True,
        )
    else:
        typer.secho(
            f"⚠ Cleaned {deleted_count} item(s) with {error_count} error(s).",
            fg=typer.colors.YELLOW,
            bold=True,
        )
        raise typer.Exit(code=1)


def _print_outputs(config, artifacts: List) -> None:
    typer.echo("Evidence & artifacts:")
    for artifact in artifacts:
        typer.echo(f"- {artifact.path}")
    typer.echo(f"- {config.outputs.evidence_jsonl}")


def _print_summary(status: str, config: VibeGateConfig) -> None:
    summary = load_run_summary(config.outputs.evidence_jsonl)
    unsuppressed = "unknown"
    if summary and isinstance(summary.get("counts"), dict):
        counts = summary.get("counts", {})
        count = counts.get("findings_unsuppressed")
        if isinstance(count, int):
            unsuppressed = str(count)

    typer.echo("Decision:")
    typer.echo(f"- Status: {status}")
    typer.echo(f"- Unsuppressed issues: {unsuppressed}")
    typer.echo(f"- Evidence report: {config.outputs.report_markdown}")
    typer.echo(f"- Evidence log: {config.outputs.evidence_jsonl}")


def _format_delta(value: int) -> str:
    if value > 0:
        return f"+{value}"
    return str(value)


def _detect_packaging_tool(tool_detection_order: List[str]) -> str:
    for tool in tool_detection_order:
        if tool_exists(tool):
            return tool
    return "pip"


def _required_tools(config: VibeGateConfig) -> Set[str]:
    required: Set[str] = set()
    if config.checks.formatting.enabled or config.checks.lint.enabled:
        required.add("ruff")
    if config.checks.typecheck.enabled:
        required.add("pyright")
    if config.checks.tests.enabled:
        required.add("pytest")
    if config.checks.sast.enabled:
        required.add("bandit")
    if config.checks.secrets.enabled:
        required.add("gitleaks")
    if config.checks.vulnerability.enabled:
        required.add("osv-scanner")
    return required


def _extract_version(raw: str) -> Optional[str]:
    for token in raw.split():
        if token and token[0].isdigit():
            return token.strip()
    return None


def _install_guidance(tool: str, expected: Optional[str]) -> str:
    """Return helpful installation guidance for a missing tool."""
    version = f"=={expected}" if expected else ""

    # Tool-specific installation guidance
    if tool == "ruff":
        return f"pipx install ruff{version} (or: pip install ruff{version})"

    if tool == "pyright":
        return f"npm i -g pyright (or: pip install pyright{version})"

    if tool == "pytest":
        return f"pip install pytest{version}"

    if tool == "bandit":
        return f"pip install bandit{version}"

    if tool == "gitleaks":
        return "brew install gitleaks (macOS) or see: https://github.com/gitleaks/gitleaks#installation"

    if tool == "osv-scanner":
        return "brew install osv-scanner (macOS) or see: https://google.github.io/osv-scanner/"

    if tool == "vulture":
        return f"pip install vulture{version}"

    # Default fallback
    return f"Install via pip: pip install {tool}{version}"


def _suppressions_template() -> str:
    return """# VibeGate suppressions
schema_version: v1alpha1
suppressions: []
  # - fingerprint: "<stable-fingerprint>"
  #   rule_id: "RULE_ID"  # Optional: match a specific rule
  #   justification: "Why this finding is acceptable"
  #   expires_at: "2099-12-31T00:00:00Z"
  #   actor: "your-name-or-team"
"""


def _labels_template() -> str:
    return """# VibeGate labels (false positive feedback)
# Labels are for tracking finding quality and informing future rule evolution.
# They do NOT affect CI/CD behavior (use suppressions.yaml for that).
version: 1
labels: []
  # - fingerprint: "<finding-fingerprint>"
  #   rule_id: "<rule_id>"
  #   label: "false_positive"  # or "true_positive" or "acceptable_risk"
  #   reason: "<short-tag>"
  #   note: "<optional-details>"
  #   created_at: "<iso-timestamp>"
"""


@app.command(name="plugins-list", hidden=True)
def plugins_list() -> None:
    """List all available plugins and check packs."""
    from vibegate.plugins.loader import discover_all_plugins, load_check_packs

    logger_instance = logging.getLogger("vibegate.plugins")
    logger_instance.setLevel(logging.WARNING)

    typer.secho("VibeGate Plugins and Check Packs", fg=typer.colors.CYAN, bold=True)
    typer.echo()

    # Discover all plugins
    all_plugins = discover_all_plugins(logger_instance)

    # List check packs
    typer.secho("Check Packs:", fg=typer.colors.GREEN, bold=True)
    loaded_packs = load_check_packs(logger_instance)
    if not loaded_packs:
        typer.echo("  (none found)")
    else:
        for pack in sorted(loaded_packs, key=lambda p: p.name):
            if pack.load_error:
                typer.secho(
                    f"  • {pack.name}: ",
                    fg=typer.colors.RED,
                    nl=False,
                )
                typer.secho(f"ERROR - {pack.load_error}", fg=typer.colors.RED)
            elif pack.metadata:
                typer.secho(f"  • {pack.name}: ", fg=typer.colors.GREEN, nl=False)
                typer.echo(
                    f"{pack.metadata.pack_name} v{pack.metadata.version} "
                    f"({len(pack.checks)} checks)"
                )
                if pack.metadata.description:
                    typer.echo(f"    {pack.metadata.description}")
                if pack.metadata.author:
                    typer.echo(f"    Author: {pack.metadata.author}")
                if pack.metadata.tags:
                    typer.echo(f"    Tags: {', '.join(pack.metadata.tags)}")
            else:
                typer.secho(f"  • {pack.name}: ", fg=typer.colors.YELLOW, nl=False)
                typer.echo("(metadata unavailable)")
    typer.echo()

    # List individual check plugins
    typer.secho("Check Plugins:", fg=typer.colors.GREEN, bold=True)
    check_plugins = all_plugins.get("vibegate.checks", [])
    if not check_plugins:
        typer.echo("  (none found)")
    else:
        for entry_point in sorted(check_plugins, key=lambda ep: ep.name):
            typer.secho(f"  • {entry_point.name}: ", fg=typer.colors.GREEN, nl=False)
            typer.echo(f"{entry_point.value}")
    typer.echo()

    # List emitter plugins
    typer.secho("Emitter Plugins:", fg=typer.colors.GREEN, bold=True)
    emitter_plugins = all_plugins.get("vibegate.emitters", [])
    if not emitter_plugins:
        typer.echo("  (none found)")
    else:
        for entry_point in sorted(emitter_plugins, key=lambda ep: ep.name):
            typer.secho(f"  • {entry_point.name}: ", fg=typer.colors.GREEN, nl=False)
            typer.echo(f"{entry_point.value}")
    typer.echo()


@app.command(name="plugins-doctor", hidden=True)
def plugins_doctor() -> None:
    """Validate all plugins and check packs load correctly."""
    from vibegate.plugins.loader import discover_all_plugins, load_check_packs

    logger_instance = logging.getLogger("vibegate.plugins")
    logger_instance.setLevel(logging.WARNING)

    typer.secho("VibeGate Plugin Health Check", fg=typer.colors.CYAN, bold=True)
    typer.echo()

    has_errors = False

    # Check all check packs
    typer.secho("Checking check packs...", fg=typer.colors.CYAN)
    loaded_packs = load_check_packs(logger_instance)
    pack_errors = 0
    pack_warnings = 0

    for pack in sorted(loaded_packs, key=lambda p: p.name):
        if pack.load_error:
            pack_errors += 1
            has_errors = True
            typer.secho(f"  ✗ {pack.name}: ", fg=typer.colors.RED, nl=False, bold=True)
            typer.secho(pack.load_error, fg=typer.colors.RED)
        elif not pack.metadata:
            pack_warnings += 1
            typer.secho(
                f"  ⚠ {pack.name}: ", fg=typer.colors.YELLOW, nl=False, bold=True
            )
            typer.secho("metadata unavailable", fg=typer.colors.YELLOW)
        elif not pack.checks:
            pack_warnings += 1
            typer.secho(
                f"  ⚠ {pack.name}: ", fg=typer.colors.YELLOW, nl=False, bold=True
            )
            typer.secho("provides 0 checks", fg=typer.colors.YELLOW)
        else:
            typer.secho(f"  ✓ {pack.name}: ", fg=typer.colors.GREEN, nl=False)
            typer.echo(f"{pack.metadata.pack_name} ({len(pack.checks)} checks) - OK")

    if pack_errors == 0 and pack_warnings == 0:
        typer.secho("  All check packs OK!", fg=typer.colors.GREEN)
    else:
        typer.echo(
            f"  Found {pack_errors} errors and {pack_warnings} warnings in check packs"
        )
    typer.echo()

    # Check individual check plugins
    typer.secho("Checking check plugins...", fg=typer.colors.CYAN)
    all_plugins = discover_all_plugins(logger_instance)
    check_plugins = all_plugins.get("vibegate.checks", [])

    if not check_plugins:
        typer.secho("  No check plugins found", fg=typer.colors.YELLOW)
    else:
        plugin_errors = 0
        for entry_point in sorted(check_plugins, key=lambda ep: ep.name):
            try:
                _ = entry_point.load()
                typer.secho(
                    f"  ✓ {entry_point.name}: ", fg=typer.colors.GREEN, nl=False
                )
                typer.echo("OK")
            except Exception as exc:
                plugin_errors += 1
                has_errors = True
                typer.secho(
                    f"  ✗ {entry_point.name}: ",
                    fg=typer.colors.RED,
                    nl=False,
                    bold=True,
                )
                typer.secho(str(exc), fg=typer.colors.RED)

        if plugin_errors == 0:
            typer.secho("  All check plugins OK!", fg=typer.colors.GREEN)
        else:
            typer.echo(f"  Found {plugin_errors} errors in check plugins")
    typer.echo()

    # Check emitter plugins
    typer.secho("Checking emitter plugins...", fg=typer.colors.CYAN)
    emitter_plugins = all_plugins.get("vibegate.emitters", [])

    if not emitter_plugins:
        typer.secho("  No emitter plugins found", fg=typer.colors.YELLOW)
    else:
        emitter_errors = 0
        for entry_point in sorted(emitter_plugins, key=lambda ep: ep.name):
            try:
                _ = entry_point.load()
                typer.secho(
                    f"  ✓ {entry_point.name}: ", fg=typer.colors.GREEN, nl=False
                )
                typer.echo("OK")
            except Exception as exc:
                emitter_errors += 1
                has_errors = True
                typer.secho(
                    f"  ✗ {entry_point.name}: ",
                    fg=typer.colors.RED,
                    nl=False,
                    bold=True,
                )
                typer.secho(str(exc), fg=typer.colors.RED)

        if emitter_errors == 0:
            typer.secho("  All emitter plugins OK!", fg=typer.colors.GREEN)
        else:
            typer.echo(f"  Found {emitter_errors} errors in emitter plugins")
    typer.echo()

    # Summary
    if has_errors:
        typer.secho("Plugin health check FAILED", fg=typer.colors.RED, bold=True)
        typer.echo("Some plugins failed to load. Check the errors above for details.")
        raise typer.Exit(code=1)
    else:
        typer.secho("Plugin health check PASSED", fg=typer.colors.GREEN, bold=True)
        typer.echo("All plugins loaded successfully.")


@app.command(name="llm-recommend", hidden=True)
def llm_recommend(
    show_details: bool = typer.Option(
        False,
        "--details",
        "-d",
        help="Show detailed system resource information",
    ),
) -> None:
    """Recommend LLM configuration based on system resources.

    Analyzes your machine's RAM, CPU, and GPU to suggest the best
    local model for VibeGate's AI features.
    """
    from vibegate.llm.recommend import format_recommendation, recommend_llm_config

    try:
        typer.echo("🔍 Analyzing your system resources...\n")
        recommendation = recommend_llm_config()

        # Display recommendation
        output = format_recommendation(recommendation, show_details=show_details)
        typer.echo(output)
        typer.echo()

        # Provide next steps
        typer.secho("Next steps:", fg=typer.colors.CYAN, bold=True)
        typer.echo("  1. Install Ollama: https://ollama.com/download")
        typer.echo(f"  2. Pull the model: ollama pull {recommendation.model}")
        typer.echo("  3. Run setup wizard: vibegate init")
        typer.echo()
        typer.echo("Or integrate into existing vibegate.yaml:")
        typer.echo()
        typer.echo("  llm:")
        typer.echo("    enabled: true")
        typer.echo("    provider: ollama")
        typer.echo("    ollama:")
        typer.echo(f"      model: {recommendation.model}")
        typer.echo(f"      timeout_sec: {recommendation.timeout_sec}")
        typer.echo()

    except Exception as e:
        typer.secho(f"Error generating recommendation: {e}", fg=typer.colors.RED)
        logger.exception("Failed to generate LLM recommendation")
        raise typer.Exit(code=1)


# ============================================================================
# Plugin and LLM command groups (with backward-compatible aliases)
# ============================================================================

# Create sub-app for "plugins" command group
plugins_app = typer.Typer(
    help="Plugin management commands",
    no_args_is_help=True,
    hidden=True,
)


@plugins_app.command(name="list")
def plugins_list_grouped() -> None:
    """List all available plugins and check packs."""
    # Delegate to existing implementation
    plugins_list()


@plugins_app.command(name="doctor")
def plugins_doctor_grouped() -> None:
    """Validate all plugins and check packs load correctly."""
    # Delegate to existing implementation
    plugins_doctor()


# Register plugins sub-app
app.add_typer(plugins_app, name="plugins")

# Create sub-app for "llm" command group
llm_app = typer.Typer(
    help="LLM configuration and recommendations",
    no_args_is_help=True,
    hidden=True,
)


@llm_app.command(name="recommend")
def llm_recommend_grouped(
    show_details: bool = typer.Option(
        False,
        "--details",
        "-d",
        help="Show detailed system resource information",
    ),
) -> None:
    """Recommend LLM configuration based on system resources."""
    # Delegate to existing implementation
    llm_recommend(show_details=show_details)


# Register llm sub-app
app.add_typer(llm_app, name="llm")


if __name__ == "__main__":
    app()
