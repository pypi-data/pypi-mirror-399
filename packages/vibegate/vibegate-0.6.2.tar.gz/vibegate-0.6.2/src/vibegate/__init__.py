"""VibeGate package."""

from importlib import metadata
from pathlib import Path

__all__ = ["__version__"]


def _get_version() -> str:
    """Get version from installed metadata, pyproject.toml, or fallback."""
    # Try installed package metadata first
    try:
        return metadata.version("vibegate")
    except metadata.PackageNotFoundError:
        # Package not installed, try reading from pyproject.toml
        pass  # Fall through to next method

    # Try reading from pyproject.toml (for dev/source installs)
    try:
        import sys

        if sys.version_info >= (3, 11):
            import tomllib
        else:
            # Python 3.10 doesn't have tomllib, so we parse manually
            pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
            if pyproject_path.exists():
                content = pyproject_path.read_text(encoding="utf-8")
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("version") and "=" in line:
                        # Extract version = "0.4.0"
                        version_str = (
                            line.split("=", 1)[1].strip().strip('"').strip("'")
                        )
                        if version_str:
                            return version_str
            return "0.4.0"  # Fallback if parsing fails

        # Use tomllib for Python 3.11+
        pyproject_path = Path(__file__).resolve().parents[2] / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
                return pyproject_data.get("project", {}).get("version", "0.4.0")
    except Exception:  # pragma: no cover
        # Failed to read pyproject.toml, use fallback version
        pass  # Fall through to final fallback

    # Final fallback
    return "0.4.0"


__version__ = _get_version()
