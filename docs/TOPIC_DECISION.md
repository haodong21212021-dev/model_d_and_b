# 选题决策：MacroAct-CUA

Date: 2026-08-17

## 一句话

**在 CUA-Gym MockApp 上，用可验证奖励把高频成功子轨迹编译成宏动作（macro actions），再按 UltraCUA / ToolCUA 的 hybrid-action 配方做 SFT + 轻量多轮 RL，把“何时调宏动作 / 何时回退 GUI”蒸馏进 7B–14B 策略，并在 WAA / OSWorld 上测真机泛化。**

内部工作名可用 `MacroAct-CUA`；不要再用 `SkillForge-CUA` 作为对外名。

## 为什么选这个，不选别的

当前 CUA 顶会赛道里，**反复中稿的同质化范式**是：

| 工作 | venue 信号 | 共同配方 |
|---|---|---|
| OpenCUA | NeurIPS 2025 Spotlight | 大规模轨迹 + 结构化 CoT + SFT |
| UGround | ICLR 2025 Oral | 合成 GUI 数据 → grounding |
| UI-TARS / UI-TARS-2 | 工业+开源主线 | native agent + multi-turn RL |
| UltraCUA | hybrid action 代表作 | GUI 原语 ⊕ 高层 tool + SFT/RL |
| ToolCUA | hybrid path orchestration | 交错 GUI-Tool 轨迹 + RFT + Online RL |
| DART-GUI | 高效 GUI RL | 解耦 rollout/训练，7B 可跑通 |
| CUA-Gym / GUI-GENESIS | 可验证合成环境 | Mock/合成 env → 后训练 → 真机迁移 |

做同类工作（hybrid action + 可验证合成环境 + SFT/轻量 RL），审稿人已有接受模板，**同质化也能发**；这比纯诊断论文或纯非参数 skill 注入更贴当前主赛道。

### 明确放弃的方向

| 方向 | 放弃原因 |
|---|---|
| 纯 HarnessFactor / Scaffold Effect 诊断 | 叙事易饱和，且与现有 GPU/环境资产咬合弱 |
| 非参数 skill 检索为主贡献 | ASI / SkillGen / W2S 已占位；Auto-SKILL.md 还给出负迁移先例 |
| 手写 skill 库复刻 CUA-Skill | 贡献落在工程库，方法新颖性弱 |
| 再做一个通用真实 App benchmark | OSWorld / WAA / SaaS-Bench 已存在 |
| 70B+ 全参 online RL | 超出 8×H20 + 8×A800 的稳妥包络 |

### 相对 UltraCUA / ToolCUA 的楔子（必须守住）

两者的高层动作来自 **文档/代码 API** 或 **对静态 GUI 轨迹的 LLM 合成 tool**，诱导阶段**不要求环境奖励通过**。

我们的楔子：

1. **宏动作必须先在 MockApp 上通过 programmatic reward 才进入动作空间**（verification-first）。
2. 训练信号来自 **CUA-Gym 可验证合成环境**，评测落在 **真桌面（WAA/OSWorld）**，回答 ToolCUA 没有单独做成主问题的点：  
   **只在 Mock 上验证过的宏动作，作为 hybrid action 训练信号，能否提升真机成功率与步数效率？**
3. 宏动作失败必须 **fallback 到 GUI 原语**，并报告 false activation / fallback success（承接 Auto-SKILL.md 的负迁移教训，但改成 parametric hybrid 设定）。

不宣称“可执行 skill 表示”或“执行级验证”本身是新贡献（ASI/SkillGen 已有）；宣称的是 **verification-first macro action space + Mock→Real hybrid policy training**。

## 裁缝清单（写作时直接挂）

| 拼接块 | 取什么 | 我们改什么 |
|---|---|---|
| UltraCUA / ToolCUA | hybrid action、交错轨迹、path efficiency | 高层动作用 verified macros，而非 API/未验证合成 tool |
| OpenCUA | 轨迹清洗、reflective CoT、SFT 配方 | 宏调用步骤写入 CoT（何时调用 / 为何回退） |
| UI-TARS-2 / DART-GUI | 多轮 RL、解耦 rollout 与更新 | 主实验停在 7B/14B；用 MockApp 降环境成本 |
| CUA-Gym / GUI-GENESIS | 可验证 Mock 环境与任务 | 不只训权重，还把 verified macros 显式并入动作空间 |
| CUA-Skill | skill 作为一等操作对象 | 自动诱导 + 写入策略，而非手写库 + 纯检索 |
| Auto-SKILL.md | 负迁移与 frequency baseline 警示 | 强制 no-macro / random-macro / frequent-macro 对照 |

## 算力落点（8×H20 + 8×A800）

| 阶段 | 卡 | 做什么 |
|---|---|---|
| 数据与宏归纳 | CPU + 少量推理端点 | 成功轨迹聚类 → 参数化宏 → MockApp reward 验收 |
| Warmup SFT | 8×A800 | Qwen2.5-VL / UI-TARS 系 **7B 全参** 或 **14B LoRA/QLoRA**；混入 GUI 原语轨迹 + 宏调用交错轨迹 |
| Online RLVR / GRPO | 8×H20 训练 + 8×A800 侧做 vLLM rollout（或对调） | 只在 MockApp 可验证任务上多轮 RL；奖励 = 成功 + 格式 + 宏适当性 + 步数 |
| 真机评测 | AGS/WAA + OSWorld | 不更新权重；报告成功率、步数、宏调用率、fallback |

刻意不做：32B/72B 全参 online RL。可选附录：32B LoRA SFT-only 做 scale 点缀。

预期效应量（按同赛道先验校准）：相对同 backbone 的 pure-GUI SFT/RL baseline，**大约 +3～10 个绝对点**，或步数 **少 10%+**；这与 UltraCUA / ToolCUA / ASI 量级同族，足以支撑主实验叙事。

## 最小可发表实验包

1. **动作空间**：GUI primitives ⊕ verified macros（每宏带参数 schema + reward check + fallback）。
2. **训练消融**：base → SFT(GUI-only) → SFT(hybrid) → SFT+RL(hybrid)。
3. **对照**：no-macro、random-macro、frequent-macro、unverified-macro（诱导但不做 reward gate）。
4. **迁移**：Mock 持有任务 → Mock 留出 app → WAA/OSWorld 重叠/近邻 app。
5. **诊断**：false activation、fallback rate、宏相关错误 taxonomy。

## 成败闸门（两周内先过）

1. 至少 **20 个** 宏在 MockApp 上稳定通过 reward（同初始态扰动）。
2. 7B hybrid SFT 相对 GUI-only SFT，在 Mock 留出集上 **至少 +3 绝对点** 或显著更短轨迹。
3. 至少一个真机 bench（优先 WAA）上 hybrid **不显著负迁移**；若全面负迁移，则改投“verification-first macro 的 Mock→Real 失效机制”实证/分析稿，而不是硬做方法 SOTA。

## 录用判断（主观）

在完整跑通上述包、且真机不崩的前提下：

- 主赛道方法稿（NeurIPS / ICLR / ICML 主会或强 workshop → 主会迭代）：大约 **30–45%**
- 若只有 Mock 增益、真机持平：仍可讲 hybrid training signal，但概率下调到 **20–30%**
- 若真机明显变差：不要硬投方法 SOTA；转 controlled study / negative-result 叙事

## 与旧方案的关系

此前定位的 “cross-implementation grounding benchmark” 仍可作为 **诊断章节与数据资产**，但**不再作为主选题**。主线改到与 UltraCUA/ToolCUA 同族的 hybrid training，以匹配算力与顶会同质化投稿策略。
