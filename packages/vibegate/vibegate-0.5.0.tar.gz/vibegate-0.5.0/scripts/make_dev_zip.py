#!/usr/bin/env python3
"""DEPRECATED: This script has been replaced by bundle_source.py.

Use instead:
    python scripts/bundle_source.py
    # or
    make bundle
"""

import sys


def main() -> None:
    """Print deprecation message and exit."""
    print("=" * 70)
    print("⚠️  DEPRECATED: make_dev_zip.py")
    print("=" * 70)
    print()
    print("This script has been replaced by bundle_source.py.")
    print()
    print("Use instead:")
    print("  python scripts/bundle_source.py")
    print("  # or")
    print("  make bundle")
    print()
    sys.exit(1)


if __name__ == "__main__":
    main()
