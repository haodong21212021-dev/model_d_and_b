# Competitive Map for Automatic Skill Induction

Date: 2026-08-13

This revises the novelty assessment recorded earlier. Two differentiators
previously treated as open are already published, so the estimate is lowered.

## Naming

`SkillForge-CUA` was an internal working name coined in this project. It collides
with existing work and must not be used in a publication:

| Existing | What it is |
|---|---|
| SkillForge (arXiv 2604.08618) | self-evolving agent skills for cloud technical support |
| skillforge.expert | commercial product converting screen recordings into `SKILL.md` |
| yvzhou1111/skillforge | agent-skill dependency and audit tooling |

The commercial product is the closest surface-level overlap, since it already
sells "recorded interaction to reusable skill".

## Differentiators that are no longer open

| Proposed differentiator | Already published as | What it covers |
|---|---|---|
| Semantic skill representation instead of coordinate or DOM action sequences | **W2S / Skill-IR** (arXiv 2606.06893) | Skill-IR decomposes a skill into workflow structure, execution semantics, and runtime attachments; segments traces, induces drafts, merges shared structure, reconciles conditional branches, and preserves verification, approval, rollback, and state management. 70 skills, +10.5% behavioural replay consistency over summarization and prompting baselines |
| Verified non-parametric skills with regression accounting and cross-model transfer | **SkillGen** (arXiv 2605.10999) | models skills as interventions, comparing outcomes on the same instances with and without the skill so that both repairs and regressions are counted; improves held-out accuracy for all eight evaluated base LLMs by +3.27 to +10.08pp; reports skills that transfer across models |

SkillGen's intervention framing is the same control this project identified as
necessary for measuring false activation. It is prior art, not a contribution.

## Crowding in the surrounding area

| Work | Contribution |
|---|---|
| ASI (COLM 2025) | induces, verifies, and applies executable programmatic skills online; WebArena +23.5% over static, +11.3% over text skills, 10.7–15.3% fewer steps |
| AWM (ICML 2025) | induces textual workflows from trajectories; WebArena and Mind2Web gains |
| MIND-Skill | induction plus deduction agent with reconstruction, outcome, and rubric losses optimized via TextGrad; AppWorld and BFCL-v3 |
| SkillX | three-level skill hierarchy with iterative refinement and exploratory expansion; AppWorld, BFCL-v3, tau2-Bench |
| Trace2Skill | consolidates trajectory-local lessons into a skill directory; transfers across model scales and families |
| AFTER | 382 enterprise tasks benchmarking procedural-memory transfer across tasks, roles, and backbones |
| SkillAxe, SkillEval, Skill Smell Detector | evaluation and refinement of authored skills |
| CUA-Skill | 452 hand-engineered Windows skills with execution and composition graphs; WAA 57.5% best-of-three |
| Auto-SKILL.md (arXiv 2606.20363) | automatic induction from GUI trajectories; negative transfer on WebArena, lost to a frequency prior |

## The remaining gap

Almost every automatic-induction result above is evaluated on tool-calling or
text-workflow agents rather than pixel-level GUI control:

| Work | Evaluation surface |
|---|---|
| SkillGen | interactive, scientific, coding, tool use |
| MIND-Skill, SkillX | AppWorld, BFCL-v3, tau2-Bench |
| W2S | execution logs and workflow traces |
| Trace2Skill | office workflows, math, visual QA |
| SkillForge | support tickets |
| Auto-SKILL.md | GUI trajectories, negative result |
| CUA-Skill | real Windows GUI, hand-authored |

So for real GUI computer-use agents, automatic skill induction has exactly one
published attempt, which failed, and one successful system built by hand.

The specific axis none of them tests is **cross-implementation grounding**: a
skill induced on one implementation of a product executing against a different,
real implementation. Existing work reuses skills within the same tool API
(AppWorld, BFCL), within the same website (ASI), or without any GUI at all.

That axis is the only one that can still carry an independent contribution here:

> whether a skill induced on a synthesized application executes on the real
> software it imitates, and whether that holds without updating model weights.

## Revised probability

The earlier estimate of 25–40% for a full-strength version assumed the semantic
representation and verified-intervention axes were open. They are not.

| Version | Venue estimate |
|---|---|
| Auto-induce from mock trajectories, evaluate on one benchmark | below 10% |
| Add semantic representation and counterfactual validation, single target | 15–25% |
| Establish cross-implementation grounding on two real benchmarks, two models, with the full control set | 20–30% |
| Workshop | high |

A negative result remains publishable if it isolates why cross-implementation
grounding fails, since Auto-SKILL.md left that mechanism unexplained.

## Consequence for the go/no-go

The pilot should be reframed to attack cross-implementation grounding first,
because it is both the only open axis and the most likely failure point. If a
skill induced on `gitlab_mock` cannot execute against real self-hosted GitLab,
the remaining contributions are already covered by SkillGen and W2S, and the
direction should be abandoned rather than scaled.
