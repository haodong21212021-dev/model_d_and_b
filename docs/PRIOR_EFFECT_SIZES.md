# Automatic Skill Induction: What Was Built, and How Much It Gained

Date: 2026-08-13

Compiled to calibrate the expected effect size for this project. Reported figures
are taken from paper abstracts, project pages, and overview summaries gathered in
this session. Where a source states a relative improvement, it is labelled as
relative; conflating relative and absolute numbers is the main way this
literature gets misread.

## Capabilities that have already been built

Automatic skill induction is not one function. Across published systems the
following components all exist:

| Component | Implemented in |
|---|---|
| Segment trajectories into candidate skill units | Auto-SKILL.md, W2S |
| Cluster segments into a skill vocabulary | Auto-SKILL.md |
| Abstract task-specific values into parameters | AWM, ASI, MIND-Skill |
| Emit skills as free text or Markdown | AWM, SkillForge, Trace2Skill |
| Emit skills as executable programs | ASI, CUA-Skill |
| Emit skills as a structured intermediate representation | W2S (Skill-IR) |
| Verify a skill by re-executing it | ASI, MIND-Skill |
| Verify a skill as an intervention, counting repairs and regressions | SkillGen |
| Induce from failed trajectories as well as successful ones | SkillGen, SEAgent, Trace2Skill |
| Retrieve and rerank skills at inference time | CUA-Skill, AWM |
| Refine or rewrite skills from execution feedback | SkillForge, SkillAxe, SkillX, Trace2Skill |
| Multi-level skill hierarchies | SkillX |
| Skill quality auditing and smell detection | SkillEval, Skill Smell Detector, SkillAxe |
| Benchmark procedural-memory transfer across tasks, roles, models | AFTER |

Little of the individual machinery is unbuilt. What varies is the evaluation
surface and whether the gain survives a transfer setting.

## Reported gains where it worked

| System | Environment | Reported gain | Relative or absolute |
|---|---|---|---|
| ASI | WebArena | 40.4% success; +23.5% over its static baseline, +11.3% over AWM; 10.7–15.3% fewer steps | gains relative |
| AWM | WebArena, Mind2Web | +51.1% success on WebArena, +24.6% step-wise on Mind2Web; also +7.9% over human-written workflows | relative |
| SkillGen | interactive, scientific, coding, tool use | +3.27 to +10.08 points held out, across all 8 base LLMs tested | absolute (points) |
| Trace2Skill | WikiTableQuestions and others | up to +57.65 points on one dataset, cross-scale and cross-family | absolute, best case |
| AFTER | 382 enterprise tasks | +3.7 to +6.7 points aggregate; +2.8 average on static split; +5.2 from one refinement round | absolute |
| W2S | 70 skills | +10.5% behavioural replay consistency | relative |
| SkillForge | cloud support tickets | +4.3pp strict, +3.6pp lenient consistency for domain-grounded over generic creator | absolute |
| OS-Copilot / FRIDAY | GAIA | +35% over previous methods | relative |
| CUA-Skill (hand-authored, not induced) | WindowsAgentArena | 57.5% best-of-three; trajectory generation 1.7–3.6× better than baselines | absolute and ratio |

Excluding the single best-case outlier, the recurring pattern for genuinely
held-out evaluation is **roughly 3 to 10 absolute points**, or **10 to 25 percent
relative**. Larger numbers usually come from a weak baseline, a single favourable
dataset, or a relative framing.

## Reported failures

| Finding | Source |
|---|---|
| Automatically induced GUI skills used for weight updates caused negative transfer: WebArena skill-step accuracy 55.8% to 44.2%; a most-frequent-skill prior beat the learned policies on the source domain | Auto-SKILL.md (arXiv 2606.20363) |
| LLM-authored skills provided no measurable improvement over bare agents despite being fluent and superficially plausible | SkillsBench, as cited in SkillAxe |
| Some procedural skills specialize to a role and lose effectiveness under transfer | AFTER |
| Rule-level refinement cannot detect a skill that teaches a fundamentally wrong strategy while staying internally consistent | SkillAxe, stated limitation |

So the field contains both consistent positive results and at least one clear
negative result and one no-effect finding.

## What separates the successes from the failures

Four patterns hold across the evidence.

**Executable beats free text.** ASI's programmatic skills outperformed AWM's
textual workflows by 11.3% relative on the same benchmark, attributed to being
verifiable by execution.

**Verification is the load-bearing part.** Every positive result includes some
execution-grounded check: ASI verifies correctness, skill usage, and skill
validity; MIND-Skill adds reconstruction, outcome, and rubric losses; SkillGen
measures the skill as an intervention so regressions are counted. The failure
case had only offline clustering plus an offline reward model.

**Non-parametric injection is safer than weight updates.** The negative transfer
appeared when an induced vocabulary was used to fine-tune a policy. Systems that
attach skills at inference time report positive or neutral outcomes.

**Reuse within a domain is far better evidenced than transfer across
implementations.** ASI reuses skills across websites in the same benchmark;
AppWorld and BFCL systems reuse within one tool API. No published system shows a
skill induced on one implementation of a product executing on a different real
implementation of that product.

## Calibration for this project

The go/no-go threshold of +5 absolute points sits inside the normal band of
published gains, so it is achievable but not a formality. It should not be
loosened, because a gain below that range is indistinguishable from the added
context effect the random-skill and fixed-frequent-skill controls are designed to
detect.

The environment matters as much as the method. ASI and AWM succeeded on WebArena,
where the accessibility tree and DOM provide stable handles. The one GUI-native
automatic induction attempt failed. Pixel-level grounding is therefore the part
of this project most likely to determine the outcome, which is consistent with
targeting cross-implementation grounding first.
