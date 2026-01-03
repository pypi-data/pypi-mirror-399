#!/usr/bin/env python3
"""
Bundle VibeGate source code into a clean zip file for sharing.

This script creates a source distribution that excludes build artifacts,
caches, virtual environments, and runtime outputs.

Strategy:
1. Prefer git ls-files: Use tracked files only (cleanest approach)
2. Fallback to filesystem walk: If git unavailable, use exclusion patterns

Output: dist/vibegate-source.zip or dist/source-<sha>.zip
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from pathlib import Path

# Exclusion patterns for filesystem fallback
EXCLUDE_DIRS = {
    "__MACOSX",
    ".DS_Store",
    ".venv",
    "venv",
    "dist",
    "build",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
}

EXCLUDE_PATTERNS = {
    "*.egg-info",
    ".vibegate/artifacts",
    ".vibegate/evidence",
    ".vibegate/ui/runs",
    ".vibegate/llm_cache",
}


def get_git_sha() -> str | None:
    """Get current git SHA (short form) if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return None


def get_git_tracked_files(repo_root: Path) -> list[Path] | None:
    """
    Get list of git-tracked files using git ls-files.

    Returns None if git is not available or command fails.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=repo_root,
            capture_output=True,
            check=True,
            timeout=10,
        )
        # -z uses null-terminated output for safe parsing
        files_raw = result.stdout.decode("utf-8").split("\0")
        # Filter out empty strings from trailing null
        files = [repo_root / f for f in files_raw if f]
        return files
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return None


def should_exclude_path(path: Path, repo_root: Path) -> bool:
    """
    Check if a path should be excluded based on patterns.

    Used only for filesystem fallback when git is not available.
    """
    rel_path = path.relative_to(repo_root)
    parts = rel_path.parts

    # Check directory exclusions
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
        if part.startswith(".venv"):
            return True

    # Check pattern exclusions
    for pattern in EXCLUDE_PATTERNS:
        if pattern.endswith("*"):
            # Suffix match (e.g., *.egg-info)
            if any(part.endswith(pattern[1:]) for part in parts):
                return True
        else:
            # Exact path match
            if str(rel_path).startswith(pattern):
                return True

    return False


def collect_files_filesystem(repo_root: Path) -> list[Path]:
    """
    Collect files using filesystem walk with exclusions.

    Fallback method when git is not available.
    """
    files: list[Path] = []
    for path in repo_root.rglob("*"):
        if path.is_file() and not should_exclude_path(path, repo_root):
            files.append(path)
    return sorted(files)


def create_source_bundle(
    repo_root: Path, output_path: Path, use_git: bool = True
) -> int:
    """
    Create a clean source zip bundle.

    Args:
        repo_root: Repository root directory
        output_path: Output zip file path
        use_git: Whether to try using git ls-files first

    Returns:
        Exit code (0 = success)
    """
    # Collect files to bundle
    files: list[Path] | None = None
    method = "unknown"

    if use_git:
        files = get_git_tracked_files(repo_root)
        if files is not None:
            method = "git ls-files"
            print(f"Using git-tracked files ({len(files)} files)")
        else:
            print("Git not available, falling back to filesystem walk")

    if files is None:
        files = collect_files_filesystem(repo_root)
        method = "filesystem walk"
        print(f"Using filesystem walk with exclusions ({len(files)} files)")

    if not files:
        print("ERROR: No files found to bundle", file=sys.stderr)
        return 1

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create zip file
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            # Store with relative path to preserve structure
            arcname = file_path.relative_to(repo_root)
            zf.write(file_path, arcname)

    # Report success
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print("\nSource bundle created successfully!")
    print(f"  Method: {method}")
    print(f"  Files: {len(files)}")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"  Output: {output_path}")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bundle VibeGate source code into a clean zip file"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output zip file path (default: dist/vibegate-source.zip or dist/source-<sha>.zip)",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Skip git ls-files and use filesystem walk",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Determine repository root
    repo_root = Path(__file__).resolve().parents[1]

    # Determine output path
    if args.output:
        output_path = args.output.resolve()
    else:
        # Use SHA in filename if available
        sha = get_git_sha()
        if sha:
            filename = f"source-{sha}.zip"
        else:
            filename = "vibegate-source.zip"
        output_path = repo_root / "dist" / filename

    # Create bundle
    use_git = not args.no_git
    return create_source_bundle(repo_root, output_path, use_git=use_git)


if __name__ == "__main__":
    raise SystemExit(main())
