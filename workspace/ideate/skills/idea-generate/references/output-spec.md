# Output Spec

Return:

1. one normalized Idea Generation Brief
2. one short evidence summary
3. 5-10 candidate Idea Cards
4. wiki writeback candidates when ideas are anchored to wiki papers
5. optional open questions
6. a lightweight human feedback prompt for follow-up refinement

For each Idea Card:

- keep it concise
- include `anchor_sources` with one specific paper/wiki page or a same-type cluster of 2–4 papers/wiki pages
- include a concrete `target_problem` pain point exposed by those sources
- include `paper_insight_or_limitation`
- include at least 2 evidence anchors when possible in `evidence_chain`
- include one `minimum_experiment`
- include at least one expected metric in `expected_metric_change`
- include one main `risks` entry
- include `recommendation_reason`
- include `wiki_writeback` when `anchor_sources` refers to wiki papers/pages

Prefer fewer high-signal cards over a longer list of weak ideas.

## Wiki Writeback Candidates

When an idea uses a wiki paper/page as an anchor, add a short section or final-report block for main agent:

- anchor source path/title
- related idea IDs
- conclusions, pain points, or findings that should be compiled back into wiki
- any new external papers/sources discovered during the run

## Required Quality Checks

Before export, verify:

- every idea follows `idea-card-template.md`
- every idea names anchor sources and a specific pain point
- weak evidence is marked `low-confidence`
- every idea names a minimum validation experiment
- every idea names at least one metric
- every idea respects code, data, compute, and time constraints from the brief
- open questions are listed instead of silently filled in

## Follow-Up Feedback

After the first export, the user can ask to keep, reject, revise, re-rank, or expand ideas. Return the revised output inline in the reply text; do not write versioned files to disk.
