from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


_WORDS = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]+")
_QUOTED = re.compile(r"""["']([^"' \n][^"'\n]*?)["']""")
_NUMBER = re.compile(r"\b\d+(?:\.\d+)?\b")
_STOP_WORDS = {
    "a",
    "all",
    "and",
    "app",
    "application",
    "be",
    "in",
    "into",
    "it",
    "of",
    "on",
    "open",
    "please",
    "the",
    "then",
    "to",
    "using",
    "with",
}
_INTENTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("create", ("create", "add", "insert", "new", "write")),
    ("edit", ("edit", "change", "modify", "replace", "rename", "update")),
    ("delete", ("clear", "delete", "remove")),
    ("search", ("count", "filter", "find", "locate", "search")),
    ("format", ("align", "bold", "color", "format", "style")),
    ("configure", ("disable", "enable", "preference", "set", "setting")),
    ("transfer", ("copy", "download", "export", "move", "save", "upload")),
    ("media", ("pause", "play", "seek", "speed", "volume")),
    ("calculate", ("calculate", "compute", "formula", "sum")),
    ("open", ("launch", "open", "start")),
)


@dataclass(frozen=True)
class Trajectory:
    path: str
    app: str
    instruction: str
    actions: tuple[str, ...]
    steps: int
    success: bool

    @property
    def intent(self) -> str:
        words = set(_tokenize(self.instruction))
        for intent, hints in _INTENTS:
            if words.intersection(hints):
                return intent
        return "other"

    @property
    def instruction_tokens(self) -> frozenset[str]:
        return frozenset(_tokenize(self.instruction))

    @property
    def action_ngrams(self) -> frozenset[str]:
        if len(self.actions) < 2:
            return frozenset(self.actions)
        return frozenset(
            f"{left}>{right}" for left, right in zip(self.actions, self.actions[1:])
        )


def _tokenize(text: str) -> list[str]:
    return [
        word.lower()
        for word in _WORDS.findall(text)
        if word.lower() not in _STOP_WORDS and len(word) > 1
    ]


def _normalize_action(action: dict[str, Any]) -> str:
    name = str(action.get("name", "unknown")).lower()
    arguments = action.get("arguments") or {}
    kind = str(arguments.get("action", name)).lower()
    if kind == "key":
        keys = arguments.get("keys") or []
        return "key:" + "+".join(str(key).lower() for key in keys)
    if kind == "type":
        return "type:<text>"
    if kind == "wait":
        return "wait"
    if kind in {"left_click", "right_click", "double_click"}:
        return kind
    if kind == "scroll":
        pixels = arguments.get("pixels", 0)
        return "scroll:down" if isinstance(pixels, (int, float)) and pixels < 0 else "scroll:up"
    return f"{name}:{kind}"


def load_trajectory(path: Path, root: Path | None = None) -> Trajectory:
    raw = json.loads(path.read_text(encoding="utf-8"))
    actions: list[str] = []
    for step in raw.get("trajectory", []):
        for action in step.get("actions", []):
            normalized = _normalize_action(action)
            if not normalized.endswith(":terminate"):
                actions.append(normalized)
    relative = path.relative_to(root) if root else path
    app = (
        raw.get("app")
        or raw.get("domain")
        or (relative.parts[0] if len(relative.parts) >= 3 else path.parent.parent.name)
    )
    status = str(raw.get("final_status", "")).lower()
    success = status == "success" and bool(raw.get("done", True))
    return Trajectory(
        path=str(path),
        app=str(app),
        instruction=str(raw.get("instruction", "")),
        actions=tuple(actions),
        steps=int(raw.get("steps", len(actions))),
        success=success,
    )


def find_trajectories(root: Path) -> list[Trajectory]:
    trajectories: list[Trajectory] = []
    for path in sorted(root.rglob("result.json")):
        try:
            trajectories.append(load_trajectory(path, root))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    return trajectories


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def similarity(left: Trajectory, right: Trajectory) -> float:
    if left.app != right.app or left.intent != right.intent:
        return 0.0
    action_score = _jaccard(left.action_ngrams, right.action_ngrams)
    instruction_score = _jaccard(left.instruction_tokens, right.instruction_tokens)
    return 0.7 * action_score + 0.3 * instruction_score


def cluster_trajectories(
    trajectories: Iterable[Trajectory],
    threshold: float = 0.35,
    min_size: int = 2,
) -> list[list[Trajectory]]:
    """Greedily form complete-link clusters under a similarity threshold."""
    rows = sorted(
        (trajectory for trajectory in trajectories if trajectory.success),
        key=lambda row: row.path,
    )
    buckets: dict[tuple[str, str], list[Trajectory]] = {}
    for row in rows:
        buckets.setdefault((row.app, row.intent), []).append(row)
    groups: list[list[Trajectory]] = []
    for bucket_rows in buckets.values():
        bucket_groups: list[list[Trajectory]] = []
        for row in bucket_rows:
            compatible = [
                group
                for group in bucket_groups
                if all(similarity(row, member) >= threshold for member in group)
            ]
            if compatible:
                best = max(
                    compatible,
                    key=lambda group: (
                        sum(similarity(row, member) for member in group) / len(group),
                        -len(group),
                    ),
                )
                best.append(row)
            else:
                bucket_groups.append([row])
        groups.extend(bucket_groups)
    return sorted(
        (group for group in groups if len(group) >= min_size),
        key=lambda group: (-len(group), group[0].app, group[0].intent),
    )


def _common_action_skeleton(group: list[Trajectory]) -> list[str]:
    frequency = Counter(action for row in group for action in set(row.actions))
    required = {
        action
        for action, count in frequency.items()
        if count / len(group) >= 0.6
    }
    representative = min(group, key=lambda row: (row.steps, row.path))
    return [action for action in representative.actions if action in required]


def _parameter_examples(group: list[Trajectory]) -> list[str]:
    values: list[str] = []
    for row in group:
        values.extend(_QUOTED.findall(row.instruction))
        values.extend(_NUMBER.findall(row.instruction))
    return sorted(set(values))[:20]


def build_manifest(
    trajectories: list[Trajectory],
    threshold: float = 0.35,
    min_size: int = 2,
) -> dict[str, Any]:
    groups = cluster_trajectories(trajectories, threshold, min_size)
    skills: list[dict[str, Any]] = []
    counters: Counter[tuple[str, str]] = Counter()
    for group in groups:
        app, intent = group[0].app, group[0].intent
        counters[(app, intent)] += 1
        suffix = counters[(app, intent)]
        name = f"{app}_{intent}_{suffix}".replace("-", "_")
        pair_scores = [
            similarity(left, right)
            for index, left in enumerate(group)
            for right in group[index + 1 :]
        ]
        skills.append(
            {
                "name": name,
                "app": app,
                "intent": intent,
                "trajectory_count": len(group),
                "mean_pair_similarity": round(
                    sum(pair_scores) / len(pair_scores) if pair_scores else 1.0, 4
                ),
                "median_steps": sorted(row.steps for row in group)[len(group) // 2],
                "action_skeleton": _common_action_skeleton(group),
                "parameter_examples": _parameter_examples(group),
                "instruction_examples": [row.instruction for row in group],
                "source_paths": [row.path for row in group],
                "status": (
                    "needs_review"
                    if intent == "other"
                    or (sum(pair_scores) / len(pair_scores) if pair_scores else 1.0)
                    < 0.45
                    else "candidate"
                ),
            }
        )
    successful = [row for row in trajectories if row.success]
    return {
        "schema_version": 1,
        "settings": {"threshold": threshold, "min_size": min_size},
        "summary": {
            "trajectories_total": len(trajectories),
            "trajectories_successful": len(successful),
            "candidate_skills": len(skills),
            "covered_successful_trajectories": sum(
                skill["trajectory_count"] for skill in skills
            ),
        },
        "skills": skills,
    }
