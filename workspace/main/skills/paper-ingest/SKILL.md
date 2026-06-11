# paper-ingest

## 概述 / Overview

Two-stage pipeline to ingest a paper into the research wiki and verify quality: ingest creates the wiki page, curate lints for consistency. Trigger words: "入库", "ingest paper", "add to wiki", "文献笔记", "整理这篇论文".

## 应用场景 / Scenario

Add a paper (PDF or URL) to the research wiki. Produces a verified, linted wiki entry with correct metadata and evidence levels.

## Subagent 调用链 / Agent Chain

1. **ingest** — PDF ingestion, text extraction, structured wiki page creation
2. **curate** — Quality linting, metadata verification, cross-page consistency check

## 编排步骤 / Orchestration Steps

### Pre-check (main agent)

1. Use `wiki_search` to check for existing entry. Skip if already present unless user requests re-ingest.
2. Validate user provided a PDF path or URL. If neither, ask.
3. Record paper metadata for downstream context.

### Step 1: Spawn ingest

```
sessions_spawn(
  agentId: "ingest",
  task: """将以下论文入库。

## 论文信息
- 标题：{title}
- PDF路径：{pdf_path_or_url}
- 用户备注：{user_notes, if any}

## 执行要求
按 Capture → Extract → Create Paper Page → Update Index 流程处理。
完成后汇报入库位置和 evidence_level。""",
  mode: "run",
  runTimeoutSeconds: 1800
)
```

Input: user-provided title, PDF/URL, optional notes. Output: wiki page path, evidence_level. Timeout: 1800s.

### Step 2: Spawn curate

After ingest completes, before reporting to user:

```
sessions_spawn(
  agentId: "curate",
  task: """对新入库页面执行质量检查。

## 目标页面
{ingest output: wiki page path}

## 检查范围
1. frontmatter 完整性（title, authors, year, venue, evidence_level）
2. evidence_level 与实际阅读深度一致
3. Results 是否包含具体数字
4. 孤立链接、矛盾 claim、index.md 条目正确性

输出 lint report。不修改 raw sources。""",
  mode: "run",
  runTimeoutSeconds: 600
)
```

Input: ingest inline reply. Output: lint report (pass/fail, findings). Timeout: 600s.

### Step 3: Report to user

- **Curate passes**: Report wiki path, evidence_level, key metadata. Suggest next steps (paper-review, idea-generate, cross-paper compare).
- **Curate finds blocking issues**: Report issues to user. Do not auto-re-spawn ingest.

### Error handling

| Stage | Failure | Action |
|-------|---------|--------|
| ingest | PDF unreadable | Ask user for alternative source |
| ingest | Extract insufficient | Suggest manual abstract entry |
| curate | Blocking lint issues | Report to user, await instruction |

### Quality gate

The curate stage is the quality gate for this skill — no separate `reviewer` spawn. For stricter review (benchmark scoring), spawn `reviewer` separately.

## 输入规范 / Input Specification

| Field | Required | Description |
|-------|----------|-------------|
| PDF path or URL | Yes | Absolute path or accessible URL |
| Title | Recommended | Extracted from PDF if omitted |
| User notes | Optional | Focus areas or special instructions |

## 输出规范 / Output Specification

User receives:

```
✅ 论文已入库并通过质量检查
📁 Wiki 页面：{path}
📊 Evidence level：{level}
🔍 Curate：{N} 项通过 / {M} 个建议
💡 下一步：paper-review / idea-generate / curate compare
```

## 示例 / Examples

**Example 1**: User: "帮我把 /workspace/raw/sources/2024-01-15-mhkc.pdf 入库"
→ Pre-check (not in wiki) → spawn ingest (1800s) → page created → spawn curate (600s) → 0 blocking, 1 suggestion → report success.

**Example 2**: User: "入库 https://arxiv.org/abs/2401.01234，重点看实验设计"
→ Pre-check → spawn ingest with user note → page created → spawn curate → report, suggest paper-review for deeper experiment analysis.
