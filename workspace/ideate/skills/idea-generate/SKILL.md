---
name: idea-generate
description: 从论文、wiki、实验结果和用户约束中生成有证据支撑、可比较、可验证的研究 idea card。
---

# Idea Generate

## Overview

Generate candidate research ideas from evidence. The simple demo path still supports papers under a local `paper/` folder, but the normal OpenClaw path can also intake relevant wiki pages, paper-review outputs, experiment logs, failed attempts, repository context, and user preferences. The skill summarizes the research landscape, proposes improvement ideas, filters and ranks them, and returns the most recommended ideas inline in the reply text.

Do not produce unconstrained brainstorming. Produce ideas that are grounded in paper evidence, comparable side by side, and ready for human review or downstream evaluation. Each idea must target one concrete pain point from a specific paper/wiki page, or from a same-type cluster of 2–4 related papers; broad directions without a named pain point are not valid idea cards.

## Requirement Alignment

This skill is part of the `ideate` sub-agent. Keep it aligned with the workspace-level requirement documents:

- `docs/task-requirements.md`: four required deliverables from the task brief.
- `docs/design-paradigm.md`: mixed checklist plus harness design.
- `docs/context-intake.md`: flexible OpenClaw workspace context intake.
- `docs/interactive-refinement.md`: human feedback and second-pass refinement workflow.
- `docs/io-spec.md`: stage-by-stage input/output contract.
- `docs/skill-split.md`: current and future skill/module boundaries.
- `../../benchmarks/idea-generate/seed-qa.md`: seed benchmark cases for self-test.

## OpenClaw Compatibility

This is an OpenClaw workspace skill. It should live at:

```text
skills/idea-generate/SKILL.md
```

The skill follows the OpenClaw / AgentSkills layout: one `SKILL.md` with YAML frontmatter, optional `references/`, optional `scripts/`, and no per-agent YAML config. Resolve referenced helper files relative to `{baseDir}` or this skill directory.

## Dependencies

The scripts use the Python standard library by default. Two extractors are optional:

- `pypdf` for PDF text extraction
- `python-docx` for DOCX text extraction

Install them with:

```bash
python -m pip install -r {baseDir}/requirements.txt
```

If an optional dependency is missing, the extractor records an unavailable-extraction note instead of failing the whole run.

## Minimum Runnable Workflow

Use this workflow for the minimum runnable path. Internal scripts may write intermediate files to temp directories for processing, but the final delivery to the caller is always inline reply text (the full recommended-ideas.md content).

1. Normalize the user request into the checklist fields in `references/brief-template.md`; mark missing fields as assumptions.
2. Build a concise context digest from user-provided materials, relevant OpenClaw workspace pages, experiment results, failed attempts, code constraints, and user preferences.
3. Locate the paper folder when present. Default to `<workspace>/paper`.
4. Create a temp run directory for script intermediates (e.g., `idea-runs/YYYYMMDD-HHMMSS-<topic-slug>/`).
5. Run `scripts/build_paper_context_pack.py` to extract paper text and limitation/future-work snippets when papers are available.
6. Read the generated `paper-context.md` and `paper-context.json` if they exist.
7. As the agent, write `paper-analysis.md` with paper-by-paper summary, cross-paper findings, limitations/gaps, transferable insights, and constraints (needed by step 12's `--analysis` flag).
8. As the agent, write `draft-ideas.json` with 5-10 candidate Idea Cards (needed by steps 9-10 scripts).
9. Run `scripts/idea_dedup.py`.
10. Run `scripts/validate_idea_cards.py`.
11. Fix any validation errors.
12. Run `scripts/write_idea_markdown.py` to generate the final recommended-ideas.md.
13. **Return the complete recommended-ideas.md content inline in the reply text** along with a short summary.
14. If the ideas use wiki papers, include `Wiki writeback candidates` in the final summary.

Example commands (internal intermediates, temp dir):

```bash
python <skill-root>/scripts/build_paper_context_pack.py --paper-dir paper --topic "<topic>" --out idea-runs/<run-name>
python <skill-root>/scripts/idea_dedup.py idea-runs/<run-name>/draft-ideas.json idea-runs/<run-name>/ideas.dedup.json
python <skill-root>/scripts/validate_idea_cards.py idea-runs/<run-name>/ideas.dedup.json idea-runs/<run-name>/validation.json
python <skill-root>/scripts/write_idea_markdown.py idea-runs/<run-name>/ideas.dedup.json idea-runs/<run-name>/recommended-ideas.md --context idea-runs/<run-name>/paper-context.json --analysis idea-runs/<run-name>/paper-analysis.md
```

## Required Inputs

Before generating ideas, build or normalize an `Idea Generation Brief`. Use `references/brief-template.md`.

Try to fill these fields:

- `research_topic`
- `target_task`
- `current_baseline`
- `available_data`
- `available_code`
- `available_compute`
- `preferred_metrics`
- `hard_constraints`
- `known_failures`
- `desired_risk_level`

If some fields are missing, infer conservatively from local context and mark them as assumptions.

For the demo, only `research_topic` is strictly required. If the user does not provide it, infer from filenames, paper snippets, workspace context, or user discussion, then mark it as an assumption.

Use the checklist policy in `docs/design-paradigm.md`: continue with explicit assumptions when possible, and ask a follow-up only when there is no research topic, no evidence material, or an explicit hard constraint cannot be resolved.

## Read Order

Read only the files needed for the current request, in this order:

1. User-provided files, folders, links, or pasted notes.
2. `paper/` folder via `scripts/build_paper_context_pack.py`, if present.
3. Generated `paper-context.md`, if present.
4. Relevant wiki pages (via `wiki_get` / `wiki_search`), starting from the wiki index when available.
5. Relevant reviewed papers or extracted experiments from wiki (use `wiki_search`/`wiki_get`).
6. Experiment logs, result tables, ablations, failed attempts, or qualitative observations.
7. Relevant `memory/` or `MEMORY.md` entries for recent discussion and failures, if present.
8. Repo files needed to understand the baseline or implementation scope, if needed.

Do not bulk-load the entire wiki.

## Core Workflow

1. Build the `Idea Generation Brief`
2. Build a compact context digest when the task uses workspace context beyond papers.
3. Build paper context from `paper/` when available.
4. Write `paper-analysis.md` and `draft-ideas.json` before running dedup/validate scripts.
5. Group evidence into candidate opportunity buckets:
   - literature gaps
   - contradictory findings
   - transferable methods
   - historical failures
   - metric weaknesses
   - engineering constraints
6. Convert opportunity buckets into narrow pain points. A pain point is valid only if it names: source paper(s), affected mechanism or evaluation setting, observed limitation/failure/contradiction, and why this matters for the requested topic.
7. Generate candidate ideas using `references/generation-strategies.md`.
8. Deduplicate and cluster similar ideas.
9. Validate every idea against `references/idea-card-template.md`.
10. Score ideas lightly for:
   - evidence strength
   - testability
   - feasibility
   - novelty
   - expected impact
11. Output recommended Idea Cards using `references/idea-card-template.md`.
12. If the user provides feedback, apply `docs/interactive-refinement.md` and return the revised output inline in the reply text.

Use `references/paper-demo-output-spec.md` for the runnable demo output contract.

## Hard Rules

1. Ground every idea in evidence, not only model intuition
2. Anchor every idea to one specific paper/wiki page or a same-type cluster of 2–4 papers; name those sources explicitly
3. `target_problem` must be a concrete pain point, not a broad research area or method family label
4. Include a minimum validation experiment for every idea
5. Name at least one metric the idea expects to change
6. Identify a likely risk or failure mode for every idea
7. Mark weakly supported ideas as `low-confidence`
8. Prefer 5-10 high-signal ideas over a long noisy list
9. Do not claim a paper says something unless it appears in `paper-context.md` or another cited source
10. Prepare ideas for human review or downstream evaluation; do not declare the final winner inside this skill

## Human Feedback Refinement

After `recommended-ideas.md`, accept lightweight user feedback such as selected idea IDs, rejected ideas with reasons, new constraints, preferred risk level, or new experiment results. Use that feedback to re-rank existing ideas, revise selected ideas, or add a small number of new ideas.

Return the revised output inline in the reply text.

## Output Structure

For the final reply, return the complete recommended-ideas.md content inline and include a short summary with:

1. run directory (for reference)
2. number of papers processed
3. number of recommended ideas
4. `Wiki writeback candidates` when any idea is anchored to wiki papers: source path/title, idea IDs, and concise findings for main agent to compile into wiki

The primary artifact is the inline reply content. Each Idea Card should follow `references/idea-card-template.md`.

## Benchmark and Self-Test

When this skill changes materially, update or run the benchmark docs:

1. Extend `../../benchmarks/idea-generate/seed-qa.md` if the change adds a new behavior class.
2. Use `../../benchmarks/idea-generate/benchmark-spec.md` to build or expand QA cases.
3. Run self-test cases in clean sessions.
4. Record results with `../../benchmarks/idea-generate/self-test-report-template.md`.
5. Mention pass/fail status in the PR.

## Quality Bar

Good outputs are:

- structured
- evidence-backed
- tied to repo or task context
- easy to compare side by side
- concrete enough to pass into idea-evaluate or idea-to-prd

Bad outputs are:

- generic advice
- vague “try transformer / diffusion / rag” suggestions
- ideas without metrics
- ideas with no minimum experiment
- ideas detached from current data, code, or constraints
