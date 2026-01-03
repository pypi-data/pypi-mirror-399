#!/usr/bin/env python3
"""
Pre-release verification checklist for VibeGate.

Runs a series of checks to ensure the project is ready for release:
1. Git working tree is clean
2. Unit tests pass
3. VibeGate run passes on itself
4. Package builds successfully
5. Package passes twine validation

Usage:
    python scripts/pre_release_check.py
"""

import subprocess
import sys
from pathlib import Path


def run_command(
    cmd: list[str],
    description: str,
    capture_output: bool = False,
    env: dict | None = None,
) -> tuple[bool, str]:
    """
    Run a command and return success status and output.

    Args:
        cmd: Command and arguments as list
        description: Human-friendly description of what the command does
        capture_output: Whether to capture stdout/stderr
        env: Optional environment variables to set

    Returns:
        Tuple of (success: bool, output: str)
    """
    print(f"\n{'=' * 70}")
    print(f"⏳ {description}...")
    print(f"{'=' * 70}")

    try:
        import os

        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        if capture_output:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False, env=run_env
            )
            success = result.returncode == 0
            output = result.stdout + result.stderr
            return success, output
        else:
            result = subprocess.run(cmd, check=False, env=run_env)
            success = result.returncode == 0
            return success, ""
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)


def print_result(success: bool, step_name: str, help_text: str = ""):
    """Print a friendly success/failure message."""
    if success:
        print(f"\n✅ PASS: {step_name}")
    else:
        print(f"\n❌ FAIL: {step_name}")
        if help_text:
            print(f"\n💡 Next steps:\n{help_text}")


def main() -> int:
    """Run all pre-release checks."""
    print("=" * 70)
    print("🚀 VibeGate Pre-Release Verification Checklist")
    print("=" * 70)
    print("\nThis script validates that your code is ready for release.")
    print("All checks must pass before merging a release PR.\n")

    # Track overall success
    all_passed = True

    # Step 1: Check git working tree is clean
    success, output = run_command(
        ["git", "status", "--porcelain"],
        "Checking git working tree is clean",
        capture_output=True,
    )

    git_clean = success and output.strip() == ""
    print_result(
        git_clean,
        "Git working tree is clean",
        "You have uncommitted changes. Please commit or stash them:\n"
        "  git status\n"
        "  git add -A && git commit -m 'chore: pre-release cleanup'\n"
        "  # or\n"
        "  git stash",
    )
    all_passed = all_passed and git_clean

    # Step 2: Run unit tests
    success, _ = run_command(
        [sys.executable, "-m", "pytest"],
        "Running unit tests (pytest)",
        capture_output=False,
    )
    print_result(
        success,
        "Unit tests pass",
        "Tests are failing. Fix them before releasing:\n"
        f"  {sys.executable} -m pytest -xvs",
    )
    all_passed = all_passed and success

    # Step 3: Run VibeGate run on itself
    # Use PYTHONPATH to run from source (works with Python 3.14+)
    repo_root = Path(__file__).resolve().parent.parent
    success, _ = run_command(
        [
            sys.executable,
            "-m",
            "vibegate",
            "run",
            ".",
            "--profile",
            "strict",
            "--detail",
            "deep",
            "--no-view",
        ],
        "Running VibeGate run on itself",
        capture_output=False,
        env={"PYTHONPATH": str(repo_root / "src")},
    )
    print_result(
        success,
        "VibeGate run passes",
        "VibeGate found issues. Fix them before releasing:\n"
        f"  {sys.executable} -m vibegate run . --profile strict --detail deep --no-view\n"
        "  # Review .vibegate/artifacts/vibegate_report.md for details",
    )
    all_passed = all_passed and success

    # Step 4: Build package
    # Clean old builds first
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\n🧹 Cleaning old dist/ directory...")
        for item in dist_dir.iterdir():
            item.unlink()

    success, _ = run_command(
        [sys.executable, "-m", "build"],
        "Building package (sdist + wheel)",
        capture_output=False,
    )
    print_result(
        success,
        "Package builds successfully",
        "Build failed. Check build dependencies:\n"
        f"  {sys.executable} -m pip install build\n"
        f"  {sys.executable} -m build",
    )
    all_passed = all_passed and success

    # Step 5: Validate package with twine
    if success:  # Only run if build succeeded
        success, _ = run_command(
            [sys.executable, "-m", "twine", "check", "dist/*"],
            "Validating package with twine",
            capture_output=False,
        )
        print_result(
            success,
            "Package passes twine validation",
            "Package validation failed. Check package metadata:\n"
            f"  {sys.executable} -m pip install twine\n"
            f"  {sys.executable} -m twine check dist/*",
        )
        all_passed = all_passed and success
    else:
        print("\n⏭️  SKIP: Package validation (build failed)")
        all_passed = False

    # Final summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("=" * 70)
        print("\n🎉 Your code is ready for release!")
        print("\nNext steps:")
        print("  1. Ensure CI is green on your PR")
        print("  2. Merge PR with conventional commit message")
        print("  3. semantic-release.yml will publish automatically")
        print("\nConventional commit examples:")
        print("  feat: add new feature")
        print("  fix: resolve bug")
        print("  docs: update documentation")
        print("  chore: maintenance task")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 70)
        print("\n⚠️  Please fix the issues above before releasing.")
        print("\nRerun this script after fixing:")
        print(f"  {sys.executable} scripts/pre_release_check.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
