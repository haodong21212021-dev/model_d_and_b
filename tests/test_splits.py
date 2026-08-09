from skillforge_cua.splits import build_experiment_split


def _rows(app: str, count: int) -> list[dict]:
    return [
        {
            "id": f"{app}-{index}",
            "instruction": f"Complete operation {index} in {app}",
            "app_type": app,
            "app_family": "mock_web",
            "difficulty": "medium",
        }
        for index in range(count)
    ]


def test_split_has_no_task_or_app_leakage() -> None:
    rows = []
    for index in range(10):
        rows.extend(_rows(f"app_{index}", 10))
    manifest = build_experiment_split(rows, seed="test")
    splits = manifest["splits"]
    all_ids = [row["id"] for partition in splits.values() for row in partition]
    assert len(all_ids) == len(set(all_ids)) == 100

    train_apps = set(manifest["apps"]["train"])
    dev_apps = set(manifest["apps"]["dev"])
    test_apps = set(manifest["apps"]["test"])
    assert not (train_apps & dev_apps or train_apps & test_apps or dev_apps & test_apps)
    assert {row["app_type"] for row in splits["unseen_app_dev"]} == dev_apps
    assert {row["app_type"] for row in splits["unseen_app_test"]} == test_apps
    assert all(
        row["app_type"] in train_apps
        for name in ("skill_induction", "skill_validation", "seen_app_test")
        for row in splits[name]
    )


def test_split_is_deterministic_and_filters_family() -> None:
    rows = _rows("calendar_mock", 10) + _rows("crm_mock", 10)
    rows.append(
        {
            "id": "desktop-1",
            "instruction": "Desktop task",
            "app_type": "vscode",
            "app_family": "desktop",
            "difficulty": "hard",
        }
    )
    first = build_experiment_split(rows, seed="fixed")
    second = build_experiment_split(reversed(rows), seed="fixed")
    assert first == second
    assert first["summary"]["source_rows"] == 20
