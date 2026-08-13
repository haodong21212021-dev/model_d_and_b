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
