---
name: brainstorm
description: Research idea generation from literature. Two-stage chain: curate wiki context then ideate evidence-grounded research ideas.
---

# brainstorm

## 概述 / Overview

Two-stage orchestration: **curate** produces quality-checked literature context, then **ideate** generates structured research idea cards. Use when the user wants research opportunities grounded in wiki evidence, not speculation.

**Triggers**: "brainstorm ideas", "research ideas", "generate ideas", "research directions", "find research gaps", "科研 idea", "研究思路", "头脑风暴"

## 应用场景 / Scenario

Generate research ideas from existing wiki literature.

## Subagent 调用链 / Agent Chain

1. **curate** -- Wiki curation, quality linting, cross-paper comparison, literature queries
2. **ideate** -- Research idea generation, opportunity synthesis, deduplication, validation

## 编排步骤 / Orchestration Steps

### Step 0: Pre-flight

Main agent uses `wiki_get` to read the wiki index and relevant domain pages. If insufficient, browser-searches arXiv/Scholar. Collect page IDs, summaries, gaps into a context packet.

### Step 1: Spawn curate (timeout: 900s)

```
sessions_spawn(
  agentId: "curate",
  task: """Prepare a curated context digest for research idea generation.

## Scope
- Domain / papers: {user domain or paper list}
- Focus areas: {user constraints}

## Produce
1. Cross-paper comparison: methods, datasets, metrics, evidence_level
2. Lint report: contradictions, gaps, stale claims in scope
3. Literature summary: limitations, future-work signals, untested claims
4. Gap list: concrete pain points from 2-4 same-type paper clusters

## Constraints
- Wiki content only. Cite page_id for every claim. Distinguish evidence levels.
- Output structured Markdown.

## Context from main agent
- Wiki pages read: {paths}
- Key facts: {summary}
- Supplementary sources: {URLs or none}""",
  mode: "run",
  runTimeoutSeconds: 900
)
```

### Step 2: Review curate output (timeout: 300s)

Spawn `reviewer` to validate digest (completeness, evidence accuracy, gap specificity). On FAIL, send fix prompt to curate via `sessions_send` and re-review. Max 2 fix rounds; then escalate to user.

### Step 3: Spawn ideate (timeout: 1200s)

```
sessions_spawn(
  agentId: "ideate",
  task: """Generate research idea cards from curated context.

## Curated context
{reviewed curate output}

## User requirements
{domain, constraints, focus}

## Requirements
- 5-10 cards, each anchored to a paper or 2-4 paper cluster with named pain point
- Per card: pain point evidence, why now, proposed mechanism, minimum validation experiment, expected metric, risk
- Deduplicate; mark weak cards low-confidence
- Return complete idea cards inline in reply text
- Include wiki writeback candidates""",
  mode: "run",
  runTimeoutSeconds: 1200
)
```

### Step 4: Review ideate output (timeout: 300s)

Spawn `reviewer` to validate cards (evidence anchoring, testable experiments, deduplication). Same fix-loop rules.

### Step 5: Present and writeback

1. Present summary table (title, anchor papers, novelty, risk, cost) and idea cards to user.
2. If writeback candidates reference existing wiki pages, spawn `curate` to update them.
3. Suggest next steps (run experiment, deep-dive, ingest more papers).

## 输入规范 / Input Specification

| Field | Required | Description |
|-------|----------|-------------|
| Domain / topic | No | Scope for idea generation. Defaults to all wiki papers. |
| Paper list | No | Specific papers (titles, wiki paths, URLs). |
| Constraints | No | Methods, datasets, problems, time horizon. |

Minimum: domain/topic or at least one paper reference. If neither, ask user.

## 输出规范 / Output Specification

1. **Idea summary table** for quick scanning
2. **Detailed idea cards** inline in reply text with full evidence chain and validation plan
3. **Wiki update notice** for any updated pages
4. **Next-step suggestions**

## 示例 / Examples

**Example 1 -- Domain-scoped**: User asks "帮我找联邦学习领域的研究空缺". Pre-flight finds 5 FL papers. curate produces comparison and gaps. ideate generates 7 cards. reviewer passes both. Present top ideas, update wiki comparison pages.

**Example 2 -- Paper-anchored**: User asks "基于 MHKC 和 FedDyn 生成 idea". curate cross-compares, highlights complementary weaknesses. ideate produces 5 cards anchored to both papers. Present with validation experiment suggestions for top 2.
