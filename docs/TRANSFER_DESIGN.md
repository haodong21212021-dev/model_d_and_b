# Skill Source and Transfer Target Design

Date: 2026-08-13

## The problem with a MockApp-primary design

The pilot mined skills from CUA-Gym MockApps and planned to demonstrate
improvement on WAA and OSWorld. Measured against the real application sets,
that transfer claim does not hold.

Application overlap between the 29 MockApp applications and the 148-task WAA
run used in this project is **zero**. WAA covers VS Code, LibreOffice Calc and
Writer, VLC, File Explorer, browsers, Settings, Clock, Paint, Calculator and
Notepad. MockApps cover Instagram, HubSpot, Salesforce, Slack, Notion and
similar SaaS products. No application appears on both sides, so a skill induced
from `hubspot_mock` cannot be exercised by any WAA task.

A benchmark also has to contain the target application before it can measure
transfer into it. WAA and OSWorld are desktop-application benchmarks; neither
contains the SaaS web products the MockApps imitate.

## What the task index actually contains

CUA-Gym is not primarily a MockApp corpus. Of 10,910 released tasks:

| Family | Tasks | Applications |
|---|---:|---|
| `desktop_office` | 6,071 | libreoffice_calc 2,576; libreoffice_writer 2,093; libreoffice_impress 1,402 |
| `desktop` | 1,958 | vscode 1,178; pdf 679; vlc 71; gimp 30 |
| `other` | 1,375 | mostly multi-application |
| `mock_web` | 1,075 | 29 synthesized SaaS applications |
| `multi_apps` | 430 | cross-application MockApp workflows |

The real desktop portion is **8,029 tasks**, and every one carries a
programmatic reward. These are the same real applications the desktop
benchmarks evaluate.

## Corrected design

Mine skills from the real-application portion of CUA-Gym and evaluate transfer
on benchmarks that contain those same applications.

Overlap between CUA-Gym real desktop applications and the WAA run:

| Application | CUA-Gym mining tasks | WAA tasks |
|---|---:|---:|
| libreoffice_calc | 2,576 | 23 |
| libreoffice_writer | 2,093 | 19 |
| vs_code | 1,178 | 24 |
| vlc | 71 | 21 |
| **Total** | **5,918** | **87 of 148 (59%)** |

OSWorld additionally shares `libreoffice_impress` and `gimp` with the CUA-Gym
pool, so the same induced library covers a further share of that benchmark.

This removes the synthetic-to-real gap from the primary claim: skills are
induced on real LibreOffice, VS Code and VLC, and are tested on held-out tasks
in real LibreOffice, VS Code and VLC.

## Revised role of MockApps

MockApps remain useful, but not as the source of the headline result:

1. **Mechanism validation.** Deterministic state injection and reset make them
   the cheapest place to prove that a parameterized skill survives changed
   arguments and perturbed initial states. The 3/3 calendar validation already
   used them this way.
2. **Cross-application generalization.** With 29 applications they support an
   application-disjoint split, which desktop benchmarks cannot provide at that
   breadth.
3. **Throughput.** They reset in one HTTP call, so induction and validation
   loops do not need a Windows sandbox.

The claim they support is that the skill *mechanism* generalizes across
applications, not that synthetic applications improve real-application ability.

## Consequences for the frozen split

The existing `skillforge-v1` split covers `mock_web` only. It stays valid for
the mechanism and cross-application experiments. A second split over
`desktop_office` and `desktop` families is required for the transfer claim, with
tasks held out by template inside each application so that induction never sees
an evaluation task.

## Web-application transfer, if it is wanted

If real SaaS-style web transfer becomes a goal, the target should be a benchmark
built on real deployed web software rather than a desktop benchmark. That is a
separate axis from the desktop claim above and should not be mixed into it.

## The published negative-transfer precedent

`Automating SKILL.md Generation for Computer-Using Agents via Interaction
Trajectory Mining` (arXiv 2606.20363) ran the closest published pipeline to the
one proposed here: segment GUI trajectories, cluster segments into skills, then
train a skill-aware policy on the induced vocabulary. Its source benchmark is
synthetic and its transfer checks include WebArena, so the structure matches a
synthetic-to-real setting.

Reported outcome:

| Metric | Zero-shot | After GRPO |
|---|---:|---:|
| Source skill-step accuracy | 18.5% | 20.5% |
| WebArena skill-step accuracy | 55.8% | 44.2% |
| BrowseComp+ skill-step accuracy | 43.5% | 43.3% |

Two properties of that result matter for reading it correctly. The metric is
next-skill prediction accuracy, not end-to-end task success. And the drop follows
from updating model weights toward a source-domain skill taxonomy, not from
attaching skills at inference time.

The mechanism is visible in their target-domain diagnostics: with the source
segmentation threshold, boundary F1 on WebArena falls to 0.119, and the induced
embedding reaches NMI 0.049 with silhouette -0.255. The skill boundaries and
categories learned from synthetic trajectories effectively do not exist in the
target domain, so fine-tuning toward them degraded ability the base model already
had. A most-frequent-skill baseline also beat their learned policies on the source
domain, which indicates the learned components captured class imbalance rather
than reusable composition structure.

### What this changes in this project

The dominant failure mode does not apply to a non-parametric design. Skills are
retrieved and executed at inference time and model weights are never updated, so
base capability cannot be destroyed; an unhelpful skill can at worst go unused.

A different negative-transfer channel does apply: **false activation**. A skill
induced on a mock application can be retrieved in a real application, execute
incorrectly, consume the step budget, and leave the environment in a state from
which the task can no longer be completed. In the recorded baseline, six of ten
failures already exhausted the action budget, so wasted steps are a live risk
rather than a hypothetical one. Preconditions, postconditions, and fallback to
primitive actions are the controls against this channel, not optional polish.

The result is also a warning about representation. Clustering by action signature
is source-bound. The first discovery run in this project reproduced a small
version of the same failure: browser tasks for enabling Do Not Track and for
changing default font size were merged into one candidate purely because their
click skeletons matched. That is why candidates now carry instruction examples
and a review status, and why the skill representation must be semantic rather
than a coordinate or DOM action sequence.

### Metrics that must be reported

To avoid repeating the precedent, and to let a reviewer rule out the same
confounds, every transfer experiment reports:

| Metric | Purpose |
|---|---|
| End-to-end task success on real software | primary claim; skill-step accuracy is not a substitute |
| False activation rate | direct measure of the negative-transfer channel |
| Fallback trigger rate and fallback success | evidence the conservative design works |
| Success with skills disabled, same tasks and seeds | confirms no aggregate harm |
| Most-frequent-skill baseline | the control that defeated the published pipeline |
| Random-skill baseline | separates skill content from extra prompt context |
| Cross-model consistency | rules out a single-model artifact |
