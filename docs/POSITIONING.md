# Publication Positioning

Date: 2026-08-13

## The proposal as stated

1. Use CUA-Gym MockApps as the environment.
2. Follow CUA-Skill for the skill abstraction.
3. Automatically induce many skills that are executable rather than free text,
   with execution-level checks.
4. Show the skills improve ability on real applications.
5. Build a benchmark if no objective real-application benchmark exists.

## Why points 1 to 3 do not carry novelty

Point 3 is the core claim of ASI (arXiv 2504.06821, COLM 2025). ASI already
represents skills as executable programs rather than text, verifies each induced
skill by execution against three checks, and argues explicitly that programs beat
text because they are verifiable. It reports 40.4% on WebArena, a 23.5% relative
gain over its static baseline and 11.3% relative over the text-skill system AWM,
with 10.7 to 15.3 percent fewer steps.

Adding "executable, with execution-level checks" therefore restates a published
result rather than extending it. Two further systems tighten the same axis:
SkillGen verifies a skill as an intervention so that regressions are counted, and
MIND-Skill adds reconstruction, outcome, and rubric losses.

Points 1 and 2 are reuse of published infrastructure. Both are legitimate and
neither is a contribution.

## Point 5 is not justified as stated

Objective real-application benchmarks do exist, with programmatic rewards:
OSWorld and OSWorld-Verified, WindowsAgentArena, WeaveBench, WebArena and
VisualWebArena, SaaS-Bench, and TheAgentCompany. Building another general
real-application CUA benchmark would duplicate them and invite rejection on those
grounds.

There is, however, a real gap next to it. No existing benchmark pairs a
synthesized application with the real product it imitates so that skill-level
transfer can be measured under control. CUA-Gym does measure mock-to-real transfer,
but at the level of model weights after RL, not at the level of individual skills,
and without a per-application mapping.

## The only remaining open axis

Cross-implementation grounding: a skill induced on one implementation of a product
executing against a different, real implementation of that product, with model
weights unchanged.

Published systems reuse skills within one tool API (AppWorld, BFCL-v3), within one
benchmark's websites (ASI), or without a GUI at all. The single GUI-native
automatic induction attempt reported negative transfer and did not explain the
mechanism.

## Three framings, with different risk profiles

### A. Method paper

Claim: automatically induced executable skills improve real-application success.

This competes directly with ASI, SkillGen, and W2S on method novelty and loses,
because the representation and verification contributions are already published.
The result also has to be positive for the paper to exist.

Estimated main-track acceptance: **10–20%**.

### B. Paired transfer benchmark and protocol

Claim: a benchmark and protocol that measure, per application and per skill, what
transfers from a synthesized application to the real product, plus the controls
required to make such a measurement trustworthy.

Contents:

- matched application pairs, for example `gitlab_mock` to real self-hosted GitLab,
  `shopify_admin_mock` and `amazon_mock` to Magento, `monday_mock` and `jira_mock`
  to OpenProject or Plane, `hubspot_mock` and `salesforce_mock` to Twenty CRM;
- for each pair, real-application tasks that an inducible mock skill could in
  principle satisfy, with programmatic rewards inherited from WebArena or
  SaaS-Bench;
- an annotation of which skill should apply to which task, so activation can be
  scored separately from execution;
- the mandatory control set: no skills, fixed frequent skills, random skills,
  unverified skills;
- diagnostics: false activation rate, fallback rate and fallback success, and a
  grounding-failure taxonomy.

This framing is robust to the outcome. The artifact is a contribution whether
transfer turns out positive or negative, which removes the dependency on a
favourable result.

Estimated acceptance, benchmark-oriented venue: **25–35%**.

### C. Controlled empirical study

Claim: a controlled account of what transfers from synthetic user interfaces and
why, using the published negative result as the motivation and supplying the
mechanism it left unexplained.

Requires a crisp diagnosis, for example that semantic-level steps transfer while
layout-dependent steps do not, supported by ablations that hold the induction
fixed and vary only the grounding layer.

Estimated acceptance: **20–30%**, higher if the diagnosis is clean and reproducible.

## Recommendation

Pursue B as the primary framing, with C as the analysis section inside it, and
treat any method gain as a secondary result rather than the headline. Do not
present the executable-skill representation or execution-level verification as
contributions; cite ASI, SkillGen, and MIND-Skill for those and describe the
implementation as adopted.

The same experiments serve all three framings, so the decision does not change
what to run next. It changes what the paper claims, and it removes the risk that
the entire result depends on the transfer being positive.

## Unchanged gate

Build three matched pairs first. If a skill induced on a mock application cannot
execute against the real product at all, then the benchmark still stands as a
contribution but the method direction should be abandoned rather than scaled.
