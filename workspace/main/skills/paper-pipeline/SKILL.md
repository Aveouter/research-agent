# paper-pipeline

## 概述 / Overview

End-to-end deep paper analysis and validation. Orchestrates 6 subagents in a strict linear chain from ingestion to quality audit.

**Trigger words**: "完整分析", "full pipeline", "deep review", "S1-S6", "全流程分析", "paper pipeline", "端到端审稿"

## 应用场景 / Scenario

Deep paper analysis and validation. User provides a paper (PDF/URL) and receives a complete chain: wiki entry, experiment extraction, problem critique, validation design, implementation spec, and quality audit.

## Subagent 调用链 / Agent Chain

| # | Agent | Stage | Role |
|---|-------|-------|------|
| 1 | **ingest** | S1 | Paper PDF ingestion, structured wiki page creation |
| 2 | **extract** | S2 | Deep experiment extraction from paper text |
| 3 | **critic** | S3 | Reviewer-perspective problem and claim analysis |
| 4 | **design** | S4 | Validation experiment design for identified problems |
| 5 | **spec** | S5 | Implementation spec and claude-code task prompt generation |
| 6 | **audit** | S6 | Cross-stage quality auditing and consistency check |

## 编排步骤 / Orchestration Steps

### Pre-pipeline

Use `wiki_search` to check if paper entry exists. If found, note the page ID for downstream stages; otherwise ingest (S1) will create it.

### Per-stage spawn pattern

Each stage follows the same pattern: spawn, wait, verify output, proceed.

**S1 — ingest** | Timeout: 900s (15 min)
- `sessions_spawn(agentId: "ingest", task: "将以下论文入库。标题：{title}。PDF路径：{path}。按 Capture→Extract→Create Paper Page→Update Index 流程执行。", mode: "run", runTimeoutSeconds: 900)`
- Output: Wiki page path, raw source path, evidence_level (inline reply)
- Gate: Wiki page >= 100 lines, at least one numeric result

**S2 — extract** | Timeout: 1800s (30 min)
- `sessions_spawn(agentId: "extract", task: "对以下论文执行实验深度提取（S2）。标题：{title}。Wiki页面：{page_id}（使用 wiki_get 读取）。使用 paper-experiment-deep-extractor skill。在 reply 中直接返回完整 12 节实验提取文档（## 0–## 11）。", mode: "run", runTimeoutSeconds: 1800)`
- Input: Wiki path from S1, PDF as fallback
- Output: Inline reply containing full 12-section experiment extraction
- Gate: Reply contains all 12 sections (## 0–## 11) per extract skill template

**S3 — critic** | Timeout: 1200s (20 min)
- `sessions_spawn(agentId: "critic", task: "对以下论文执行审稿式问题分析（S3）。标题：{title}。Wiki页面：{page_id}（使用 wiki_get 读取）。S2 实验提取文档如下（从上游 agent 的 reply 中传递）：\n{S2 reply content}", mode: "run", runTimeoutSeconds: 1200)`
- Input: Wiki path, S2 experiment doc (inline)
- Output: Inline reply containing full problem analysis
- Gate: >= 1 concrete problem with evidence traceability

**S4 — design** | Timeout: 1200s (20 min)
- `sessions_spawn(agentId: "design", task: "对以下论文执行验证实验设计（S4）。标题：{title}。Wiki页面：{page_id}（使用 wiki_get 读取）。S3 问题分析文档如下（从上游 agent 的 reply 中传递）：\n{S3 reply content}。在 reply 中直接返回完整 10 节验证实验设计文档（## 0–## 9）", mode: "run", runTimeoutSeconds: 1200)`
- Input: Wiki path, S3 problem doc (inline)
- Output: Inline reply containing full validation experiment design
- Gate: Reply contains all 10 sections (## 0–## 9) per design skill template; each experiment maps to an S3 problem with expected results

**S5 — spec** | Timeout: 600s (10 min)
- `sessions_spawn(agentId: "spec", task: "生成 claude-code 任务提示词（S5）。代码仓库：{repo, optional}。S3 问题分析：\n{S3 reply content}\n\nS4 验证设计：\n{S4 reply content}", mode: "run", runTimeoutSeconds: 600)`
- Input: S3 + S4 outputs (inline), optional code repo
- Output: Inline reply containing full claude-code task prompt
- Gate: File-level specific, no unfilled placeholders

**S6 — audit** | Timeout: 600s (10 min)
- `sessions_spawn(agentId: "audit", task: "执行流水线质量审计（S6）。以下是 S2-S5 的完整产出内容：\n\n=== S2 实验提取 ===\n{S2 reply}\n=== S3 问题分析 ===\n{S3 reply}\n=== S4 验证设计 ===\n{S4 reply}\n=== S5 Codex 提示词 ===\n{S5 reply}", mode: "run", runTimeoutSeconds: 600)`
- Input: All S2-S5 inline reply content
- Output: Inline reply containing full audit report
- Gate: Covers all 6 audit dimensions; blocking issues are actionable

### Error Handling

- **Stage fails**: Log failure, inform user with stage + error detail. Offer retry or checkpoint resume.
- **Checkpoint resume**: Record completed stages **with the full inline Markdown content for each completed stage**, not only summaries or session keys. Store this checkpoint in the main session/memory or a wiki note that can be retrieved after the original session ends. When `Start stage` is S3 or later, verify that every prerequisite stage's full content is available; if any required upstream content is missing, ask the user to provide it or rerun the missing stage before continuing. Pass recovered completed output content inline and resume from the requested stage.
- **Quality gate failure**: Re-spawn same agent with previous output attached + fix instructions. One retry per stage max.

## 输入规范 / Input Specification

| Field | Required | Description |
|-------|----------|-------------|
| Paper title | Yes | Full paper title |
| PDF path or URL | Yes | Absolute path or accessible URL |
| Code repo | No | Local path or remote URL |
| User notes | No | Focus areas, constraints, questions |
| Start stage | No | Default S1; set to "S3" etc. for checkpoint resume |

## 输出规范 / Output Specification

Each stage returns its full output as inline reply text (Markdown). The orchestrator passes content between stages by embedding upstream reply text into downstream task parameters.

| Stage | Agent | Content |
|-------|-------|---------|
| S1 | ingest | Wiki page path, evidence_level |
| S2 | extract | Structured experiment extraction (12-section Markdown) |
| S3 | critic | Prioritized problem and claim analysis (8-section Markdown) |
| S4 | design | Validation experiment designs (10-section Markdown) |
| S5 | spec | Ready-to-use claude-code task prompt (Markdown) |
| S6 | audit | Cross-stage quality audit report (Markdown) |

User receives: top 3 problems, priority validation experiments, audit verdict, next steps.

## 示例 / Examples

### Example 1: Full pipeline

User: "帮我完整分析这篇论文 /Users/papers/attention.pdf"

1. Check wiki: no entry. 2. Spawn **ingest** (S1). Wiki page created. 3. Spawn **extract** (S2). Receive full experiment extraction inline. 4. Spawn **critic** (S3) with S2 content embedded. 5. Spawn **design** (S4) with S3 content embedded. 6. Spawn **spec** (S5) with S3+S4 content embedded. 7. Spawn **audit** (S6) with S2-S5 content embedded. 8. Report summary.

### Example 2: Checkpoint resume

User: "从S3继续分析 attention-is-all-you-need"

1. Retrieve the checkpoint containing the full S2 inline Markdown (not just a summary or session key). 2. If full S2 content is missing, ask the user to paste it or rerun S2. 3. Spawn **critic** (S3) with wiki + full S2 content inline. 4. Continue S4-S6 normally, recording each full stage reply in the checkpoint.
