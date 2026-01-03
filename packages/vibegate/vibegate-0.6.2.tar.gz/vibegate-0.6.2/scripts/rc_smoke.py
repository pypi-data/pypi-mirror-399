#!/usr/bin/env python3
"""
Release-candidate smoke test for VibeGate.

Creates a temporary Python project with intentional issues and validates
that VibeGate handles all profiles correctly:
- fast: Quick checks only
- balanced: Default profile with standard checks
- ci: Full CI profile with all artifacts

Usage:
    python scripts/rc_smoke.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def create_test_project(project_dir: Path) -> None:
    """Create a minimal Python project with intentional issues."""
    # Create package directory
    pkg_dir = project_dir / "myapp"
    pkg_dir.mkdir()

    # Write __init__.py
    (pkg_dir / "__init__.py").write_text('"""Sample package."""\n')

    # Write main.py with intentional lint issue (unused import)
    (pkg_dir / "main.py").write_text(
        """\"\"\"Main module.\"\"\"

import os  # noqa: F401 - intentionally unused for smoke test
import sys


def greet(name: str) -> str:
    \"\"\"Greet someone by name.\"\"\"
    return f"Hello, {name}!"


def main() -> int:
    \"\"\"Entry point.\"\"\"
    print(greet("World"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""
    )

    # Write a simple test
    tests_dir = project_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_main.py").write_text(
        """\"\"\"Tests for main module.\"\"\"

from myapp.main import greet


def test_greet():
    \"\"\"Test greet function.\"\"\"
    assert greet("Test") == "Hello, Test!"
"""
    )

    # Write minimal pyproject.toml
    (project_dir / "pyproject.toml").write_text(
        """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp"
version = "0.1.0"
description = "Test project for VibeGate smoke test"
requires-python = ">=3.10"
"""
    )

    # Write vibegate.yaml with all three profiles
    (project_dir / "vibegate.yaml").write_text(
        """version: 2

# Base configuration
format_check:
  enabled: true
lint:
  enabled: true
typecheck:
  enabled: false  # Keep fast for smoke test
tests:
  enabled: true
  command: pytest

# Profile definitions
profiles:
  fast:
    format_check:
      enabled: true
    lint:
      enabled: true
    typecheck:
      enabled: false
    tests:
      enabled: false

  balanced:
    format_check:
      enabled: true
    lint:
      enabled: true
    typecheck:
      enabled: false
    tests:
      enabled: true
    artifacts_dir: .vibegate

  ci:
    format_check:
      enabled: true
    lint:
      enabled: true
    typecheck:
      enabled: false
    tests:
      enabled: true
    artifacts_dir: artifacts
    evidence_dir: evidence
"""
    )


def run_vibegate_profile(
    project_dir: Path, profile: str, venv_python: Path
) -> tuple[bool, str]:
    """
    Run vibegate with a specific profile.

    Returns:
        Tuple of (success, error_message)
    """
    cmd = [
        str(venv_python),
        "-m",
        "vibegate",
        "run",
        str(project_dir),
        "--profile",
        profile,
        "--no-view",
    ]

    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(Path(__file__).resolve().parent.parent / "src")},
    )

    # Exit code should be 0 (pass) or 1 (findings), never 2 (config error)
    if result.returncode == 2:
        return False, f"Config error (exit 2): {result.stderr}"
    if result.returncode not in (0, 1):
        return False, f"Unexpected exit code {result.returncode}: {result.stderr}"

    return True, ""


def validate_profile_outputs(project_dir: Path, profile: str) -> tuple[bool, str]:
    """
    Validate that profile created expected output directories.

    Returns:
        Tuple of (success, error_message)
    """
    if profile == "balanced":
        vibegate_dir = project_dir / ".vibegate"
        if not vibegate_dir.exists():
            return False, f"Profile '{profile}' should create .vibegate/ but didn't"
        if not (vibegate_dir / "plain_report.md").exists():
            return (
                False,
                f"Profile '{profile}' should create .vibegate/plain_report.md",
            )

    elif profile == "ci":
        artifacts_dir = project_dir / "artifacts"
        evidence_dir = project_dir / "evidence"
        if not artifacts_dir.exists():
            return False, f"Profile '{profile}' should create artifacts/ but didn't"
        if not evidence_dir.exists():
            return False, f"Profile '{profile}' should create evidence/ but didn't"
        if not (artifacts_dir / "vibegate_report.md").exists():
            return (
                False,
                f"Profile '{profile}' should create artifacts/vibegate_report.md",
            )
        if not (evidence_dir / "vibegate.jsonl").exists():
            return (
                False,
                f"Profile '{profile}' should create evidence/vibegate.jsonl",
            )

    return True, ""


def main() -> int:
    """Run RC smoke test."""
    print("=" * 70)
    print("🚀 VibeGate Release Candidate Smoke Test")
    print("=" * 70)
    print("\nValidating VibeGate profiles on a minimal test project...\n")

    # Create temporary directory for test project
    temp_dir = Path(tempfile.mkdtemp(prefix="vibegate-rc-smoke-"))
    venv_dir = None

    try:
        # Create test project
        print("📦 Creating test project...")
        create_test_project(temp_dir)
        print(f"   Created project in: {temp_dir}")

        # Create virtual environment and install vibegate
        print("\n🔧 Setting up virtual environment...")
        venv_dir = temp_dir / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

        # Determine venv python path
        if (venv_dir / "bin" / "python").exists():
            venv_python = venv_dir / "bin" / "python"
        else:
            venv_python = venv_dir / "Scripts" / "python.exe"

        # Install vibegate from source
        repo_root = Path(__file__).resolve().parent.parent
        print(f"   Installing vibegate from: {repo_root}")
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-q", str(repo_root)],
            check=True,
        )

        # Install pytest for test running
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-q", "pytest"], check=True
        )

        # Test each profile
        profiles = ["fast", "balanced", "ci"]
        all_passed = True

        for profile in profiles:
            print(f"\n🧪 Testing profile: {profile}")
            print("-" * 70)

            # Run vibegate
            success, error_msg = run_vibegate_profile(temp_dir, profile, venv_python)
            if not success:
                print(f"  ❌ FAIL: {error_msg}")
                all_passed = False
                continue

            # Validate outputs
            success, error_msg = validate_profile_outputs(temp_dir, profile)
            if not success:
                print(f"  ❌ FAIL: {error_msg}")
                all_passed = False
                continue

            print(f"  ✅ PASS: Profile '{profile}' works correctly")

        # Final summary
        print("\n" + "=" * 70)
        if all_passed:
            print("✅ ALL PROFILE TESTS PASSED!")
            print("=" * 70)
            print("\n🎉 VibeGate is ready for release!")
            return 0
        else:
            print("❌ SOME PROFILE TESTS FAILED")
            print("=" * 70)
            print("\n⚠️  Fix the issues above before releasing.")
            return 1

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1

    finally:
        # Cleanup
        if temp_dir.exists():
            print(f"\n🧹 Cleaning up: {temp_dir}")
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    sys.exit(main())
