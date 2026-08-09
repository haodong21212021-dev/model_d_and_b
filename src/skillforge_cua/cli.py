from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import build_manifest, find_trajectories


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skillforge-cua",
        description="Discover reusable CUA skill candidates from trajectory result files.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    discover = subcommands.add_parser("discover")
    discover.add_argument("trajectory_root", type=Path)
    discover.add_argument("--output", type=Path, required=True)
    discover.add_argument("--threshold", type=float, default=0.35)
    discover.add_argument("--min-size", type=int, default=2)
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.command == "discover":
        trajectories = find_trajectories(args.trajectory_root)
        manifest = build_manifest(
            trajectories,
            threshold=args.threshold,
            min_size=args.min_size,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(manifest["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
