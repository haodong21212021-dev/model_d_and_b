#!/usr/bin/env python3
"""Select a deterministic, non-floor pilot task set from a frozen CUA-Gym split."""
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path

import pyarrow.parquet as pq
import zstandard


def select(rows, split, partition, difficulties, per_app, limit):
    allowed = {entry["id"] for entry in split["splits"][partition]}
    pool = [
        row
        for row in rows
        if row["id"] in allowed and row.get("difficulty") in difficulties
    ]
    pool.sort(
        key=lambda row: hashlib.sha256(
            f"{split['seed']}:pilot:{row['id']}".encode()
        ).hexdigest()
    )
    per_app_count: dict[str, int] = {}
    selected = []
    for row in pool:
        app = str(row["app_type"])
        if per_app_count.get(app, 0) >= per_app:
            continue
        per_app_count[app] = per_app_count.get(app, 0) + 1
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def extract(archive: Path, task_ids: set[str], destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    resolved_root = destination.resolve()
    extracted = 0
    with archive.open("rb") as raw:
        with zstandard.ZstdDecompressor().stream_reader(raw) as stream:
            with tarfile.open(fileobj=stream, mode="r|") as tar:
                for member in tar:
                    parts = Path(member.name).parts
                    if not parts or parts[0] not in task_ids:
                        continue
                    target = (destination / member.name).resolve()
                    if resolved_root not in target.parents:
                        raise RuntimeError(f"unsafe archive member: {member.name}")
                    tar.extract(member, destination, filter="data")
                    extracted += 1
    return extracted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks_parquet", type=Path)
    parser.add_argument("split_manifest", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--artifacts-dir", type=Path)
    parser.add_argument("--partition", default="skill_induction")
    parser.add_argument("--difficulties", default="easy,medium")
    parser.add_argument("--per-app", type=int, default=2)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = pq.read_table(args.tasks_parquet).to_pylist()
    split = json.loads(args.split_manifest.read_text(encoding="utf-8"))
    difficulties = {value for value in args.difficulties.split(",") if value}
    selected = select(
        rows, split, args.partition, difficulties, args.per_app, args.limit
    )

    manifest = {
        "seed": split["seed"],
        "partition": args.partition,
        "difficulties": sorted(difficulties),
        "task_count": len(selected),
        "tasks": [
            {
                "id": row["id"],
                "app_type": row["app_type"],
                "difficulty": row["difficulty"],
                "instruction": row["instruction"],
            }
            for row in selected
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if args.archive and args.artifacts_dir:
        members = extract(
            args.archive, {row["id"] for row in selected}, args.artifacts_dir
        )
        manifest["extracted_members"] = members
        args.output.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(
        json.dumps(
            {
                "task_count": manifest["task_count"],
                "apps": sorted({row["app_type"] for row in selected}),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
