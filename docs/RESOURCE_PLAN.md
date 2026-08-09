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
| Qwen3.6-35B-A3B endpoint | Configuration and credential present, service returns HTTP 503 |
| Internal historical endpoint | Unreachable |

The AGS smoke sandbox was closed after the screenshot check.

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
   - restore one OpenAI-compatible multimodal Qwen3.6-35B-A3B endpoint; or
   - allocate 2× H20 96GB for one TP=2 inference replica.
2. **Concurrency**
   - model concurrency: 2 stable requests;
   - AGS Windows sandboxes: 2;
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

1. The configured Qwen endpoint responds with HTTP 503 for both `/models` and
   `/chat/completions`.
2. The remote host cannot directly reach Hugging Face. The task parquet was
   transferred through the cloud agent; the larger task archive transfer is
   slower but not required for split construction.
3. The remote Python environment was missing `sshtunnel` and `vncdotool`; both
   were installed and AGS sandbox creation now passes.
