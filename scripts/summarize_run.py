#!/usr/bin/env python3
"""Summarize a GuiAgent batch directory into comparable pilot metrics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _action_steps(stat: dict[str, Any]) -> int:
    steps = stat.get("steps")
    if isinstance(steps, list):
        return sum(1 for entry in steps if entry.get("kind") == "step")
    return int(steps or 0)


def summarize(batch: Path) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for case_dir in sorted(path for path in batch.iterdir() if path.is_dir()):
        verdict_path = case_dir / "judge_result.json"
        if not verdict_path.exists():
            continue
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
        stat_path = case_dir / "execution_stat.json"
        stat = json.loads(stat_path.read_text(encoding="utf-8")) if stat_path.exists() else {}
        cases.append(
            {
                "task_id": case_dir.name.split("_", 1)[-1],
                "score": float(verdict.get("overall_score") or 0.0),
                "passed": bool(verdict.get("passed")),
                "action_steps": _action_steps(stat),
                "failure_reason": verdict.get("failure_reason"),
            }
        )
    if not cases:
        raise SystemExit(f"no judged cases under {batch}")

    passed = [case for case in cases if case["passed"]]
    total_steps = sum(case["action_steps"] for case in cases)
    return {
        "batch": batch.name,
        "cases": len(cases),
        "passed": len(passed),
        "pass_rate": round(len(passed) / len(cases), 4),
        "mean_score": round(sum(case["score"] for case in cases) / len(cases), 4),
        "action_steps_total": total_steps,
        "action_steps_mean": round(total_steps / len(cases), 2),
        "action_steps_per_success": (
            round(total_steps / len(passed), 2) if passed else None
        ),
        "results": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summary = summarize(args.batch_dir)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    headline = {key: summary[key] for key in list(summary)[:-1]}
    print(json.dumps(headline, ensure_ascii=False))


if __name__ == "__main__":
    main()
