# Pilot Baseline Results

Date: 2026-08-09

## Configuration

| Item | Value |
|---|---|
| Model | `youtu-SFT-35B-a3B` (`ms-559hnlc2`, sglang, model id `/data/model`) |
| Agent | GuiAgent `qwenvl_v2`, `custom_v2` action space |
| Environment | Windows AGS sandbox with hosted CUA-Gym-Hub MockApps |
| Reward | Official per-task `reward.py`, pass threshold 0.5 |
| Step budget | 20 actions |
| Workers | 2 |
| Temperature | 0.0, reasoning traces disabled |

## Task selection

Ten tasks were drawn deterministically from the `skill_induction` partition of
the frozen `skillforge-v1` split, restricted to `easy` and `medium` difficulty
and capped at two tasks per application. Nine MockApp applications are covered.

An earlier three-task Google Calendar attempt is excluded: every Calendar task
in the public release is labeled `hard`, and all three scored zero, leaving no
measurement room.

## Result

| Metric | Value |
|---|---:|
| Tasks | 10 |
| Passed | 4 |
| Pass rate | 40.0% |
| Mean reward | 0.300 |
| Total action steps | 162 |
| Mean action steps | 16.2 |
| Action steps per success | 40.5 |

Per-task outcomes:

| Application | Score | Steps | Passed |
|---|---:|---:|:--:|
| microsoft_teams_mock | 0.8 | 6 | yes |
| notion_mock | 0.6 | 20 | yes |
| wechat_mock | 0.6 | 20 | yes |
| pinterest_mock | 1.0 | 5 | yes |
| uber_eats_mock | 0.0 | 20 | no |
| monday_mock | 0.0 | 20 | no |
| hubspot_mock | 0.0 | 20 | no |
| microsoft_teams_mock | 0.0 | 11 | no |
| outlook_web_mock | 0.0 | 20 | no |
| instacart_mock | 0.0 | 20 | no |

## Interpretation

The baseline is not at a floor or ceiling, so the frozen set can distinguish
methods. Six of ten failures ran to the 20-action budget, which is the pattern
verified skills are meant to improve: replacing long primitive click sequences
with one parameterized call.

This is a pilot-scale measurement. Ten tasks and a single seed cannot support a
confidence claim; it establishes the comparison point and the harness.

## Next step

Run the same frozen tasks under the skill-augmented system with fallback
enabled, then compare pass rate, mean reward, and action steps per success. The
pilot advances only with at least +5 percentage points pass rate, or at least
15% fewer action steps without a pass-rate regression.
