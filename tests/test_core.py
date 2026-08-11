import json
from pathlib import Path

from skillforge_cua.core import (
    Trajectory,
    build_manifest,
    cluster_trajectories,
    load_trajectory,
    similarity,
)


def _row(path: str, instruction: str, actions: tuple[str, ...]) -> Trajectory:
    return Trajectory(
        path=path,
        app="crm_mock",
        instruction=instruction,
        actions=actions,
        steps=len(actions),
        success=True,
    )


def test_load_trajectory_normalizes_values_and_coordinates(tmp_path: Path) -> None:
    result = tmp_path / "crm" / "task" / "result.json"
    result.parent.mkdir(parents=True)
    result.write_text(
        json.dumps(
            {
                "instruction": "Create lead Alice",
                "done": True,
                "final_status": "success",
                "steps": 3,
                "trajectory": [
                    {
                        "actions": [
                            {
                                "name": "computer_use",
                                "arguments": {
                                    "action": "left_click",
                                    "coordinate": [10, 20],
                                },
                            }
                        ]
                    },
                    {
                        "actions": [
                            {
                                "name": "computer_use",
                                "arguments": {"action": "type", "text": "Alice"},
                            }
                        ]
                    },
                    {
                        "actions": [
                            {
                                "name": "computer_use",
                                "arguments": {
                                    "action": "key",
                                    "keys": ["CTRL", "S"],
                                },
                            }
                        ]
                    },
                    {
                        "actions": [
                            {
                                "name": "computer_use",
                                "arguments": {"action": "terminate"},
                            }
                        ]
                    },
                ],
            }
        )
    )
    row = load_trajectory(result, tmp_path)
    assert row.app == "crm"
    assert row.actions == ("left_click", "type:<text>", "key:ctrl+s")
    assert row.success


def test_similarity_requires_same_app_and_intent() -> None:
    left = _row(
        "a",
        'Create a lead named "Alice"',
        ("left_click", "type:<text>", "left_click"),
    )
    right = _row(
        "b",
        'Add a new lead named "Bob"',
        ("left_click", "type:<text>", "left_click"),
    )
    other = Trajectory(
        path="c",
        app="calendar_mock",
        instruction="Create an event",
        actions=right.actions,
        steps=3,
        success=True,
    )
    assert similarity(left, right) > 0.7
    assert similarity(left, other) == 0.0


def test_clustering_excludes_failures_and_small_groups() -> None:
    action_flow = ("left_click", "type:<text>", "left_click")
    rows = [
        _row("a", 'Create lead "Alice"', action_flow),
        _row("b", 'Add new lead "Bob"', action_flow),
        _row("c", "Delete a lead", ("left_click", "key:delete")),
        Trajectory(
            path="d",
            app="crm_mock",
            instruction='Create lead "Carol"',
            actions=action_flow,
            steps=3,
            success=False,
        ),
    ]
    groups = cluster_trajectories(rows, threshold=0.3, min_size=2)
    assert [[row.path for row in group] for group in groups] == [["a", "b"]]


def test_manifest_is_auditable() -> None:
    rows = [
        _row(
            "a",
            'Create lead "Alice" at "Acme"',
            ("left_click", "type:<text>", "type:<text>", "left_click"),
        ),
        _row(
            "b",
            'Add new lead "Bob" at "Beta"',
            ("left_click", "type:<text>", "type:<text>", "left_click"),
        ),
    ]
    manifest = build_manifest(rows, threshold=0.3)
    assert manifest["summary"]["candidate_skills"] == 1
    skill = manifest["skills"][0]
    assert skill["app"] == "crm_mock"
    assert skill["trajectory_count"] == 2
    assert skill["action_skeleton"] == [
        "left_click",
        "type:<text>",
        "type:<text>",
        "left_click",
    ]
    assert skill["instruction_examples"] == [
        'Create lead "Alice" at "Acme"',
        'Add new lead "Bob" at "Beta"',
    ]
    assert {"Alice", "Acme", "Bob", "Beta"}.issubset(skill["parameter_examples"])
