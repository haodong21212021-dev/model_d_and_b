from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Iterable


def _score(value: str, seed: str) -> str:
    return hashlib.sha256(f"{seed}:{value}".encode()).hexdigest()


def _entry(row: dict[str, Any]) -> dict[str, Any]:
    instruction = str(row.get("instruction", ""))
    return {
        "id": row["id"],
        "app_type": row.get("app_type"),
        "difficulty": row.get("difficulty"),
        "instruction_sha256": hashlib.sha256(instruction.encode()).hexdigest(),
    }


def build_experiment_split(
    rows: Iterable[dict[str, Any]],
    *,
    seed: str = "skillforge-v1",
    app_family: str = "mock_web",
    train_app_ratio: float = 0.7,
    dev_app_ratio: float = 0.15,
    induction_ratio: float = 0.6,
    validation_ratio: float = 0.2,
) -> dict[str, Any]:
    selected = [
        row
        for row in rows
        if row.get("app_family") == app_family and row.get("id") and row.get("app_type")
    ]
    by_app: dict[str, list[dict[str, Any]]] = {}
    for row in selected:
        by_app.setdefault(str(row["app_type"]), []).append(row)
    apps = sorted(by_app, key=lambda app: _score(app, seed))
    train_end = max(1, round(len(apps) * train_app_ratio))
    dev_end = max(train_end + 1, round(len(apps) * (train_app_ratio + dev_app_ratio)))
    train_apps = set(apps[:train_end])
    dev_apps = set(apps[train_end:dev_end])
    test_apps = set(apps[dev_end:])

    splits: dict[str, list[dict[str, Any]]] = {
        "skill_induction": [],
        "skill_validation": [],
        "seen_app_test": [],
        "unseen_app_dev": [],
        "unseen_app_test": [],
    }
    for app, app_rows in by_app.items():
        ordered = sorted(app_rows, key=lambda row: _score(str(row["id"]), seed))
        if app in train_apps:
            induction_end = max(1, round(len(ordered) * induction_ratio))
            validation_end = max(
                induction_end + 1,
                round(len(ordered) * (induction_ratio + validation_ratio)),
            )
            partitions = (
                ("skill_induction", ordered[:induction_end]),
                ("skill_validation", ordered[induction_end:validation_end]),
                ("seen_app_test", ordered[validation_end:]),
            )
        elif app in dev_apps:
            partitions = (("unseen_app_dev", ordered),)
        else:
            partitions = (("unseen_app_test", ordered),)
        for name, partition in partitions:
            splits[name].extend(_entry(row) for row in partition)

    for partition in splits.values():
        partition.sort(key=lambda row: (str(row["app_type"]), str(row["id"])))
    counts = {name: len(partition) for name, partition in splits.items()}
    return {
        "schema_version": 1,
        "seed": seed,
        "filter": {"app_family": app_family},
        "ratios": {
            "train_apps": train_app_ratio,
            "dev_apps": dev_app_ratio,
            "test_apps": round(1 - train_app_ratio - dev_app_ratio, 10),
            "skill_induction_within_train_apps": induction_ratio,
            "skill_validation_within_train_apps": validation_ratio,
            "seen_app_test_within_train_apps": round(
                1 - induction_ratio - validation_ratio, 10
            ),
        },
        "apps": {
            "train": sorted(train_apps),
            "dev": sorted(dev_apps),
            "test": sorted(test_apps),
        },
        "summary": {
            "source_rows": len(selected),
            "apps": len(apps),
            "split_counts": counts,
            "difficulty_counts": dict(
                sorted(Counter(str(row.get("difficulty")) for row in selected).items())
            ),
        },
        "splits": splits,
    }
