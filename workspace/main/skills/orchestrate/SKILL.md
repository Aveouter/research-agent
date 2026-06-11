---
name: orchestrate
description: Task decomposition and worker dispatch. Main delegates C2/C3 complex tasks to orchestrate agent, which decomposes, dispatches to workers, and returns synthesized results.
---

# orchestrate

## 概述 / Overview

将 C2/C3 级复杂任务的拆解与派发工作委托给专门的 `orchestrate` agent。Main 负责初步分析和 judge 审查；orchestrate 负责拆解、派发 worker、合成结果。

**Triggers**: 任何 C2/C3 级任务（论文入库、论文分析、idea 生成、文献查询等），main 完成初步分析后使用本 skill 委托给 orchestrate。

## 架构变更 / Architecture Change

```
Before (flat):  Main → [ingest, curate, extract, critic, design, spec, audit, ideate, judge]
After  (nested): Main → Orchestrate → [ingest, curate, extract, critic, design, spec, audit, ideate, judge]
                     ↑ depth 0       ↑ depth 1      ↑ depth 2 (leaf workers)
```

Orchestrate 是 depth-1 orchestrator（需 `maxSpawnDepth: 2`），拥有 `sessions_spawn` 权限来管理 depth-2 的 worker subagents。

## 应用场景 / Scenario

Main 收到用户的 C2/C3 级科研需求后：
1. Main 执行初步分析（C0-C3 分级、意图识别、wiki 检索）
2. Main 委托 orchestrate 进行任务拆解和 worker 派发
3. Orchestrate 拆解→派发→等待→合成，返回汇总报告
4. Main 收到汇总报告后，按需派 judge 审查各 worker 产出
5. Main 向用户汇报最终结果

## 编排步骤 / Orchestration Steps

### Step 0: Main 初步分析

Main 先执行知识检索（读 wiki index、搜索相关页面、必要时 browser 补充），然后整理以下上下文包：

```
用户原始需求: <完整原文>
复杂度: C2 / C3
意图类型: 论文入库 / 论文分析 / idea 生成 / 文献查询 / 其他
推荐路由: <建议的 worker 列表和执行顺序>
已知上下文:
  - Wiki 页面: <路径列表>
  - 已知材料: <已有产出、browser 搜索结果等>
  - 补充信息: <browser 搜索结果>
用户约束: <用户提出的限制条件>
```

### Step 1: 委托 Orchestrate

```
sessions_spawn(
  agentId: "orchestrate",
  task: """请拆解并执行以下用户需求。

## 用户原始需求
{user's original message}

## Main 初步分析
- 复杂度: C2 / C3
- 意图: {intent}
- 推荐路由: {suggested workers and order}

## 已知上下文
- Wiki 页面: {paths}
- 已知材料: {context}
- 补充信息: {browser search results}

## 用户约束
{constraints}

## 指令
1. 将需求拆解为最少、可独立执行的子任务
2. 标注依赖关系和可并行执行的任务
3. 将每个子任务派发给最匹配的 worker subagent
4. 等待所有 worker 完成
5. 合成结果并以结构化汇总报告返回
""",
  mode: "run",
  runTimeoutSeconds: 3600
)
```

**超时说明：** orchestrate 的超时应覆盖其派发的所有 worker 的总时间。对于完整 paper-pipeline（S1-S6），预留 3600s（60 min）。较简单的任务可缩短。

### Step 2: 接收 Orchestrate 汇总报告

Orchestrate 完成后返回结构化汇总报告，包含：
- 执行摘要（总子任务数、成功/失败数）
- 各子任务结果（worker、状态、关键发现、完整 inline reply 原文）
- 建议的后续步骤

### Step 3: Judge 审查

对 orchestrate 汇总中标记为成功的 worker 产出，按需派 `judge` 审查。必须使用汇总报告中对应 worker 的完整 inline reply 原文，不要只传关键发现摘要：

```
sessions_spawn(
  agentId: "judge",
  task: """审查以下 worker 产出。

原任务: {task description}
Worker: {worker agentId}
Worker 产出: {worker's inline reply content}
""",
  mode: "run",
  runTimeoutSeconds: 300
)
```

**审查策略：**
- 关键产出（extract, critic, design, ideate）必须 judge
- 辅助产出（curate 查询、ingest 入库）可选 judge
- 如果 orchestrate 已经做了基础质量检查（回复非空且包含预期结构），judge 聚焦内容质量

### Step 4: 向用户汇报 + 回写 Wiki

按 main AGENTS.md 的「结果呈现」和「结果回写」流程执行。

## Orchestrate 与 Main 的职责边界

| 职责 | Main (depth 0) | Orchestrate (depth 1) | Worker (depth 2) |
|------|---------------|----------------------|-------------------|
| 用户对话 | ✅ | ❌ | ❌ |
| 初步分析 + 意图识别 | ✅ | ❌ | ❌ |
| Wiki 检索 | ✅ | 只读（上下文理解） | 按需 |
| 任务拆解 | ❌ | ✅ | ❌ |
| Worker 派发 | ❌ | ✅ | ❌ |
| 深度分析/生成 | ❌ | ❌ | ✅ |
| Judge 审查 | ✅ | ❌ | ❌ |
| 结果汇报 + Wiki 回写 | ✅ | ❌ | ❌ |

**关键原则：** Main 保留用户对话、初步分析、judge 审查、结果汇报、wiki 回写。Orchestrate 只管拆解和派发。Worker 只管执行。

## 输入规范 / Input Specification

Main 传递给 orchestrate 的上下文包必须包含：
- 用户原始需求（完整原文）
- Main 的复杂度判断和意图分类
- 推荐路由（至少建议首轮 worker）
- Wiki 检索结果和已知上下文
- 用户明确提出的约束

## 输出规范 / Output Specification

Orchestrate 返回给 main 的汇总报告格式：

```
## 编排完成报告

### 执行摘要
- 总子任务: N | 成功: N | 失败: N

### 各子任务结果
#### T{N}: {描述} → {worker}
- 状态: ✅/❌
- Session: {sessionKey}
- 关键发现: {summary}
- 完整产出（供 main 派 judge 审查，禁止截断）:
  ```markdown
  {worker inline reply 原文全文}
  ```

### 建议
- Judge 审查: {list of outputs to judge; reference the corresponding 完整产出 blocks, not 关键发现 summaries}
- 汇报要点: {key findings to present}
```

## 示例 / Examples

### Example 1: 完整论文分析（C3）

User: "帮我完整分析这篇论文 /Users/papers/attention.pdf"

1. Main 做 pre-flight：读 wiki index，确认无已有条目。意图=论文分析，复杂度=C3，路由=paper-pipeline (S1-S6)。
2. Main 委托 orchestrate，传入分析结论和路由建议。
3. Orchestrate 拆解为 T1(ingest)→T2(extract)→T3(critic)→T4(design)→T5(spec)→T6(audit)，串行派发。
4. Orchestrate 返回汇总报告，含 6 个子任务结果、关键发现，以及每个成功 worker 的完整 inline reply 原文（完整产出）。
5. Main 派 judge 审查 S2-S5 关键产出。
6. Judge 通过后，main 向用户汇报。

### Example 2: Idea 生成 + 文献查询（C2）

User: "帮我查一下联邦学习里的隐私保护方法，然后基于这些方法生成研究 idea"

1. Main 分析：两个子任务——文献查询(curate) + idea 生成(ideate)，依赖关系是 curate→ideate。
2. Main 委托 orchestrate。
3. Orchestrate 拆解为 T1(curate: 隐私保护方法查询)→T2(ideate: 基于查询结果生成 idea)，串行派发。
4. Orchestrate 返回汇总。
5. Main 派 judge 审查 ideate 产出，向用户汇报。

### Example 3: 多篇独立论文分析（C2）

User: "帮我分别分析 attention.pdf 和 resnet.pdf 的实验设置"

1. Main 分析：两个独立论文分析，无依赖，可并行。
2. Main 委托 orchestrate，推荐 extract × 2（并行）。
3. Orchestrate 拆解为 T1(extract: attention) 和 T2(extract: resnet)，并行派发。
4. 两者完成后合成汇总返回 main。
5. Main 审查、汇报。
