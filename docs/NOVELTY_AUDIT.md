# Novelty Audit: MacroAct vs UltraCUA / ToolCUA / CUA-Gym

Date: 2026-08-17

## Verdict

**按顶会标准，当前一句话方法与这三篇重叠过高。**  
若仍宣称“MockApp 可验证宏动作 + hybrid SFT/RL + 真机变强变快”，审稿人很可能会判为：

> ToolCUA 的轨迹合成 hybrid 配方 × CUA-Gym 的 Mock RLVR 迁移实验，外加 UltraCUA 已标准化的 SFT→online RL 模板。

估计主会 novelty desk-reject / weak reject 风险高。原先 30–45% 的录用估计应下调到 **10–20%**，除非改掉主 claim。

## 逐项重叠

| 我们原来说的 | 已被谁占 | 重叠程度 |
|---|---|---|
| hybrid action（GUI ⊕ 高层） | UltraCUA, ToolCUA | 高 |
| 从 GUI 成功轨迹抽象高层动作 | **ToolCUA 正是主贡献**：trajectory-aware tool synthesis | 极高 |
| hybrid SFT → 再 online RL | UltraCUA；ToolCUA 还多了 critical-switch RFT | 高 |
| 用 path efficiency / tool appropriateness 奖励 | ToolCUA 的 Tool-Efficient Path Reward | 高 |
| Mock/合成环境 + programmatic / verifiable reward 做 RL | UltraCUA（17k verifiable tasks）；**CUA-Gym 主贡献** | 极高 |
| 在 Mock 上训，迁到 OSWorld / WebArena / WAA | **CUA-Gym 已报告** OSWorld +10pp 级、WebArena 正迁移；UltraCUA/ToolCUA 也报 WAA OOD | 极高 |
| 高层动作压缩步数 | CUA-Gym 还报告了 emergent multi-action tool calls，轨迹缩短 33–45% | 高 |

### 原先以为的“楔子”为什么不够

原先楔子是：**宏动作必须先过 MockApp programmatic reward。**

对照后不够硬：

1. **ToolCUA** 已从 GUI 轨迹合成 tool，并用 next-state grounding / schema 过滤；训练目标也是学何时调高层、何时回 GUI。  
   “自动挖宏 + hybrid 训练”不是空位。
2. **UltraCUA** 已对 coding-agent 抽出的 tool 做 unit test，且整条 SFT+RL 模板公开。  
   “验证后再进动作空间”只有部分差异，不是独立问题。
3. **CUA-Gym** 已经用 MockApp programmatic reward 做 RLVR，并证明权重迁到真 bench 变强。  
   “在 CUA-Gym 上训、去 WAA/OSWorld 看是否变强变快”几乎是他们结果的复述，只是我们把动作空间改成显式 macros。

结论：verification-first 可以当 **implementation detail / ablation**，不能当 **唯一 novelty**。

## 顶会审稿人会怎么问

1. 相对 ToolCUA，你们的宏动作合成差在哪？只是把合成环境换成 CUA-Gym 吗？  
2. 相对 CUA-Gym，你们不是又做了一遍 Mock RLVR + OSWorld transfer 吗？  
3. hybrid SFT/RL 相对 UltraCUA 的增量在哪？  
4. 若增益来自“有高层动作”而不是“Mock 验证门控”，那 unverified-macro 消融不过关。

这四问里，当前写法至少三问答不干净。

## 还要拼接什么才够

只“多引几篇”不够，必须改 **主问题**。下面按可发性排序。

### 推荐主线（改 claim，而不是改口号）

**主问题改成：跨实现宏动作接地（cross-implementation macro grounding）。**

> 一个在 MockApp 上用 programmatic reward 验收过的宏动作，换到它所模仿的真实软件（布局/控件/实现不同）时，还能否作为 hybrid 动作被正确调用、执行、失败回退？什么情况下正迁移 / 负迁移？

这把三篇都没当成主问题的轴立起来：

| 工作 | 他们做了 | 他们没做 |
|---|---|---|
| ToolCUA | 同环境/同轨迹分布内合成 tool 并训 orchestration | 不测 Mock 宏 → 真 App 的实现级迁移 |
| UltraCUA | 真环境 tool + 合成可验证任务 | 不以 Mock↔Real 配对宏为对象 |
| CUA-Gym | Mock 上 RL 改权重，再测真 bench | 宏不是一等公民；不解释单个 skill/macro 的跨实现成败 |

### 必须再拼接的工作（写作 + 实验都要挂上）

| 拼接 | 作用 | 怎么用才不撞车 |
|---|---|---|
| **Auto-SKILL.md** | 负迁移先例 + frequency baseline | 主动机：GUI skill 会负迁移；我们给机制与对照 |
| **ASI / SkillGen** | 可执行/可干预验证 | **引用为已有**；不宣称“可验证 skill”本身新 |
| **SGCD**（Skill-Guided Continuation Distillation） | 用 skill 只做 train-time 恢复示范，部署可扔掉 | 可选项：宏动作用作 **恢复续写脚手架**，不是部署时永久工具库——与 ToolCUA 部署期 hybrid tool 区分 |
| **CUA-Skill** | 手写 skill 库上限 | 当作 oracle / upper bound，不复刻 |
| **OpenCUA** | 数据与 CoT 工程 | 工程底座，不作 novelty |
| **BEPA**（可选） | expert→policy 同化 | 若宏轨迹与 base policy 分布差大，用来稳定蒸馏 |

最少集合：**Auto-SKILL.md + ASI/SkillGen（先行引用）+ SGCD（方法区分）+ 配对 Mock↔Real 协议**。  
UltraCUA/ToolCUA/CUA-Gym 降级为 **相关工作与训练配方引用**，不再是“我们跟他们做同一件事”。

## 改写后的可发表表述

旧（重叠过高）：

> 在 CUA-Gym 上挖已验证宏，按 UltraCUA/ToolCUA 做 hybrid SFT+RL，看 WAA/OSWorld 是否变强变快。

新（仍用同一套工程，但 claim 不同）：

> **问题**：Mock 上奖励验收过的宏动作，迁移到真实实现时，作为 hybrid 动作会带来正迁移、无效，还是负迁移？  
> **方法**：配对 Mock↔Real 应用；verification-gated 宏诱导；hybrid SFT/RL 仅作载体；强制 no/random/frequent/unverified macro 对照；报告 false activation、fallback、跨实现失败 taxonomy。  
> **贡献**：不是又一个 hybrid CUA，而是 **第一份把“跨实现宏动作接地”测清楚的受控研究**（方法增益是加分项，不是唯一命门）。

这样即使真机增益不大，论文仍可能以 **机制 + 协议 + 负结果诊断** 站住；这是相对纯 SOTA 追分更稳的顶会写法。

## 更新后的主观概率

| 版本 | 估计 |
|---|---|
| 旧 MacroAct（不改 claim） | 10–20% |
| 改成 cross-implementation macro grounding，实验完整 | 25–40%（D&B / empirical 更稳；主会方法轨看增益） |
| 再叠 SGCD 式 train-time-only macro scaffold，且有清晰优于 ToolCUA 的消融 | 上限可到 ~40%，但仍取决于真机故事是否干净 |

## 对项目的直接含义

1. **不要**再把 UltraCUA + ToolCUA + CUA-Gym 当“同质化就能发”的充分条件；同配方已经挤。  
2. **要**把主 novelty 从“训练套路”挪到“跨实现宏动作是否成立 + 为何失败”。  
3. 工程上仍可复用 MockApp、hybrid SFT/RL、WAA/OSWorld；变的是论文问题，不是扔掉代码。
