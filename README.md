# SkillForge-CUA Pilot

This repository contains the first reproducible stage of the
PoA-to-Node-skill experiment:

1. read CUA trajectory `result.json` files;
2. keep evaluator-confirmed successful runs;
3. remove task values and screen coordinates from action signatures;
4. hard-bucket by application and intent;
5. cluster by action bigrams and instruction similarity;
6. emit auditable skill candidates for later NodeREPL compilation and
   CUA-Gym validation.

The first stage deliberately does not use embedding-only clustering. A GUI
trajectory must share an application, intent, and sufficiently similar action
structure before it can become a skill candidate.

## Run

```bash
python -m pip install -e ".[dev]"
skillforge-cua discover /path/to/trajectories \
  --output artifacts/skill_candidates.json \
  --threshold 0.35 \
  --min-size 2
pytest
```

The generated manifest records every source path and the normalized action
skeleton, so clusters can be manually audited before any JavaScript is executed.

## Pilot gates

The next stages compile approved candidates to restricted NodeREPL functions and
validate them against isolated CUA-Gym-Hub sessions. Private MockApp state and
reward endpoints remain unavailable to the agent; only the evaluator may use
them.

The pilot proceeds to full evaluation only if a frozen held-out task set shows
one of:

- at least 5 percentage points higher task success; or
- at least 15% fewer model calls/actions without lower task success.
