#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

from skillforge_cua.splits import build_experiment_split


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a leakage-resistant CUA-Gym skill experiment split."
    )
    parser.add_argument("tasks_parquet", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", default="skillforge-v1")
    parser.add_argument("--app-family", default="mock_web")
    args = parser.parse_args()

    source = args.tasks_parquet.read_bytes()
    rows = pq.read_table(args.tasks_parquet).to_pylist()
    manifest = build_experiment_split(
        rows,
        seed=args.seed,
        app_family=args.app_family,
    )
    manifest["source"] = {
        "path": str(args.tasks_parquet),
        "sha256": hashlib.sha256(source).hexdigest(),
        "parquet_rows": len(rows),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
