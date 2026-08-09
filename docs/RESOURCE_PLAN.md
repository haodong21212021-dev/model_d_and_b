# SkillForge-CUA Resource Plan

Resource audit date: 2026-08-09

## Detected resources

### Remote development host

| Resource | Detected state |
|---|---|
| GPU | No devices exposed; PyTorch CUDA count is 0 |
| CPU | 4-core cgroup quota, 128 CPUs in cpuset |
| Memory | 556 GiB total, about 343 GiB available during audit |
| Root disk | 91 GiB available |
| Shared notebook storage | About 908 TiB available |
| Docker host | 128 CPUs, about 598 GB memory |
| CUDA toolkit | Present, but no GPU device allocation |

### Existing experiment infrastructure

| Resource | Detected state |
|---|---|
| AGS/WAA credentials | Configured |
| Windows sandbox | Live smoke passed |
| Sandbox startup | 10.7 seconds |
| Screen / screenshot | 1024×768 / 499,353 bytes |
| CUA-Gym-Hub | 98 MockApps available |
| Existing WAA trajectories | 148 total, 89 strict successes |
| Qwen3.7-Plus (DashScope) | Active; returns a real chat completion |
| MiniMax-M3 (hosted) | Active; returns a real chat completion |
| Qwen3.6-35B-A3B (`ms-xld6dn4f`) | HTTP 503 on every path variant |
| Other `ms-*` TI gateway endpoints | Either HTTP 503, or HTTP 200 carrying `InvalidParameter.TGWRouteFailure`; none serve completions |
| Cluster `sglang` endpoints | Unreachable from this host |

A gateway that answers HTTP 200 with a `TGWRouteFailure` body is not a usable
model service, so endpoint checks must assert a parsed completion rather than a
status code.

The AGS smoke sandbox was closed after the screenshot check. A later resource
check found 12 unrelated `harness_opt` sandboxes active at once, each configured
with 4 CPU cores and 8 GiB memory. A pilot sandbox created during that workload
returned repeated HTTP 500 errors from `/screenshot`, so scientific A/B runs
should use reserved capacity rather than compete with that job.

### Public CUA-Gym data currently released

The downloaded task index contains 10,910 rows. The relevant `mock_web` subset
contains 1,075 tasks across 29 applications:

- 783 hard;
- 266 medium;
- 26 easy.

The frozen split (`skillforge-v1`) contains:

| Partition | Tasks |
|---|---:|
| Skill induction | 500 |
| Skill validation | 165 |
| Seen-application test | 166 |
| Unseen-application development | 139 |
| Unseen-application test | 105 |

Application sets are disjoint. Test-time skill updates are forbidden in the
primary experiment.

## Minimum resource request

This is sufficient for the first model-level A/B gate:

1. **Model**
   - use the verified Qwen3.7-Plus endpoint with concurrency 2;
   - preferably restore the Qwen3.6-35B-A3B endpoint for an open-weight-scale
     comparison; or
   - allocate 2× H20 96GB for one TP=2 inference replica.
2. **Concurrency**
   - model concurrency: 2 stable requests;
   - two **reserved** AGS Windows sandboxes, not shared with datagen;
   - sandbox TTL: at least 2 hours.
3. **Pilot workload**
   - 3 train applications and 3 held-out applications;
   - 30 frozen test tasks;
   - four systems and three seeds (360 episodes);
   - maximum 20 actions per episode.
4. **Storage**
   - 50–100 GB for screenshots, traces, and evaluator artifacts.

The pilot advances only with at least +5 percentage points task success, or at
least 15% fewer actions/model calls without lower success.

## Recommended formal experiment

1. **Model serving**
   - hosted endpoint with stable concurrency 4–8; or
   - 4× H20: two TP=2 inference replicas;
   - up to 8× H20 only if running planner/verifier replicas concurrently.
2. **AGS**
   - 4–8 concurrent Windows sandboxes;
   - TTL of at least 24 hours, or explicit per-task recreation;
   - fixed image/template version.
3. **Workload**
   - 500 skill-induction tasks;
   - 165 independent skill-validation tasks;
   - 271 frozen primary test tasks (166 seen-app + 105 unseen-app);
   - four systems × three seeds: 3,252 primary evaluation episodes.
4. **Storage**
   - reserve 300–500 GB on shared storage for complete visual traces.

No SFT or RL is required for the primary paper. Optional selector LoRA should
only be considered after the non-parametric skill experiment passes.

## Current blockers

1. The configured Qwen3.6 endpoint responds with HTTP 503 on every path variant.
   Qwen3.7-Plus and MiniMax-M3 are the only endpoints that currently return
   completions, and both are third-party hosted services rather than the
   open-weight model the study targets.
2. The remote host cannot directly reach Hugging Face. The task parquet was
   transferred through the cloud agent. Three selected official task bundles
   were extracted locally and transferred for smoke evaluation.
3. The remote Python environment was missing `sshtunnel` and `vncdotool`; both
   were installed and AGS sandbox creation now passes.
4. The available runtime is Python GuiAgent + `V2ActionSpace`; no NodeREPL
   implementation or repository is present in the accessible code. A true
   NodeREPL-vs-NodeREPL+Skill comparison needs that repository/path or a new
   adapter implementation.
5. The current AGS pool is occupied by 12 external datagen sandboxes. The
   corrected baseline run was stopped after repeated screenshot failures and
   produced no valid scientific score.
