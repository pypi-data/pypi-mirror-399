from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SCHEMA_NAMES = [
    "vibegate.schema.json",
    "vibegate-events.schema.json",
    "fixpack.schema.json",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync schema files into the package.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if schema files differ without copying.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    source_dir = repo_root / "schema"
    target_dir = repo_root / "src" / "vibegate" / "schemas"

    missing: list[Path] = []
    for name in SCHEMA_NAMES:
        source_path = source_dir / name
        if not source_path.exists():
            missing.append(source_path)
            continue
        target_path = target_dir / name
        if args.check:
            if not target_path.exists():
                print(f"Missing schema copy: {target_path}", file=sys.stderr)
                return 1
            if source_path.read_bytes() != target_path.read_bytes():
                print(
                    f"Schema drift detected: {source_path} != {target_path}",
                    file=sys.stderr,
                )
                return 1
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_path)

    if missing:
        for path in missing:
            print(f"Missing schema: {path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
