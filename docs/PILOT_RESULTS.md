# SkillForge-CUA Pilot Results

Date: 2026-08-09

## Available resources

- Existing WAA run: 148 trajectory result files across 12 applications.
- Strict successes: 89 (`done=true` and `final_status=success`).
- CUA-Gym repository and schemas are present on the remote development host.
- CUA-Gym-Hub commit used for MockApp validation:
  `53205689c3d88078c1375f76466d5bd799478828`.
- The current remote SSH allocation exposes no GPUs. Discovery and deterministic
  MockApp validation therefore ran on CPU.

## Discovery smoke run

The initial transparent clustering run used application/intent hard buckets and
a similarity threshold of `0.30`.

| Metric | Result |
|---|---:|
| Input trajectories | 148 |
| Strict successful trajectories | 89 |
| Candidate clusters | 15 |
| Successful trajectories covered | 39 |

Manual inspection found both useful candidates and over-broad groups:

- useful: adding world clocks with a city parameter;
- useful: renaming spreadsheet sheets with a name parameter;
- useful: changing a browser setting with setting/value parameters;
- over-broad: unrelated File Explorer tasks grouped under `other`;
- over-broad: distinct settings grouped only because their click skeletons match.

As a result, candidates are not executable by default. The pipeline now:

1. removes terminal actions before structural comparison;
2. uses complete-link rather than transitive connected-component clustering;
3. includes instruction examples in every manifest;
4. marks low-similarity and `other` clusters as `needs_review`.

## Hardened MockApp validation

A parameterized `createCalendarEvent` skill was tested on the Google Calendar
MockApp in three isolated hardened sessions. Only the harness accessed setup and
reward state; the skill interacted with the rendered UI.

| Case | Parameters changed | Reward | Primitive UI actions | Skill calls |
|---|---|---:|---:|---:|
| Architecture Review | title/time/location/description | 1 | 7 | 1 |
| Customer Follow-up | title/time/location/description | 1 | 7 | 1 |
| Experiment Retrospective | title/time/location/description | 1 | 7 | 1 |

Result: **3/3 verified**. This proves parameter substitution and programmatic
reward validation work end to end. It does not yet establish an agent-level
success-rate improvement.

## Next experimental gate

The next run requires a visible model endpoint or GPU allocation. It will compare
the same frozen held-out tasks under:

1. Computer Use primitives;
2. NodeREPL + Computer Use;
3. NodeREPL + unverified induced skills;
4. NodeREPL + verified induced skills with fallback.

The pilot expands only if verified skills improve task success by at least
5 percentage points, or reduce actions/model calls by at least 15% without
reducing success.
