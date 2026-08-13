# Why Combining Prior Systems Does Not Guarantee a Result

Date: 2026-08-13

## The composition argument, and why it fails

The plan reuses CUA-Gym as the environment, follows CUA-Skill for the skill
abstraction, and measures on published benchmarks. It is tempting to read that as
three proven components, so the combination should work. Each component's result
holds under a condition the combination removes.

| Prior result | What its evidence licenses | What it does not license |
|---|---|---|
| CUA-Skill, 57.5% best-of-three on WAA | a library of carefully engineered skills plus a retrieval agent improves a real desktop benchmark | that automatically induced skills do the same |
| CUA-Gym, OSWorld-Verified +7.6pp and WebArena +3.7pp | 32k verified tuples from mock and desktop environments improve a policy **through GSPO weight updates** | that non-parametric skills extracted from those environments transfer |
| OSWorld, WAA, WebArena, SaaS-Bench | the outcome can be measured objectively with programmatic rewards | anything about whether the method works |

CUA-Skill frames the missing piece as the absence of reusable structured skill
abstractions, and supplies them by hand. Its contribution is evidence that
human-authored skills help, not that skills can be produced automatically.

## The novel component is the one with a published negative result

Replacing hand-authored skills with automatically induced skills is the only
genuinely new element in the combination. That substitution is what
`Automating SKILL.md Generation` (arXiv 2606.20363) attempted, reporting WebArena
skill-step accuracy falling from 55.8% to 44.2% and a most-frequent-skill prior
outperforming its learned policies on the source domain.

So the accurate description of this project is not that it composes three
successful systems. It is that it targets the specific step where the closest
prior attempt failed.

## Evidence of difficulty already produced inside this project

Two measurements from the pilot bear directly on feasibility.

The first discovery run merged unrelated tasks. Two Chrome tasks, enabling Do Not
Track and changing the default font size, landed in a single candidate because
their click skeletons matched. After switching to complete-link clustering and
removing terminal actions, coverage fell from 39 successful trajectories to 25.
Being correct reduced the number of skills produced.

The 3/3 hardened MockApp validation used a **hand-written** `createCalendarEvent`
function, not an induced one. That result validates the harness — state injection,
parameter substitution, and programmatic reward checking — and says nothing about
whether induction can produce a skill of that quality.

## Stage decomposition

End-to-end success requires every stage to hold, so the risks multiply.

| Stage | Required property | Current evidence |
|---|---|---|
| Induction | produces a reusable abstraction rather than a source-bound template | first version merged unrelated tasks |
| Validation | skill survives changed arguments and perturbed state | shown only for a hand-written skill |
| Retrieval and activation | the right skill fires at the right moment | untested; this is where the prior work failed |
| Cross-implementation grounding | a skill induced on a mock application executes on the real product | untested |
| Net benefit | gains exceed false activation and context cost | untested |

Even at 70% per stage, the product is roughly 17%. Extraction is a clustering
problem while invocation is a control problem, and only the first has been
touched so far.

## The one structural advantage

The design is non-parametric with fallback, so model weights are never updated.
The dominant failure mode of the prior work, degrading a capability the base model
already had, is therefore unavailable. An unhelpful skill can go unused, and the
system falls back to primitive actions.

That bounds the downside. The expected failure shape is "no significant gain"
rather than "the agent got worse", which is what makes a small, cheap go/no-go
the rational next step instead of committing full resources.

## What raises the probability

| Measure | Stage it protects |
|---|---|
| Semantic skill representation with no coordinates, DOM selectors, or button paths | cross-implementation grounding |
| Preconditions decidable from the visible interface | activation |
| Postconditions verified against application state, not action completion | false success |
| Counterfactual validation across arguments, perturbations, and negative cases | induction quality |
| Mandatory fallback to primitive actions | bounded downside |
| Fixed-frequent-skill and random-skill controls | separates mechanism from added context |
| Two model backbones | rules out a single-model artifact |

## Go/no-go

Run three source-to-target pairs only, with roughly 20 to 30 induced skills and
20 to 30 real target tasks each, against the no-skill, fixed-frequent-skill,
random-skill, and unverified-skill controls on two models.

Continue if at least two pairs show a 5 percentage point success gain, or a 15%
reduction in action steps without a success regression, and the direction agrees
across both models. Otherwise stop, and report the negative result with the
false-activation and grounding diagnostics that explain it.
